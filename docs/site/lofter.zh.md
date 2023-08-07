# Lofter

<https://www.lofter.com/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### LOFTER_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Lofter`

存储路径。

### LOFTER_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{id}_{index} - {nickName}({blogName})`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "id": "ID",
  "type": 2,
  "blogId": "博客ID",
  "title": "",
  "publishTime": "发布时间",
  "blogInfo": {
    "blogName": "用户名",
    "blogNickName": "博客昵称"
  },
  "caption": "",
  "tagList": ["标签"],
  "permalink": "永久链接",
  "filename": "原始文件名称，不含扩展名",
  "index": "图片索引",
  "blogName": "等同于`blogInfo.blogName`",
  "nickName": "等同于`blogInfo.blogNickName`"
}
```
