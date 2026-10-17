# 验证范围

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
