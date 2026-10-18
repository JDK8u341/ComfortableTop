# 故障排查

> 当前范围：Linux 图形模式已暂停，仅保留终端模式。旧 X11/Wayland 结果对应已撤下的自有窗口，见[安装说明](installation.md)。

## 升级后浏览器提示 security protocol

Top 0.1.3 使用 TUI 0.1.2，要求协议 2 helper。更新 Python wheel 后，旧的
`.runtime/<platform>/browser` 也必须替换为完整的新运行时；不能只复制 exe。
若曾设置 COMFORTABLE_TUI_BROWSER_EXECUTABLE，清除旧覆盖或改为新路径。
此次发布不需要借用 `tui/.venv`；使用 Top 自己的 `.venv` 即可。

简体中文 | [English](en/troubleshooting.md)

## 进程详情图表不随面板缩放

v0.1.2 修复了“选中进程 CPU”图表的固定 24×5 字符内嵌尺寸。现在画布直接填充
面板内部，最大化、Alt+Enter 全屏、恢复、连续缩放时同步调整。窗口过窄时侧栏
按原规则隐藏，放宽后重新填充。此修正只需更新 Top 并重启；TUI 0.1.1 和已有
GPU／CEF 运行时不需要重建。列表和表格中有意固定尺寸的内嵌画布不受影响。

## pip 找不到 comfortable-tui

该依赖未假设存在 PyPI 发行版。使用 `tools/bootstrap.py`、requirements-tui.txt，
或先安装兼容的本地 wheel。私有 GitHub 仓库需配置本机 Git 身份。
不要把访问令牌写进命令行 URL、配置文件或提交到仓库。

## 找不到 _ctui_top_native

先运行 `tools/build_runtime.py`，并确认编译用 Python 与启动应用的 Python 相同。
默认模块位于 `.runtime/<platform>/native`；普通 wheel 安装可通过 COMFORTABLE_TOP_RUNTIME
设置完整运行时根，或通过 `--native-module DIR` 指定扩展目录。
Py3.12 的 .pyd 不能给 Py3.10 使用，Windows .pyd 不能用于 Linux。

## GPU 不可用

仅 Windows 支持当前 D3D11 路径。ComfortableTUI 本身也需要 GPU 扩展，运行
`tools/bootstrap.py --gpu`。GPU 参数是画布传输选项，不是 GPU 硬件占用率监控。
仅需查看系统数据时可运行终端模式，或使用 CPU 原生图表。

## CEF / WindowHost 不存在

确认 runtime/browser 中存在完整运行时，Linux 还需 runtime/host/ctui_linux_canvas。
用 build_runtime 的 --browser-runtime／--host-binary 复制，或 --cef-root 构建。
只复制 exe/libcef.dll 不够。设置 COMFORTABLE_TOP_RUNTIME 时应指向根目录，
不是 browser 或 native 子目录。显式 COMFORTABLE_TUI_* 环境变量会覆盖自动发现。

## 浏览器很小或模糊

0.1.0 已按面板逻辑尺寸调整网页视口；重启应用加载最新网页资源。拖动结束后约
120ms 执行重新布局。画布裁剪不会改变完整网页尺寸；小窗口请放大至建议范围。
需要报告问题时提供 DPI、终端尺寸、模式和运行时版本，不必提供 Cookie 或完整命令行。

## 退出后输入框出现 `[<35;87;1M`

这是终端 SGR 鼠标报告的可见部分：`35` 表示无按键的移动，`87;1` 为终端列、行。
旧依赖在关闭叠加层之后才关闭鼠标上报，且没有读取退出时已排队的输入，
因此 PowerShell 有时会读到残留报告。当前锁定的依赖已提前停止报告，并在恢复
宿主输入模式前等待 50ms 无输入、最多 100ms 来读取残留事件，不触发控件回调。

已有环境需重新安装更新后的 ComfortableTUI wheel，再重新启动应用；只更新网页资源
无效。使用源码安装时，按安装文档重新运行 bootstrap；旧的 `.deps/comfortable-tui-src`
如与新锁定提交不同，使用 `git -C .deps/comfortable-tui-src fetch origin` 和
`git -C .deps/comfortable-tui-src checkout --detach e25f1f62c26ec99684f5b6e0ba1cf472930665f2`
显式更新缓存后再运行 bootstrap。应用已经退出时，可用 Ctrl+C 清空当前提示符输入。
强制终止进程和高延迟远程连接仍可能无法完成退出清理。

## 列表数少于系统进程总数

Windows 无法读取创建时间的受保护进程计入 unavailable，避免错误地用 PID 关联
另一个进程。无需为查看现有数据而提升权限。首次 CPU/I/O、重置和不可用字段显示
warmup/n/a。状态 alive 只表示在快照中存在；RSS 并非独占内存。

## WSL / Wayland 连接失败

分别指定 x11 或 wayland，并确认 DISPLAY／WAYLAND_DISPLAY 与桌面会话匹配。
依赖库针对 WSLg 丢失运行目录链接的情形有子进程级 socket 探测，但没有可用 socket
仍会报错，不修改系统 XDG_RUNTIME_DIR、不静默改用 X11。
WSL 中读取的是 Linux 子系统的进程和资源。

## 浏览器条款或 CSP 错误

### 多实例提示 browser data is already in use

旧版 Top 为所有进程使用同一个固定浏览器根，即使分析 profile 不持久化也会争用
CEF 数据目录锁。当前实现改为每个进程独立临时根，可直接重复运行同一条命令。
不应删除锁或强制共享写入目录；升级 Top 后重启需要修复的旧实例即可。

服务保留 no-first-run 策略与应用私有 profile。不要自动接受外部网站协议。
本项目页面保留严格 CSP；自测通过 probe/proof 主题确认布局和消息，不调用动态 eval。
若手动在 page.evaluate() 中求值，CEF 服务的执行方式仍受页面 CSP 约束。

## 语言偏好无法保存

配置目录不可写时，F9 仍会切换当前语言，并显示保存失败提示。检查[配置路径](localization.md)，
或用 COMFORTABLE_TOP_CONFIG 指向可写文件。`--lang zh/en` 会覆盖本次启动语言，
不改写偏好。笔记、进程名、原始详情和历史日志属于数据，保持原样。中文缺字时
请安装支持 CJK 的终端字体。
