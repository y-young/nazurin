# Twitter

<https://twitter.com/>

## 配置

### TWITTER_API

:material-lightbulb-on: 可选，默认为 `web`

要使用的 API，`web` 或 `syndication`。Web API 来自网页应用，而 Syndication API 来自 <https://publish.twitter.com>。

Syndication API 无法获取被标记为敏感内容的推文，但如果设置了 [`TWITTER_AUTH_TOKEN`](#twitter_auth_token)，则可以通过 Web API 获取。

当 Web API 不可用时，你可以选择切换到 Syndication API。

_在 v2.4.0 中添加_

### TWITTER_AUTH_TOKEN

:material-lightbulb-on: 可选，获取敏感内容推文时必需

Web API 的授权令牌。

请按照以下步骤获取：

1. 在浏览器中打开 <https://twitter.com/>
2. 打开开发者工具（<kbd>F12</kbd>）
3. 切换到 应用（`Application`）标签页
4. 在侧边栏中展开 `Cookie` 部分并点击 `https://twitter.com`
5. 复制 `auth_token` Cookie 的值

_在 v2.4.0 中添加_

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### TWITTER_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Twitter`

存储路径。

### TWITTER_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{id_str}_{index} - {user[name]}({user[id_str]})`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "lang": "推文语言，例如ja",
  "favorite_count": 4814,
  "possibly_sensitive": false,
  "created_at": "创建日期",
  "id_str": "推文ID",
  "user": {
    "id_str": "用户ID",
    "name": "用户名称",
    "screen_name": "用户handle"
  },
  "photos": [
    {
      "width": "宽度",
      "height": "高度"
    }
  ],
  "filename": "twimg.com URL中的原始文件名称，不含扩展名",
  "index": "图片或视频索引"
}
```
