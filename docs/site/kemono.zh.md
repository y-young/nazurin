# Kemono.party

<https://kemono.party/>，<https://kemono.su/>

<https://pawchive.pw/>，<https://pawchive.st/>

!!! note "注意"

    部分帖子未被完整归档，即原图不可用、仅有预览图。此类帖子的图片将改为下载预览缩略图，非图片文件则会被跳过。

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### KEMONO_FILE_PATH

:material-lightbulb-on: 可选，默认为 `{site_name}/{service}/{username} ({user})/{title} ({id})`

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
  "added": "添加到 Kemono/Pawchive 的时间",
  "published": "在原始平台上的发布时间",
  "edited": "在 Kemono/Pawchive 上的修改时间，可能为 null",
  "filename": "由网站提供的默认文件名，不含扩展名",
  "pretty_name": "由作者提供的文件名，不含扩展名。如果没有则使用网站提供的 UUID 文件名",
  "site_name": "网站名称，如 Kemono、Pawchive",
  "site": "网站标识，如 kemono、pawchive"
}
```
