"""Build this app against an installed SDK; optionally build/copy its hosts."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ARCH = {"amd64": "x64", "x86_64": "x64", "aarch64": "arm64"}.get(platform.machine().lower(), platform.machine().lower())
PLATFORM = ("windows" if os.name == "nt" else "linux") + "-" + ARCH
BUILD = ROOT / ".build" / PLATFORM


def run(*arguments):
    subprocess.run([str(a) for a in arguments], check=True)


def configure(source, build, *options):
    arguments = ["cmake", "-S", source, "-B", build]
    if Path(source).resolve() == ROOT / "native":
        arguments.append(f"-DPython_EXECUTABLE={sys.executable}")
    if os.name == "nt":
        arguments += ["-A", "x64"]
    arguments += [option for option in options if not (os.name == "nt" and option.startswith("-DCMAKE_BUILD_TYPE="))]
    run(*arguments)


def copy_browser(source, runtime):
    source = Path(source).resolve()
    target = runtime / "browser"
    executable = "ctui_browser.exe" if os.name == "nt" else "ctui_browser"
    if not (source / executable).is_file():
        raise RuntimeError(f"Browser executable missing: {source / executable}")
    if target.resolve().is_relative_to(source):
        raise ValueError("Browser output directory must be outside its source directory")
    # Copy the whole CEF runtime, including resources/locales/licenses, not only exe.
    shutil.copytree(source, target, dirs_exist_ok=True, ignore=shutil.ignore_patterns(
        "CMakeFiles", "cmake_install.cmake", "Makefile", "libcef_dll_wrapper", "*.a", "*.o", "*.obj",
        "*.pdb", "*.lib", "*.exp", "*.vcxproj*"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tui-source", type=Path, help="Explicit dependency source; any directory name is accepted")
    parser.add_argument("--sdk-prefix", type=Path, default=ROOT / ".deps" / "frame-sdk" / PLATFORM)
    parser.add_argument("--runtime", type=Path, default=ROOT / ".runtime" / PLATFORM)
    parser.add_argument("--browser-runtime", type=Path, help="Copy an already built, complete CEF runtime directory")
    parser.add_argument("--host-binary", type=Path, help="Withdrawn Linux WindowHost option")
    parser.add_argument("--cef-root", type=Path, help="Build the browser using this extracted CEF SDK")
    args = parser.parse_args(argv)
    if os.name != "nt":
        parser.error("Native/hybrid runtime builds currently require Windows; Linux supports terminal mode only")
    if args.host_binary:
        parser.error("Linux WindowHost support has been withdrawn; --host-binary is no longer available")
    runtime, prefix = args.runtime.resolve(), args.sdk_prefix.resolve()
    runtime.mkdir(parents=True, exist_ok=True)
    if args.tui_source:
        source = args.tui_source.resolve()
        if not (source / "CMakeLists.txt").is_file():
            parser.error("--tui-source must contain ComfortableTUI's root CMakeLists.txt")
        sdk_build = BUILD / "frame-sdk"
        configure(source, sdk_build, "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_INSTALL_PREFIX={prefix}",
                  "-DCOMFORTABLE_TUI_BUILD_BROWSER=OFF", "-DCOMFORTABLE_TUI_BUILD_LINUX_HOST=OFF")
        targets = ["comfortable_cpu_frames", "comfortable_frames", "comfortable_compositor", "ctui_gpu_producer"]
        run("cmake", "--build", sdk_build, "--config", "Release", "--target", *targets, "--parallel", "4")
        run("cmake", "--install", sdk_build, "--config", "Release")

    import pybind11
    native_build = BUILD / "native"
    configure(ROOT / "native", native_build, "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_PREFIX_PATH={prefix}",
              f"-Dpybind11_DIR={pybind11.get_cmake_dir()}", f"-DCMAKE_INSTALL_PREFIX={runtime}")
    run("cmake", "--build", native_build, "--config", "Release", "--target", "_ctui_top_native", "--parallel", "4")
    run("cmake", "--install", native_build, "--config", "Release")

    browser_runtime = args.browser_runtime
    if args.cef_root:
        if not args.tui_source:
            parser.error("--cef-root requires --tui-source")
        host_build = BUILD / "hosts"
        configure(args.tui_source.resolve(), host_build, "-DCMAKE_BUILD_TYPE=Release",
            f"-DCEF_ROOT={args.cef_root.resolve()}", "-DCOMFORTABLE_TUI_BUILD_BROWSER=ON",
            "-DCOMFORTABLE_TUI_BUILD_LINUX_HOST=OFF")
        run("cmake", "--build", host_build, "--config", "Release", "--target", "ctui_browser", "--parallel", "4")
        browser_runtime = host_build / "native" / "browser" / "Release"
    if browser_runtime:
        copy_browser(browser_runtime, runtime)
    print(f"ComfortableTop runtime installed in {runtime}")
    if not browser_runtime:
        print("Native charts ready. Hybrid mode additionally needs --browser-runtime or --cef-root.")


if __name__ == "__main__":
    main()
