# Weibo

<https://weibo.com/>

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### WEIBO_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Weibo`

Storage path for downloaded images.

### WEIBO_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{mid}_{index} - {user[screen_name]}({user[id]})`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "created_at": "Creation date",
  "id": "ID",
  "user": {
    "id": "User ID",
    "screen_name": "User name",
    "gender": "Gender"
  },
  "reposts_count": 198,
  "comments_count": 221,
  "reprint_cmt_count": 0,
  "attitudes_count": 483,
  "pics": [
    {
      "pid": "Picture ID"
    }
  ],
  "index": "Image index",
  "pic": "Current image object in `pics`"
}
```
