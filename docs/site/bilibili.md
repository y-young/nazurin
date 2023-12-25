# Bilibili Dynamics

<https://t.bilibili.com/>

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### BILIBILI_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Bilibili`

Storage path for downloaded images.

### BILIBILI_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{id_str}_{index} - {user[name]}({user[mid]})`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "user": {
    "name": "User name",
    "mid": "User ID"
  },
  "id_str": "ID",
  "timestamp": "Timestamp",
  "filename": "Original file name, without extension",
  "pic": {
    "height": 1440,
    "width": 1080
  },
  "index": "Image index"
}
```
