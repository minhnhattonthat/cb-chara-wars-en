"""Release: check -> build -> checksum -> BPS (re-applied and verified by bps.py) -> README -> zip in dist/.

    python -X utf8 tools/release.py --version 0.1
Never publishes anything; dist/ is gitignored and stays local.
"""
import argparse, hashlib, subprocess, sys, zipfile, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BPS = ROOT / ".claude" / "skills" / "translate-retro-game" / "scripts" / "bps.py"
ROM = ROOT / "rom" / "CB Chara Wars - Ushinawareta Gag (Japan).sfc"
BUILT = ROOT / "build" / "cbcw_en.sfc"
PY = [sys.executable, "-X", "utf8"]


def run(*args):
    r = subprocess.run([*PY, *map(str, args)], cwd=ROOT)
    if r.returncode:
        sys.exit(f"release stopped: {' '.join(map(str, args))} exited {r.returncode}")


def hashes(data):
    return f"CRC32 {zlib.crc32(data):08X}, MD5 {hashlib.md5(data).hexdigest()}, SHA-1 {hashlib.sha1(data).hexdigest()}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    v = ap.parse_args().version
    run(ROOT / "tools" / "check.py")
    run(ROOT / "build.py")
    run(BPS, "snes-checksum", BUILT)
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    name = f"CBCharaWars_EN_v{v}"
    patch = dist / f"{name}.bps"
    run(BPS, "make", ROM, BUILT, patch)
    orig, built = ROM.read_bytes(), BUILT.read_bytes()
    readme = (ROOT / "docs" / "README.release.txt").read_text(encoding="utf-8")
    readme = readme.replace("{VERSION}", v).replace("{BASE}", hashes(orig)).replace("{PATCHED}", hashes(built))
    (dist / f"{name}_README.txt").write_text(readme, encoding="utf-8", newline="\r\n")
    with zipfile.ZipFile(dist / f"{name}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.write(dist / f"{name}_README.txt", "README.txt")
    print(f"release: {dist / (name + '.zip')}")


if __name__ == "__main__":
    main()
