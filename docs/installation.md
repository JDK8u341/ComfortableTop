# 安装、依赖与运行时

## 基础要求

Python 3.10+，Windows 或 Linux。终端模式需要 psutil 与 ComfortableTUI。
测试基线为 ComfortableTUI 提交 `84f37b15645b78e1a07b4dd769fee4941a5d568a`，
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
原构建目录。浏览器使用 CEF CPU 共享帧，GPU 参数只改变趋势图的传输与呈现。

从源码构建浏览器时，CEF 基线为
`152.0.14+g8a0b5b9+chromium-152.0.7977.167`。依赖源码附带安全下载器：

```powershell
.\.venv\Scripts\python.exe .deps/comfortable-tui-src/tools/fetch_cef.py --platform windows64
# 将上一步输出的 SDK 绝对路径作为 --cef-root：
.\.venv\Scripts\python.exe tools/build_runtime.py --tui-source .deps/comfortable-tui-src --cef-root C:\path\to\cef-sdk
```

CEF 构建需要 C++20，通用帧 SDK 和本项目图表模块用 C++17。浏览器保留沙箱和
no-first-run 策略，不通过自动点击、放开 eval 或关闭沙箱来跳过初始化。

## Linux / WSL2

需要 GCC 11+、CMake、Qt 6 开发包与真实 X11／Wayland 会话；CEF 还需系统图形库。
Ubuntu 22.04 示例：

```bash
sudo apt-get update
sudo apt-get install -y build-essential cmake ninja-build python3-venv python3-dev \
  qt6-base-dev qt6-wayland libgtk-3-dev libnss3 libgbm1 libasound2 \
  libatk-bridge2.0-0 libxkbcommon-x11-0
python3 -m venv .venv
.venv/bin/python tools/bootstrap.py --tui-source /path/to/ComfortableTUI
# 构建 CEF 和 WindowHost：
.venv/bin/python tools/build_runtime.py --tui-source /path/to/ComfortableTUI --cef-root /path/to/cef-sdk
.venv/bin/comfortable-top --mode hybrid --platform x11
.venv/bin/comfortable-top --mode hybrid --platform wayland
```

Linux CEF SDK 下载器参数为 `--platform linux64`。已有产物可用
`--browser-runtime DIR --host-binary /path/to/ctui_linux_canvas` 复制，避免重复构建。
Qt 等系统动态库仍需安装；不宣称产物可跨任意 Linux 发行版直接运行。
WSL 显示 Linux 子系统的进程，非 Windows 宿主进程；构建输出和 venv 建议放在 Linux
文件系统。X11 与 Wayland 分别测试。WindowHost 为自有窗口，不是外部终端附加层。

## 安装 wheel 后的运行时位置

源码 editable 安装默认使用本项目 `.runtime/<platform>`。普通 wheel 安装在 Windows 默认查找
`%LOCALAPPDATA%/ComfortableTop/runtime/windows-x64`，Linux 查找
`$XDG_DATA_HOME/ComfortableTop/runtime/linux-x64` 或 `~/.local/share/ComfortableTop/runtime/linux-x64`。
可以用 `COMFORTABLE_TOP_RUNTIME` 指定完整运行时根，并将 `tools/build_runtime.py`
的 `--runtime PATH` 设置到同一目录。

优先级：显式 `--native-module`、`COMFORTABLE_TOP_NATIVE_DIR`、运行时 native 目录、
本项目 `.build/<platform>/native/Release` 或 `.build/<platform>/native`。显式设置的
`COMFORTABLE_TUI_BROWSER_EXECUTABLE`／`COMFORTABLE_TUI_LINUX_HOST_EXECUTABLE` 保持优先。
`<platform>` 在已验证环境中为 windows-x64 或 linux-x64；SDK 和构建缓存也按平台
分目录，Windows 与 WSL 可共享同一源码目录。运行时不按兄弟目录名查找原 TUI 项目。
