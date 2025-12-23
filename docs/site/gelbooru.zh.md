# Gelbooru

<https://gelbooru.com/>

## 配置

### 认证

为了防止滥用行为，Gelbooru 有时需要认证才能访问 API，并对 API 访问进行限制，详见 [Gelbooru API 文档](https://gelbooru.com/index.php?page=wiki&s=view&id=18780)。

要获取 API 密钥和用户 ID，先在 Gelbooru 上创建一个账户，并在 [账户设置](https://gelbooru.com/index.php?page=account&s=options) 中找到 API 访问凭证。

#### GELBOORU_API_KEY

:material-lightbulb-on: 可选

Gelbooru API 密钥。

#### GELBOORU_USER_ID

:material-lightbulb-on: 可选

Gelbooru 用户 ID。

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### GELBOORU_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Gelbooru`

存储路径。

### GELBOORU_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{id}`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "id": "ID",
  "created_at": "创建日期",
  "score": 3,
  "width": 900,
  "height": 1800,
  "md5": "MD5",
  "rating": "general",
  "owner": "danbooru",
  "creator_id": "上传者ID",
  "parent_id": 0,
  "title": ""
}
```
