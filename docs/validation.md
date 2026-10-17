# 验证范围

简体中文 | [English](en/validation.md)

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

上述性能采样使用基础动效提交 2b4ea47；当前依赖 40a4b45 进一步在退场首次归零时
释放不可见快照和原生画布遮挡。[Windows GPU](validation/standalone/motion-retirement-windows-gpu.json)、
[X11](validation/standalone/motion-retirement-linux-x11.json)、
[Wayland](validation/standalone/motion-retirement-linux-wayland.json) 各十项最终复查通过，
库测试仍为 Windows 220、WSL2 204 项通过（5 项跳过）。
