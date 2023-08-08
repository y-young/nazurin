# Wallhaven

<https://wallhaven.cc/>

## 配置

### WALLHAVEN_API_KEY

:material-lightbulb-on: 可选，根据 [API 文档](https://wallhaven.cc/help/api#wallpapers)，在浏览 NSFW 壁纸时需要使用

Wallhaven API 密钥，可在 [账号设置](https://wallhaven.cc/settings/account) 中找到。

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### WALLHAVEN_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Wallhaven`

存储路径。

### WALLHAVEN_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{id}`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "id": "壁纸ID",
  "uploader": {
    "username": "上传者用户名",
    "group": "上传者用户组，如User"
  },
  "views": "浏览量",
  "favorites": "收藏量",
  "purity": "分级，例如sfw",
  "category": "分类，如anime",
  "dimension_x": "宽度",
  "dimension_y": "高度",
  "resolution": "分辨率，如1920x1080",
  "ratio": "宽高比",
  "file_size": "文件大小",
  "file_type": "文件类型，如image/png",
  "created_at": "创建日期",
  "colors": ["色盘"],
  "tags": [
    {
      "id": "标签 ID",
      "name": "标签名称",
      "alias": "标签别名",
      "category_id": "标签分类ID",
      "category": "标签分类",
      "purity": "标签分级，例如sfw"
    }
  ]
}
```
