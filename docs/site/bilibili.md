# Bilibili Dynamics

<https://t.bilibili.com/>

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](../#customizing-storage-path--file-name).

### BILIBILI_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Bilibili`

Storage path for downloaded images.

### BILIBILI_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{dynamic_id_str}_{index} - {user[name]}({user[uid]})`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "item": {
    "pictures": [
      {
        "img_height": 900,
        "img_size": 840.989990234375,
        "img_width": 1600
      }
    ],
    "pictures_count": 1,
    "reply": 5,
    "title": "",
    "upload_time": "Upload time"
  },
  "user": {
    "name": "User name",
    "uid": "User ID"
  },
  "dynamic_id_str": "ID",
  "view": 497,
  "repost": 5,
  "comment": 5,
  "like": 68,
  "timestamp": "Timestamp",
  "filename": "Original file name, without extension",
  "pic": "Current image object in `item.pictures`",
  "index": "Image index"
}
```
