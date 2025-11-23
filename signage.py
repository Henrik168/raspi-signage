# run_signage.py
import threading
import webbrowser
import platform
import subprocess
from app.CustomLogger import getLogger
from app.config import check_directories
from app import create_app

log = getLogger(level=20)  # type: ignore
check_directories()


def open_browser(port: int = 8000) -> None:
    url = f"http://127.0.0.1:{port}"
    system = platform.system()

    # Auf Linux → Raspberry Pi → Chromium im Kioskmodus
    if system == "Linux":
        try:
            subprocess.Popen([
                "chromium-browser",
                "--kiosk",
                "--noerrdialogs",
                "--disable-infobars",
                "--incognito",
                url,
            ])
        except FileNotFoundError:
            # Fallback: normaler Browser
            webbrowser.open(url)

    # Auf macOS / Windows → normaler Standardbrowser
    else:

        webbrowser.open(url)


def main() -> None:
    t = threading.Timer(1.0, open_browser, args=(8000,))
    t.start()

    app = create_app()
    print("http://127.0.0.1:8000/admin")
    app.run(host="0.0.0.0", port=8000, debug=True)


if __name__ == "__main__":
    main()
