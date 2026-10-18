# ComfortableTop

简体中文 | [English](README.en.md)

版本 **0.1.6** 默认使用 Windows GPU WebView，支持多个 Top 实例同时运行。
需要 ComfortableTUI **0.1.5** 和本次配套的新 Windows 运行时，见[安装说明](docs/installation.md)。

一个独立的混合系统监视器：实时进程表、资源趋势、固定对比、进程树、调查笔记，
以及可选 C++ CPU/GPU 画布和独立浏览器分析页。当前仅支持 Windows；Apache-2.0。

当前版本 **0.1.6**，依赖 **ComfortableTUI 0.1.5**。升级混合模式时还需同时更新
完整的安全协议 2 浏览器运行时；发布页提供匹配平台的运行时归档，见安装文档。

本项目依赖 ComfortableTUI，但不依赖它的 examples 目录、源码位置或原来的虚拟环境。
Python 包、命令行、原生模块、网页资源、文档与测试均由本仓库独立管理。

## 安装与运行

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe tools/bootstrap.py --terminal-only
.\.venv\Scripts\comfortable-top.exe
```

ComfortableTUI 尚未假设发布到 PyPI，bootstrap 会从 GitHub 获取锁定版本，再构建并
安装普通 wheel。私有仓库需要已配置的 Git HTTPS 身份；不需要 PyPI 上传权限。
已有本地依赖源码时使用 `--tui-source C:\path\to\ComfortableTUI`，目录名称不限。

已准备好依赖 wheel 的环境也可以执行 `python -m pip install -e .`。
安装后，无论当前目录在哪里，都可运行 `comfortable-top` 或 `python -m comfortable_top`。
GitHub Release 同时提供应用 wheel、源包、通用 ComfortableTUI 依赖 wheel 与离线 HTML
文档；先安装依赖 wheel，再安装应用 wheel，即可使用基础终端模式。

Windows 完整模式：

```powershell
.\.venv\Scripts\python.exe tools/bootstrap.py --gpu --browser-runtime C:\path\to\cef-runtime
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu
```

`--browser-runtime` 指向已经构建好的完整目录，含 ctui_browser.exe、libcef.dll、
资源、locale 和许可证；工具会复制到本项目 `.runtime/<platform>/browser`。也可用 `--cef-root`
从 CEF SDK 构建。详细步骤见 [安装与构建](docs/installation.md)。

当前仅提供 **Windows x64** 安装包和原生运行时，Linux 版本已停止提供；
macOS 暂不支持。库 ComfortableTUI 的纯 TUI 平台范围与本应用分别管理。

## 主要功能

- 真实 CPU、内存、网络、磁盘与进程采样；筛选、排序、用户过滤、稳定进程身份。
- 最多四个固定进程，独立网页分析页，虚拟列表／表格内嵌画布。
- C++ 线程绘图，经共享 CPU 帧或 Windows D3D11 纹理显示；Python 不逐帧传像素。
- 调查笔记、活动日志、文件树、后台快照导出与预览。
- DPI 感知的网页视口，窄／矮面板重新布局，保留原有 TUI 焦点和菜单操作。
- 中英文实时切换，同步所有分析网页，保留当前工作状态，并保存语言偏好。

F1 帮助、F2 搜索、F3 排序、F4 固定、F7 暂停采样、F8 详情、F9 中/En、F6 菜单、
Ctrl+1…5 切页、Ctrl+E 导出、Ctrl+Q 退出。建议终端至少 120×38。

也可在“设置 → Language / 语言”切换；`--lang zh/en/auto` 指定启动语言。
默认优先使用已保存偏好，然后检测系统语言。详见[语言设置](docs/localization.md)。

## 独立文档

- [安装、依赖与原生运行时](docs/installation.md)
- [使用指南、指标与快捷键](docs/guide.md)
- [中英文切换与偏好保存](docs/localization.md)
- [弹性动效、体验与验证](docs/motion.md)
- [架构、图像传输与网页服务](docs/architecture.md)
- [开发、测试和打包](docs/development.md)
- [故障排查](docs/troubleshooting.md)
- [验证范围和记录](docs/validation.md)
- [研究依据](docs/research.md)

本地文档站点：`python -m pip install -e ".[docs]"` 后执行 `mkdocs serve`；
离线站点构建命令为 `mkdocs build --strict`。
所有手册均提供[英文版本](docs/en/index.md)，页面顶部可切换语言。

## 协议与来源

[Apache License 2.0](LICENSE)。初始监视器源自 ComfortableTUI 的示例，原作者声明与
来源保留在 [NOTICE](NOTICE)。CEF、Qt、psutil 等依赖分别遵循各自许可证；运行时
复制会保留 CEF 的许可证和资源，不将第三方组件改称 Apache 授权。
