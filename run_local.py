"""Build and launch ZeroedIn locally at http://127.0.0.1:8000."""
from pathlib import Path
import os
import subprocess
import sys
import threading
import webbrowser


ROOT = Path(__file__).resolve().parent


def main():
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    subprocess.run([npm, "run", "build"], cwd=ROOT / "frontend", check=True)
    sys.path.insert(0, str(ROOT / "backend"))
    import uvicorn

    if os.getenv("ZEROEDIN_NO_BROWSER") != "1":
        threading.Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:8000")).start()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, app_dir=str(ROOT / "backend"))


if __name__ == "__main__":
    main()
