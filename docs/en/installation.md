# Installation, dependencies and runtime

[简体中文](../installation.md) | English

## Current branch: GPU WebView testing

Windows hybrid mode now defaults to GPU WebView textures; Linux graphical modes are suspended.
`--canvas` selects native chart transport, while `--web-render-mode cpu|gpu` selects browser output.
Published v0.1.3 / TUI 0.1.2 stable assets do not contain this new API. Use the current pinned
TUI commit `6069afed2934af9137fe7fe3fa12fc8b04e3acb8` and rebuild/copy its complete CEF runtime.
Security protocol 2 alone is insufficient; the helper must advertise `gpu_texture_transport=1`.

The local project `.venv` and `.runtime/windows-x64/browser` have been updated:

```powershell
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu --web-render-mode cpu
```

No browser path or TUI build directory is needed at launch. An explicitly set old
COMFORTABLE_TUI_BROWSER_EXECUTABLE overrides discovery; remove it from the launching shell
if applicable. Unsupported GPU requests fail explicitly. Reports include actual per-page
backends, accelerated paint and CPU paint counts. GPU copies and synchronization remain necessary.

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
is pinned to commit `6069afed2934af9137fe7fe3fa12fc8b04e3acb8` in both bootstrap and
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
into `.runtime/<platform>/browser`; subsequent launches use that copy. This branch defaults
to GPU browser frames on Windows, with `--web-render-mode cpu` for CPU comparison.
Linux graphical modes are suspended. The separate `--canvas` flag controls charts only.

To build CEF, the tested SDK version is
`152.0.14+g8a0b5b9+chromium-152.0.7977.167`. Download it using the dependency's helper:

```powershell
.\.venv\Scripts\python.exe .deps/comfortable-tui-src/tools/fetch_cef.py --platform windows64
.\.venv\Scripts\python.exe tools/build_runtime.py --tui-source .deps/comfortable-tui-src --cef-root C:\path\to\cef-sdk
```

CEF requires C++20. The frame SDK and this app's chart producer use C++17. Sandbox
and no-first-run policies remain enabled; setup does not click through external terms,
allow unsafe eval, or disable the sandbox.

## Linux and WSL2: terminal mode only

Linux native/hybrid and the separate Qt WindowHost are withdrawn. They did not
integrate with an existing terminal. The old v0.1.3 Linux graphical runtime archive
is a historical artifact, not current support; do not install it for this branch.

```bash
python3 -m venv .venv
.venv/bin/python tools/bootstrap.py --terminal-only
.venv/bin/comfortable-top --mode terminal
```

No Qt, CEF or desktop session is required. WSL reports Linux subsystem processes,
not Windows host processes. CLI rejects graphical modes before starting resources;
the runtime builder rejects Linux graphical builds.
See the [research decision](https://github.com/JDK8u341/ComfortableTUI/blob/codex/webview-gpu-textures/docs/linux-support-decision.md).

## Runtime discovery after wheel installation

Windows editable installs use `.runtime/windows-x64`; regular wheels default to
`%LOCALAPPDATA%/ComfortableTop/runtime/windows-x64`. Override using
`COMFORTABLE_TOP_RUNTIME`, passing the same path to `build_runtime.py --runtime`.
Native precedence is `--native-module`, `COMFORTABLE_TOP_NATIVE_DIR`, runtime native
directory, then local build directories. Explicit `COMFORTABLE_TUI_BROWSER_EXECUTABLE`
takes precedence over discovery. Linux terminal mode no longer activates old GUI runtimes;
legacy host environment variables do not restore withdrawn graphical modes.
See [language settings](localization.md) for preferences stored separately.
