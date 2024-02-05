# Kemono.party

<https://kemono.party/>，<https://kemono.su/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### KEMONO_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Kemono/{service}/{username} ({user})/{title} ({id})`

存储路径。

### KEMONO_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{pretty_name}`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "id": "在原始平台（如 Fanbox）上的 Post ID",
  "user": "在原始平台（如 Fanbox）上的 User ID",
  "title": "",
  "added": "添加到 Kemono 的时间",
  "published": "在原始平台上的发布时间",
  "edited": "在 Kemono 上的修改时间，可能为 null",
  "filename": "由 Kemono 提供的默认文件名，不含扩展名",
  "pretty_name": "由作者提供的文件名，不含扩展名。如果没有则使用 Kemono 提供的 UUID 文件名"
}
```
