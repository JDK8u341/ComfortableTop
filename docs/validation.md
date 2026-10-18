# 验证范围

> 0.1.6 当前发布只支持 Windows。以下旧 Linux 与旧版本性能记录保留原始版本号；本次发布的验证结果随 release-validation.json 提供。

> 当前范围：Top 仅支持 Windows，Linux 版本已停止提供。旧 X11/Wayland 结果对应已撤下的自有窗口，见[安装说明](installation.md)。

简体中文 | [English](en/validation.md)

## Windows GPU WebView 测试分支

当前分支锁定 TUI `e25f1f62c26ec99684f5b6e0ba1cf472930665f2`，Windows 普通 `.venv`
安装对应的非 editable GPU wheel；CEF 完整运行时复制进本项目自己的 `.runtime/windows-x64`。
WSL 普通环境也升级了匹配的 CPU wheel/helper。测试清除开发环境覆盖，通过本项目运行时自动发现。

- [Windows 默认 GPU 网页](validation/standalone/webview-gpu.json)：十项混合检查通过；
  两个独立页面均为 native_gpu_d3d11、cpu_paints=0，并实际收到加速帧。
- [Windows 显式 CPU 对照](validation/standalone/webview-cpu.json)：十项通过，两页均为 native_cpu。
- [X11](validation/standalone/webview-x11-cpu.json)、[Wayland](validation/standalone/webview-wayland-cpu.json)：
  各十项通过，网页默认 CPU。没有新增 Linux GPU 支持。
- Windows 30 项单元测试通过；WSL 29 项通过、1 项平台跳过。Ruff、MkDocs strict、pip check 通过。

这是本项目 CLI 的真实模式选择，没有 monkeypatch BrowserService.open，也不使用 TUI 源码的
editable 导入或其构建目录作为启动依赖。测试入口仅清除开发覆盖，使用本项目 `.venv` 的
标准 main 和自测参数。新增 browser_frames 报告会核对 GPU 后端、CPU 绘制为零和有效加速回调，
不会仅凭相同返回值判定通过。正式发布的 v0.1.3 归档尚未包含此测试分支功能。

## v0.1.3 / ComfortableTUI v0.1.2 发布复测

2026-10-18：Windows 普通 `.venv` 和 WSL2 普通开发环境均安装 TUI 0.1.2 非 editable
wheel，并重建本应用的生产者、替换协议 2 CEF 运行时。清除开发路径覆盖后，依靠本项目
`.runtime/<platform>` 自动发现运行时。

- [Windows GPU](validation/standalone/release-0.1.3-windows-gpu.json)、
  [X11](validation/standalone/release-0.1.3-linux-x11.json)、
  [Wayland](validation/standalone/release-0.1.3-linux-wayland.json) 各十项混合模式检查通过。
- 新建 venv、仓库外启动的 [Windows](validation/standalone/release-0.1.3-installed-windows.json)
  和 [Linux](validation/standalone/release-0.1.3-installed-linux.json) 各五项 wheel 检查通过，
  覆盖实际采样、中英文、资源和许可证。
- Windows 29 项单元测试通过，Linux 28 项通过、1 项平台跳过；Ruff 与双语手册严格构建通过。
- 首次 X11 冷启动在固定四秒预热检查时尚未完成采样，原测试未改动，重试通过；
  此自测的固定时间点仍可能受机器负载影响。上述检查不构成帧率或任意 Linux compositor 兼容保证。

发布包提供独立双语手册、匹配的 Windows CPython 3.12 / Linux CPython 3.10 运行时和
SHA256 校验。浏览器权限由原生边界执行；宿主 Python 和原生生产者仍是受信任代码，
不宣称将任意第三方原生插件安全隔离。详情见[安装](installation.md)和库的安全文档。

独立项目的检查包括模型／采集、网页自适应、命令行、包资源和运行时发现。
构建并在独立 venv 安装应用 wheel，从仓库之外启动；确认依赖来自普通 ComfortableTUI
wheel，而非原项目的 editable 路径。原生模块通过安装后的 SDK 构建，不引用原 examples。

Windows 使用真实 Terminal，Linux 分别使用 WSL2 X11 与 native Wayland WindowHost。
集成自测确认有效采样、筛选固定、暂停、独立页面及 Enter/Esc、业务消息往返、网页
视口匹配面板及图表有效填充。生产者另验证 GIL 独立发布、静止不重发与拒绝非法样本。

`docs/validation/origin-example/` 保留拆分前基线记录，仅代表原示例；不把它冒充
独立仓库验证。独立运行的新报告保存在 `docs/validation/standalone/`。
报告不保存用户名、进程名称、Cookie 或调查笔记，计数不等同屏幕 FPS。

详细复现命令见 [开发文档](development.md)。Linux 结论针对已测试的 WSLg，会话和
系统图形依赖仍然重要，不能外推至所有 compositor 或任意外部终端。

## 2026-10-17 独立仓库实测

| 检查 | 结果 |
| --- | --- |
| Windows Python 3.12.14 | 17 项单元／安装入口测试通过 |
| WSL2 Ubuntu 22.04 Python 3.10.12 | 16 项通过，1 项 Windows 原生读取测试跳过 |
| Ruff / MkDocs strict | 通过；独立文档站点可离线构建 |
| [Windows 完整混合模式](validation/standalone/windows-gpu.json) | 新 venv、安装版 TUI wheel、自有运行时，八项集成检查通过 |
| [X11](validation/standalone/linux-x11.json) | 从 /tmp 启动新环境，实际 Qt platform=xcb，八项通过 |
| [Wayland](validation/standalone/linux-wayland.json) | 从 /tmp 启动，实际 Qt platform=wayland，八项独立通过 |
| [独立 wheel 安装](validation/standalone/installed-wheel.json) | 应用和库均从独立 venv 的 site-packages 导入，空工作目录启动，资源／许可证／真实采样通过 |
| [Windows CPU](validation/standalone/producer-windows-cpu.json)、[GPU](validation/standalone/producer-windows-gpu.json)、[Linux CPU](validation/standalone/producer-linux-cpu.json) | 本项目独立 C++ 模块的生产、GIL、静止发布与非法样本检查通过 |

CEF 152.0.14、psutil 7.2.2、pybind11 3.1.0；Windows MSVC 19.44，Linux GCC 11.4。
应用构建／安装与运行时位于 ComfortableTop 目录，原 TUI 仓库仅在准备依赖时读取，
原项目工作区没有改动。历史来源报告与独立验证报告分目录保存。


## 2026-10-17 中英文更新验证

- Windows：27 项单元测试通过；WSL2：26 项通过、1 项 Win32 测试跳过。
- [Windows GPU](validation/standalone/i18n-windows-gpu.json)、[WSL2 X11](validation/standalone/i18n-linux-x11.json)、[WSL2 Wayland](validation/standalone/i18n-linux-wayland.json)：各十项混合模式检查通过，包含暂停时中文同步、英文切回、所有浏览器页身份保留，以及实际网页标题确认。
- [独立 wheel](validation/standalone/i18n-installed-wheel.json)：仓库外的安装包中，中英文分别真实采样两次、输出对应语言终端帧。
- 单元测试覆盖三种窗口尺寸、两个初始语言、下拉菜单和已打开弹窗、Unicode 菜单宽度、状态保留、配置优先级／无效配置／保存失败、弱引用回收与加载较慢的网页同步。
- 双语手册均通过 MkDocs strict，Ruff 通过。库中已删除的示例相关测试已由独立项目负责；库剩余 203 项测试通过。

旧验证工具在 Windows 默认 GBK 下读取含中文网页曾报解码错误，现已显式使用 UTF-8。
一次 Wayland 复查在启动四秒时尚未完成两次采样，触发自测预热断言；独立复查已通过。
该自测使用固定时间点，机器繁忙或冷启动时仍需留意启动时序；这些检查不代表帧率保证。

## 2026-10-17 弹性动效依赖更新

Windows 应用 27 项测试、WSL2 26 项测试（1 项跳过）通过。安装锁定库的普通 wheel，
未改为引用库源码。实际组合：[Windows GPU](validation/standalone/motion-windows-gpu.json)、
[X11](validation/standalone/motion-linux-x11.json)、[Wayland](validation/standalone/motion-linux-wayland.json)
各十项检查通过，继续验证内嵌网页焦点、业务消息、语言和画布尺寸。

[Expressive](validation/standalone/motion-expressive.json)、[Subtle](validation/standalone/motion-subtle.json)、
[减少动效](validation/standalone/motion-reduced.json)使用真实进程快照，覆盖快速切页和
换焦点、开关、滑块、弹窗、通知及 PageStack；最后 90 帧差分为空。
[旧依赖基线](validation/standalone/motion-baseline.json)与新版均为 140×42 的 CPU 渲染/
编码采样：资源页 P95 33.857→11.611ms，弹窗退场 27.904→13.900ms。机器负载和
进程数会变化；这是单机采样，不能称为终端呈现 FPS 或保证所有帧低于 16.7ms。
复现步骤见[动效文档](motion.md)。

上述性能采样使用基础动效提交 2b4ea47；当时依赖 40a4b45 进一步在退场首次归零时
释放不可见快照和原生画布遮挡。[Windows GPU](validation/standalone/motion-retirement-windows-gpu.json)、
[X11](validation/standalone/motion-retirement-linux-x11.json)、
[Wayland](validation/standalone/motion-retirement-linux-wayland.json) 各十项最终复查通过，
库测试仍为 Windows 220、WSL2 204 项通过（5 项跳过）。

## 2026-10-18 帧调度修正

Windows Python 3.12 的粗 monotonic 时钟导致截止时间量化；依赖改用高精度
perf_counter、保持连续截止时间，并缓存短文本绘制。对照已启用相同文本缓存，
仅保留旧时钟，从而隔离调度因素。真实 Terminal、已安装普通 wheel、GPU 图表、
CEF 与持续采样，每轮换焦点／切页／开关弹窗，剔除前 3 秒：

| 目标 | 对照循环 FPS | 修正后循环 FPS | 间隔 P95 前／后 |
| --- | --- | --- | --- |
| 60 | [32.00](validation/standalone/pacing-coarse-60.json) | [59.67](validation/standalone/pacing-after-60.json) | 32.744／17.259ms |
| 120 | [64.01](validation/standalone/pacing-coarse-120.json) | [117.77](validation/standalone/pacing-after-120.json) | 17.492／8.984ms |

60 FPS 修正后 538 个采样仅 1 个超过 1.5 倍帧预算；120 FPS 的 1060 个采样中
有 13 个超过。两轮都没有超过 50ms 的间隔。这是实际循环节奏，不能称为显示器
呈现 FPS 或端到端输入延迟。复现工具与限制见[动效文档](motion.md)。

[Windows GPU](validation/standalone/pacing-windows-gpu.json)、
[WSL2 X11](validation/standalone/pacing-linux-x11.json)、
[WSL2 Wayland](validation/standalone/pacing-linux-wayland.json)各十项混合模式复查通过。
应用测试 Windows 27 项通过；WSL2 26 项通过、1 项跳过。库分别 225 项通过、
208 项通过及 6 项平台跳过。Ruff 与两份手册的 MkDocs strict 通过。

## v0.1.1 发布包验证

应用与依赖版本均为 0.1.1，应用声明至少需要 ComfortableTUI 0.1.1，避免保留旧库而
遗漏帧调度修正。通用 wheel 从 Git 提交的干净源码构建；另提供 Windows x64
CPython 3.12 的可选 GPU/C++ wheel，不包含 CEF 或应用原生运行时。

[Windows](validation/standalone/release-0.1.1-installed-windows.json) 和
[WSL2 Linux](validation/standalone/release-0.1.1-installed-linux.json) 的独立 venv
均通过五项发布包检查，包括普通 wheel 导入、Apache 许可证、CLI 版本和中英文
真实采样。新依赖还通过 [Windows GPU](validation/standalone/release-0.1.1-windows-gpu.json)
混合模式十项检查；安装发布 wheel 后的
[X11](validation/standalone/release-0.1.1-linux-x11.json) 和
[Wayland](validation/standalone/release-0.1.1-linux-wayland.json)分别十项通过。
应用 27 项单元测试、Ruff 和严格文档构建通过；库发布提交 CI 全绿。

## v0.1.2 选中进程图表缩放修正

删除所选 CPU 图表固定 24×5 字符的 Text 内嵌布局，直接填充面板内部。
新增回归覆盖终端画布与原生画布在五次尺寸切换中的填充、窄屏隐藏和恢复。
Windows 29 项单元测试通过；WSL2 28 项通过、1 项平台跳过。

真实 Windows Terminal 的 [GPU](validation/standalone/resize-windows-gpu.json) 和
[CPU](validation/standalone/resize-windows-cpu.json) 均通过初始、最大化、Alt+Enter
全屏、退出全屏、缩小、放大、恢复七阶段检查，逐次核对面板内部尺寸、附加层
物理像素与 stretch 变换。图表高度依次为 184、368、483、368、46、230、184px。
[完整 GPU/CEF 混合模式](validation/standalone/resize-hybrid.json)十项复查通过。
可用 tools/verify_chart_resize.py 复现，详见[开发文档](development.md)。
