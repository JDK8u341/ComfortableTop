# Validation scope and records

[简体中文](../validation.md) | English

Standalone validation builds/installs the app wheel into a separate venv and launches
outside the repository. ComfortableTUI is imported from a regular installed wheel,
not the original editable checkout. Native modules link the installed SDK and do not
reference the removed example.

Windows tests use a real Terminal; Linux X11 and native Wayland WindowHost are tested
separately under WSL2. Integration checks cover real samples, filtering/pinning, pause,
independent pages, embedded Enter/Esc, message round trips and responsive page/chart
dimensions. Producer tests cover GIL-independent publishing, stopping while unchanged
and rejection of invalid samples.

`validation/origin-example/` is a historical pre-extraction baseline, not a replacement
for standalone checks. New records are in `validation/standalone/`. Reports omit
usernames, process names, cookies and investigation notes. Producer counts are not
display FPS. See [development](development.md) for commands. WSLg results do not prove
support for every compositor or arbitrary external-terminal overlay.

## Initial standalone baseline, 2026-10-17

| Check | Result |
| --- | --- |
| Windows Python 3.12.14 | 17 unit/entry-point tests passed |
| WSL2 Ubuntu 22.04, Python 3.10.12 | 16 passed, 1 Win32-specific test skipped |
| Ruff / strict MkDocs | Passed |
| [Windows hybrid GPU](../validation/standalone/windows-gpu.json) | New venv, installed dependency wheel and own runtime; eight integration checks passed |
| [X11](../validation/standalone/linux-x11.json) | Launched from /tmp, actual Qt platform=xcb, eight passed |
| [Wayland](../validation/standalone/linux-wayland.json) | Launched from /tmp, actual Qt platform=wayland, eight passed independently |
| [Fresh wheel](../validation/standalone/installed-wheel.json) | Both packages imported from site-packages; assets, notices and real sampling passed |
| [Windows CPU](../validation/standalone/producer-windows-cpu.json), [GPU](../validation/standalone/producer-windows-gpu.json), [Linux CPU](../validation/standalone/producer-linux-cpu.json) | Independent native module producer, GIL, idle and invalid-input checks passed |

Baseline tools: CEF 152.0.14, psutil 7.2.2, pybind11 3.1.0, MSVC 19.44 and GCC 11.4.
App builds, installation and runtime live in ComfortableTop. The initial extraction
only read the original library checkout. Historical and standalone reports remain separate.

## Bilingual update, 2026-10-17

- Windows: 27 unit tests passed. WSL2: 26 passed, one Win32-only check skipped.
- [Windows GPU](../validation/standalone/i18n-windows-gpu.json), [WSL2 X11](../validation/standalone/i18n-linux-x11.json) and [WSL2 Wayland](../validation/standalone/i18n-linux-wayland.json) each passed ten hybrid checks, including Chinese updates while paused, switching back to English, retained page identities and actual webpage titles.
- [Fresh wheel](../validation/standalone/i18n-installed-wheel.json) collected two real samples in each language and produced the corresponding translated terminal frames outside the checkout.
- Unit tests cover three viewport sizes, both startup languages, dropdowns and open dialogs, Unicode tab bounds, retained state, preference precedence, invalid/unwritable settings, weak binding cleanup and late-loading pages.
- Both manuals pass strict MkDocs; Ruff passes. Monitor-specific tests now belong to the standalone app; the library's remaining 203 tests passed after removing the old example.

The old verification script used Windows' default GBK encoding for web assets; it now
reads UTF-8 explicitly. One Wayland recheck reached the fixed four-second checkpoint
before two samples were ready; an independent recheck passed. Integration checks still
use fixed timing, so busy machines or cold starts can hit that startup assertion.
These results are not a screen FPS guarantee.
