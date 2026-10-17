# Research and inherited scope

[简体中文](../research.md) | English

The initial app was extracted from the ComfortableTUI example at commit
`84f37b15645b78e1a07b4dd769fee4941a5d568a`. Attribution is preserved in NOTICE.
The original example used Exa research; these primary sources support its interactions
and metric semantics:

| Source | Design relevance |
| --- | --- |
| [htop](https://github.com/htop-dev/htop) | Search, sorting, mouse/keyboard navigation and process relationships |
| [btop](https://github.com/aristocratos/btop#features) | Resource trends, interface/disk rates, pause and details |
| [psutil API](https://psutil.readthedocs.io/en/stable/) | Invalid initial CPU sample, CPU above 100%, permissions and exit races |
| [psutil performance](https://psutil.io/performance/) | Batch required fields; fetch expensive details on demand |
| [Toolhelp](https://learn.microsoft.com/en-us/windows/win32/toolhelp/taking-a-snapshot-and-viewing-processes) | Batch process relationships and thread counts |
| [GetProcessTimes](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes) | Accessible creation and CPU times |
| [NtQuerySystemInformation](https://learn.microsoft.com/en-us/windows/win32/api/winternl/nf-winternl-ntquerysysteminformation) | Documented RSS fields; reserved fields remain opaque |

No htop/btop implementation was copied, and this app does not claim their complete
feature set. Frame transport remains the external SDK's responsibility; this app adds
chart producers and the higher-level business UI. CEF continues to use CPU frames.
macOS, hardware GPU utilization, sensors and process termination are outside current scope.
