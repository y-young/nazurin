# Telegram

!!! note

    Since v2.0, Telegram has become a standalone storage type.

Use a Telegram channel (album channel) to store downloaded files.

!!! warning

    Due to the file size limit of Telegram bot API, files larger than 50MB cannot be stored in Telegram.

## Configuration

### STORAGE

Append `Telegram`. For more information, see [Configuration](../getting-started/configuration.md/#storage).

### ALBUM_ID

:material-exclamation-thick: Required

Telegram channel ID used for storing files.

!!! tip

    You need to add your bot to channel administrators.
