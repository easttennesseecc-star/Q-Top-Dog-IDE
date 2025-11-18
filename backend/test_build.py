from fastapi.testclient import TestClient
import subprocess

from backend.main import app, BUILD_STORE, run_local_build

client = TestClient(app)


def test_run_build_enqueue_and_run(monkeypatch, tmp_path):
    # Mock subprocess.Popen to simulate a successful build run
    class DummyProc:
        def __init__(self, *args, **kwargs):
            self.returncode = 0
            self._stdout = ["Starting tests...\n", "All tests passed\n"]
            self.stdout = self
        def __iter__(self):
            return iter(self._stdout)

        def __next__(self):
            raise StopIteration

        def read(self):
            return "".join(self._stdout)

        def wait(self):
            return 0

    def dummy_popen(*args, **kwargs):
        return DummyProc()

    monkeypatch.setattr(subprocess, 'Popen', dummy_popen)

    # Call the API to enqueue a build
    resp = client.post('/build/run')
    assert resp.status_code == 200
    data = resp.json()
    assert data['status'] == 'ok'
    bid = data['build_id']
    assert bid in BUILD_STORE
    # Now run the build synchronously by calling run_local_build
    # This should update BUILD_STORE for the build
    run_local_build(bid)
    build_info = BUILD_STORE.get(bid)
    assert build_info is not None
    assert build_info['status'] in ('success', 'failed', 'error')
    assert 'log' in build_info
