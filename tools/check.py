"""One-command check (pre-commit runs this): text lint, then pytest (roundtrip, identity build, marker build)."""
import subprocess, sys
from pathlib import Path

tools = Path(__file__).resolve().parent
sys.exit(subprocess.call([sys.executable, "-X", "utf8", str(tools / "lint.py")])
         or subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-x", "tests"]))
