from importlib.resources import files
import os
from pathlib import Path
import subprocess
import sys

from comfortable_top import paths


def test_installed_web_assets():
    for name in ("analytics.html", "analytics.css", "analytics.js"):
        asset = files("comfortable_top").joinpath("web", name)
        assert asset.is_file() and asset.read_text(encoding="utf-8")


def test_cli_works_outside_checkout(tmp_path):
    result = subprocess.run([sys.executable, "-m", "comfortable_top", "--version"], cwd=tmp_path,
                            capture_output=True, text=True, check=True)
    assert result.stdout.strip() == "ComfortableTop 0.1.2"
    result = subprocess.run([sys.executable, "-m", "comfortable_top", "--help"], cwd=tmp_path,
                            capture_output=True, text=True, check=True)
    assert "--mode" in result.stdout and "--canvas" in result.stdout


def test_runtime_override_and_explicit_environment_precedence(tmp_path, monkeypatch):
    monkeypatch.setenv("COMFORTABLE_TOP_RUNTIME", str(tmp_path))
    browser = tmp_path / "browser" / ("ctui_browser.exe" if os.name == "nt" else "ctui_browser")
    browser.parent.mkdir()
    browser.touch()
    monkeypatch.delenv("COMFORTABLE_TUI_BROWSER_EXECUTABLE", raising=False)
    assert paths.runtime_dir() == tmp_path
    paths.configure_runtime()
    assert Path(os.environ["COMFORTABLE_TUI_BROWSER_EXECUTABLE"]) == browser
    monkeypatch.setenv("COMFORTABLE_TUI_BROWSER_EXECUTABLE", "explicit-own-host")
    paths.configure_runtime()
    assert os.environ["COMFORTABLE_TUI_BROWSER_EXECUTABLE"] == "explicit-own-host"


def test_explicit_native_dir_has_priority(tmp_path, monkeypatch):
    explicit, configured, runtime = (tmp_path / name for name in ("explicit", "configured", "runtime"))
    for directory in (explicit, configured, runtime / "native"):
        directory.mkdir(parents=True)
    monkeypatch.setenv("COMFORTABLE_TOP_NATIVE_DIR", str(configured))
    monkeypatch.setenv("COMFORTABLE_TOP_RUNTIME", str(runtime))
    assert paths.native_dirs(explicit)[:3] == [explicit, configured, runtime / "native"]
