# Danbooru

<https://danbooru.donmai.us/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### DANBOORU_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Danbooru`

存储路径。

### DANBOORU_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{id} - {filename}`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "id": "ID",
  "created_at": "创建时间",
  "uploader_id": "上传者ID",
  "score": 10,
  "md5": "MD5",
  "rating": "s",
  "image_width": "图片宽度",
  "image_height": "图片高度",
  "fav_count": 10,
  "file_ext": "png",
  "parent_id": null,
  "has_children": false,
  "approver_id": "批准者ID",
  "tag_count_general": 1,
  "tag_count_artist": 1,
  "tag_count_character": 1,
  "tag_count_copyright": 1,
  "file_size": "文件大小",
  "up_score": 10,
  "down_score": 0,
  "tag_count": 5,
  "updated_at": "上传时间",
  "pixiv_id": "Pixiv ID，可能为空",
  "tag_count_meta": 1,
  "tag_string_character": "",
  "tag_string_copyright": "",
  "tag_string_artist": "",
  "tag_string_meta": "",
  "filename": "类似网站上下载时的易读文件名，由标签组成，不含扩展名"
}
```
