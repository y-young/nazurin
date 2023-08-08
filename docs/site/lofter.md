# Lofter

<https://www.lofter.com/>

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### LOFTER_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Lofter`

Storage path for downloaded images.

### LOFTER_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{id}_{index} - {nickName}({blogName})`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "id": "ID",
  "type": 2,
  "blogId": "Blog ID",
  "title": "",
  "publishTime": "Publish time",
  "blogInfo": {
    "blogName": "Blog username",
    "blogNickName": "Blog name"
  },
  "caption": "",
  "tagList": ["Tag"],
  "permalink": "Permanent link",
  "filename": "Original file name, without extension",
  "index": "Image index",
  "blogName": "Shortcut for `blogInfo.blogName`",
  "nickName": "Shortcut for `blogInfo.blogNickName`"
}
```
