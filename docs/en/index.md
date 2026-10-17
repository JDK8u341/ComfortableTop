# ComfortableTop documentation

[简体中文](../index.md) | English

ComfortableTop is an independent Python system monitor built on ComfortableTUI widgets
and its general frame SDK. This manual covers version 0.1.1 on Windows x64 and Linux.
macOS is outside the current scope.

Start with [installation](installation.md), then read the [user guide](guide.md).
Terminal mode displays real metrics without compiling native code. Native mode adds
C++ charts; hybrid mode adds local browser analytics and explicit application messages.
The installed package includes its web assets and runs from any working directory.

Run `comfortable-top` or `python -m comfortable_top`. Press **F9** to switch between
English and Chinese, or use **Settings → Language / 语言**. See [language settings](localization.md).

The repository contains its own LICENSE and NOTICE and uses Apache-2.0.
Build this bilingual documentation offline with `mkdocs build --strict`.

- [Installation and runtime](installation.md)
- [Controls, metrics and shortcuts](guide.md)
- [Architecture and boundaries](architecture.md)
- [Development, tests and distribution](development.md)
- [Troubleshooting](troubleshooting.md)
- [Validation](validation.md)
- [Research and attribution](research.md)
