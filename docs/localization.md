# 中英文与语言切换

[English](en/localization.md) | 简体中文

按 **F9** 随时切换中文与英文，也可在 **设置 → Language / 语言** 中选择。
主标签、按钮、下拉菜单、表头、帮助、动态指标、提示，以及总览和每个固定进程的
浏览器分析页都会更新。暂停采样时也立即生效，不重启应用或重新创建网页。

```sh
comfortable-top --lang zh
comfortable-top --lang en
comfortable-top --lang auto
comfortable-top --snapshot --interval .25 --lang zh
```

默认 `auto` 的顺序是：已保存的偏好 → 操作系统语言。中文系统选中文，其他语言选英文。
`--lang zh/en` 只覆盖本次启动；在界面中选择或按 F9 会保存偏好供下次启动使用。
语言检测读取 LC_ALL、LC_MESSAGES、LANGUAGE、LANG，或系统 locale。

偏好保存在 Windows `%APPDATA%/ComfortableTop/settings.json`，Linux
`$XDG_CONFIG_HOME/ComfortableTop/settings.json`（默认 `~/.config/ComfortableTop/settings.json`）。
设置 `COMFORTABLE_TOP_CONFIG` 可指定完整配置文件路径。无效或不可读的文件会回退到
系统语言；写入失败会提示，但当前语言仍然生效。启动时不会主动创建配置文件。

语言切换保留当前页面、焦点、筛选、排序、固定身份、采样历史、暂停状态、导出字段、
笔记和输出目录。标签宽度按 Unicode 显示宽度重新计算。浏览器保留 DOM 页面、滚动
位置和独立图表范围；仅通过授权的 `monitor.locale` 主题更新界面，初始 URL 和后续
指标消息也携带语言，因此页面加载较慢时仍能取得最新语言。

进程名称、用户名、文件路径、用户笔记、既有日志、原始进程详情字段和 JSON 导出
结构不做翻译，以保持数据原貌。新日志使用当时选择的语言。初始笔记模板使用启动
语言，切换时不会覆盖笔记。CPU、PID、RSS、KiB 等标准缩写和命令行参数名保持一致。
命令行帮助、构建工具和底层库异常仍使用英文。

开发时在 `src/comfortable_top/i18n.py` 维护应用文案与控件绑定，在
`web/analytics.js` 维护网页词典。显示文本与模型排序键分离；不要用翻译后的“内存”
去访问模型的 RSS 字段，也不要将本机采集数据作为词典键批量替换。
