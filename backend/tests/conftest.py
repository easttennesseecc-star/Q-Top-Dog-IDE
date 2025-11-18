"""
Test configuration for backend tests.

Goals:
- Disable background loops (autopilot, push reminders) to prevent hangs.
- Isolate assistant inbox storage to a test-specific file to avoid cross-test interference.
- Ensure FastAPI lifespan runs so DB + AI manager initialize for all tests via a shared TestClient fixture.
"""
import os
from pathlib import Path
import pytest
import sys
from fastapi.testclient import TestClient

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# -----------------------
# Session-level settings
# -----------------------

# Disable background loops unequivocally during tests
os.environ.setdefault("ASSISTANT_AUTOPILOT", "false")
os.environ.setdefault("REMINDER_LOOP_ENABLED", "false")
os.environ.setdefault("REMINDER_PUSH_ENABLED", "false")
os.environ.setdefault("PYTHONWARNINGS", "ignore")

# Use a test-local inbox store to avoid sharing with dev runs
TEST_INBOX = Path(".assistant_inbox.test.json").resolve()
os.environ.setdefault("ASSISTANT_INBOX_STORE", str(TEST_INBOX))

# Use a test-local SQLite database file to allow multiple connections across threads
TEST_DB = Path("./test_topdog_ide.db").resolve()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB}")

# Always disable regulated domains for tests for simpler defaults
os.environ["ENABLE_REGULATED_DOMAINS"] = "false"


def pytest_sessionfinish(session, exitstatus):  # type: ignore
    """Cleanup test artifacts we created (best-effort)."""
    try:
        if TEST_INBOX.exists():
            TEST_INBOX.unlink()
    except Exception:
        pass
    # Optionally clean DB file to avoid residue between runs
    try:
        if TEST_DB.exists():
            TEST_DB.unlink()
    except Exception:
        pass


def pytest_sessionstart(session):
    """Initialize test session.

    Note: Compliance enforcement remains active by default. Use headers to control behavior per test:
    - X-Compliance-Bypass: true   (skip enforcement)
    - X-Compliance-Mode: skip     (skip enforcement)
    - X-Compliance-Mode: enforce  (force enforcement)
    """
    pass


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async (requires pytest-asyncio)"
    )


def pytest_collection_modifyitems(config, items):
    """Add markers to tests"""
    for item in items:
        if "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        elif "benchmark" in item.nodeid:
            item.add_marker(pytest.mark.benchmark)
        elif "performance" in item.nodeid or "perf" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        elif "accuracy" in item.nodeid:
            item.add_marker(pytest.mark.accuracy)


# Ensure pytest-asyncio plugin is loaded
pytest_plugins = ["pytest_asyncio"]


# -----------------------
# Global fixtures
# -----------------------

@pytest.fixture
def test_client():
    """Shared TestClient that guarantees lifespan runs so DB + AI manager are initialized.

    Note: We no longer purge DB state between tests; uniqueness is enforced via per-test IDs.
    """
    from backend.main import app
    with TestClient(app) as client:
        yield client


@pytest.fixture
def ai_manager(test_client):
    """Provide AI orchestration manager via app.state for tests that request it."""
    return test_client.app.state.ai_orchestration_manager


@pytest.fixture
def orchestration_service(test_client):
    """Provide orchestration service via app.state for tests that request it."""
    return test_client.app.state.orchestration_service
