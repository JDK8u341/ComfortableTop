# Architecture and boundaries

[简体中文](../architecture.md) | English

## App and library

ComfortableTop owns its Python package, command, web assets, C++ chart module, tests
and documentation. ComfortableTUI is an external dependency supplying widgets,
terminal rendering, the shared-frame SDK, Windows overlay and CEF service. Linux currently supports terminal mode only. Its installed wheel does not reference a source checkout. This app links
the installed ComfortableFrames CMake package using `find_package`.

Setup may read user-provided dependency source or fetch a pinned commit. It installs
the wheel, SDK and hosts into this project's environment and ignored directories
without resetting a user checkout. Copied browser runtimes contain the files needed
by the Windows app; Linux terminal mode requires neither Qt nor CEF.

## Data paths

```text
Collector (one worker) → immutable Sample → MonitorModel → TUI widgets
                                             ├→ numeric samples → C++ Trend → CPU frames / D3D11 texture
                                             └→ authorized messages → CEF pages → image display service
```

Terminal mode uses PixelCanvas, negotiating Kitty or braille. Native and hybrid modes
submit up to 180 numeric values, descriptors and layout controls through Python.
An independent C++ thread interpolates, generates pixels and publishes CPU frames or
Windows GPU textures, stopping when unchanged. Producer and display consumer remain
separate; Python does not acquire frame leases on every display frame.

Web pages are an upper service. URLs, cookies, profiles and topics never enter the
general frame protocol. `--web-render-mode` controls browser transport independently
(Windows defaults to GPU; Linux graphical modes are suspended); `--canvas gpu` only affects native trend charts.

## Collection and identity

At most one collection runs at a time. Collection seconds and UI FPS are independent.
CPU/I/O use actual monotonic intervals. Process identities combine PID and creation
time; first readings, new processes, resets and protected fields never become fake zeros.
Linux collects psutil attributes in batches. Windows uses batched relationships and RSS,
then reads accessible process times, avoiding a whole-system fallback for each protected
process. Unreadable creation times count as unavailable; `alive` means present and swap
is unavailable on that Windows path.

Histories are bounded at 180 points per live process, with up to four pinned histories
retained after exit. Sorting tracks identity. Filtering or exit chooses a nearby ordinary
row; pinned items do not change identity when their PID is reused.

## Web isolation and focus

The application id is `org.comfortabletop.app`, separate from the old example. Its
temporary analytics profile belongs to this app and must not be reused across apps.
Each pinned identity opens a separate page; DOM, scroll and chart range are independent.
There are at most four process pages and one overview. Only exact local origins and
explicit topics are authorized.

`monitor.sample` carries telemetry; `monitor.select` returns stable identities.
`monitor.locale` updates the display language, including while sampling is paused.
`monitor.probe/proof` validates the normal message bridge without eval or relaxing CSP.
Notes and process-detail command lines are not sent to webpages. Each Top process,
including self-tests, owns a separate temporary browser root, removed after CEF
closes. Instances can run concurrently without sharing cookies, caches or messages.
The library still locks each individual data directory.

ResponsiveWebView divides full canvas pixels by DPI and waits 120ms before resizing
the page source. Moving/clipping does not resize it. Old sources remain alive until
the display consumer confirms replacement. Each axis is limited to 4096 pixels.
Responsive CSS and ResizeObserver keep charts filling available space.

Tab/Shift+Tab retain the TUI focus chain. Enter/click starts browser interaction;
Esc returns to the table; F6 returns to the menu. Read-only charts do not capture
keyboard focus and pass mouse input to their containers.

## Language and lifecycle

The app's Localizer explicitly binds application copy to existing widgets. Switching
updates those attributes and Unicode tab geometry without recreating the widget tree.
Weak bindings allow dismissed dialogs to be collected. Model sort identifiers and
export keys remain stable; user content is not translated. UI preference persistence
is separate from the browser profile and frame SDK. See [localization](localization.md).

Shutdown order is display host → logical App widgets/native consumers → collection
thread → browser service → chart producers → buffer owners. Logical widget closure
alone does not prove a display consumer has released its source; attachment confirmation
governs buffer lifetimes. Explicit exports use background workers and exclusive file creation.
