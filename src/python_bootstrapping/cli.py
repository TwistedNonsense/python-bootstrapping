import os, sys, shlex, subprocess
from pathlib import Path
from .ensure_env import ensure_environment

def main():
    vpy = ensure_environment()
    if Path(sys.executable).resolve() != Path(vpy).resolve():
        os.execv(vpy, [vpy] + ["-m", "python_bootstrapping"] + sys.argv[1:])

    # After we are inside the venv:
    app_factory = os.environ.get("APP_FACTORY")
    app_cmd = os.environ.get("APP_CMD")

    if len(sys.argv) > 1:
        # If args provided, treat them as the command to run inside the venv.
        subprocess.check_call(sys.argv[1:])
        return

    if app_factory:
        mod, func = app_factory.split(":")
        m = __import__(mod, fromlist=[func])
        app = getattr(m, func)()
        print("[bootstrap] Starting Flask app from factory", app_factory)
        app.run(debug=True)
    elif app_cmd:
        print("[bootstrap] Executing APP_CMD:", app_cmd)
        subprocess.check_call(shlex.split(app_cmd))
    else:
        print(
            "Usage:\n"
            "  bootstrap-run [<command ...>]\n\n"
            "Environment options:\n"
            "  APP_FACTORY='app:create_app'  # Flask factory\n"
            "  APP_CMD='flask run'           # Command to execute\n"
            "  PYTHON_VERSION='3.12' or .python-version\n"
            "  BOOTSTRAP_WATCH='requirements.txt,pyproject.toml,src/**.py'\n"
        )
        sys.exit(2)

if __name__ == "__main__":
    main()
