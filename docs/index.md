# ComfortableTop 文档

简体中文 | [English](en/index.md)

ComfortableTop 是独立 Python 应用，使用 ComfortableTUI 控件和通用图像 SDK。
本手册对应 0.1.4，依赖 ComfortableTUI 0.1.3 和协议 2 浏览器 helper。
当前只支持 Windows x64，不再提供 Linux 版本；macOS 暂不支持。

从 [安装与构建](installation.md) 开始；日常操作见 [使用指南](guide.md)。
无需原生编译的终端模式即可读取真实指标；native 模式添加 C++ 图表，hybrid 模式
添加本机网页分析和显式消息联动。源码包包含完整网页资源，安装后支持从任意目录启动。

独立入口为 `comfortable-top` 和 `python -m comfortable_top`。
独立协议文件为仓库根目录 LICENSE 与 NOTICE；此站点可用 MkDocs 离线构建。

按 **F9** 或在“设置 → Language / 语言”实时切换中英文；启动参数 `--lang zh/en/auto`。
详见[语言设置](localization.md)，本手册各页均提供英文对应版本。
