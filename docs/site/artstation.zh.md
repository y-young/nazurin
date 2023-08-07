# ArtStation

<https://www.artstation.com/>

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### ARTSTATION_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Artstation`

存储路径。

### ARTSTATION_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{title} ({hash_id}) - {filename}`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "tags": ["标签"],
  "assets": [
    {
      "id": "图片ID",
      "title": "标题",
      "width": 3840,
      "height": 2160,
      "position": "图片索引"
    }
  ],
  "asset": "当前图片asset对象",
  "user": {
    "id": "用户ID",
    "username": "用户名",
    "headline": "签名",
    "full_name": "全名"
  },
  "medium": {
    "name": "媒介名称，如Digital 2D",
    "id": "媒介ID"
  },
  "categories": [
    {
      "name": "分类名称",
      "id": "分类ID"
    }
  ],
  "id": "作品ID",
  "user_id": "用户ID",
  "title": "标题",
  "created_at": "创建日期",
  "updated_at": "修改日期",
  "views_count": 0,
  "likes_count": 0,
  "comments_count": 0,
  "editor_pick": false,
  "adult_content": false,
  "slug": "URL别名",
  "hash_id": "URL hash ID",
  "index": "当前图片索引",
  "filename": "原始文件名称，不含扩展名"
}
```
