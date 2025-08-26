#!/usr/bin/env python3
import hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv"
STATE_FILE = VENV_DIR / ".env_state.json"

DEFAULT_WATCH = [
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "poetry.lock",
    "Pipfile.lock",
    "setup.cfg",
]
IGNORE_FILE = ROOT / ".bootstrapignore"

def _glob_many(patterns):
    out = []
    for pat in patterns:
        out.extend(ROOT.rglob(pat) if ("**" in pat or "/" in pat) else ROOT.glob(pat))
    return sorted({p for p in out if p.is_file()})

def _load_ignores():
    pats = []
    if IGNORE_FILE.exists():
        pats = [ln.strip() for ln in IGNORE_FILE.read_text().splitlines() if ln.strip() and not ln.strip().startswith("#")]
    return pats

def _filter_ignored(paths, ignore_patterns):
    if not ignore_patterns:
        return paths
    keep = []
    for p in paths:
        text = str(p.relative_to(ROOT))
        if any(Path(text).match(pat) for pat in ignore_patterns):
            continue
        keep.append(p)
    return keep

def _python_version():
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def _hash_files(files):
    h = hashlib.sha256()
    for f in files:
        h.update(b"\n--file--\n")
        h.update(str(f.relative_to(ROOT)).encode())
        with open(f, "rb") as fp:
            h.update(fp.read())
    return h.hexdigest()

def _desired_python():
    pv = os.environ.get("PYTHON_VERSION")
    if not pv:
        pyver_file = ROOT / ".python-version"
        if pyver_file.exists():
            pv = pyver_file.read_text().strip()
    return pv

def _venv_python():
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def _run(cmd, env=None):
    print(f"[bootstrap] $ {' '.join(cmd)}")
    subprocess.check_call(cmd, env=env)

def _create_or_recreate_venv(reason):
    if VENV_DIR.exists():
        shutil.rmtree(VENV_DIR)
    print(f"[bootstrap] creating venv: {reason}")
    _run([sys.executable, "-m", "venv", str(VENV_DIR)])
    py = str(_venv_python())
    _run([py, "-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools"])
    return py

def _needs_install(state, new_hash):
    if not state:
        return True
    if state.get("hash") != new_hash:
        return True
    return not (VENV_DIR / "lib").exists() and not (VENV_DIR / "Lib").exists()

def _save_state(d):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(d, indent=2))

def ensure_environment():
    desired = _desired_python()
    current_py = _python_version()

    watch_env = os.environ.get("BOOTSTRAP_WATCH")
    watch = [w.strip() for w in watch_env.split(",")] if watch_env else DEFAULT_WATCH
    files = _glob_many(watch)
    files = _filter_ignored(files, _load_ignores())

    if (ROOT / "requirements.txt").exists() and (ROOT / "requirements.txt") not in files:
        files.append(ROOT / "requirements.txt")

    dep_hash = _hash_files(files) if files else ""

    prior = {}
    if STATE_FILE.exists():
        try:
            prior = json.loads(STATE_FILE.read_text())
        except Exception:
            prior = {}

    vpy = _venv_python()

    recreate_reasons = []
    if not vpy.exists():
        recreate_reasons.append("missing venv")
    if desired and not re.match(rf"^{re.escape(desired)}", current_py):
        if prior.get("desired_python") != desired:
            recreate_reasons.append(f"python version drift (desired {desired})")

    if recreate_reasons:
        py = _create_or_recreate_venv(", ".join(recreate_reasons))
    else:
        py = str(vpy)

    need_install = _needs_install(prior, dep_hash)
    if need_install:
        if (ROOT / "requirements.txt").exists():
            _run([py, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
        elif (ROOT / "pyproject.toml").exists():
            _run([py, "-m", "pip", "install", "-e", ".[dev]"])
        else:
            print("[bootstrap] no requirements.txt or pyproject.toml found; skipping installs")

    _save_state({
        "hash": dep_hash,
        "python": current_py,
        "desired_python": desired,
        "venv_interpreter": py,
        "watched": [str(p.relative_to(ROOT)) for p in files],
    })

    return py

if __name__ == "__main__":
    ensure_environment()
