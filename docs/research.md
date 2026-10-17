# 研究依据与继承范围

本应用最初从 ComfortableTUI 示例拆分，基线提交
`84f37b15645b78e1a07b4dd769fee4941a5d568a`，来源声明见仓库 NOTICE。
原示例使用 Exa 调研，以下资料支撑当前交互和指标语义：

| 原始来源 | 应用中的用途 |
| --- | --- |
| [htop](https://github.com/htop-dev/htop) | 搜索排序、鼠标／键盘导航、进程关系 |
| [btop](https://github.com/aristocratos/btop#features) | 资源趋势、逐接口／磁盘速率、暂停和详情 |
| [psutil API](https://psutil.readthedocs.io/en/stable/) | 首次 CPU 无效、进程 CPU 可超过 100%、权限和退出竞争 |
| [psutil 性能](https://psutil.io/performance/) | 批量必要属性，昂贵详情按需获取 |
| [Toolhelp](https://learn.microsoft.com/en-us/windows/win32/toolhelp/taking-a-snapshot-and-viewing-processes) | 批量进程关系和线程数 |
| [GetProcessTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes) | 可访问进程创建时间和 CPU 时间 |
| [NtQuerySystemInformation](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntquerysysteminformation) | 已公开 RSS 字段批量读取；保留字段不解读 |

没有复制 htop/btop 实现，不声称具有其全部功能。CPU/GPU 帧传输继续由外部 SDK
负责，本应用只增加图表生产者和上层业务界面。CEF 继续用 CPU 帧；macOS、GPU
硬件占用率、传感器和系统进程结束操作未纳入当前范围。
