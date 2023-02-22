# Bilibili 动态

<https://t.bilibili.com/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](../#customizing-storage-path--file-name)。

### BILIBILI_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Bilibili`

存储路径。

### BILIBILI_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{dynamic_id_str}_{index} - {user[name]}({user[uid]})`

文件名称。

### 可用变量

_此处只列出常用项。_

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
    "upload_time": "上传时间"
  },
  "user": {
    "name": "用户名称",
    "uid": "用户ID"
  },
  "dynamic_id_str": "ID",
  "view": 497,
  "repost": 5,
  "comment": 5,
  "like": 68,
  "timestamp": "时间戳",
  "filename": "原始文件名称，不含扩展名",
  "pic": "当前图片在`item.pictures`中的对象",
  "index": "当前图片索引"
}
```
