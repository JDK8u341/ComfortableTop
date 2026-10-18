# Validation scope and records

[简体中文](../validation.md) | English

## Windows GPU WebView test branch

This branch pins TUI `e25f1f62c26ec99684f5b6e0ba1cf472930665f2`. The ordinary Windows
`.venv` uses its non-editable GPU wheel and the complete matching CEF runtime under
this project's `.runtime/windows-x64`. The ordinary WSL environment also uses matching
CPU wheels/helpers. Development overrides were cleared for automatic runtime discovery.

- [Windows default GPU browser](../validation/standalone/webview-gpu.json): ten hybrid
  checks passed; both independent pages reported native_gpu_d3d11, zero CPU paints and
  actual accelerated frames.
- [Windows explicit CPU comparison](../validation/standalone/webview-cpu.json): ten checks,
  both pages using native_cpu.
- [X11](../validation/standalone/webview-x11-cpu.json) and
  [Wayland](../validation/standalone/webview-wayland-cpu.json): ten checks each, default CPU.
  Linux GPU support was not added.
- Windows: 30 unit tests passed. WSL: 29 passed, one platform skip. Ruff, strict docs
  and pip check passed.

These runs used the app's real CLI selection, without monkeypatching BrowserService.open,
an editable TUI import or launch-time access to its build directory. The test launcher only
clears development overrides and calls the normal app main with self-test options.
The new browser_frames report checks negotiated GPU backends, zero CPU paints and nonzero
accelerated callbacks. Published v0.1.3 assets do not yet include this test-branch feature.

## v0.1.3 / ComfortableTUI v0.1.2 release checks

On 2026-10-18, both the ordinary Windows `.venv` and the WSL2 development environment
were upgraded to a regular TUI 0.1.2 wheel, rebuilt app producers and the protocol 2
CEF runtime. Development overrides were cleared; runtimes were discovered through
this project's `.runtime/<platform>` directory.

- Ten hybrid checks passed on [Windows GPU](../validation/standalone/release-0.1.3-windows-gpu.json),
  [X11](../validation/standalone/release-0.1.3-linux-x11.json) and
  [Wayland](../validation/standalone/release-0.1.3-linux-wayland.json).
- Five fresh-venv wheel checks passed on [Windows](../validation/standalone/release-0.1.3-installed-windows.json)
  and [Linux](../validation/standalone/release-0.1.3-installed-linux.json), launched outside
  the checkout, covering real sampling, both languages, assets and licenses.
- Windows: 29 unit tests passed. Linux: 28 passed, one platform skip. Ruff and strict
  bilingual documentation builds passed.
- The first cold X11 run had not completed sampling at the fixed four-second warmup
  assertion; the unchanged test passed on retry. Fixed test timings remain sensitive
  to host load. These checks do not guarantee frame rates or arbitrary compositor support.

Release assets include an offline bilingual manual, matching Windows CPython 3.12 /
Linux CPython 3.10 runtimes and SHA256 checksums. Browser restrictions are enforced
at the native boundary; host Python and native producers remain trusted code, without
an OS sandbox for arbitrary native plugins. See [installation](installation.md) and
the library security documentation.

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

## Expressive motion dependency update, 2026-10-17

Application tests passed: 27 on Windows; 26 passed and one skipped on WSL2. The library
was installed as an ordinary wheel. [Windows GPU](../validation/standalone/motion-windows-gpu.json),
[X11](../validation/standalone/motion-linux-x11.json) and
[Wayland](../validation/standalone/motion-linux-wayland.json) each passed ten real-display
integration checks, including embedded-browser focus, messages, language and canvas size.

[Expressive](../validation/standalone/motion-expressive.json),
[Subtle](../validation/standalone/motion-subtle.json) and
[Reduced motion](../validation/standalone/motion-reduced.json) use live system snapshots
and exercise rapid tab/focus reversal, controls, dialogs, notifications and PageStack.
The final 90 frames have empty diffs. At 140×42, CPU render+encode P95 in the
[old baseline](../validation/standalone/motion-baseline.json) versus the new snapshot:
resource transitions 33.857→11.611ms; modal exit 27.904→13.900ms. Process counts and
machine load vary; these measurements do not promise presentation FPS or every frame
below 16.7ms. See [reproduction steps](motion.md).

These performance samples use the base motion commit 2b4ea47. The then-pinned 40a4b45
additionally releases retired snapshots and native occlusion at the first zero crossing.
Final [Windows GPU](../validation/standalone/motion-retirement-windows-gpu.json),
[X11](../validation/standalone/motion-retirement-linux-x11.json) and
[Wayland](../validation/standalone/motion-retirement-linux-wayland.json) rechecks each
passed ten checks. Library tests remain 220 passed on Windows, 204 passed and five
skipped on WSL2.

## Frame pacing correction, 2026-10-18

Windows Python 3.12's coarse monotonic clock quantized frame deadlines. The dependency
now uses perf_counter, preserves frame phase and caches short text drawing. The control
already included the same text caches, retaining only the old clock to isolate scheduling.
Each run used an installed ordinary wheel, real Terminal, GPU charts, CEF and live
sampling, with focus/tab/dialog changes and the first three seconds excluded:

| Target | Control loop FPS | Corrected loop FPS | Interval P95 before / after |
| --- | --- | --- | --- |
| 60 | [32.00](../validation/standalone/pacing-coarse-60.json) | [59.67](../validation/standalone/pacing-after-60.json) | 32.744 / 17.259ms |
| 120 | [64.01](../validation/standalone/pacing-coarse-120.json) | [117.77](../validation/standalone/pacing-after-120.json) | 17.492 / 8.984ms |

The corrected 60 FPS run had one of 538 intervals exceed 1.5 times the budget; at 120,
13 of 1060 exceeded it. Neither run had an interval above 50ms. These are actual loop
timings, not monitor presentation FPS or end-to-end latency. See [motion](motion.md)
for reproduction and limitations.

[Windows GPU](../validation/standalone/pacing-windows-gpu.json),
[WSL2 X11](../validation/standalone/pacing-linux-x11.json) and
[WSL2 Wayland](../validation/standalone/pacing-linux-wayland.json) each passed ten hybrid
integration checks. App tests: 27 passed on Windows; 26 passed and one skipped on WSL2.
Library tests: 225 passed on Windows; 208 passed and six platform skips on WSL2.
Ruff and strict MkDocs builds for both manuals passed.

## v0.1.1 distribution verification

Both packages are version 0.1.1. The app requires ComfortableTUI 0.1.1 or newer so an
old library cannot silently omit the pacing correction. Universal wheels are built
from clean Git source snapshots. An optional Windows x64 CPython 3.12 GPU/C++ wheel
is also provided; it includes neither CEF nor the application's native runtime.

Fresh venv checks passed on [Windows](../validation/standalone/release-0.1.1-installed-windows.json)
and [WSL2 Linux](../validation/standalone/release-0.1.1-installed-linux.json): five checks
cover ordinary wheel imports, Apache notices, CLI version and live snapshots in both
languages. The new dependency also passed ten [Windows GPU](../validation/standalone/release-0.1.1-windows-gpu.json)
hybrid checks. Installed release wheels passed ten checks each under
[X11](../validation/standalone/release-0.1.1-linux-x11.json) and
[Wayland](../validation/standalone/release-0.1.1-linux-wayland.json).
All 27 app unit tests, Ruff and strict documentation builds passed; library release CI is green.

## v0.1.2 selected-process chart resizing

The selected CPU chart now fills its panel directly instead of using a fixed 24×5-cell
inline Text layout. New regression coverage exercises terminal and native canvases
through five viewport sizes, narrow-sidebar hiding and restoration. Windows: 29 tests
passed; WSL2: 28 passed and one platform skip.

Real Windows Terminal [GPU](../validation/standalone/resize-windows-gpu.json) and
[CPU](../validation/standalone/resize-windows-cpu.json) checks passed seven stages:
initial, maximized, Alt+Enter fullscreen, leaving fullscreen, smaller, larger and restored.
Each checks panel interior bounds, physical overlay pixels and stretch transforms.
Chart heights were 184, 368, 483, 368, 46, 230 and 184px respectively.
All ten [GPU/CEF hybrid checks](../validation/standalone/resize-hybrid.json) also passed.
Run tools/verify_chart_resize.py to reproduce; see [development](development.md).
