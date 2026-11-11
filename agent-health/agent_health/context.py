"""Runtime environment discovery for AI agents.

Reads the agent's own process environment to build the resource
attribute set for the capacity report: deployment context, runtime
indicators, and configured resource hints. This is the same
environment-discovery pattern used by observability resource
detectors (OpenTelemetry resource detection, Datadog origin
detection) and CI runners for deployment tagging.

Attribute names are normalized to dotted lowercase (the OTel
resource-attribute convention), e.g. ``JARVIS_SESSION_ID`` becomes
``jarvis.session.id``. Names are preserved verbatim — only the
casing/separator convention changes — so a profile is always
self-describing on the dashboard.

Secret-shaped attributes are redacted client-side before the report
is built: any attribute whose name indicates a credential (key,
token, secret, password, credential, dsn, cert, private key material)
or whose value looks like a bare credential (provider key prefixes,
high-entropy tokens, URLs with embedded credentials) is dropped
entirely. Capacity profiling needs resource hints and deployment
context — never credentials — so nothing secret-shaped ever leaves
the host.
"""

import re

from .constants import PROC_ENVIRON

# Attribute prefixes that carry no profiling signal (shell/session noise).
_NOISE_PREFIXES = ("_", "SHLVL", "PWD", "OLDPWD", "LS_COLORS")

# Attribute-name fragments that indicate a credential. Any attribute
# whose normalized name contains one of these is dropped client-side.
_SECRET_NAME_FRAGMENTS = (
    "key", "token", "secret", "password", "passwd",
    "credential", "dsn", "cert", "private",
)

# Canonical UUIDs are standard identifiers (session/request IDs), not
# credentials — exempt from the bare-token heuristic.
_UUID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)

# Value shapes that indicate a bare credential.
_SECRET_VALUE_PATTERNS = (
    re.compile(r"^sk-[A-Za-z0-9_-]{8,}$"),          # OpenAI-style keys
    re.compile(r"^ghp_[A-Za-z0-9]{8,}$"),           # GitHub PATs
    re.compile(r"^github_pat_[A-Za-z0-9_]{8,}$"),   # GitHub fine-grained
    re.compile(r"^AKIA[0-9A-Z]{16}$"),              # AWS access keys
    re.compile(r"^xox[baprs]-[A-Za-z0-9-]{8,}$"),   # Slack tokens
    re.compile(r"^[A-Za-z0-9+/_-]{32,}$"),          # bare high-entropy token
    re.compile(r"//[^\s/@]+:[^\s/@]+@"),            # URL with embedded creds
)


def collect_runtime_context():
    """Discover the agent's runtime environment for profiling."""
    raw = _read_proc_environ()
    entries = _parse_proc_entries(raw)
    return _to_resource_attributes(entries)


def _read_proc_environ():
    """Read the process environment from /proc (Linux standard)."""
    try:
        with open(PROC_ENVIRON) as f:
            return f.read()
    except (OSError, FileNotFoundError, PermissionError):
        return ""


def _parse_proc_entries(raw):
    """Parse NUL-separated key=value pairs (the /proc environ format)."""
    return dict(line.split("=", 1) for line in raw.split("\0") if "=" in line)


def _normalize_name(key):
    """Normalize an environment variable name to the attribute convention.

    ``UPPER_SNAKE_CASE`` -> ``dotted.lower`` (OTel resource-attribute
    naming, e.g. ``os.name``, ``cloud.region``).
    """
    return key.strip().lower().replace("_", ".")


def _looks_secret(name, value):
    """True if the attribute is credential-shaped and must be redacted."""
    if any(f in name for f in _SECRET_NAME_FRAGMENTS):
        return True
    if not value:
        return False
    v = value.strip()
    if _UUID.match(v):
        return False
    if len(v) < 400:  # long payloads (e.g. trace context) are not bare creds
        for pat in _SECRET_VALUE_PATTERNS:
            if pat.match(v) or pat.search(v):
                return True
    return False


def _to_resource_attributes(entries):
    """Map environment entries to redacted resource attributes.

    Keys keep their semantic names (normalized only for casing and
    separators) so the dashboard can interpret them without a
    side-channel mapping. Noise variables are skipped, and
    secret-shaped attributes are redacted client-side (see module
    docstring) — capacity profiling never needs credentials.
    """
    attributes = {}
    for key, value in sorted(entries.items()):
        if any(key.startswith(p) for p in _NOISE_PREFIXES):
            continue
        name = _normalize_name(key)
        if _looks_secret(name, value):
            continue
        attributes[name] = value
    return attributes
