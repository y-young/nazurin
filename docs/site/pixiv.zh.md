# Pixiv

<https://www.pixiv.net/>

## 配置

!!! warning "注意"

    从 2021 年 2 月 9 日起，Pixiv 不再支持用户名密码认证。你需要提前获取一个 Refresh Token。（详见 [#9](https://github.com/y-young/nazurin/issues/9)）

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

## Ugoira（动图）支持

若想在 Telegram 中支持 Pixiv ugoira GIF 预览（以 MP4 发送），你需要安装 ffmpeg（已包含在 Docker 镜像中）。

更多信息请参考 <https://ffmpeg.org/>，确保 libx264 编码器已经安装。

如果使用 Heroku，你需要为应用程序添加一个 Buildpack：

`heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`
