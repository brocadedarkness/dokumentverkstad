from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import shutil
from uuid import uuid4


@contextmanager
def workspace_tempdir():
    root = Path("test_tmp")
    root.mkdir(exist_ok=True)
    path = root / f"case_{uuid4().hex}"
    path.mkdir()
    try:
        yield str(path)
    finally:
        shutil.rmtree(path, ignore_errors=True)
