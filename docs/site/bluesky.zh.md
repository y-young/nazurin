# Bluesky

<https://bsky.app/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### BLUESKY_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Bluesky`

存储路径。

### BLUESKY_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{rkey}_{index} - {user[display_name]}({user[handle]})`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "rkey": "帖子的 Record Key",
  "uri": "帖子的 at:// uri",
  "cid": "帖子的 cid",
  "user": {
    "did": "用户 DID",
    "handle": "用户 handle",
    "display_name": "用户显示名称"
  },
  "filename": "原始文件名称，不含扩展名",
  "index": "图片索引",
  "timestamp": "时间戳",
  "extension": "扩展名",
  "reply_count": "回复数",
  "repost_count": "转发数",
  "like_count": "点赞数",
  "pic": {
    "aspectRatio": {
      "height": 1440,
      "width": 1080
    },
    "image": {
      "mimeType": "image/jpeg",
      "size": 123456,
    }
  }
}
```
