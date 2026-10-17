"""Install built wheels into a fresh environment and run outside the checkout."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import venv
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--tui-wheel", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    target = ROOT / ".build" / ("wheel-check-windows" if os.name == "nt" else "wheel-check-linux")
    target.mkdir(parents=True, exist_ok=True)
    venv.EnvBuilder(with_pip=True).create(target / "venv")
    python = target / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    work = target / "work"
    work.mkdir(exist_ok=True)
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    subprocess.run([str(python), "-m", "pip", "install", "--force-reinstall", str(args.tui_wheel.resolve()),
                    str(args.wheel.resolve())], check=True, cwd=work, env=environment)
    result = {"checks": []}
    with zipfile.ZipFile(args.wheel) as package:
        names = set(package.namelist())
        assert all("comfortable_top/web/" + name in names for name in ("analytics.html", "analytics.css", "analytics.js"))
        assert any(n.endswith("/licenses/LICENSE") for n in names)
        assert any(n.endswith("/licenses/NOTICE") for n in names)
        result["checks"].append("wheel_contains_web_assets_and_apache_notices")
    script = ("import pathlib,sys,comfortable_top,comfortable_tui;from importlib.resources import files;"
              "assert pathlib.Path(comfortable_top.__file__).is_relative_to(pathlib.Path(sys.prefix));"
              "assert pathlib.Path(comfortable_tui.__file__).is_relative_to(pathlib.Path(sys.prefix));"
              "assert files('comfortable_top').joinpath('web','analytics.js').read_text();"
              "print('independent wheel imports verified')")
    subprocess.run([str(python), "-c", script], check=True, cwd=work, env=environment)
    result["checks"].append("both_packages_are_installed_wheels_outside_checkout")
    subprocess.run([str(python), "-m", "comfortable_top", "--version"], check=True, cwd=work, env=environment)
    command = python.parent / ("comfortable-top.exe" if os.name == "nt" else "comfortable-top")
    subprocess.run([str(command), "--help"], check=True, cwd=work, env=environment, stdout=subprocess.DEVNULL)
    result["checks"].append("module_and_console_entrypoints")
    snapshot_report = target / "snapshot.json"
    with (target / "snapshot.txt").open("w", encoding="utf-8") as output:
        subprocess.run([str(command), "--snapshot", "--interval", ".25", "--report", str(snapshot_report)],
                       check=True, cwd=work, env=environment, stdout=output)
    snapshot = json.loads(snapshot_report.read_text(encoding="utf-8"))
    assert snapshot["result"] == "passed" and snapshot["samples"] >= 2
    result["checks"].append("real_sampling_and_snapshot_from_installed_wheel")
    result["result"] = "passed"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
