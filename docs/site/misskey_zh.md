# Misskey Notes

从任何 Misskey 实例获取。

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### Misskey_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Misskey`

存储路径。

### Misskey_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{id} - {filename} - {user[name]}({user[username]})`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "id": "<note id>",
  "createdAt": "2023-10-05T23:10:13.016Z",
  "userId": "<用户 id>",
  "user": {
    "id": "<用户 id>",
    "name": "<用户展示名称>",
    "username": "<用户名>",
    "host": "<用户所在实例 URL>"
  },
  "text": "<note 文字>",
  "fileIds": ["<文件 id>"],
  "files": [
    {
      "id": "<文件 id>",
      "createdAt": "2023-10-05T23:10:16.445Z",
      "name": "<文件名>",
      "type": "image/webp",
      "md5": "<文件 md5>",
      "size": 800000,
      "isSensitive": false,
      "properties": {
        "width": 2048,
        "height": 1969
      },
      "url": "<文件 URL>",
      "thumbnailUrl": "<缩略图 URL>"
    }
  ],
  "uri": "<该 note 在源实例的 URL>" // Only available when the note is from a remote instance.
}
```
