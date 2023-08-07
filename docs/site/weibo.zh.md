# 微博

<https://weibo.com/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### WEIBO_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Weibo`

存储路径。

### WEIBO_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{mid}_{index} - {user[screen_name]}({user[id]})`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "created_at": "创建日期",
  "id": "ID",
  "user": {
    "id": "用户 ID",
    "screen_name": "用户名称",
    "gender": "性别"
  },
  "reposts_count": 198,
  "comments_count": 221,
  "reprint_cmt_count": 0,
  "attitudes_count": 483,
  "pics": [
    {
      "pid": "图片ID"
    }
  ],
  "index": "图片索引",
  "pic": "当前图片在`pics`中的对象"
}
```
