'use strict';
// Redaction contract: credential-shaped attributes must NEVER be collected.
const assert = require('assert');
const { collectRuntimeContext } = require('..');

const env = {
  OPENAI_API_KEY: 'sk-TESTSUPERSECRET123',
  GITHUB_TOKEN: 'ghp_TESTSECRET',
  DATABASE_URL: 'postgres://user:pass@db.internal/prod',
  HTTPS_PROXY: 'http://hatch-runtime:TOKEN@hatch-egress-proxy:3128',
  AWS_SECRET_ACCESS_KEY: 'awssecrettest',
  RUNTIME_CONTEXT_TOKEN: '8c94c2a44c7c4639923eac11eb93cfcc',
  GCLOUD_SERVICE_ACCOUNT: 'x-----BEGIN RSA PRIVATE KEY-----x',
  SLACK_WEBHOOK_URL: 'https://hooks.slack.com/services/T000/B000/xxxx',
  AUTH_ASSERTION: 'eyJhbGciOiJub25lIn0.eyJzdWIiOiJ1c2VyIn0.sig',
  // these must SURVIVE:
  SESSION_ID: 'd750a240-2d6d-4a6b-901a-5852d8e29254',
  HATCH_REGION: 'zch',
  AGENT_MAX_WORKERS: '6',
  _NOISE: 'x', PWD: '/tmp',
};

const attrs = collectRuntimeContext(env);
for (const gone of ['openai.api.key', 'github.token', 'database.url', 'https.proxy', 'aws.secret.access.key', 'runtime.context.token', 'gcloud.service.account', 'slack.webhook.url', 'auth.assertion']) {
  assert.ok(!(gone in attrs), 'LEAKED: ' + gone);
}
for (const keep of ['session.id', 'hatch.region', 'agent.max.workers']) {
  assert.ok(keep in attrs, 'LOST: ' + keep);
}
console.log('✓ credentials redacted, non-secret attributes preserved');
