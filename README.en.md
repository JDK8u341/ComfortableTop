# ComfortableTop

Version **0.1.5** defaults to GPU WebViews on Windows and supports multiple Top
instances. It requires ComfortableTUI **0.1.4** and the matching new Windows runtime.
See [installation](docs/en/installation.md).

[简体中文](README.md) | English

An independent hybrid system monitor: live processes, resource trends, pinned
comparisons, process trees and investigation notes, with optional C++ CPU/GPU charts
and isolated browser analytics. Windows only; Apache-2.0.

ComfortableTop depends on ComfortableTUI, but not its examples, source location or
old virtual environment. This repository owns its Python package, command, native
producer, web assets, tests and bilingual documentation.

## Install and run

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe tools/bootstrap.py --terminal-only
.\.venv\Scripts\comfortable-top.exe --lang en
```

Bootstrap fetches a pinned ComfortableTUI commit and installs a regular wheel; it does
not assume a PyPI distribution exists. Private source requires configured Git credentials.
Use `--tui-source C:\path\to\ComfortableTUI` for an existing checkout. If a dependency
wheel is already installed, `pip install -e .` installs the app. GitHub releases also
include a generic dependency wheel: install it before the app wheel for terminal mode.

Once installed, `comfortable-top` and `python -m comfortable_top` work from any directory.
Press **F9** or use **Settings → Language / 语言** to switch between English and Chinese.
`--lang en`, `--lang zh` and `--lang auto` select the startup language. UI choices are
saved; switching retains your current work and synchronizes all browser analytics pages.

Windows hybrid mode:

```powershell
.\.venv\Scripts\python.exe tools/bootstrap.py --gpu --browser-runtime C:\path\to\cef-runtime
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu --lang en
```

The browser runtime must include the executable, libcef.dll, assets, locales and
licenses. It is copied into `.runtime/<platform>/browser`. Use `--cef-root` to build
from an SDK instead. See [installation](docs/en/installation.md).

Current packages and runtimes target **Windows x64 only**. Linux distribution is
withdrawn; macOS is not supported. ComfortableTUI's core platform scope is managed separately.

## Features

- Real CPU, memory, network, disk and process sampling, filters, sorting and stable identities.
- Up to four pinned processes, independent browser pages and embedded list/table canvases.
- C++ rendering through CPU shared frames or Windows D3D11 textures, without Python pixel transfer per frame.
- Notes, logs, directory tree, background snapshot exports and preview.
- DPI-aware responsive browser panels, normal TUI focus/menu controls and live Chinese/English switching.

F1 help, F2 search, F3 sort, F4 pin, F6 menu, F7 pause, F8 details, F9 language,
Ctrl+1…5 pages, Ctrl+E export, Ctrl+Q exit. Recommended terminal size: 120×38 or larger.

## Documentation

- [Installation and native runtime](docs/en/installation.md)
- [User guide and metric semantics](docs/en/guide.md)
- [Language settings](docs/en/localization.md)
- [Expressive motion and verification](docs/en/motion.md)
- [Architecture and services](docs/en/architecture.md)
- [Development and distribution](docs/en/development.md)
- [Troubleshooting](docs/en/troubleshooting.md)
- [Validation](docs/en/validation.md)
- [Research](docs/en/research.md)

Install `.[docs]` and run `mkdocs serve`. Build both languages offline with
`mkdocs build --strict`. Each manual page links to its translated counterpart.

## License and attribution

[Apache License 2.0](LICENSE). The original monitor came from ComfortableTUI's example;
its attribution is retained in [NOTICE](NOTICE). CEF, Qt, psutil and other dependencies
keep their own licenses. Runtime copying preserves CEF notices and does not relicense
third-party components as Apache.
