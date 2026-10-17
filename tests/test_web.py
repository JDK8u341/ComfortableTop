from concurrent.futures import Future

import pytest

from comfortable_tui import browser


class FakeProcess:
    calls = []

    def __init__(self, command, **kwargs):
        self.command = command
        self.capabilities = {"startup_ui_suppressed": True}
        self.messages = []
        self.calls.append(self)

    def close(self):
        pass

    def request(self, op, **kwargs):
        return {}

    def send(self, op, **kwargs):
        self.messages.append((op, kwargs))
        future = Future()
        future.set_result({})
        return future

    def events(self):
        return []

@pytest.fixture
def browser_service(monkeypatch, tmp_path):
    monkeypatch.setattr(browser, "NativeProcess", FakeProcess)
    executable = tmp_path / "ctui_browser"
    executable.touch()
    with browser.BrowserService(executable=executable) as service:
        yield service

def test_top_browser_reflows_to_latest_panel_size_with_dpi_and_debounce(browser_service):
    from comfortable_tui import App, CanvasEvent, CanvasTransform
    from comfortable_top.web import ResponsiveWebView
    page = browser_service.open("about:blank", width=720, height=400)
    view = ResponsiveWebView(page)
    with App(view) as app:
        app.render(40, 12)
        original = page.source
        def transform(width, height):
            view._emit(CanvasEvent("transform", {"transform": CanvasTransform.calculate(
                (page.source.info.width, page.source.info.height), (width, height), "stretch", 1.5)}))
        transform(900, 180)
        app.render(40, 12, dt=.05)
        assert page.source is original
        transform(1200, 300)
        app.render(40, 12, dt=.10)
        assert page.source is original
        app.render(40, 12, dt=.03)
        assert (page.source.info.width, page.source.info.height) == (800, 200)
        assert view.buffer is page.source and view.fit == "stretch"
        settled = page.source
        # Moving/clipping a panel at the same full size must not allocate again.
        transform(1200, 300)
        app.render(40, 12, dt=1)
        assert page.source is settled and len(page._buffers) == 1

def test_top_browser_defers_hidden_resize_and_preserves_attached_source(browser_service):
    from comfortable_tui import App, CanvasEvent, CanvasTransform, Label, Tabs
    from comfortable_top.web import ResponsiveWebView
    page = browser_service.open("about:blank", width=720, height=400)
    view = ResponsiveWebView(page)
    tabs = Tabs({"Hidden": Label("Other page"), "Web": view})
    with App(tabs, reduced_motion=True) as app:
        app.render(40, 12)
        original = page.source
        view._emit(CanvasEvent("transform", {"transform": CanvasTransform.calculate((720, 400), (700, 160))}))
        app.render(40, 12, dt=1)
        assert page.source is original
        tabs.select(1)
        app.render(40, 12, dt=1)
        view._session = object()
        view._emit(CanvasEvent("buffer_attached", {"buffer": original.info}))
        app.render(40, 12, dt=.2)
        assert (page.source.info.width, page.source.info.height) == (700, 160)
        original._check_open()
        view._emit(CanvasEvent("buffer_attached", {"buffer": page.source.info}))
        with pytest.raises(RuntimeError, match="closed"):
            original._check_open()
        current = page.source
        view._emit(CanvasEvent("transform", {"transform": CanvasTransform.calculate((700, 160), (800, 200))}))
        view._emit(CanvasEvent("transform", {"transform": CanvasTransform.calculate((700, 160), (0, 0))}))
        app.render(40, 12, dt=1)
        assert page.source is current
        view._session = None
