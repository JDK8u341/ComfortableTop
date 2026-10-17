# English and Chinese

[简体中文](../localization.md) | English

Press **F9** to switch languages immediately, or choose **Settings → Language / 语言**.
The change updates tabs, buttons, dropdowns, table headings, help, live metric text,
notifications, and every browser analytics page. It also works while sampling is paused.
No restart or browser page replacement is required.

```sh
comfortable-top --lang en
comfortable-top --lang zh
comfortable-top --lang auto
comfortable-top --snapshot --interval .25 --lang zh
```

The default, `auto`, first reads a saved preference, then the system locale. Chinese
locales select Chinese; other locales select English. `--lang en/zh` overrides the
language for this launch. F9 and the settings selector save a preference for future launches.
Detection reads LC_ALL, LC_MESSAGES, LANGUAGE, LANG, or the system locale.

Preferences live at `%APPDATA%/ComfortableTop/settings.json` on Windows, or
`$XDG_CONFIG_HOME/ComfortableTop/settings.json` on Linux, defaulting to
`~/.config/ComfortableTop/settings.json`. Set `COMFORTABLE_TOP_CONFIG` to override the
complete file path. Unreadable or invalid files fall back to the system language.
A failed write displays a notification while retaining the active language.
Starting the app alone does not create a preference file.

Switching preserves the current page, focus, filter, sort order, pinned identities,
history, pause state, export fields, notes and output directory. Tab bounds are
recalculated with Unicode display widths. Browser pages retain their identity, scroll
position and independent chart range. The authorized `monitor.locale` message updates
them without waiting for a sample. Initial URLs and telemetry also carry the language
so a page that loads late receives the current setting.

Process names, usernames, paths, user notes, existing log entries, raw process-detail
fields and JSON export keys retain their original values. New logs use the active
language. The initial notes template uses the startup language and is never overwritten
when switching. Standard abbreviations such as CPU, PID, RSS and KiB remain unchanged.
CLI help, build tools and errors originating from dependencies remain in English.

Maintain Python application copy in `src/comfortable_top/i18n.py` and web copy in
`web/analytics.js`. Keep translated labels separate from model identifiers: selecting
the Chinese memory label must still sort on RSS. Do not translate arbitrary collected
data by treating every displayed string as a dictionary key.
