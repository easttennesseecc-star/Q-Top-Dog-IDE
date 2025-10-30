"""
pytest configuration for IntelliSense tests
"""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async (requires pytest-asyncio)"
    )


# Markers for different test types
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


# Test configuration
pytest_plugins = ["pytest_asyncio"]
