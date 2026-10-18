# 安装、依赖与运行时

简体中文 | [English](en/installation.md)

## 当前分支：GPU WebView 测试

当前源码在 Windows `--mode hybrid` 下默认使用 GPU 网页纹理；Linux 图像混合模式已暂停。
`--canvas gpu` 单独控制原生图表，网页通过 `--web-render-mode cpu|gpu` 选择。
发布页的 v0.1.3 / TUI 0.1.2 稳定包没有这个新增接口；测试应使用当前分支锁定的
TUI 提交 `6069afed2934af9137fe7fe3fa12fc8b04e3acb8` 并重新构建/复制完整 CEF helper。
安全协议 2 本身不足以证明支持 GPU，helper 还需提供 `gpu_texture_transport=1`。

本机已更新项目自己的 `.venv` 和 `.runtime/windows-x64/browser`，可直接运行：

```powershell
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu
# 同一套新版运行时，网页切回 CPU 对照：
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu --web-render-mode cpu
```

不需要传 `--browser` 或访问 TUI 构建目录。旧的 `COMFORTABLE_TUI_BROWSER_EXECUTABLE`
环境变量会优先于自动发现；如果自己曾设置旧路径，请在当前终端删除该变量再启动。
GPU 模式不能满足时会报错，不会静默回退。测试报告会记录每页的实际 frame_backend、
加速回调和 CPU 绘制次数。GPU 模式仍包含 CEF 生命周期要求的 GPU 内部复制和同步。

## 基础要求

v0.1.3 的基础终端模式可直接从[发布页](https://github.com/JDK8u341/ComfortableTop/releases/tag/v0.1.3)
下载两个通用 wheel，在下载目录中安装：

```powershell
python -m pip install --upgrade ./comfortable_tui-0.1.2-py3-none-any.whl ./comfortable_top-0.1.3-py3-none-any.whl
comfortable-top --version
comfortable-top
```

版本应显示 `ComfortableTop 0.1.3`。库至少需要 0.1.2；旧库和旧浏览器运行时需要一起更新。
浏览器 helper 必须使用安全协议 2，不能仅更新 Python wheel 而保留旧 CEF helper。GPU／浏览器模式仍需
下面的原生运行时，通用 wheel 不包含 GPU 扩展或 CEF。离线手册 zip 同步提供中英文。

Python 3.10+，Windows 或 Linux。终端模式需要 psutil 与 ComfortableTUI。
当前源码测试基线为 ComfortableTUI 提交 `6069afed2934af9137fe7fe3fa12fc8b04e3acb8`，
bootstrap 和 requirements-tui.txt 均锁定此版本；不会假设 PyPI 上已存在该依赖。
GitHub 私有依赖需有访问权限，Git 凭证由本机 Git／gh 管理，项目不保存令牌。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe tools/bootstrap.py --terminal-only
.\.venv\Scripts\comfortable-top.exe
```

Linux 将 `.venv\Scripts\python.exe` 换为 `.venv/bin/python`。
bootstrap 会在 `.deps/comfortable-tui-src` 获取依赖源码并安装非 editable wheel，
随后以 editable 方式安装本应用。本地已有源码可传 `--tui-source PATH`；该路径
仅在安装／构建时读取，不被重置或修改源码，运行时不依赖它。

手动安装可先 `python -m pip install -r requirements-tui.txt`，再执行
`python -m pip install -e .`。如果使用发布页附带的匹配平台 ComfortableTUI wheel，
先安装该 wheel，再安装 ComfortableTop wheel；不要同时依赖未发布的 PyPI 包名。

## Windows 原生与混合模式

发布页提供 `comfortable_top-runtime-windows-x64-cp312-0.1.3.zip`，内含完整协议 2 CEF
运行时、图表模块和许可证。先安装同页的 CPython 3.12 Windows x64 TUI 原生 wheel
与 Top wheel，将 zip 解压到仓库的 `.runtime/windows-x64`（应直接出现 browser/native
子目录），即可使用本节最后的启动命令。其他 Python 版本请从源码构建匹配模块。
普通 wheel 安装者应解压到下文的默认运行时目录，或设置 COMFORTABLE_TOP_RUNTIME。

```powershell
python -m pip install --upgrade "./comfortable_tui-0.1.2-cp312-cp312-win_amd64.whl[overlay]" ./comfortable_top-0.1.3-py3-none-any.whl
```

需要 x64 Python、VS 2022 C++ 工具链、CMake；GPU 需要可用 D3D11.1。

```powershell
.\.venv\Scripts\python.exe tools/bootstrap.py --tui-source C:\path\to\ComfortableTUI --gpu
.\.venv\Scripts\comfortable-top.exe --mode native --canvas gpu
```

不加 `--gpu` 时使用 CPU 帧。bootstrap 构建依赖 wheel 和已安装的 ComfortableFrames
CMake SDK，本项目只用 find_package 链接 SDK，不向原仓库 add_subdirectory。
本项目原生模块安装在 `.runtime/<platform>/native`。

已有完整 CEF 运行时可以直接复制：

```powershell
.\.venv\Scripts\python.exe tools/build_runtime.py --tui-source C:\path\to\ComfortableTUI --browser-runtime C:\path\to\browser\Release
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu
```

目录必须包含 ctui_browser.exe、ctui_browser.dll、libcef.dll、pak、locale、快照及
CEF 许可证。工具复制整个目录到 `.runtime/<platform>/browser`，不只复制 exe；启动不再访问
原构建目录。当前分支的 Windows 网页默认使用 GPU；`--web-render-mode cpu` 使用 CPU
共享帧；Linux 图形路径已暂停。`--canvas` 只控制趋势图。

从源码构建浏览器时，CEF 基线为
`152.0.14+g8a0b5b9+chromium-152.0.7977.167`。依赖源码附带安全下载器：

```powershell
.\.venv\Scripts\python.exe .deps/comfortable-tui-src/tools/fetch_cef.py --platform windows64
# 将上一步输出的 SDK 绝对路径作为 --cef-root：
.\.venv\Scripts\python.exe tools/build_runtime.py --tui-source .deps/comfortable-tui-src --cef-root C:\path\to\cef-sdk
```

CEF 构建需要 C++20，通用帧 SDK 和本项目图表模块用 C++17。浏览器保留沙箱和
no-first-run 策略，不通过自动点击、放开 eval 或关闭沙箱来跳过初始化。

## Linux / WSL2：仅终端模式

当前撤下 Linux native/hybrid 及 WindowHost；它没有嵌入现有终端。
旧 v0.1.3 Linux 图形运行时归档属于历史交付，不代表当前支持，也不再推荐安装。

```bash
python3 -m venv .venv
.venv/bin/python tools/bootstrap.py --terminal-only
.venv/bin/comfortable-top --mode terminal
```

不需要 Qt、CEF 或桌面会话。WSL 采集 Linux 子系统进程，不采集 Windows 宿主进程。
CLI 在启动任何图形资源前拒绝 Linux native/hybrid；构建工具不再构建 Linux 图形运行时。
研究依据与恢复标准见 [ComfortableTUI 决策报告](https://github.com/JDK8u341/ComfortableTUI/blob/codex/webview-gpu-textures/docs/linux-support-decision.md)。

## 安装 wheel 后的运行时位置

Windows editable 安装读取本项目 `.runtime/windows-x64`；普通 wheel 默认读取
`%LOCALAPPDATA%/ComfortableTop/runtime/windows-x64`。`COMFORTABLE_TOP_RUNTIME`
可指定其他目录，构建时向 `tools/build_runtime.py --runtime` 传入相同路径。
原生模块依次查找 `--native-module`、`COMFORTABLE_TOP_NATIVE_DIR`、运行时 native
目录和本项目构建目录。显式 `COMFORTABLE_TUI_BROWSER_EXECUTABLE` 优先于自动发现。
Linux 终端模式不自动激活旧图形运行时；设置旧 host 环境变量也不能恢复已撤下的路径。

## 界面语言

`comfortable-top --lang zh` 启动中文，`--lang en` 启动英文；默认 `auto` 读取已保存偏好，
否则检测系统语言。F9 或设置页可实时切换并保存。[配置与数据边界](localization.md)。
