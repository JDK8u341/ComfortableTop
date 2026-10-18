# 使用指南

简体中文 | [English](en/guide.md)

安装后执行 `comfortable-top` 或 `python -m comfortable_top`。

当前测试分支 Windows 混合模式的网页默认使用 GPU；加 `--web-render-mode cpu`
可对照 CPU 路径。Linux 仅保留终端模式，图像混合模式已暂停。原生图表继续由 `--canvas cpu|gpu` 独立控制。
需要匹配的新库与运行时，见[安装说明](installation.md)。
完整安装步骤见 [安装](installation.md)。建议至少 120×38，窄窗口会隐藏详情侧栏；表格可水平滚动。

## 页面和操作

| 页面 | 用途和组合功能 |
| --- | --- |
| 进程 / Processes | 实时虚拟 DataTable、内嵌 Sparkline、筛选排序、用户过滤、身份跟踪、后台详情弹窗；Text 混排趋势画布 |
| 资源 / Resources | CPU 曲线、逐核 BarChart、内存 ProgressBar、网卡／磁盘吞吐表，以及交互式网页分析 |
| 对比 / Compare | 四个固定进程；Virtual List 内嵌画布、DataTable 内嵌独立 WebView；可展开的真实进程树 |
| 工作区 / Workspace | Unicode TextArea 笔记、Log、DirectoryTree、SelectionList 导出字段、后台 JSON 导出、PageStack 预览 |
| 设置 / Settings | 中英文语言选择、Slider 采样频率、RadioGroup 排序方向、Collapsible 指标说明、ScrollView 和帮助弹窗 |

顶栏还使用 Input、Select、Switch、Checkbox、Spinner、Rule；Tabs、焦点和进度条
沿用库的动画。只读取进程，不提供结束系统进程等操作。

| 按键 | 行为 |
| --- | --- |
| F1 / F2 | 帮助 / 搜索；匹配 PID、名称、用户和状态，空格分隔的词须全部匹配 |
| F3 / F4 | 循环 CPU／内存／PID／名称排序；固定／取消固定选中进程 |
| F9 | 切换中文／英文并保存偏好 |
| F7 / F8 | 暂停采样／恢复；后台读取当前进程详情 |
| Ctrl+1…5 | 切换主要页面 |
| Ctrl+E | 导出当前快照和笔记到界面指定目录，生成新 JSON 文件 |
| F6 / Tab / Shift+Tab | 菜单与内容／原有焦点链 |
| Enter / Esc | 进程行打开详情；Compare 表格进入当前行网页／退回表格；关闭弹窗或返回预览 |
| Ctrl+Q / Ctrl+C | 退出并释放消费者、生产者、服务和共享缓冲区 |

进程身份为 **PID + 创建时间**。刷新排序继续跟踪身份；固定项退出后显示 exited，
不会把重用 PID 的新进程当成原进程。在 Compare 列表／表格上按 F4 可移除已退出项。
普通进程表中原选择退出／被过滤时会选择邻近行。暂停冻结整个采样快照，不暂停系统
进程，丢弃一份已经在后台执行的采样。

每个固定项的网页单独调用 `BrowserService.open()`，DOM、滚动位置、图表范围独立。
这些页属于本应用私有的临时 `local-analytics` profile。联动使用明确授权的
`monitor.sample/select` 主题；语言通过 `monitor.locale` 独立同步，暂停时也能切换；`monitor.probe/proof` 用于消息桥验证。
网页保留 CSP，验证不使用动态 eval。最多五页，取消固定后关闭对应页面。
分析页按画布的完整逻辑像素尺寸重新布局（物理尺寸除以 DPI），不再把固定比例网页
缩成小图；图表随剩余空间铺开，矮面板使用紧凑工具栏。拖动调整大小时等待 120ms
稳定后更换网页缓冲区，每边最多 4096 像素；移动位置和局部裁剪不会重建网页。
这是本例每页一个视图的自适应策略，普通 WebView 镜像仍使用原有固定源尺寸语义。
非混合模式下，同一 PID 的两个小图可镜像同一图像源；不同固定项的源独立。


## 参数和架构

`--lang zh/en/auto` 控制启动语言，按 F9 随时切换，详见[语言设置](localization.md)。

`--interval .25..5` 控制采样秒数，默认 1；`--fps 1..240` 控制 UI 目标，默认 60。
`--output DIR` 预填导出目录；`--snapshot` 真实采样两次后输出终端帧。
`--smoke-seconds N` 自动退出，`--report PATH` 保存验证数量和检查项。
`--self-test` 自动验证交互，需至少 14 秒；不用它即可正常交互使用。

```text
后台采样 → 不可变 Sample → 有界 Model → 终端控件
                                  ├→ 低频数值 → C++图表线程 → CPU共享帧 / Win GPU纹理
                                  └→ 业务消息 → 独立CEF页面 → 现有图像显示层
```

基础模式在 Python 绘制小尺寸 PixelCanvas。原生模式中 Python **不生成、复制或逐帧
传递像素**，仅分配缓冲区、传递描述符、每次采样提交最多 180 个数值及处理标准布局／
缩放／生命周期事件。C++ 插值并发布帧，静止后停止重复发布。最多六个图表生产者，
固定项复用四个槽，不按系统进程数创建线程或网页。帧 SDK 不包含 URL/profile。
图表是只读显示，鼠标穿透给容器；网页通过原有焦点规则交互。

进程 CPU = 相邻 user+system 时间差 / 实际单调时钟间隔，100% 为一个核心；可超过
100%。系统 CPU 为各核平均。曲线固定 0..100% 并裁剪，表格保留精确值；横轴为有效
采样点，缺失值不画成零。Sparkline、逐核条形图相对缩放，旁边数值为实际百分比。
第一次 CPU/I/O、新进程、重置和不可读字段为 warmup/n/a，不伪造零值。
RSS 为驻留内存，非独占内存；系统内存显示 total-available。网络包含回环；磁盘
总量是 OS 设备计数之和，分层设备可能重复，应结合逐设备表解读。

Linux 通过 psutil.process_iter(attrs=...) 采集。Windows 一次 Toolhelp 获取关系／
线程数，一次 NtQuerySystemInformation 读取公开 RSS 字段，再用 GetProcessTimes
取得可访问进程的身份和 CPU；reserved 字段保持不透明。取不到创建时间的受保护进程
计入 unavailable，不显示为稳定身份行；状态 alive 仅表示存在，交换区为 n/a。
用户名按身份缓存。一次采集未完成时不提交下一份，实际频率受系统读取开销约束。

每个当前进程最多保留 180 个历史点；退出后只保留四个固定项的历史。笔记不发送给
网页，只有显式导出才写文件，生成新名称并以排他方式创建，不覆盖现有文件。


构建见 [安装](installation.md)，测试和文件布局见 [开发](development.md)。
