# Zerochan

<https://www.zerochan.net/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### ZEROCHAN_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Zerochan`

存储路径。

### ZEROCHAN_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{id} - {name}`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "id": "ID",
  "name": "名称",
  "created_at": "创建日期",
  "image_width": "2480",
  "image_height": "1500",
  "file_ext": "png",
  "file_size": "文件大小",
  "uploader": "上传者用户名",
  "filename": "原始文件名称，不含扩展名"
}
```
