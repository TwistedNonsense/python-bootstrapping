import os, sys
from pathlib import Path
from bootstrap.ensure_env import ensure_environment

VENV_PY = ensure_environment()
if Path(sys.executable).resolve() != Path(VENV_PY).resolve():
    os.execv(VENV_PY, [VENV_PY] + sys.argv)

app_factory = os.environ.get("APP_FACTORY")
app_cmd = os.environ.get("APP_CMD")

if app_factory:
    mod, func = app_factory.split(":")
    m = __import__(mod, fromlist=[func])
    app = getattr(m, func)()
    print("[run] Starting Flask app from factory", app_factory)
    app.run(debug=True)
elif app_cmd:
    import shlex, subprocess
    print("[run] Executing APP_CMD:", app_cmd)
    subprocess.check_call(shlex.split(app_cmd))
else:
    print(
        "No entry configured.\n"
        "Set one of:\n"
        "  APP_FACTORY='app:create_app'       # Flask factory\n"
        "  APP_CMD='flask run'                # Any shell command\n"
        "Optional: PYTHON_VERSION='3.12' or use a .python-version file.\n"
        "Optional: BOOTSTRAP_WATCH='requirements.txt,pyproject.toml,src/**.py'\n"
        "Then run: python run.py"
    )
    sys.exit(2)
