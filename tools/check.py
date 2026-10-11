"""One-command check (pre-commit runs this). Extend with lint/roundtrip as the pipeline grows."""
import subprocess, sys

sys.exit(subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-x", "tests"]))
