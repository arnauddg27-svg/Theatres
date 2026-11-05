"""Every tracked Python file must compile on Python 3.11.

predict.py once used a 3.12-only nested f-string (same quote type inside the
replacement field), so it failed to import on 3.11 and every predict test
errored at collection. CI runs 3.12, so production kept working, but local and
audit runs on 3.11 could not run the suite at all.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PY311 = shutil.which("python3.11")


@pytest.mark.skipif(PY311 is None, reason="python3.11 not installed")
def test_all_modules_compile_on_python311():
    files = [str(p) for p in ROOT.rglob("*.py")
             if "__pycache__" not in p.parts and ".venv" not in p.parts]
    code = (
        "import sys\n"
        "bad=[]\n"
        "for f in sys.argv[1:]:\n"
        "    try: compile(open(f,encoding='utf-8').read(), f, 'exec')\n"
        "    except SyntaxError as e: bad.append(f'{f}:{e.lineno}: {e.msg}')\n"
        "print('\\n'.join(bad)); sys.exit(1 if bad else 0)\n"
    )
    res = subprocess.run([PY311, "-c", code, *files], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
