import subprocess
import sys
from pathlib import Path


def test_app_imports_when_started_from_src_directory():
    project_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "-c", "import app"],
        cwd=project_root / "src",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
