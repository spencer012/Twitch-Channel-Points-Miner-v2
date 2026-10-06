"""Home Assistant add-on entrypoint.

Takes run.py from the add-on's `run_py` option, checks it, then runs it with
the miner's state directories (cookies, logs, analytics) kept in /data.
If the new run_py is unusable, the last run.py that passed is used instead.
"""

import json
import os
import shutil
import sys
import time
from pathlib import Path

APP_DIR = Path("/usr/src/app")
DATA_DIR = Path("/data")
OPTIONS_FILE = DATA_DIR / "options.json"
LAST_GOOD = DATA_DIR / "run.py"
IMPORT_DIR = Path("/share/twitch_miner_import")
STATE_DIRS = ("cookies", "logs", "analytics")


def log(message):
    print(f"[launcher] {message}", flush=True)


def link_state_dirs():
    for name in STATE_DIRS:
        target = DATA_DIR / name
        target.mkdir(exist_ok=True)
        link = APP_DIR / name
        if link.is_symlink():
            continue
        if link.is_dir():
            shutil.rmtree(link)
        elif link.exists():
            link.unlink()
        link.symlink_to(target)


def import_once():
    # Copies state from /share/twitch_miner_import into empty /data dirs only,
    # so it never overwrites what the add-on already has.
    if not IMPORT_DIR.is_dir():
        return
    for name in STATE_DIRS:
        source = IMPORT_DIR / name
        target = DATA_DIR / name
        if not source.is_dir():
            continue
        if any(target.iterdir()):
            log(f"Import: skipping {name}/, /data/{name} is not empty")
            continue
        shutil.copytree(source, target, dirs_exist_ok=True)
        count = sum(1 for p in target.rglob("*") if p.is_file())
        log(f"Import: copied {count} file(s) into /data/{name}")
    log(f"Import done. Delete {IMPORT_DIR} once the miner is running.")


def check_run_py(source):
    """Return None if source is usable, otherwise a description of the problem."""
    if not source.strip():
        return (
            "run_py is empty. Paste your run.py under Configuration, "
            "three-dot menu -> Edit in YAML, as a `run_py: |` block."
        )
    if "\n" not in source.strip():
        return (
            "run_py is a single line; its line breaks were probably lost by "
            "saving from the form view. Re-paste it in Edit in YAML mode."
        )
    try:
        compile(source, "run_py", "exec")
    except SyntaxError as e:
        line = (e.text or "").rstrip()
        return f"run_py has a syntax error on line {e.lineno}: {e.msg}\n    {line}"
    except ValueError as e:
        return f"run_py cannot be compiled: {e}"
    return None


def resolve_run_py():
    options = json.loads(OPTIONS_FILE.read_text()) if OPTIONS_FILE.exists() else {}
    source = options.get("run_py") or ""
    if not source.endswith("\n"):
        source += "\n"

    problem = check_run_py(source)
    if problem is None:
        if not LAST_GOOD.exists() or LAST_GOOD.read_text() != source:
            LAST_GOOD.write_text(source)
            log("run_py OK, saved as the new last good run.py")
        else:
            log("run_py OK (unchanged)")
        return LAST_GOOD

    log(problem)
    if LAST_GOOD.exists():
        saved = time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(LAST_GOOD.stat().st_mtime))
        log(f"Falling back to the last good run.py (saved {saved}). Fix run_py and restart the add-on.")
        return LAST_GOOD
    log("No previous good run.py to fall back to; stopping.")
    sys.exit(1)


def main():
    link_state_dirs()
    import_once()
    run_py = resolve_run_py()
    os.chdir(APP_DIR)
    # exec so the miner receives SIGTERM directly and can save its state.
    os.execv(sys.executable, [sys.executable, str(run_py)])


if __name__ == "__main__":
    main()
