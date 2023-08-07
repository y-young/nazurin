# DeviantArt

<https://www.deviantart.com/ >

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### DEVIANT_ART_FILE_PATH

:material-lightbulb-on: 可选，默认为 `DeviantArt`

存储路径。

### DEVIANT_ART_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{title} - {deviationId}`

图像文件名称。

### DEVIANT_ART_DOWNLOAD_NAME

:material-lightbulb-on: 可选，默认为 `{title} - {deviationId} - {prettyName}`

下载文件的名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "deviationId": "Deviation ID",
  "type": "image",
  "typeId": 1,
  "title": "标题",
  "publishedTime": "发布时间",
  "author": {
    "userId": "用户ID",
    "useridUuid": "用户UUID",
    "username": "用户名"
  },
  "stats": {
    "comments": 51,
    "favourites": 202,
    "views": 1058,
    "downloads": 0
  },
  "media": {
    "prettyName": "易读文件名"
  },
  "extended": {
    "deviationUuid": "Deviation UUID",
    "originalFile": {
      "type": "original",
      "width": "宽度",
      "height": "高度",
      "filesize": "文件大小"
    }
  },
  "filename": "默认文件名（UUID），不含扩展名"
}
```
