# 安装、依赖与运行时

简体中文 | [English](en/installation.md)

## 支持范围与版本

ComfortableTop **0.1.5** 仅支持 Windows x64，需要 Python 3.10+、psutil 和
ComfortableTUI **0.1.4**。发布的完整原生运行时与 TUI 原生 wheel 针对 CPython 3.12 x64。
其他 Python ABI 需要自行构建原生部分。当前不提供 Linux 或 macOS 版本；旧 Linux
归档仅保留历史记录，不能作为当前支持或升级路径。

Windows hybrid 默认 GPU WebView，`--web-render-mode cpu` 可切回 CPU 对照。
`--canvas cpu|gpu` 独立控制趋势图。GPU 模式要求 helper 能力
`gpu_texture_transport=1`；安全协议 2 本身不能证明 GPU 可用，不满足时会明确报错。
GPU 输出仍包含 CEF 生命周期要求的 GPU 内部复制和同步。

## 从发布页安装

从 [v0.1.5 发布页](https://github.com/JDK8u341/ComfortableTop/releases/tag/v0.1.5)
下载应用 wheel、匹配的 TUI wheel；混合模式另需 Windows 运行时 zip。
基础终端模式可安装 TUI 通用 wheel，无需 Qt/CEF：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install .\comfortable_tui-0.1.4-py3-none-any.whl .\comfortable_top-0.1.5-py3-none-win_amd64.whl
.\.venv\Scripts\comfortable-top.exe --version
.\.venv\Scripts\comfortable-top.exe
```

完整 GPU 混合模式使用 **CPython 3.12 x64**：

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade .\comfortable_tui-0.1.4-cp312-cp312-win_amd64.whl .\comfortable_top-0.1.5-py3-none-win_amd64.whl
.\.venv\Scripts\python.exe -m pip install "PySide6-Essentials>=6.7,<7" "comtypes>=1.4"
```

将 `comfortable_top-runtime-windows-x64-cp312-0.1.5.zip` 解压到：
源码 editable 安装为本项目 `.runtime/windows-x64`；普通 wheel 安装为
`%LOCALAPPDATA%/ComfortableTop/runtime/windows-x64`。
解压后该目录直接包含 `browser/`、`native/`、`licenses/` 和 `runtime-manifest.json`。
升级前退出所有正在运行的 Top，避免 Windows 锁定原生模块或 CEF DLL。
保留完整的 CEF 资源、locale 和许可证，不要只替换 exe。

```powershell
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu --web-render-mode cpu
```

多个实例可重复运行相同命令。每个实例有独立临时浏览器根，不共享 Cookie、缓存或
消息；关闭 CEF 后清理目录。基础终端模式与混合模式均可中英文切换。
发布页还提供离线中英文手册、验证报告和 SHA256SUMS.txt。

## 从源码构建

bootstrap 从 GitHub 获取锁定的 TUI 发布提交，构建普通 wheel，然后安装本应用。
TUI 私有源码需要已配置的 Git HTTPS 身份；本项目不保存令牌。
已有源码可使用 `--tui-source PATH`，不会重置它，也不把源码位置作为运行时依赖。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe tools/bootstrap.py --terminal-only
```

原生构建需要 VS 2022 C++、CMake、pybind11。可以复制完整预构建 CEF 运行时：

```powershell
.\.venv\Scripts\python.exe tools/bootstrap.py --gpu --browser-runtime C:\path\to\cef-runtime
```

或者通过 `--cef-root C:\path\to\cef-sdk` 构建 CEF helper。
固定 CEF SDK 为 `152.0.14+g8a0b5b9+chromium-152.0.7977.167`，CEF 宿主使用 C++20。
`tools/build_runtime.py --tui-source PATH --cef-root PATH` 可单独更新运行时。
安装工具、CLI 和源码打包入口均拒绝 Linux；不再构建 WindowHost。

## 运行时发现与语言

显式 `COMFORTABLE_TOP_RUNTIME` 覆盖默认运行时根。
显式 `COMFORTABLE_TUI_BROWSER_EXECUTABLE` 优先于自动发现；曾设置旧路径时请先删除该变量。
原生模块依次查找 `--native-module`、`COMFORTABLE_TOP_NATIVE_DIR`、运行时 native 目录和
本项目构建目录。正常启动不需要 `--browser`，也不依赖 TUI 的构建目录。
使用 `--lang zh/en/auto` 或 F9 切换语言，偏好路径见[语言设置](localization.md)。
