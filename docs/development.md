# 开发、测试和发布

简体中文 | [English](en/development.md)

## 独立源码布局

| 路径 | 内容 |
| --- | --- |
| src/comfortable_top | 应用包、入口、采集、模型、界面与本地化 |
| src/comfortable_top/web | 随 wheel 打包的 HTML/CSS/JS |
| native | 本应用图表 C++ 生产者，通过 find_package 链接外部 SDK |
| tools | 依赖 bootstrap、原生构建／运行时复制 |
| tests | 模型、采集、界面、网页尺寸、路径与安装入口测试 |
| docs | 独立 MkDocs 文档和验证记录 |

本项目不包含原来的 examples 命名空间，也不通过 sys.path 指向原 TUI 源码。
应用内部的相对导入属于正常 Python 包导入。可从任何目录运行安装好的命令。

## 测试和文档

先按安装文档准备依赖，然后：

```powershell
python -m pip install -e ".[dev,docs]"
python -m pytest -q
python -m ruff check .
python -m mkdocs build --strict
comfortable-top --snapshot --interval .25 --lang en
comfortable-top --snapshot --interval .25 --lang zh
python -m comfortable_top.verify_native --canvas cpu
python -m comfortable_top.verify_native --canvas gpu
python -m comfortable_top.verify_motion --report .build/motion-check.json
```

Windows 集成测试创建自己的 Terminal，14 秒内结束，仅操作本应用控件和消息桥：

```powershell
python -m comfortable_top.verify_windows --mode hybrid --canvas gpu --report .build/verify-windows.json
python -m comfortable_top.verify_pacing --fps 60 --report .build/pacing-check-60.json
python -m comfortable_top.verify_pacing --fps 120 --report .build/pacing-check-120.json
python tools/verify_chart_resize.py --canvas gpu --report .build/resize-check.json
```

报告须为新路径。verify_chart_resize 会打开自己的 Windows Terminal，最大化、
通过 Alt+Enter 进入／退出全屏、改变尺寸再恢复，核对图表填充与物理像素变换。
需有足够宽的桌面显示侧栏及已构建的原生运行时，也支持 `--canvas cpu`。
verify_pacing 默认用 12 秒测试实际 App.run 调度，剔除前 3 秒，
与离屏 verify_motion 的 CPU 耗时互补；生产循环频率仍不等于屏幕呈现 FPS。
该工具要求 Windows Terminal，默认混合模式包含 GPU 和浏览器运行时。
当前仅在 Windows 上构建和运行；历史 Linux 验证不再是操作指引。

真实显示验证不以 offscreen/minimal 结果代替。生产者 GIL 检查不是屏幕 FPS。
动效工具使用真实 Monitor 与已安装的库，支持 `--motion subtle` 和 `--reduced-motion`；
暂停采样后验证快速重定向、弹窗、通知和空闲差分，CPU 耗时不代表显示帧率。
操作说明见[动效与验证](motion.md)。
也应测试 wheel 在独立 venv、仓库之外的工作目录中启动，确认资源与导入独立。

```powershell
python tools/verify_distribution.py --wheel dist/comfortable_top-0.1.4-py3-none-win_amd64.whl --tui-wheel PATH/comfortable_tui-WHEEL.whl --report .build/wheel-check.json
```

这个检查会创建独立测试 venv，在空工作目录中验证包／网页／许可证和命令行，并真实
采样两次。当前发行和校验只针对 Windows x64；应用 wheel 不在 Linux 安装或运行。

## 构建发行包

```powershell
python -m build --no-isolation
```

`dist/` 包含纯 Python 应用 wheel 和源归档。wheel 包含网页资源、LICENSE、NOTICE；
源包额外含原生源码、构建工具、文档和测试。原生二进制和 CEF 不塞入纯 Python wheel。
需要 GPU 的 ComfortableTUI 平台 wheel 由 bootstrap 构建，Python ABI／平台必须匹配。

发布到 GitHub 的应用包并不等于发布到 PyPI。依赖访问方式、native／CEF 构建及运行时
位置必须随版本说明保留。发布页提供匹配的完整 Windows 运行时；也可从 SDK 构建，始终保留第三方许可证。

Git 标签与版本号应一致，先通过测试和独立 wheel 安装，再创建 GitHub release。
原项目许可证与来源保留在 NOTICE。变更应用时不需要修改库；若要求改动控件／帧
协议，应在 ComfortableTUI 中独立处理并更新依赖提交，不复制一份库进本项目。

## 双语维护

更新中文手册时同步维护 `docs/en/` 的对应页面、页首语言链接与 MkDocs 导航。
中英文 UI 文案见 `i18n.py` 和 `web/analytics.js`。集成自测会在暂停采样后切换
中文，再切回英文，确认所有网页同步且页面未重建；测试不保存用户语言偏好。
