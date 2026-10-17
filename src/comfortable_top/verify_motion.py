"""Measure real Monitor rendering and verify motion without claiming screen FPS."""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import json
from pathlib import Path
import statistics
import time

import comfortable_tui

from .collector import Collector
from .paths import configure_runtime
from .rendering import Charts
from .ui import Monitor


def percentile(values, fraction):
    return sorted(values)[min(len(values) - 1, int((len(values) - 1) * fraction))]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--motion", choices=("expressive", "subtle"), default="expressive")
    parser.add_argument("--reduced-motion", action="store_true")
    parser.add_argument("--mode", choices=("terminal", "native"), default="terminal")
    parser.add_argument("--canvas", choices=("cpu", "gpu"), default="cpu")
    parser.add_argument("--width", type=int, default=140)
    parser.add_argument("--height", type=int, default=42)
    args = parser.parse_args()
    if args.report.exists():
        parser.error("choose a new report path")
    configure_runtime()
    with ExitStack() as stack:
        collector = Collector()
        stack.callback(collector.close)
        charts = Charts(args.mode, gpu=args.canvas == "gpu")
        stack.callback(charts.close)
        monitor = Monitor(collector, charts, language="en")
        app = stack.enter_context(monitor.app)
        supported = hasattr(app, "set_motion")
        if supported:
            app.set_motion(args.motion)
        app.animator.reduced_motion = args.reduced_motion
        monitor.accept(collector.collect())
        time.sleep(.25)
        monitor.accept(collector.collect())
        monitor.pause_changed(True)
        app.renderer.synchronized = True
        stages = {}

        def run(name, action=lambda: None, frames=48, per_frame=None):
            action()
            times, sizes, changed = [], [], 0
            previous_cells, unstable = None, []
            for index in range(frames):
                if per_frame:
                    per_frame(index)
                start = time.perf_counter()
                frame = app.render(args.width, args.height, dt=1 / 60)
                data = app.encode(frame)
                times.append((time.perf_counter() - start) * 1000)
                sizes.append(len(data.encode("utf-8")))
                changed += bool(data)
                if name == "settled" and previous_cells is not None and data and len(unstable) < 4:
                    unstable.append([(i % frame.width, i // frame.width, a.text != b.text)
                        for i, (a, b) in enumerate(zip(previous_cells, frame.cells)) if a != b][:12])
                previous_cells = frame.cells
            stages[name] = dict(p50_ms=round(statistics.median(times), 3),
                p95_ms=round(percentile(times, .95), 3), max_ms=round(max(times), 3),
                p95_bytes=percentile(sizes, .95), changed_frames=changed, frames=frames)
            if unstable:
                stages[name]["unstable_cells"] = unstable

        run("warmup")
        run("focus", lambda: app.focus(monitor.pause))
        # Exercise programmatic state changes while keeping sampling paused.
        run("switch", lambda: setattr(monitor.pause, "checked", False))
        monitor.pause.checked = True
        run("selection", lambda: (app.focus(monitor.table), monitor.table.select(min(8, len(monitor.table.items) - 1))))
        run("resources", lambda: monitor.tabs.select(1))
        run("modal_enter", monitor.help)
        run("modal_exit", app.close_modal)
        run("notification_enter", lambda: app.notify("Motion verification", duration=.9), frames=30)
        run("notification_exit", frames=72)
        run("workspace", lambda: monitor.tabs.select(3))
        run("page_push", monitor.preview_export)
        run("page_pop", monitor.pages.pop)
        run("settings", lambda: monitor.tabs.select(4))
        run("slider", lambda: monitor.cadence.set_value(2))
        run("rapid_tabs", frames=90, per_frame=lambda i:
            monitor.tabs.select((1, 3, 2, 4, 0)[i // 6]) if i < 30 and i % 6 == 0 else None)
        assert monitor.tabs.selected == 0
        run("rapid_focus", frames=90, per_frame=lambda i:
            app.focus((monitor.search, monitor.pause, monitor.sort, monitor.own, monitor.search)[i // 6])
            if i < 30 and i % 6 == 0 else None)
        run("return", lambda: monitor.tabs.select(0), frames=90)
        run("settled", frames=90)
        assert not app.animator.active, "animations must stop when settled"
        assert stages["settled"]["changed_frames"] == 0, f"settled output must be empty: {stages['settled']}"
        assert app.modal is None and len(monitor.pages.children) == 1
        assert monitor.paused and monitor.count >= 2
        if supported and not args.reduced_motion:
            assert stages["focus"]["changed_frames"] > 1
            assert stages["modal_exit"]["changed_frames"] > 1
            assert stages["rapid_tabs"]["changed_frames"] > 10
        report = dict(result="passed", installed_library=str(Path(comfortable_tui.__file__).resolve()),
            semantic_motion_supported=supported, motion=args.motion, reduced_motion=args.reduced_motion,
            mode=args.mode, canvas=args.canvas, size=[args.width, args.height], samples=monitor.count,
            readable_processes=len(monitor.model.sample.processes),
            note="CPU render+encode timings, not terminal presentation latency or screen FPS", stages=stages)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
