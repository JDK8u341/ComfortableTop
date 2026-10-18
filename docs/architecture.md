# 架构与边界

简体中文 | [English](en/architecture.md)

## 独立项目与库依赖

ComfortableTop 拥有 `src/comfortable_top` Python 包、命令行入口、网页资源、C++ 图表
模块、测试和文档。ComfortableTUI 是外部库依赖，提供控件、终端渲染、共享帧 SDK、
Windows 附加层及 CEF 服务；Linux 仅保留终端模式。正常安装的库 wheel 不引用其源码
目录；本项目原生模块通过已安装的 ComfortableFrames CMake package 链接。

安装脚本可读取任意位置的依赖源码或获取锁定 Git 提交，将 wheel、SDK、宿主分别
安装到本项目环境／忽略目录。它不会重置用户提供的依赖仓库。复制后的运行时自包含
应用所需的 Windows 浏览器文件；Linux 终端模式无需 Qt／CEF。

## 三条数据路径

```text
Collector(单后台线程) → 不可变 Sample → MonitorModel → 原有 TUI 控件
                                             ├→ 低频指标 → C++ Trend → CPU共享帧 / D3D11纹理
                                             └→ 显式业务消息 → 独立CEF页面 → 图像显示服务
```

终端模式通过 PixelCanvas 绘制小图，自动协商 Kitty 或 braille。
native/hybrid 中 Python 只提交最多 180 个数值、握手描述符和布局控制；C++ 线程
独立插值、生成像素、发布 CPU 帧或 Windows GPU 纹理。静止后停止重发未改变图像。
窗口显示消费者与 C++ 生产者分离，不要求 Python 每帧获取租约。

网页是图像层之上的服务，URL、Cookie、profile、主题不进入通用帧协议。
`--web-render-mode` 单独控制浏览器传输（Windows 默认 GPU；Linux 图形模式已暂停），
`--canvas gpu` 只改变本项目趋势图。

## 采样与身份

Collector 最多一个任务在途，采样秒数与 UI FPS 分离。CPU/I/O 使用实际单调时间
差值；进程身份为 PID＋创建时间，首次、新进程、重置、受保护字段不填假零。
Linux 以 psutil 批量属性采集；Windows 以批量进程关系／RSS 加可访问进程时间
避免每个受保护进程触发一次全系统回退。Windows 不能获得创建时间的进程计入
unavailable，状态 alive 仅表示存在，交换区为 n/a。

每个当前进程最多 180 个历史点，退出后最多保留四个固定项的历史。排序保留选中
身份；过滤或退出后普通表格选邻近项。固定项不随 PID 重用变为新进程。

## 网页、隔离和焦点

应用身份为 `org.comfortabletop.app`，独立于原示例。分析 profile 临时且属于本应用；
不同应用不得借用。每个固定项 open() 一个页面，DOM、滚动和范围独立。最多四个
固定页加一个总览页。只有精确本机 origin 和明确主题被授权。

`monitor.sample` 发送指标，`monitor.select` 返回稳定身份；`monitor.probe/proof`
用于正常消息桥验证，不放开 CSP 或使用 eval。笔记和进程详情命令行不发送给网页。
每个 Top 进程（包括自测）使用独立临时浏览器根，退出时关闭 CEF 后删除。
多个实例可同时运行，不共享 Cookie、缓存或消息；库仍锁定各自的数据目录。

ResponsiveWebView 使用完整画布尺寸除以 DPI 作为网页视口，等待 120ms 稳定后
更换源尺寸；移动／裁剪不改变视口。旧源等待显示端确认解除附加后再回收。
单边上限 4096 像素。响应式 CSS 与 ResizeObserver 保持图表铺满剩余空间。

Tab/Shift+Tab 保留 TUI 焦点链；Enter／点击进入网页，Esc 返回表格；F6 返回菜单。
只读趋势图不持有键盘，鼠标穿透到外层控件，避免焦点困在画布上。

## 生命周期

退出顺序：显示宿主 → App 逻辑控件和原生消费者 → 采集线程 → 浏览器服务 → 图表
生产者 → 缓冲区 owner。图像传输沿用附加确认机制，不能通过关闭逻辑控件推断
显示消费者已释放源。显式导出使用后台任务和排他创建的新文件名。

## 语言层

Localizer 仅绑定明确声明的应用文案，切换时更新现有控件与 Unicode 标签宽度，
不重建控件树；弱引用允许已关闭弹窗被回收。模型排序键和导出键保持稳定，用户
内容不做批量替换。语言偏好与浏览器 profile、图像协议独立。`monitor.locale` 在
暂停时仍可通知每个页面；初始 URL 与采样消息也携带当前语言。详见[语言设置](localization.md)。
