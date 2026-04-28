"""Live WSGI server + WebDriver fixtures for browser E2E tests."""

from __future__ import annotations

import os
import socket
import threading
from pathlib import Path

import pytest
from werkzeug.serving import make_server

from app import create_app
from app.config import Config


class E2EAppConfig(Config):
    """Exercise real form CSRF paths (same as normal dev, not the unit-test shortcut)."""

    TESTING = True
    WTF_CSRF_ENABLED = True


def _free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = int(s.getsockname()[1])
    s.close()
    return port


@pytest.fixture(scope="module")
def selenium_live_server(tmp_path_factory: pytest.TempPathFactory) -> str:
    """Real HTTP server on localhost; same process as tests, separate thread."""
    db_dir = tmp_path_factory.mktemp("selenium_sqlite")
    db_path: Path = db_dir / "live.db"

    class TC(E2EAppConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"

    application = create_app(TC)
    port = _free_port()
    httpd = make_server("127.0.0.1", port, application, threaded=True)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    try:
        yield base
    finally:
        httpd.shutdown()
        thread.join(timeout=10.0)


@pytest.fixture()
def driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions

    opts = ChromeOptions()
    if os.environ.get("HEADLESS", "1").lower() not in ("0", "false", "no"):
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,800")

    try:
        drv = webdriver.Chrome(options=opts)
    except Exception as exc:  # noqa: BLE001 — surface skip reason to developers
        pytest.skip(f"Chrome / WebDriver not available for Selenium: {exc}")

    yield drv
    drv.quit()
