# 动效与实际应用验证

简体中文 | [English](en/motion.md)

当前依赖默认使用 Expressive。焦点和列表选择带回弹，按钮有按压反馈；开关、滑块、
柱状图、弹窗和通知都有过渡。进度和数字保持真实样本语义：柱条会插值，旁边的
CPU 数字立即更新，不延后采样、不向数据注入过冲。键盘和网页进入/退出规则不变。

## 启动

本机 `.venv` 已安装新库 wheel，通常直接运行即可：

```powershell
.\.venv\Scripts\comfortable-top.exe --mode hybrid --canvas gpu --fps 60
```

源码更新用户先按[安装](installation.md)更新依赖。仍使用旧版 wheel 时，更新
应用源码不会自动更新底层动效；bootstrap/requirements 已锁定带动效的库提交。
本次代码已合并到两个仓库的 `main`，并包含在 v0.1.1 发布包中。

```powershell
# 本机已有依赖源码时重新安装，保留 GPU 扩展与既有浏览器运行时：
.\.venv\Scripts\python.exe tools/bootstrap.py --tui-source ..\tui --gpu
```

不需要原生模式时按安装指南使用 `--terminal-only`，然后执行 comfortable-top。
原生/浏览器的 C++ 协议没有改变，无需重建 CEF。GitHub 旧 v0.1.0 发布包不包含本次
依赖更新，测试结果针对锁定提交安装的 wheel，不代表旧发布附件。

## 帧调度优化（2026-10-18）

本机 Windows Python 3.12 的 monotonic 使用 GetTickCount64，粒度约 15.625ms。
此前的等待条件把目标 60/120 FPS 分别限制在约 32/64 FPS。底层库现使用
perf_counter 的高精度截止时间，保持连续帧节奏，并缓存短文本的字形和样式。
原有回弹参数不变。原因参见 [CPython 时钟修改](https://github.com/python/cpython/pull/116781)。

真实 Windows Terminal、GPU 图表和 CEF 混合模式测试中，60 FPS 目标的循环频率
从 32.00 升至 59.67，120 FPS 从 64.01 升至 117.77。帧间隔 P95 分别从
32.744→17.259ms、17.492→8.984ms。它们是实际生产循环节奏，不是显示器呈现
帧率或输入到显示延迟；终端写入偶尔仍会阻塞。

本机已安装修正后的 wheel，退出旧进程再启动即可。默认 60 FPS 保持不变，
需要时可用 `--fps 120`。验证工具会新建自己的 Windows Terminal 并持续采样：

```powershell
.\.venv\Scripts\python.exe -m comfortable_top.verify_pacing --fps 60 --report .build/pacing-new-60.json
.\.venv\Scripts\python.exe -m comfortable_top.verify_pacing --fps 120 --report .build/pacing-new-120.json
```

使用不存在的报告路径；默认运行 12 秒并剔除前 3 秒。它记录实际循环间隔及
tick/render/encode/write/overlay 耗时，覆盖连续换焦点、切页和弹窗。
`passed` 表示采集了足够的有效帧和系统样本，不表示达到机器无关的 FPS 保证。
原始数据与平台复查见[验证记录](validation.md#2026-10-18)。

## 手动体验

1. 用 Tab / Shift+Tab 在搜索、排序、暂停和用户筛选之间快速来回，观察高亮拉伸及回弹。
2. F6 进入菜单，左右切页并在动画中反向；进程列表上下切换，逻辑选择立即生效。
3. F1 打开帮助、Esc 关闭；退场是无输入能力的单元格快照，焦点立即归还。
4. 资源页观察逐核柱条，设置页调整 Slider；采样数字不跟随动画产生假波动。
5. Compare 中进入网页并按 Esc 返回表格，确认嵌入画布在页面运动/裁剪后仍对齐。

可选择更温和的动效，或关闭动态效果：

```powershell
$env:COMFORTABLE_TUI_MOTION = 'subtle'
.\.venv\Scripts\comfortable-top.exe
$env:COMFORTABLE_TUI_REDUCED_MOTION = '1'
.\.venv\Scripts\comfortable-top.exe
Remove-Item Env:COMFORTABLE_TUI_MOTION, Env:COMFORTABLE_TUI_REDUCED_MOTION
```

减少动效不会暂停采样、CEF 页面或外部视频提供者；它只约束库内的装饰性运动。

## 自动验证

```powershell
.\.venv\Scripts\python.exe -m comfortable_top.verify_motion --report .build/my-motion.json
.\.venv\Scripts\python.exe -m comfortable_top.verify_motion --motion subtle --report .build/my-subtle.json
.\.venv\Scripts\python.exe -m comfortable_top.verify_motion --reduced-motion --report .build/my-reduced.json
.\.venv\Scripts\python.exe -m comfortable_top.verify_windows --mode hybrid --canvas gpu --report .build/my-display.json
```

报告路径须不存在。verify_motion 使用真实 Monitor、两次系统采样、已安装 TUI，
暂停采样后检查快速切页、焦点、通知、弹窗、PageStack，确认最后 90 帧没有差分。
统计 CPU render+encode 的 P50/P95、输出字节和变化帧数，不把它称为实际屏幕 FPS。
这部分无图形桌面也可执行；真正的原生组合需使用 Windows 验证工具或 Linux 自测：

```bash
comfortable-top --mode hybrid --platform x11 --self-test --smoke-seconds 15 --report .build/my-x11.json
comfortable-top --mode hybrid --platform wayland --self-test --smoke-seconds 15 --report .build/my-wayland.json
```

本次 Windows GPU、WSL2 X11 和 Wayland 各十项组合检查通过；Windows 应用单元测试
27 项通过，WSL2 26 项通过、1 项跳过。独立记录见[验证](validation.md)。
