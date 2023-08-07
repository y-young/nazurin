# Moebooru

<https://yande.re/>

<https://konachan.com/>

<https://lolibooru.moe/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### MOEBOORU_FILE_PATH

:material-lightbulb-on: 可选，默认为 `{site_name}`

存储路径。

### MOEBOORU_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{filename}`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "id": "ID",
  "created_at": "创建时间",
  "creator_id": "上传者ID",
  "author": "上传者用户名",
  "score": 133,
  "md5": "MD5",
  "file_size": "文件大小",
  "jpeg_width": 2048,
  "jpeg_height": 1520,
  "jpeg_file_size": "JPEG文件大小",
  "rating": "s",
  "has_children": false,
  "parent_id": null,
  "status": "active",
  "width": 2048,
  "height": 1520,
  "filename": "原始文件名称，不含扩展名，不同网站格式可能不同",
  "site_name": "网站名称，如Yandere",
  "site_url": "网站URL，如yande.re"
}
```
