# Installation, dependencies and runtime

[简体中文](../installation.md) | English

## Platforms and versions

ComfortableTop **0.1.4** supports Windows x64 only, with Python 3.10+, psutil and
ComfortableTUI **0.1.3**. The bundled native runtime and TUI native wheel target
CPython 3.12 x64. Other Python ABIs require rebuilding native modules.
Linux and macOS are not supported. Old Linux archives are historical artifacts,
not a current installation or upgrade path.

Windows hybrid mode defaults to GPU WebViews; `--web-render-mode cpu` selects CPU
for comparison. `--canvas cpu|gpu` independently controls native trend charts.
GPU requires the helper capability `gpu_texture_transport=1`; security protocol 2
alone is insufficient. Unsupported GPU requests fail explicitly. GPU copies and
completion waits required by CEF's callback lifetime remain.

## Install release packages

Download the app and matching TUI wheels from the
[v0.1.4 release](https://github.com/JDK8u341/ComfortableTop/releases/tag/v0.1.4).
Terminal mode uses the universal TUI wheel without Qt or CEF:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install .\comfortable_tui-0.1.3-py3-none-any.whl .\comfortable_top-0.1.4-py3-none-win_amd64.whl
.\.venv\Scripts\comfortable-top.exe --version
.\.venv\Scripts\comfortable-top.exe --lang en
```

For full GPU hybrid mode, use **CPython 3.12 x64**:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade .\comfortable_tui-0.1.3-cp312-cp312-win_amd64.whl .\comfortable_top-0.1.4-py3-none-win_amd64.whl
.\.venv\Scripts\python.exe -m pip install "PySide6-Essentials>=6.7,<7" "comtypes>=1.4"
```

Extract `comfortable_top-runtime-windows-x64-cp312-0.1.4.zip` into
`.runtime/windows-x64` for an editable checkout, or
`%LOCALAPPDATA%/ComfortableTop/runtime/windows-x64` for a normal wheel installation.
The directory must directly contain `browser/`, `native/`, `licenses/` and
`runtime-manifest.json`. Exit all running Top instances before upgrading, as Windows
locks native modules and CEF DLLs. Preserve the complete CEF resources, locales and
licenses rather than replacing only the executable.

```powershell
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu --lang en
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu --web-render-mode cpu
```

Repeat the same command for multiple instances. Each owns a temporary browser root,
with independent cookies, caches and messages, removed after CEF closes.
Offline bilingual docs, a validation report and SHA256SUMS.txt are included.

## Build from source

Bootstrap fetches a pinned TUI release commit, builds a regular wheel and installs
this app. Private TUI source needs configured Git HTTPS credentials; no tokens are
stored by the project. `--tui-source PATH` uses existing source without resetting it
or requiring its location at runtime.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe tools/bootstrap.py --terminal-only
```

Native builds require VS 2022 C++, CMake and pybind11. Supply a complete browser runtime:

```powershell
.\.venv\Scripts\python.exe tools/bootstrap.py --gpu --browser-runtime C:\path\to\cef-runtime
```

Alternatively, use `--cef-root C:\path\to\cef-sdk` to build the helper.
The pinned CEF SDK is `152.0.14+g8a0b5b9+chromium-152.0.7977.167`; its host uses C++20.
`tools/build_runtime.py --tui-source PATH --cef-root PATH` updates the runtime separately.
Installation, execution and source packaging reject Linux; WindowHost is not built.

## Runtime discovery and language

`COMFORTABLE_TOP_RUNTIME` overrides the runtime root.
Explicit `COMFORTABLE_TUI_BROWSER_EXECUTABLE` overrides automatic discovery; remove
stale development overrides before testing. Native precedence is `--native-module`,
`COMFORTABLE_TOP_NATIVE_DIR`, runtime native directory, then local build directories.
Normal launches need neither a `--browser` option nor the TUI build directory.
Use `--lang en/zh/auto` or F9; see [language settings](localization.md) for preferences.
