# Xfolio

<https://xfolio.jp/>

## 配置

### XFOLIO_SESSION

:material-lightbulb-on: 可选

浏览器登录后 Cookie 中的 `xfolio_session` 值（Xfolio 服务端默认提供 30 天滚动有效期）。

- **未配置 `XFOLIO_SESSION` 时**：直接抓取公开作品集的展示大图（`assets.xfolio.jp`，最高 1200px 的 WebP）。
- **配置 `XFOLIO_SESSION` 时**：
  - 优先获取未压缩原图（通过 `fullscale_image` 解析 `user_asset.php` 并自动识别 PNG/JPEG/WebP 真实后缀），若创作者未开启全尺寸查看则自动回退至 `assets.xfolio.jp` 源。
  - 可直接访问开启了「Bot対策機能（reCAPTCHA）」的作品集。
  - 收藏作品时支持自动点赞与自动加入站内收藏夹。

### XFOLIO_BOOKMARK

:material-lightbulb-on: 可选，默认为 `True`

当配置了 `XFOLIO_SESSION` 时，是否在收集作品时自动将其加入 Xfolio 收藏夹（Favorite）。

### XFOLIO_LIKE

:material-lightbulb-on: 可选，默认为 `True`

当配置了 `XFOLIO_SESSION` 时，是否在收集作品时自动为作品点赞（Like）。

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### XFOLIO_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Xfolio`

存储路径。

### XFOLIO_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{id}_{index} - {title} - {user[name]}({user[code]})`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "id": "作品 ID",
  "title": "作品标题",
  "description": "作品描述",
  "url": "作品链接",
  "user": {
    "id": "创作者 ID",
    "user_id": "用户 ID",
    "code": "创作者作品集代号 (creator code)",
    "name": "创作者显示名称",
    "profile": "创作者简介",
    "url": "创作者作品集主页链接"
  },
  "tags": ["标签 1", "标签 2"],
  "series": {
    "id": "系列 ID",
    "title": "系列标题",
    "url": "系列链接"
  },
  "likes_num": "点赞数",
  "favorites_num": "收藏数",
  "filename": "原始文件名称，不含扩展名",
  "image_id": "全尺寸原图 ID（登录且作者开启全尺寸查看时可用）",
  "index": "图片索引",
  "extension": "扩展名，含前导点"
}
```
