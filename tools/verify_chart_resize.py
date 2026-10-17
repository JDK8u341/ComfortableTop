"""Check chart alignment in a dedicated Windows Terminal, including Alt+Enter fullscreen."""
import argparse
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / '.build/selected-chart-resize-fullscreen.json'


def worker(canvas):
    from comfortable_top.collector import Collector
    from comfortable_top.paths import configure_runtime
    from comfortable_top.rendering import Charts
    from comfortable_top.ui import Monitor
    configure_runtime()
    user = ctypes.WinDLL('user32', use_last_error=True)
    user.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                  ctypes.c_int, ctypes.c_int, wintypes.UINT]
    user.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
    user.SystemParametersInfoW.argtypes = [wintypes.UINT, wintypes.UINT, ctypes.c_void_p, wintypes.UINT]
    user.GetForegroundWindow.restype = wintypes.HWND
    user.SetForegroundWindow.argtypes = [wintypes.HWND]

    class Keyboard(ctypes.Structure):
        _fields_ = [('vk', wintypes.WORD), ('scan', wintypes.WORD), ('flags', wintypes.DWORD),
                    ('time', wintypes.DWORD), ('extra', ctypes.c_size_t)]

    class MouseInput(ctypes.Structure):
        _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG), ('data', wintypes.DWORD),
                    ('flags', wintypes.DWORD), ('time', wintypes.DWORD), ('extra', ctypes.c_size_t)]

    class Payload(ctypes.Union):
        _fields_ = [('keyboard', Keyboard), ('mouse', MouseInput)]

    class Input(ctypes.Structure):
        _fields_ = [('type', wintypes.DWORD), ('payload', Payload)]

    user.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(Input), ctypes.c_int]
    collector, charts = Collector(), Charts('native', gpu=canvas == 'gpu')
    monitor = Monitor(collector, charts, language='en')
    app = monitor.app
    view = monitor.selected_chart_view
    records = []
    latest = {}
    callback = view.on_canvas_event

    def event(value):
        callback(value)
        if value.kind == 'transform':
            latest.update(value.data)

    view.on_canvas_event = event
    output = {'result': 'failed', 'stages': records}
    handle = [None]
    original = wintypes.RECT()
    work = wintypes.RECT()
    user.SystemParametersInfoW(0x30, 0, ctypes.byref(work), 0)

    def resize(ratio_w, ratio_h):
        user.ShowWindow(handle[0], 9)
        width, height = round((work.right - work.left) * ratio_w), round((work.bottom - work.top) * ratio_h)
        assert user.SetWindowPos(handle[0], None, work.left + 20, work.top + 20, width, height, 0x14)

    def ready():
        handle[0] = app._native_overlay_host.hwnd
        user.GetWindowRect(handle[0], ctypes.byref(original))
        check('initial')
        user.ShowWindow(handle[0], 3)

    def check(stage):
        assert view.rect == monitor.selected_chart_panel.rect.inset(1)
        assert app._size[0] >= 100, 'test desktop must show the process sidebar'
        transform = view.transform
        assert transform and latest
        screen, layer = latest['screen_rect'], latest['layer_rect']
        assert abs(screen.width - layer.width * view.rect.width / app._size[0]) <= 2
        assert abs(screen.height - layer.height * view.rect.height / app._size[1]) <= 2
        assert transform.viewport_size == (screen.width, screen.height)
        assert abs(transform.destination.width - screen.width) <= .01
        assert abs(transform.destination.height - screen.height) <= .01
        assert charts.get('selected').provider.frames > 0
        records.append(dict(stage=stage, grid=list(app._size),
                            cells=[view.rect.x, view.rect.y, view.rect.width, view.rect.height],
                            viewport=list(transform.viewport_size), scale=list(transform.scale)))

    def maximum():
        check('maximized')
        fullscreen()

    def fullscreen():
        user.SetForegroundWindow(handle[0])
        assert user.GetForegroundWindow() == handle[0], 'send keys only to our test terminal'
        inputs = (Input * 4)(*[Input(1, Payload(keyboard=Keyboard(vk, 0, flags, 0, 0)))
                              for vk, flags in ((0x12, 0), (0x0d, 0), (0x0d, 2), (0x12, 2))])
        assert user.SendInput(4, inputs, ctypes.sizeof(Input)) == 4

    def full():
        check('fullscreen')
        assert records[-1]['grid'][1] > records[-2]['grid'][1]
        fullscreen()

    def leave_fullscreen():
        check('left_fullscreen')
        resize(.88, .70)

    def smaller():
        check('resized_smaller')
        resize(.94, .88)

    def larger():
        check('resized_larger')
        user.SetWindowPos(handle[0], None, original.left, original.top,
                          original.right - original.left, original.bottom - original.top, 0x14)

    def finish():
        check('restored')
        assert len({entry['cells'][3] for entry in records}) >= 3
        output['result'] = 'passed'
        app.exit()

    try:
        with app:
            app.call_later(3, ready)
            app.call_later(5, maximum)
            app.call_later(7, full)
            app.call_later(9, leave_fullscreen)
            app.call_later(11, smaller)
            app.call_later(13, larger)
            app.call_later(15, finish)
            app.call_later(20, app.exit)
            app.run()
    except BaseException as error:
        output['error'] = repr(error)
        raise
    finally:
        collector.close()
        charts.close()
        REPORT.write_text(json.dumps(output, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--canvas', choices=('cpu', 'gpu'), default='gpu')
    args = parser.parse_args()
    REPORT = args.report.resolve()
    if sys.platform != 'win32':
        parser.error('requires Windows Terminal and a desktop wide enough for the process sidebar')
    if REPORT.exists():
        parser.error('choose a new report path')
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    if args.worker:
        worker(args.canvas)
    else:
        subprocess.Popen(['wt.exe', '-w', 'new', 'new-tab', '--title', 'Selected chart resize regression',
            '-d', str(ROOT), sys.executable, str(Path(__file__).resolve()), '--worker',
            '--report', str(REPORT), '--canvas', args.canvas], creationflags=0x08000000)
        deadline = time.perf_counter() + 50
        while time.perf_counter() < deadline:
            if REPORT.exists():
                result = json.loads(REPORT.read_text())
                print(json.dumps(result, indent=2))
                assert result['result'] == 'passed', result
                break
            time.sleep(.2)
        else:
            raise TimeoutError('resize worker did not complete')
