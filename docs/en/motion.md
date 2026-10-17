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
the motion implementation. Both repositories use branch `codex/expressive-motion`.

```powershell
.\.venv\Scripts\python.exe tools/bootstrap.py --tui-source ..\tui --gpu
```

Use `--terminal-only` without native requirements. Existing CEF and frame protocols
are unchanged. The old v0.1.0 release attachments do not include this dependency update.

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
