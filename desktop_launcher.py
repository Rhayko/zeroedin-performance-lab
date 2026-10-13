"""Launch the packaged macOS showcase with private, user-local storage."""
from pathlib import Path
import os
import threading
import webbrowser


def configure_local_storage() -> None:
    data_dir = Path.home() / "Library" / "Application Support" / "ZeroedIn Performance Lab"
    data_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("DATABASE_URL", f"sqlite:///{data_dir / 'zeroedin.db'}")


def main() -> None:
    configure_local_storage()

    import uvicorn
    from backend.app.main import app

    threading.Timer(1.25, lambda: webbrowser.open("http://127.0.0.1:8000")).start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")


if __name__ == "__main__":
    main()
