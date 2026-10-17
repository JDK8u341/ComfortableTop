# Motion and real application verification

[简体中文](../motion.md) | English

The pinned library defaults to Expressive: spring focus and selection, press feedback,
animated switches, sliders, bars, dialogs and notifications. Bar lengths interpolate;
numeric CPU readings immediately show the latest sample. Actions do not wait for
animations. Existing keyboard and embedded-browser focus rules remain in effect.

## Run and update

The local Windows `.venv` already has the new library wheel installed:

```powershell
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu --fps 60
```

For another source installation, follow [installation](installation.md). Updating only
the application does not replace an installed library wheel. The lock files now pin
the motion implementation. Both repositories merged it into `main`; v0.1.1 includes it.

```powershell
.\.venv\Scripts\python.exe tools/bootstrap.py --tui-source ..\tui --gpu
```

Use `--terminal-only` without native requirements. Existing CEF and frame protocols
are unchanged. The old v0.1.0 release attachments do not include this dependency update.

## Frame pacing update, 2026-10-18

On this Windows Python 3.12 installation, monotonic uses GetTickCount64 with roughly
15.625ms resolution. The old wait condition limited 60/120 FPS targets to about
32/64 FPS. The library now uses perf_counter deadlines, preserves frame phase and
caches short text runs and styles. Spring parameters are unchanged. See the
[CPython clock change](https://github.com/python/cpython/pull/116781).

Real Windows Terminal tests with GPU charts and CEF measured producer loop cadence
of 32.00→59.67 FPS at a 60 FPS target, and 64.01→117.77 at 120. Interval P95 improved
from 32.744→17.259ms and 17.492→8.984ms respectively. These are actual loop timings,
not display presentation FPS or input-to-photon latency. Terminal writes can still block.

The local wheel is updated; restart an existing app process. The default stays at 60 FPS;
optionally select `--fps 120`. The Windows probe opens its own Terminal with live sampling:

```powershell
.\.venv\Scripts\python.exe -m comfortable_top.verify_pacing --fps 60 --report .build/pacing-new-60.json
.\.venv\Scripts\python.exe -m comfortable_top.verify_pacing --fps 120 --report .build/pacing-new-120.json
```

Use new report paths. The default is 12 seconds, excluding the first three. It records
loop intervals and tick/render/encode/write/overlay phases while changing focus, tabs
and dialogs. A passed result means enough valid frames and system samples were
collected, not a machine-independent FPS guarantee. See [validation](validation.md)
for raw data and platform rechecks.

## Try the interactions

Use Tab/Shift+Tab to quickly reverse focus; F6 and arrows to reverse tab transitions;
F1/Esc to open and close help; Settings to change the slider; Resources to observe bar
interpolation. Verify Enter/Esc still enters and leaves Compare's embedded browser.
Closing dialogs restores focus immediately; their outgoing cell snapshots cannot
receive input or retain browser/native surfaces.

```powershell
$env:COMFORTABLE_TUI_MOTION = 'subtle'
.\.venv\Scripts\comfortable-top.exe
$env:COMFORTABLE_TUI_REDUCED_MOTION = '1'
.\.venv\Scripts\comfortable-top.exe
Remove-Item Env:COMFORTABLE_TUI_MOTION, Env:COMFORTABLE_TUI_REDUCED_MOTION
```

Reduced motion controls the library's decorative motion. It does not pause sampling,
CEF pages or external video producers.

## Verify

```powershell
.\.venv\Scripts\python.exe -m comfortable_top.verify_motion --report .build/my-motion.json
.\.venv\Scripts\python.exe -m comfortable_top.verify_motion --motion subtle --report .build/my-subtle.json
.\.venv\Scripts\python.exe -m comfortable_top.verify_motion --reduced-motion --report .build/my-reduced.json
.\.venv\Scripts\python.exe -m comfortable_top.verify_windows --mode hybrid --canvas gpu --report .build/my-display.json
```

Use new report paths. The motion verifier instantiates the real Monitor with two live
system samples and the installed TUI wheel, pauses sampling, then exercises quick
tab/focus reversals, notifications, dialogs and PageStack. The last 90 frames must
produce no diff. P50/P95 CPU render+encode times, bytes and changed frames are not
terminal presentation latency or screen FPS. This test is headless; real display
verification still requires Windows Terminal or a Linux graphical session:

```bash
comfortable-top --mode hybrid --platform x11 --self-test --smoke-seconds 15 --report .build/my-x11.json
comfortable-top --mode hybrid --platform wayland --self-test --smoke-seconds 15 --report .build/my-wayland.json
```

Windows GPU, WSL2 X11 and Wayland each passed ten integration checks. Application
unit tests: 27 on Windows; 26 passed and one skipped on WSL2. See [validation](validation.md).
