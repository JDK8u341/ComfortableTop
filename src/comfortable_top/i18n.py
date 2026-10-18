"""Application text and live widget bindings; telemetry and user data stay intact."""
from __future__ import annotations

import json
import locale
import os
from pathlib import Path
import tempfile
from weakref import WeakKeyDictionary

from comfortable_tui import ListView, Panel, Select
from comfortable_tui.canvas import text_width


ZH = {
    "Comfortable Top · waiting for live system data": "Comfortable Top · 等待系统数据",
    "F1 help · F2 search · F3 sort · F4 pin · F6 menu · F9 中/En · Tab focus · Ctrl+Q quit":
        "F1 帮助 · F2 搜索 · F3 排序 · F4 固定 · F6 菜单 · F9 中/En · Tab 焦点 · Ctrl+Q 退出",
    "Collecting": "采集中", "CPU warmup": "CPU 预热中", "RAM": "内存",
    "Network/disk rates warmup": "网络/磁盘速率预热中", "Filter PID / name / user": "筛选 PID / 名称 / 用户",
    "CPU": "CPU", "Memory": "内存", "PID": "PID", "Name": "名称", "User": "用户",
    "State": "状态", "Trend": "趋势", "RSS": "RSS", "CPU%": "CPU%",
    "Pause": "暂停", "My user": "当前用户", "Select a process": "请选择进程",
    "Selected CPU · 0..100%": "选中进程 CPU · 0..100%", "Inspect": "详情", "Pin/unpin": "固定/取消",
    "Processes · arrows scroll · Enter inspect": "进程 · 方向键滚动 · Enter 查看详情",
    "Interface": "网卡", "Receive/s": "接收/秒", "Send/s": "发送/秒",
    "Device": "设备", "Read/s": "读取/秒", "Write/s": "写入/秒",
    "Use --mode hybrid for interactive browser analytics. Native CPU/GPU charts use --mode native. "
    "This mode already plots the same real metrics using Kitty graphics or braille.":
        "使用 --mode hybrid 启用交互式网页分析，--mode native 启用原生 CPU/GPU 图表。"
        "当前模式通过 Kitty 图像或盲文点阵绘制相同的真实指标。",
    "System CPU · 0..100%": "系统 CPU · 0..100%", "Independent browser analytics": "独立网页分析",
    "Rendering modes": "渲染模式", "Logical cores · 0..100%": "逻辑核心 · 0..100%",
    "Network and disks": "网络与磁盘", "Watch": "固定项", "Independent analysis": "独立分析",
    "Watch list": "固定列表", "Pinned histories · up to four": "固定历史 · 最多四项",
    "Per-process pages · Enter interact / Esc leave": "独立进程页面 · Enter 交互 / Esc 返回",
    "Process tree": "进程树", "Parent relationships · arrows expand · Enter select": "父子关系 · 方向键展开 · Enter 选择",
    "# Investigation notes\n\nPin a process, inspect it and record what you observe.\n":
        "# 调查笔记\n\n固定进程、查看详情，并记录观察结果。\n",
    "System + interface counters": "系统与网卡计数", "Process snapshot": "进程快照",
    "Session notes · not sent to browser": "会话笔记 · 不发送给浏览器", "Activity log": "活动日志",
    "Preview export": "预览导出", "Export JSON": "导出 JSON", "Output directory": "输出目录",
    "Files and export": "文件与导出",
    "Collection cadence is separate from UI FPS. One collection may run at a time.":
        "采样周期与界面帧率独立。同一时间最多执行一次采样。",
    "Sample interval / seconds": "采样间隔 / 秒", "Descending": "降序", "Ascending": "升序",
    "Metric meanings": "指标含义",
    "CPU: process 100% means one core; system 100% means the whole machine. "
    "Unknown or first readings show warmup/n/a. Process RSS is resident memory, not unique memory. "
    "Disk counters are per-device OS totals and can include layered devices. Network totals include loopback.":
        "进程 CPU 100% 表示一个核心，系统 CPU 100% 表示整机。首次或未知读数显示预热中/不可用。"
        "RSS 是驻留内存，并非独占内存。磁盘为系统设备计数，可能包含分层设备；网络总量包含回环。",
    "Rendering / transport": "渲染 / 传输", "Keyboard help": "快捷键帮助",
    "Processes": "进程", "Resources": "资源", "Compare": "对比", "Workspace": "工作区",
    "Settings": "设置", "Monitor settings": "监视器设置", "Throughput": "吞吐量",
    "Language / 语言": "Language / 语言", "Choose": "选择", "Close": "关闭", "Back": "返回", "Export": "导出",
    "Process detail · Esc closes": "进程详情 · Esc 关闭", "Export preview": "导出预览",
    "Comfortable Top / help": "Comfortable Top / 帮助",
    "Sampler started. Process CPU: 100% = one logical core. No process actions are executed.":
        "采样已启动。进程 CPU 100% = 一个逻辑核心。本应用仅读取进程。",
    "Sample interval {value:g}s": "采样间隔 {value:g} 秒", "Sampling paused": "采样已暂停",
    "Sampling resumed": "采样已恢复", "Sampler error: {error}": "采样错误：{error}",
    "Sampler error: {error} · F1 help": "采样错误：{error} · F1 帮助",
    "up {hours:.1f}h · {count} readable processes · {ms:.0f}ms sample":
        "运行 {hours:.1f} 小时 · {count} 个可读进程 · 采样 {ms:.0f} 毫秒",
    "{value} · {count} logical CPUs": "{value} · {count} 个逻辑 CPU",
    "swap {value}": "交换区 {value}", "{count} partial/unavailable process records": "{count} 条不完整/不可用的进程记录",
    "PID {pid} · parent {parent}": "PID {pid} · 父进程 {parent}", "Threads {count}": "线程数 {count}",
    "Pinned": "已固定", "F4 to pin": "F4 固定", "No matching process": "无匹配进程",
    "Process already exited": "进程已退出", "{pid} · exited\nF4 to unpin": "{pid} · 已退出\nF4 取消固定",
    "Select a live process; at most four watches": "请选择存活进程；最多固定四项",
    "Watch set: {pids}": "固定列表：{pids}", "Processes: {count}\nDirectory: {path}\n\n{notes}":
        "进程数：{count}\n目录：{path}\n\n{notes}",
    "Exported {path}": "已导出 {path}", "Saved {path}": "已保存 {path}", "Export failed: {error}": "导出失败：{error}",
    "warmup": "预热中", "n/a": "不可用", "alive": "存活", "running": "运行中", "sleeping": "休眠",
    "disk-sleep": "磁盘等待", "stopped": "已停止", "tracing-stop": "跟踪停止", "zombie": "僵尸",
    "dead": "已终止", "idle": "空闲", "locked": "已锁定", "waiting": "等待中", "parked": "停驻",
    "waking": "唤醒中", "wake-kill": "唤醒终止", "suspended": "已挂起",
    "{mode} mode. Charts: {transport}. CEF, profiles and message topics are an independent optional upper service.":
        "{mode} 模式。图表：{transport}。CEF、配置隔离与消息主题属于独立的可选上层服务。",
    "terminal": "终端", "native": "原生", "hybrid": "混合", "D3D11 shared GPU": "D3D11 共享 GPU",
    "native shared CPU": "原生 CPU 共享帧", "Kitty / braille": "Kitty / 盲文点阵",
    "Could not save language preference: {error}": "无法保存语言偏好：{error}",
    "F2 search · F3 cycle sort · F4 pin/unpin · F7 pause sampling · F8 process detail · F9 中/En\n"
    "Ctrl+1..5 pages · Ctrl+E export · F6 menu/content · Tab/Shift+Tab focus\n"
    "Arrows navigate/edit · Enter inspect row or enter embedded browser · Esc leave browser/close modal\n\n"
    "Pin up to four identities in Processes, then open Compare. Each browser analysis is a separate page; "
    "they exchange only explicit telemetry and selection messages. View ranges are independent.\n\n"
    "CPU warmup is intentional. Process CPU may exceed 100%; plots clip to 100%. "
    "Filtering/sorting follows identity, not row number. Sampling never overlaps.\n\n"
    "Notes stay local and are included only in explicit exports.":
        "F2 搜索 · F3 排序 · F4 固定/取消 · F7 暂停采样 · F8 进程详情 · F9 中/En\n"
        "Ctrl+1..5 页面 · Ctrl+E 导出 · F6 菜单/内容 · Tab/Shift+Tab 焦点\n"
        "方向键导航/编辑 · Enter 查看进程或进入内嵌网页 · Esc 离开网页/关闭弹窗\n\n"
        "在进程页面最多固定四项，再进入对比。每个网页独立，仅交换明确的指标与选择消息，显示范围互不影响。\n\n"
        "CPU 首次预热是正常行为。进程 CPU 可超过 100%，曲线裁剪到 100%。"
        "筛选排序跟踪进程身份，不跟踪行号；采样任务不重叠。\n\n笔记保留在本机，仅在手动导出时写入文件。",
}


def config_path():
    if os.environ.get("COMFORTABLE_TOP_CONFIG"):
        return Path(os.environ["COMFORTABLE_TOP_CONFIG"]).expanduser()
    root = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming")) if os.name == "nt" else Path(
        os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "ComfortableTop" / "settings.json"


def system_language():
    try:
        # getlocale alone ignores LANGUAGE on some Linux distributions.
        name = next((os.environ[k] for k in ("LC_ALL", "LC_MESSAGES", "LANGUAGE", "LANG")
                     if os.environ.get(k)), None) or locale.getlocale()[0] or "en"
    except (ValueError, TypeError):
        name = "en"
    return "zh" if name.lower().startswith("zh") else "en"


def resolve_language(requested="auto"):
    if requested in ("en", "zh"):
        return requested
    if requested != "auto":
        raise ValueError("language must be auto, en or zh")
    try:
        data = json.loads(config_path().read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("language") in ("en", "zh"):
            return data["language"]
    except (OSError, ValueError):
        pass
    return system_language()


def save_language(language):
    if language not in ("en", "zh"):
        raise ValueError("language must be en or zh")
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as output:
            temporary = Path(output.name)
            json.dump({"language": language}, output)
            output.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


class LocalizedSelect(Select):
    """The app's dropdown also translates the toolkit's default popup title."""
    def activate(self):
        if not self.app:
            return super().activate()
        def chosen(index, text):
            self.set_value(index)
            self.app.close_modal()
        sources = self.localizer.bindings[self]["options"]
        options = self.localizer.make(ListView, sources, on_select=chosen)
        options.select(self.selected)
        self.app.show_modal(self.localizer.make(Panel, options, "Choose", width=48,
                                                height=min(16, len(self.options) + 2)))


class Localizer:
    def __init__(self, language="en"):
        self.language = resolve_language(language)
        self.bindings = WeakKeyDictionary()

    def text(self, message, **values):
        translated = ZH.get(message, message) if self.language == "zh" else message
        return translated.format(**values) if values else translated

    def _value(self, source):
        if callable(source):
            return source()
        if isinstance(source, (list, tuple)):
            return [self.text(v) for v in source]
        return self.text(source)

    def make(self, kind, *args, **kwargs):
        """Bind only explicitly declared application copy, never arbitrary widget content."""
        fields = {
            "Label": (0, "text"), "Paragraph": (0, "text"), "Button": (0, "label"),
            "Checkbox": (0, "label"), "Switch": (0, "label"), "Spinner": (0, "label"),
            "Panel": (1, "title"), "Collapsible": (0, "title"), "Select": (0, "options"),
            "RadioGroup": (0, "items"), "SelectionList": (0, "items"), "ListView": (0, "items"),
            "DataTable": (0, "columns"),
        }
        sources, args = {}, list(args)
        if kind.__name__ == "Tabs":
            sources["titles"] = list(args[0])
            args[0] = dict(zip(self._value(sources["titles"]), args[0].values()))
        elif kind.__name__ in fields:
            index, attr = fields[kind.__name__]
            if len(args) > index:
                sources[attr] = args[index]
                args[index] = self._value(args[index])
        if kind.__name__ == "Input" and "placeholder" in kwargs:
            sources["placeholder"] = kwargs["placeholder"]
            kwargs["placeholder"] = self._value(kwargs["placeholder"])
        if kind is Select:
            widget = LocalizedSelect(*args, **kwargs)
            widget.localizer = self
        else:
            widget = kind(*args, **kwargs)
        self.bindings[widget] = sources
        return widget

    def set_language(self, language):
        if language not in ("en", "zh"):
            raise ValueError("language must be en or zh")
        self.language = language
        for widget, fields in list(self.bindings.items()):
            for attr, source in fields.items():
                setattr(widget, attr, self._value(source))
                if attr == "titles":
                    x, widget._tab_bounds = 0, []
                    for title in widget.titles:
                        width = text_width(title) + 2
                        widget._tab_bounds.append((x, width))
                        x += width + 1
                    widget._bar_width = max(0, x - 1)
                elif attr == "options":
                    widget.label = widget.options[widget.selected] + " ▾"
            widget.invalidate()
