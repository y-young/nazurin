# Bilibili 动态

<https://t.bilibili.com/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### BILIBILI_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Bilibili`

存储路径。

### BILIBILI_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{id_str}_{index} - {user[name]}({user[mid]})`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "user": {
    "name": "用户名称",
    "mid": "用户ID"
  },
  "id_str": "ID",
  "timestamp": "时间戳",
  "filename": "原始文件名称，不含扩展名",
  "pic": {
    "height": 1440,
    "width": 1080
  },
  "index": "当前图片索引"
}
```
