"""Standalone app runtime discovery, with no assumptions about a TUI checkout."""
import os
from pathlib import Path
import platform


def platform_key():
    architecture = platform.machine().lower()
    architecture = {"amd64": "x64", "x86_64": "x64", "aarch64": "arm64"}.get(architecture, architecture)
    return ("windows" if os.name == "nt" else "linux") + "-" + architecture


def project_root():
    package = Path(__file__).resolve().parent
    if package.parent.name == "src" and (package.parent.parent / "pyproject.toml").is_file():
        return package.parent.parent
    return None


def runtime_dir():
    override = os.environ.get("COMFORTABLE_TOP_RUNTIME")
    if override:
        return Path(override).expanduser().resolve()
    checkout = project_root()
    if checkout:
        return checkout / ".runtime" / platform_key()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "ComfortableTop" / "runtime" / platform_key()


def configure_runtime():
    if os.name != "nt":
        return  # Top is Windows-only; never activate archived Linux runtimes.
    root = runtime_dir()
    browser = root / "browser" / "ctui_browser.exe"
    if browser.is_file():
        os.environ.setdefault("COMFORTABLE_TUI_BROWSER_EXECUTABLE", str(browser))


def native_dirs(override=None):
    candidates = []
    if override:
        candidates.append(Path(override).expanduser())
    if os.environ.get("COMFORTABLE_TOP_NATIVE_DIR"):
        candidates.append(Path(os.environ["COMFORTABLE_TOP_NATIVE_DIR"]).expanduser())
    candidates.append(runtime_dir() / "native")
    checkout = project_root()
    if checkout:
        candidates.extend([checkout / ".build" / platform_key() / "native" / "Release",
                           checkout / ".build" / platform_key() / "native"])
    return [path.resolve() for path in candidates if path.is_dir()]
