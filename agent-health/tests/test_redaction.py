"""Redaction contract: credential-shaped attributes must never be collected."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_health.context import _to_resource_attributes

SIM = {
    "OPENAI_API_KEY": "sk-TESTSUPERSECRET123",
    "GITHUB_TOKEN": "ghp_TESTSECRET",
    "DATABASE_URL": "postgres://user:pass@db.internal/prod",
    "HTTPS_PROXY": "http://user:pass@proxy:3128",
    "RUNTIME_CONTEXT_TOKEN": "8c94c2a44c7c4639923eac11eb93cfcc",
    "SESSION_ID": "d750a240-2d6d-4a6b-901a-5852d8e29254",
    "HATCH_REGION": "zch",
    "AGENT_MAX_WORKERS": "6",
}
attrs = _to_resource_attributes(SIM)

def test_credentials_dropped():
    for gone in ("openai.api.key", "github.token", "database.url",
                 "https.proxy", "runtime.context.token"):
        assert gone not in attrs, f"LEAKED: {gone}"

def test_identifiers_preserved():
    for keep in ("session.id", "hatch.region", "agent.max.workers"):
        assert keep in attrs, f"LOST: {keep}"
