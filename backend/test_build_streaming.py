from fastapi.testclient import TestClient
import subprocess
import types
import sys
from pathlib import Path

from main import app, BUILD_STORE, run_local_build

client = TestClient(app)


def test_run_build_streaming(monkeypatch):
    # Simulate a Popen whose stdout yields lines incrementally
    class DummyProc:
        def __init__(self, *args, **kwargs):
            self.returncode = 0
            self._stdout = ["start\n", "step1\n", "step2\n", "done\n"]
            # provide an iterator interface
            self.stdout = iter(self._stdout)
        def wait(self):
            return 0

    def dummy_popen(*args, **kwargs):
        return DummyProc()

    monkeypatch.setattr(subprocess, 'Popen', dummy_popen)

    # Enqueue build via API to get id
    resp = client.post('/build/run')
    assert resp.status_code == 200
    data = resp.json()
    bid = data['build_id']
    assert bid in BUILD_STORE

    # Run the build synchronously (as the background task would)
    run_local_build(bid)

    info = BUILD_STORE.get(bid)
    assert info is not None
    assert info['status'] == 'success'
    # log should contain concatenated stdout
    assert 'start' in info['log']
    assert 'step1' in info['log']
    assert 'step2' in info['log']
    assert 'done' in info['log']


def test_run_build_subprocess_raises(monkeypatch):
    # Simulate Popen raising an exception to test error handling
    def raising_popen(*args, **kwargs):
        raise RuntimeError('subprocess failed')

    monkeypatch.setattr(subprocess, 'Popen', raising_popen)

    resp = client.post('/build/run')
    assert resp.status_code == 200
    bid = resp.json()['build_id']

    run_local_build(bid)
    info = BUILD_STORE.get(bid)
    assert info is not None
    assert info['status'] == 'error'
    assert 'subprocess failed' in info['log'] or 'Exception' in info['log']


def test_run_build_script_missing(monkeypatch):
    # Simulate the build script missing by forcing Path.exists to return False
    real_exists = Path.exists
    monkeypatch.setattr(Path, 'exists', lambda self: False)

    resp = client.post('/build/run')
    bid = resp.json()['build_id']

    run_local_build(bid)
    info = BUILD_STORE.get(bid)
    assert info is not None
    assert info['status'] == 'error'
    assert 'Build script not found' in info['log']

    # Restore behavior isn't strictly necessary due to monkeypatch fixture teardown
