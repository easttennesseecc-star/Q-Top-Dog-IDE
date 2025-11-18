"""
Simple cross-process file lock using lock file creation.

This avoids adding external dependencies and works on Windows and Unix by
atomically creating a lock file with O_EXCL. The lock auto-expires only when
released; a timeout prevents tests from hanging.
"""
from __future__ import annotations

import os
import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def file_lock(lock_path: str | Path, timeout: float = 2.0, poll_interval: float = 0.05):
    lock_file = Path(lock_path)
    start = time.time()
    fd: int | None = None
    try:
        while True:
            try:
                fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_RDWR)
                break
            except FileExistsError:
                if (time.time() - start) >= timeout:
                    raise TimeoutError(f"Timed out acquiring lock: {lock_file}")
                time.sleep(poll_interval)
        yield
    finally:
        try:
            if fd is not None:
                os.close(fd)
            if lock_file.exists():
                os.unlink(lock_file)
        except Exception:
            pass
