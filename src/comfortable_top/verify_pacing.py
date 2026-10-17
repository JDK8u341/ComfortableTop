"""Real Windows Terminal pacing probe; CPU timings do not measure display scanout."""
from __future__ import annotations

import argparse
from collections import deque
from contextlib import ExitStack
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import time

from .collector import Collector
from .paths import configure_runtime
from .rendering import Charts
from .ui import Monitor
from .web import WebPanels


def stats(values):
    ordered = sorted(values)
    return dict(p50=round(statistics.median(ordered), 3),
        p95=round(ordered[int((len(ordered) - 1) * .95)], 3),
        p99=round(ordered[int((len(ordered) - 1) * .99)], 3), max=round(max(ordered), 3))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--fps", type=int, choices=(60, 120), default=60)
    parser.add_argument("--mode", choices=("terminal", "native", "hybrid"), default="hybrid")
    parser.add_argument("--seconds", type=float, default=12)
    args = parser.parse_args()
    report = args.report.resolve()
    if report.exists() or args.seconds < 10:
        parser.error("use a new report path and at least ten seconds")
    if not args.worker:
        if os.name != "nt" or not shutil.which("wt.exe"):
            parser.error("requires Windows Terminal; run the headless motion verifier on other systems")
        subprocess.Popen(["wt.exe", "-w", "new", "new-tab", "--title", "ComfortableTop pacing probe",
            "-d", str(Path.cwd()), sys.executable, "-m", "comfortable_top.verify_pacing", "--worker",
            "--fps", str(args.fps), "--mode", args.mode, "--seconds", str(args.seconds), "--report", str(report)],
            creationflags=0x08000000)
        deadline = time.monotonic() + args.seconds + 40
        while time.monotonic() < deadline:
            if report.exists():
                try:
                    data = json.loads(report.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    time.sleep(.05)
                    continue
                print(json.dumps(data, indent=2))
                if data["result"] != "passed":
                    raise RuntimeError(data.get("error", "pacing probe failed"))
                return
            time.sleep(.2)
        raise TimeoutError("The pacing terminal did not produce its report")

    configure_runtime()
    result = {}
    try:
        with ExitStack() as stack:
            collector = Collector()
            stack.callback(collector.close)
            charts = Charts(args.mode, gpu=args.mode != "terminal")
            stack.callback(charts.close)
            web = WebPanels(temporary=True, language="en") if args.mode == "hybrid" else None
            if web:
                stack.callback(web.close)
            monitor = Monitor(collector, charts, web=web, fps=args.fps, language="en")
            app = stack.enter_context(monitor.app)
            timings = deque(maxlen=6000)
            app.on_frame = timings.append
            controls = [monitor.search, monitor.sort, monitor.pause, monitor.own]
            index = [0]

            def move():
                if app.modal is None:
                    app.focus(controls[index[0] % len(controls)])
                    index[0] += 1

            app.call_later(.12, move, repeat=True)
            app.call_later(4, lambda: monitor.tabs.select(1))
            app.call_later(7, monitor.help)
            app.call_later(7.5, app.close_modal)
            app.call_later(9, lambda: monitor.tabs.select(0))
            app.call_later(args.seconds, app.exit)
            app.run()
            origin = timings[0].started
            samples = [s for s in timings if s.started - origin >= 3 and s.rendered]
            if len(samples) < 60 or monitor.count < 2:
                raise RuntimeError("Insufficient live frames or process samples")
            intervals = [1000 * s.interval for s in samples]
            budget = 1000 / args.fps
            fields = ("tick", "render", "encode", "write", "overlay")
            result = dict(result="passed", target_fps=args.fps, mode=args.mode,
                size=list(app._size), samples=monitor.count, measured_frames=len(samples),
                rendered_fps=round((len(samples) - 1) / (samples[-1].started - samples[0].started), 2),
                interval_ms=stats(intervals),
                intervals_over_1_5_budget=sum(v > budget * 1.5 for v in intervals),
                intervals_over_50ms=sum(v > 50 for v in intervals),
                phases_ms={name: stats([1000 * getattr(s, name) for s in samples]) for name in fields},
                synchronized=app.renderer.synchronized, renderer=app.renderer.backend,
                note="Actual producer loop cadence and blocking phases, excluding first 3s; not screen FPS or input-to-photon latency")
    except BaseException as error:
        result = dict(result="failed", error=str(error))
        raise
    finally:
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
