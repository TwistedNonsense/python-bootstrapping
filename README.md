# Project Bootstrap Helper

This package makes it easy to set up and run any Python project with a
consistent virtual environment workflow. It ensures that `.venv`
is always up-to-date with the correct dependencies, and allows me to
start my project simply with:

```bash
python run.py
```

## Installation

1. Copy these files into the root of a new or existing project:
   - `run.py`
   - `bootstrap/ensure_env.py`
   - (Optional) `.bootstrapignore`
   - (Optional) `setup.ps1` This is a Windows convenience wrapper if I ever have to use PowerShell

2. Ensure I already have a `requirements.txt` (or `pyproject.toml`) file.

3. Run:

```bash
python run.py
```

The script will:
- Create `.venv` if it doesn’t exist
- Install/upgrade `pip`, `setuptools`, `wheel`
- Install dependencies from `requirements.txt` (or `pyproject.toml`)
- Save environment state to `.venv/.env_state.json`

## Configuration

- `APP_FACTORY="pkg.module:create_app"`  
  Import a Flask app factory and run it.

- `APP_CMD="flask run"`  
  Run an arbitrary shell command inside the environment.

- `PYTHON_VERSION="3.12"` or a `.python-version` file  
  Forces a specific Python version for the venv.

- `BOOTSTRAP_WATCH="requirements.txt,pyproject.toml,src/**.py"`  
  Override the list of files that trigger reinstall.

## Example usage

```bash
export APP_FACTORY="myapp:create_app"
python run.py
```

or

```bash
export APP_CMD="flask run"
python run.py
```

## Optional ignores

Add file/directory patterns to `.bootstrapignore` to prevent unnecessary
reinstalls when unrelated files change.

Example `.bootstrapignore`:

```
.git/**
**/__pycache__/**
node_modules/**
```

## Notes

- Works on macOS, Linux, Windows (with `py` launcher or PowerShell wrapper).
- Does not require bash or external tools.
- Idempotent: reuses `.venv` unless dependencies change.
