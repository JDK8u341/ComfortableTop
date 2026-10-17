# Development, testing and releases

[简体中文](../development.md) | English

## Source layout

| Path | Contents |
| --- | --- |
| src/comfortable_top | Entry point, collection, model, UI, localization and runtime discovery |
| src/comfortable_top/web | Packaged HTML/CSS/JS |
| native | App chart producer, linked to the installed external SDK |
| tools | Dependency bootstrap, native builds and runtime copying |
| tests | Model, collection, UI, language/state preservation, web resize, paths and packaging |
| docs | Independent Chinese/English MkDocs manuals and validation records |

The app does not include the old examples namespace or point sys.path at the library
source. Internal relative imports are ordinary Python package imports. Installed
commands work from any directory.

## Checks and documentation

Prepare dependencies as described in [installation](installation.md), then run:

```powershell
python -m pip install -e ".[dev,docs]"
python -m pytest -q
python -m ruff check .
python -m mkdocs build --strict
comfortable-top --snapshot --interval .25 --lang en
comfortable-top --snapshot --interval .25 --lang zh
python -m comfortable_top.verify_native --canvas cpu
python -m comfortable_top.verify_native --canvas gpu
python -m comfortable_top.verify_motion --report .build/motion-check.json
```

Windows integration opens its own Terminal and finishes in 14 seconds, operating only
this app and its local message bridge. Choose a new report path:

```powershell
python -m comfortable_top.verify_windows --mode hybrid --canvas gpu --report .build/verify-windows.json
python -m comfortable_top.verify_pacing --fps 60 --report .build/pacing-check-60.json
python -m comfortable_top.verify_pacing --fps 120 --report .build/pacing-check-120.json
```

verify_pacing measures actual App.run scheduling for 12 seconds by default, excluding
the first three. It complements headless verify_motion CPU timings; producer cadence
is still not screen presentation FPS. It requires Windows Terminal, and its default
hybrid mode needs GPU and browser runtimes.

The headless motion verifier exercises the actual Monitor and installed library with
live samples, rapid reversals, dialogs, notifications and empty settled diffs. It also
accepts `--motion subtle` and `--reduced-motion`. Its CPU timings are not screen FPS.
See [motion and verification](motion.md).

```bash
comfortable-top --mode hybrid --platform x11 --self-test --smoke-seconds 14 --report .build/x11.json
comfortable-top --mode hybrid --platform wayland --self-test --smoke-seconds 14 --report .build/wayland.json
```

Self-tests now also change Chinese/English while paused, confirm all browser pages
receive the setting, and check page identity remains stable. They do not save the test
language to user preferences. Do not substitute offscreen/minimal for real display checks.
Producer frame counts in the GIL test do not represent screen FPS.

Validate a built wheel in a fresh environment outside the checkout:

```powershell
python tools/verify_distribution.py --wheel dist/comfortable_top-0.1.1-py3-none-any.whl --tui-wheel PATH/comfortable_tui-WHEEL.whl --report .build/wheel-check.json
```

This creates a separate venv, verifies package imports, web assets, Apache notices,
entry points and two real samples in an empty working directory. Windows/Linux SDKs,
builds, runtimes and verification environments use platform-specific directories.

## Distribution

```powershell
python -m build --no-isolation
```

`dist/` contains the pure Python app wheel and source archive. The wheel includes web
assets, LICENSE and NOTICE. The source archive also includes native code, tools,
Chinese/English documentation and tests. Native binaries and CEF are separate from
the pure Python wheel. GPU dependency wheels must match the interpreter ABI/platform.

A GitHub release is not a PyPI release. Preserve installation instructions for private
dependency source, native/CEF builds and runtime locations. The initial release does
not bundle the large CEF runtime; build from the SDK or copy an authorized existing
runtime, retaining third-party notices.

Keep Git tags and package versions consistent. Run tests and fresh-wheel checks before
creating a release. Update each Chinese document together with its English counterpart,
including reciprocal language links and MkDocs navigation. Application changes normally
need no library changes; modify shared controls/protocols separately in ComfortableTUI
and update the pinned dependency rather than copying the library into this project.
