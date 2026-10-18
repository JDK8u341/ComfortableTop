from concurrent.futures import Future

import pytest

from comfortable_tui import browser


class FakeProcess:
    calls = []

    def __init__(self, command, **kwargs):
        self.command = command
        self.capabilities = {"startup_ui_suppressed": True, "security_protocol": 2}
        self.messages = []
        self.calls.append(self)

    def close(self):
        pass

    def request(self, op, **kwargs):
        self.messages.append((op, kwargs))
        return {"security": kwargs["security"]} if op == "open" else {}

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


def test_browser_language_sync_does_not_recreate_pages_or_depend_on_sampling(browser_service, monkeypatch):
    from urllib.parse import parse_qs, urlparse
    from comfortable_top import web
    monkeypatch.setattr(web, "BrowserService", lambda *args, **kwargs: browser_service)
    panels = web.WebPanels(language="zh")
    try:
        view = panels.widget()
        page, buffer = view.page, view.buffer
        opened = [data for op, data in browser_service._rpc.messages if op == "open"][-1]
        assert parse_qs(urlparse(opened["url"]).query)["lang"] == ["zh"]
        assert "monitor.locale" in opened["subscribe_topics"]
        browser_service._rpc.messages.clear()
        panels.set_language("en")
        assert panels.pages["overview"] is page and view.buffer is buffer
        messages = browser_service._rpc.messages
        assert any(data.get("topic") == "monitor.locale" and data.get("payload") == {"language": "en"}
                   for op, data in messages)
        # A page that finished loading late receives the current language.
        messages.clear()
        panels._event({"event": "loaded", "view": page.id})
        assert any(data.get("payload") == {"language": "en"} for op, data in messages)
        panels.widget((12, 1.))
        opened = [data for op, data in browser_service._rpc.messages if op == "open"][-1]
        assert parse_qs(urlparse(opened["url"]).query)["lang"] == ["en"]
        assert panels.pages["overview"] is page
    finally:
        panels.close()


def test_web_panels_pass_selected_transport_to_every_independent_page(monkeypatch):
    from comfortable_top import web

    opened = []

    class Service:
        def __init__(self, *args, **kwargs):
            pass

        def profile(self, *args, **kwargs):
            return "profile"

        def on_event(self, callback):
            pass

        def open(self, *args, **kwargs):
            opened.append(kwargs)
            return object()

        def close(self):
            pass

    monkeypatch.setattr(web, "BrowserService", Service)
    monkeypatch.setattr(web, "ResponsiveWebView", lambda page: page)
    panels = web.WebPanels(render_mode="gpu")
    try:
        panels.widget()
        panels.widget((42, 1.))
        assert len(opened) == 2 and all(call["render_mode"] == "gpu" for call in opened)
        with pytest.raises(RuntimeError, match="GPU import failed"):
            panels._event({"event": "error", "data": {"message": "GPU import failed"}})
    finally:
        panels.close()
