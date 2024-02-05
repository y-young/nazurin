# Pixiv

<https://www.pixiv.net/>

## 配置

!!! warning "注意"

    从 2021 年 2 月 9 日起，Pixiv 不再支持用户名密码认证。你需要提前获取一个 Refresh Token。（详见 [#9](https://github.com/y-young/nazurin/issues/9)）

!!! warning "注意"

    由于 Pixiv 的 Access Token 和 Refresh Token 被缓存在数据库中，切换账号后，你需要从数据库中删除 `nazurin` 集合中的 `pixiv` 文档。

### PIXIV_TOKEN

:material-exclamation-thick: 必填，除非在数据库中已有缓存

你的 **Refresh** Token，可使用 [此工具](https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde) 获取。

### PIXIV_MIRROR

:material-lightbulb-on: 可选，默认为 `i.pximg.net`，即官方图片服务器

**浏览**作品时的图片代理，用于帮助 Telegram 服务器更稳定地获取图片，**下载**作品时仍然会使用 Pixiv 服务器。

返回图片地址时将使用配置值替换 URL 中的 `i.pximg.net`。

例如：`i.pixiv.cat`

### PIXIV_TRANSLATION

:material-lightbulb-on: 可选

标签的显示语言，如果没有可用翻译则使用日语原文。

默认使用原文，配置值将设置在 HTTP Header 的 `Accept-Language` 选项中。

例如：`zh-CN`, `en-US`

### PIXIV_BOOKMARK_PRIVACY

:material-lightbulb-on: 可选，默认为 `public`

收藏可见性，`public` 或 `private`。

## 自定义存储路径和文件名

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### PIXIV_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Pixiv`

存储路径。

### PIXIV_FILE_NAME

:material-lightbulb-on: 可选，默认为 `{filename} - {title} - {user[name]}({user[id]})`

文件名称。

### 可用变量

_此处只列出常用项。_

```json
{
  "create_date": "创建日期",
  "series": "系列名称",
  "page_count": "图片总数",
  "height": "第一张图片的高度",
  "total_view": "总浏览量",
  "id": "作品ID",
  "title": "作品标题",
  "width": "第一张图片的宽度高度",
  "type": "作品类型，例如illust、manga",
  "tags": [
    {
      "name": "标签名",
      "translated_name": "标签名翻译"
    }
  ],
  "user": {
    "account": "画师用户名",
    "id": "画师用户ID",
    "name": "画师名称"
  },
  "total_bookmarks": "收藏总数",
  "filename": "原始文件名称，不含扩展名，如12345_p0",
  "page": "单张图片在所有图片中的顺序，从零开始"
}
```

## Ugoira（动图）支持

若想在 Telegram 中支持 Pixiv ugoira GIF 预览（以 MP4 发送），你需要安装 ffmpeg（已包含在 Docker 镜像中）。

更多信息请参考 <https://ffmpeg.org/>，确保 libx264 编码器已经安装。

如果使用 Heroku，你需要为应用程序添加一个 Buildpack：

`heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`
