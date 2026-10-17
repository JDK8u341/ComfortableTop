import gc
import json

import pytest

from comfortable_top import i18n
from comfortable_top.collector import Collector
from comfortable_top.rendering import Charts
from comfortable_top.ui import Monitor
from comfortable_tui import Key, Panel
from comfortable_tui.canvas import text_width

from test_monitor import FakePsutil, process, sample


def test_language_precedence_invalid_preferences_and_atomic_save(monkeypatch, tmp_path):
    path = tmp_path / "config" / "settings.json"
    monkeypatch.setenv("COMFORTABLE_TOP_CONFIG", str(path))
    monkeypatch.setattr(i18n, "system_language", lambda: "zh")
    assert i18n.resolve_language() == "zh"
    i18n.save_language("en")
    assert i18n.resolve_language() == "en"
    assert i18n.resolve_language("zh") == "zh"
    assert json.loads(path.read_text())["language"] == "en"
    for invalid in ('{"language":"fr"}', '[]', '{broken', 'null'):
        path.write_text(invalid)
        assert i18n.resolve_language() == "zh"
    with pytest.raises(ValueError):
        i18n.save_language("fr")
    assert list(path.parent.iterdir()) == [path]


@pytest.mark.parametrize("language", ["en", "zh"])
@pytest.mark.parametrize("size", [(140, 42), (80, 24), (40, 12)])
def test_live_switch_preserves_state_and_layout(monkeypatch, tmp_path, language, size):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COMFORTABLE_TOP_CONFIG", str(tmp_path / "settings.json"))
    collector, charts = Collector(FakePsutil()), Charts("terminal")
    monitor = Monitor(collector, charts, language=language)
    try:
        with monitor.app as app:
            monitor.accept(sample(process(), process(20, cpu=None)))
            monitor.choose((10, 1.))
            monitor.pin()
            monitor.sort.set_value(1)  # Translated Memory must still sort the RSS field.
            monitor.search.set_value("python")
            monitor.export_fields.checked = {1}
            monitor.notes.text = "My notes / 我的笔记 / {CPU}"
            monitor.pause_changed(True)
            monitor.tabs.select(4)
            app.render(*size, dt=1)
            app.focus(monitor.language)
            history, count = list(monitor.model.timeline), monitor.count
            old_table, old_pages = monitor.table, list(monitor.tabs.children)
            app.dispatch(Key("f9"))
            target = "zh" if language == "en" else "en"
            assert monitor.i18n.language == target
            assert i18n.resolve_language() == target
            assert monitor.table is old_table and monitor.tabs.children == old_pages
            assert monitor.tabs.selected == 4 and app.focused is monitor.language
            assert monitor.model.sort == "Memory" and monitor.sort.selected == 1
            assert monitor.model.selected == (10, 1.) and monitor.model.pins == [(10, 1.)]
            assert monitor.model.query == "python" and monitor.search.text == "python"
            assert monitor.notes.text == "My notes / 我的笔记 / {CPU}"
            assert monitor.export_fields.checked == {1}
            assert list(monitor.model.timeline) == history and monitor.count == count and monitor.paused
            assert monitor.table.columns[1] == ("名称" if target == "zh" else "Name")
            assert monitor.tabs.titles[4] == ("设置" if target == "zh" else "Settings")
            for title, (_, width) in zip(monitor.tabs.titles, monitor.tabs._tab_bounds):
                assert width == text_width(title) + 2
            for index in range(5):
                monitor.tabs.select(index)
                app.render(*size, dt=1)
            monitor.help()
            app.render(*size)
            # An already open help modal changes in place too.
            modal = app.modal
            app.dispatch(Key("f9"))
            assert app.modal is modal and monitor.i18n.language == language
            assert modal.title == monitor.t("Comfortable Top / help")
            app.close_modal()
            monitor.language.activate()
            assert isinstance(app.modal, Panel) and app.modal.title == monitor.t("Choose")
            app.close_modal()
            monitor.sort.activate()
            app.dispatch(Key("f9"))
            assert app.modal.children[0].items[1] == monitor.t("Memory")
            app.close_modal()
            monitor.preview_export()
            app.dispatch(Key("f9"))
            app.render(*size, dt=1)
            assert monitor.pages.children[-1].title == monitor.t("Export preview")
    finally:
        collector.close()
        charts.close()


def test_transient_widgets_are_not_retained_by_translation_registry():
    from comfortable_tui import Label
    localizer = i18n.Localizer("en")
    widget = localizer.make(Label, "Close")
    assert len(localizer.bindings) == 1
    del widget
    gc.collect()
    assert len(localizer.bindings) == 0


def test_config_write_failure_keeps_active_language(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    blocked = tmp_path / "not-a-directory"
    blocked.write_text("occupied")
    monkeypatch.setenv("COMFORTABLE_TOP_CONFIG", str(blocked / "settings.json"))
    collector, charts = Collector(FakePsutil()), Charts("terminal")
    monitor = Monitor(collector, charts)
    try:
        with monitor.app as app:
            monitor.set_language("zh")
            assert monitor.tabs.titles[0] == "进程"
            assert "无法保存语言偏好" in app._toast
    finally:
        collector.close()
        charts.close()
