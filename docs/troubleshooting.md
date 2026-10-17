# 故障排查

## pip 找不到 comfortable-tui

该依赖未假设存在 PyPI 发行版。使用 `tools/bootstrap.py`、requirements-tui.txt，
或先安装兼容的本地 wheel。私有 GitHub 仓库需配置本机 Git 身份。
不要把访问令牌写进命令行 URL、配置文件或提交到仓库。

## 找不到 _ctui_top_native

先运行 `tools/build_runtime.py`，并确认编译用 Python 与启动应用的 Python 相同。
默认模块位于 `.runtime/native`；普通 wheel 安装可通过 COMFORTABLE_TOP_RUNTIME
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

服务保留 no-first-run 策略与应用私有 profile。不要自动接受外部网站协议。
本项目页面保留严格 CSP；自测通过 probe/proof 主题确认布局和消息，不调用动态 eval。
若手动在 page.evaluate() 中求值，CEF 服务的执行方式仍受页面 CSP 约束。
