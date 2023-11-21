# Telegram

!!! note "注意"

    从 2.0 版本起，Telegram 已成为一个独立的存储类型。

使用 Telegram 频道（相册频道）存储下载的文件。

!!! warning "警告"

    由于 Telegram 机器人 API 的文件大小限制，大于 50MB 的文件无法存储在 Telegram 中。

## 配置

### STORAGE

追加 `Telegram`，详见 [配置](../getting-started/configuration.zh.md/#storage)。

### ALBUM_ID

:material-exclamation-thick: 必需

用于存储文件的 Telegram 频道 ID。

!!! tip "提示"

    你需要将机器人添加为频道管理员。
