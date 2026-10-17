# Troubleshooting

[简体中文](../troubleshooting.md) | English

## pip cannot find comfortable-tui

Do not assume the dependency exists on PyPI. Use bootstrap, requirements-tui.txt or
install a compatible local wheel first. Private Git source requires local Git credentials.
Never put access tokens into command URLs, configuration or commits.

## Missing _ctui_top_native

Run `tools/build_runtime.py` with the same Python used to launch the app. The default
module directory is `.runtime/<platform>/native`. Use COMFORTABLE_TOP_RUNTIME for a
complete runtime root, or `--native-module DIR` for a module directory. Python 3.12
extensions cannot be used with 3.10; Windows .pyd files cannot run on Linux.

## GPU unavailable

The current D3D11 route is Windows-only and the ComfortableTUI dependency needs its GPU
extension too. Run `tools/bootstrap.py --gpu`. This option selects chart transport;
it does not collect hardware GPU utilization. Terminal or native CPU mode can display
the same system telemetry.

## Missing CEF or WindowHost

Check the complete runtime/browser directory; Linux also needs runtime/host/ctui_linux_canvas.
Copy using build_runtime's --browser-runtime/--host-binary or build using --cef-root.
Copying only an exe or libcef.dll is insufficient. COMFORTABLE_TOP_RUNTIME points to
the root, not its browser/native child. Explicit COMFORTABLE_TUI_* variables override discovery.

## Browser appears tiny or blurry

The app reflows the page viewport to the panel's logical size. Restart to load current
web assets. Reflow occurs approximately 120ms after resizing settles; clipping alone
does not change the full page size. Enlarge small terminals to the recommended dimensions.
Report DPI, terminal size, mode and runtime version, without cookies or full command lines.

## Fewer rows than the system process count

Protected Windows processes without readable creation times count as unavailable to
avoid associating a reused PID with the wrong identity. Reading existing data does not
require elevation. First CPU/I/O readings, resets and unavailable fields display
warmup/n/a (translated in Chinese). `alive` only means present; RSS is not unique memory.

## WSL or Wayland connection fails

Select x11/wayland explicitly and check DISPLAY/WAYLAND_DISPLAY against the desktop
session. The library probes child-process sockets for missing WSLg runtime-directory
links. Without an available socket it reports an error; it does not modify the system's
XDG_RUNTIME_DIR or silently switch to X11. WSL metrics refer to the Linux subsystem.

## Browser terms or CSP errors

The service keeps its no-first-run policy and application-private profile. It does not
automatically accept external website agreements. Local pages retain strict CSP;
self-tests use probe/proof messages, not dynamic eval. Manual page.evaluate() calls
remain subject to that page's CSP.

## Language preference is not saved

F9 still changes the current UI if the configuration directory is unwritable; a
notification explains the failure. Check [preference paths](localization.md), or set
COMFORTABLE_TOP_CONFIG to a writable file location. `--lang en/zh` deliberately overrides
the saved choice for one launch. Invalid configuration falls back to the system locale.
Original notes, process names, raw detail fields and existing logs are data and remain
unchanged. Install a CJK-capable terminal font if Chinese glyphs are missing.
