# Installation, dependencies and runtime

[简体中文](../installation.md) | English

## Terminal mode

For v0.1.3 terminal mode, download both universal wheels from the
[release page](https://github.com/JDK8u341/ComfortableTop/releases/tag/v0.1.3), then run
in the download directory:

```powershell
python -m pip install --upgrade ./comfortable_tui-0.1.2-py3-none-any.whl ./comfortable_top-0.1.3-py3-none-any.whl
comfortable-top --version
comfortable-top
```

The version should read `ComfortableTop 0.1.3`. The library requires 0.1.2 or newer;
upgrade both the library and the browser runtime. The helper must use security protocol 2;
updating only Python wheels while retaining an old helper is insufficient. GPU/browser modes
still require the native runtimes described below; the universal wheel contains neither
GPU extensions nor CEF. The offline documentation zip includes both languages.

Requires Python 3.10+ on Windows or Linux, psutil and ComfortableTUI. The tested dependency
is pinned to commit `0480fe7bd62ab1bbc811bab7b46e95d324d4f610` in both bootstrap and
requirements-tui.txt. Do not assume it is published on PyPI. Access to its private GitHub
source requires local Git credentials; no tokens are stored in this project.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe tools/bootstrap.py --terminal-only
.\.venv\Scripts\comfortable-top.exe --lang en
```

On Linux use `.venv/bin/python` and `.venv/bin/comfortable-top`. Bootstrap fetches the
dependency into `.deps/comfortable-tui-src`, builds and installs a regular wheel, then
installs this app in editable mode. `--tui-source PATH` uses existing source without
resetting or modifying it. The installed app does not need that checkout at runtime.

For manual installation, install `requirements-tui.txt` first, then `pip install -e .`.
Alternatively, install the ComfortableTUI wheel supplied with the GitHub release,
then the ComfortableTop wheel. This enables terminal mode without private source access.

## Windows native and hybrid modes

The release includes `comfortable_top-runtime-windows-x64-cp312-0.1.3.zip` with
the complete protocol-2 CEF runtime, chart module and notices. Install the matching
CPython 3.12 Windows x64 TUI native wheel and the Top wheel, then extract the archive
into `.runtime/windows-x64` so it directly contains browser/native subdirectories.
Other Python ABIs require rebuilding. Wheel-only installs should use the runtime
location below or COMFORTABLE_TOP_RUNTIME.

```powershell
python -m pip install --upgrade "./comfortable_tui-0.1.2-cp312-cp312-win_amd64.whl[overlay]" ./comfortable_top-0.1.3-py3-none-any.whl
```

Requires x64 Python, VS 2022 C++ tools and CMake. GPU charts require D3D11.1 support.

```powershell
.\.venv\Scripts\python.exe tools/bootstrap.py --tui-source C:\path\to\ComfortableTUI --gpu
.\.venv\Scripts\comfortable-top.exe --mode native --canvas gpu
```

Without `--gpu`, charts use CPU shared frames. Bootstrap installs the dependency wheel
and ComfortableFrames CMake SDK. This project's native module links the installed SDK
using `find_package`; it does not add the dependency source tree as a subdirectory.
The module is installed into `.runtime/<platform>/native`.

To reuse a complete CEF runtime:

```powershell
.\.venv\Scripts\python.exe tools/build_runtime.py --tui-source C:\path\to\ComfortableTUI --browser-runtime C:\path\to\browser\Release
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu --lang en
```

The runtime directory must include ctui_browser.exe, ctui_browser.dll, libcef.dll,
pak files, locales, snapshots and CEF licenses. The tool copies the whole directory
into `.runtime/<platform>/browser`; subsequent launches use that copy. CEF uses CPU
shared frames even when GPU transport is selected for native charts.

To build CEF, the tested SDK version is
`152.0.14+g8a0b5b9+chromium-152.0.7977.167`. Download it using the dependency's helper:

```powershell
.\.venv\Scripts\python.exe .deps/comfortable-tui-src/tools/fetch_cef.py --platform windows64
.\.venv\Scripts\python.exe tools/build_runtime.py --tui-source .deps/comfortable-tui-src --cef-root C:\path\to\cef-sdk
```

CEF requires C++20. The frame SDK and this app's chart producer use C++17. Sandbox
and no-first-run policies remain enabled; setup does not click through external terms,
allow unsafe eval, or disable the sandbox.

## Linux and WSL2

`comfortable_top-runtime-linux-x64-cp310-0.1.3.tar.gz` targets Ubuntu 22.04 and
CPython 3.10. Extract into `.runtime/linux-x64`; it contains CEF, the CPU chart module
and the Qt host. System Qt/GTK dependencies are still required. Rebuild for other
Python ABIs or distributions; arbitrary binary compatibility is not promised.

Requires GCC 11+, CMake, Qt 6 development packages and a real X11 or Wayland session.
CEF also requires system graphics libraries. For Ubuntu 22.04:

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake ninja-build python3-venv python3-dev \
  qt6-base-dev qt6-wayland libgl1-mesa-dev libopengl-dev libgtk-3-dev libnss3 libgbm1 libasound2 \
  libatk-bridge2.0-0 libxkbcommon-x11-0
python3 -m venv .venv
.venv/bin/python tools/bootstrap.py --tui-source /path/to/ComfortableTUI
.venv/bin/python tools/build_runtime.py --tui-source /path/to/ComfortableTUI --cef-root /path/to/cef-sdk
.venv/bin/comfortable-top --mode hybrid --platform x11 --lang en
.venv/bin/comfortable-top --mode hybrid --platform wayland --lang zh
```

Use `--platform linux64` with fetch_cef.py. Existing binaries can be copied using
`--browser-runtime DIR --host-binary /path/to/ctui_linux_canvas`. Qt and other shared
libraries must still be installed on the target system. Builds are not guaranteed to
work across arbitrary Linux distributions. WSL monitors Linux subsystem processes,
not Windows host processes. Prefer the Linux filesystem for WSL builds and virtual
environments. Linux native modes use an app-owned WindowHost, not an external terminal overlay.

## Runtime discovery after wheel installation

Editable installs use this checkout's `.runtime/<platform>`. Regular wheel installs
look in `%LOCALAPPDATA%/ComfortableTop/runtime/windows-x64` on Windows, and
`$XDG_DATA_HOME/ComfortableTop/runtime/linux-x64` on Linux, defaulting to
`~/.local/share/ComfortableTop/runtime/linux-x64`. Set `COMFORTABLE_TOP_RUNTIME` to
override the runtime root and pass the same path to `tools/build_runtime.py --runtime`.

Native module precedence: `--native-module`, `COMFORTABLE_TOP_NATIVE_DIR`, runtime
native directory, then this checkout's `.build/<platform>/native/Release` or
`.build/<platform>/native`. Explicit `COMFORTABLE_TUI_BROWSER_EXECUTABLE` and
`COMFORTABLE_TUI_LINUX_HOST_EXECUTABLE` settings take precedence over discovery.

Tested platform keys are windows-x64 and linux-x64. SDK and build caches are separated
by platform, allowing Windows and WSL to share source without overwriting binaries.
Runtime discovery does not look for a sibling TUI directory. See [language settings](localization.md)
for UI preferences, which are stored separately from runtime files.
