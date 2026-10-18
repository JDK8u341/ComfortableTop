# User guide

[简体中文](../guide.md) | English

Run `comfortable-top` or `python -m comfortable_top` after [installation](installation.md).
Version 0.1.4 defaults to GPU browser frames in Windows hybrid mode; select
`--web-render-mode cpu` for comparison. Top no longer provides a Linux version. Native charts continue
to use the independent `--canvas cpu|gpu` option. Matching new runtime files are required.
A terminal of at least 120×38 is recommended. Narrow windows hide the detail sidebar;
tables can scroll horizontally. Press **F9** or use **Settings → Language / 语言** to
switch between English and Chinese. `--lang en/zh/auto` chooses the startup language.

## Pages and controls

| Page | Purpose |
| --- | --- |
| Processes | Live virtual DataTable, embedded sparklines, filtering, sorting, user filter, stable identities, background detail dialogs and a selected-process chart mixed with text |
| Resources | CPU history, per-core bars, memory progress, interface/disk rates and interactive browser analytics |
| Compare | Up to four pinned processes; canvas in a virtual list, independent WebView in each table row, expandable process tree |
| Workspace | Unicode notes, activity log, directory tree, export-field selection, background JSON export and PageStack preview |
| Settings | Language, sampling interval, sort direction, collapsible metric definitions, rendering information and keyboard help |

The toolbar uses Input, Select, Switch, Checkbox, Spinner and Rule. Tabs, focus and
progress bars retain the toolkit's animations. The monitor reads processes; it does not terminate them.

| Shortcut | Action |
| --- | --- |
| F1 / F2 | Help / search PID, name, user and raw status; all space-separated terms must match |
| F3 / F4 | Cycle CPU, memory, PID and name sorting / pin or unpin |
| F7 / F8 | Pause or resume sampling / read process details in the background |
| F9 | Switch English/Chinese and save the preference |
| Ctrl+1…5 | Switch main pages |
| Ctrl+E | Export snapshot and notes into a new JSON file in the chosen directory |
| F6 / Tab / Shift+Tab | Menu/content focus and the normal focus chain |
| Enter / Esc | Inspect a process; enter an embedded browser in Compare / return to its table; close dialog or preview |
| Ctrl+Q / Ctrl+C | Exit and release consumers, producers, services and shared buffers |

Identity is **PID + creation time**. Sorting follows identity. A pinned process that
exits remains explicitly marked as exited; PID reuse never turns it into a new process.
F4 removes an exited watch when its Compare list/table row is selected. Ordinary process
tables select a neighboring row when a selected process exits or is filtered out.
Pause freezes the monitor snapshot and discards one sample already in flight; it does
not suspend system processes. Language changes remain available while paused.

## Browser analytics

Each pinned process has its own `BrowserService.open()` page: DOM, scroll and chart
range are independent. Pages share this application's private, temporary local-analytics
profile. Explicitly authorized `monitor.sample/select` messages link telemetry and
selection; `monitor.locale` updates language and `monitor.probe/proof` verifies the bridge.
Pages keep a strict CSP; validation does not use dynamic eval. At most five pages exist;
unpinning closes the corresponding process page.

ResponsiveWebView uses full viewport physical pixels divided by DPI. It reflows instead
of shrinking a fixed-aspect page into a thumbnail. Charts fill the remaining area; short
panels use compact controls. A 120ms resize debounce replaces the source buffer only
after the size settles, with a 4096-pixel limit per axis. Moving or clipping a view does
not resize its page. This is an app-level one-page-per-view policy; ordinary library
WebView mirrors keep their fixed-source semantics. Outside hybrid mode, two charts for
the same process may mirror a source; sources for different pinned slots are independent.

## Options and metric semantics

`--interval .25..5` controls collection seconds (default 1); `--fps 1..240` controls
the UI target (default 60). `--output DIR` pre-fills the export directory. `--snapshot`
collects twice and prints a terminal frame. `--smoke-seconds N` exits automatically;
`--report PATH` writes aggregate checks. `--self-test` exercises the UI and needs at
least 14 seconds; omit it for ordinary use. See [localization](localization.md) for `--lang`.

```text
Background collector → immutable Sample → bounded Model → TUI widgets
                                             ├→ numeric data → C++ chart thread → CPU frames / Win GPU texture
                                             └→ application messages → CEF pages → image display layer
```

Terminal charts use a small PixelCanvas with Kitty graphics or braille fallback. In
native modes Python does not generate, copy or transfer pixels per frame. It allocates
buffers, passes descriptors, submits at most 180 values per sample and handles layout,
scale and lifecycle events. C++ interpolates and publishes, then stops when unchanged.
There are at most six chart producers; four watch slots are reused. Threads and browser
pages do not grow with the system process count. Read-only charts pass pointer input
to their containers; browser interaction follows the normal focus rules.

Process CPU is the user+system time delta divided by the actual monotonic sample interval;
100% means one core and values may exceed 100%. System CPU averages all cores. Charts
clip to 0…100%; tables keep exact values. Missing values leave gaps, not invented zeros.
Sparklines scale relatively. Per-core bars use a fixed 100% maximum: 58.6% fills about
58.6% of the track regardless of other cores. Numbers show the latest actual percentage;
bar lengths interpolate smoothly between samples.
First readings, new processes, resets and unreadable fields show warmup/n/a, localized
in Chinese. RSS is resident memory, not unique memory. System memory is total−available.
Network includes loopback. Disk totals sum OS device counters and can double-count layers.

Linux uses `psutil.process_iter(attrs=...)`. Windows batches Toolhelp relationships
and thread counts, reads documented RSS fields through NtQuerySystemInformation and
uses GetProcessTimes for accessible identities and CPU. Reserved fields are opaque.
Protected processes without readable creation times count as unavailable. Windows
status `alive` only means present; swap is unavailable. Usernames are cached by identity.
Collection tasks never overlap; actual cadence is bounded by OS read cost.

Each live identity retains at most 180 points. Only four pinned histories survive exit.
Notes are not sent to webpages. Explicit exports create exclusive, uniquely named files
and never overwrite existing files. JSON field names and original process data remain
unchanged when the UI language changes.
