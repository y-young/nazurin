# Twitter

<https://twitter.com/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](../#customizing-storage-path--file-name)。

### TWITTER_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Twitter`

存储路径。

### TWITTER_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{id_str}_{index} - {user[name]}({user[id_str]})`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "lang": "推文语言，例如ja",
  "favorite_count": 4814,
  "possibly_sensitive": false,
  "created_at": "创建日期",
  "id_str": "推文ID",
  "user": {
    "id_str": "用户ID",
    "name": "用户名称",
    "screen_name": "用户handle"
  },
  "photos": [
    {
      "width": "宽度",
      "height": "高度"
    }
  ],
  "filename": "twimg.com URL中的原始文件名称，不含扩展名",
  "index": "图片或视频索引"
}
```
