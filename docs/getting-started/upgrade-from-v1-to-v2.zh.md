# 从 v1 升级到 v2

## 新功能

### 忽略图片说明中的条目

可设置在生成图片说明时要忽略的条目。

用法：

: 在环境变量中设置 `CAPTION_IGNORE`，例如 `CAPTION_IGNORE = bookmarked`。

默认为空。

### 使机器人完全公开

通过设置 `IS_PUBLIC = true` 与任何人共享你的机器人，默认为 `false`。

### API 服务器搭配 Nazurin 扩展程序

Nazurin 现已内置一个 API 服务器，搭配 [Nazurin 扩展程序](https://github.com/y-young/nazurin-extension) 使用可极大提升你的桌面端使用体验。

### Ugoira 支持

若想在 Telegram 中支持 Pixiv ugoira GIF 预览（以 MP4 发送），你需要安装 **ffmpeg**。

更多信息请参考 <https://ffmpeg.org/>，确保 libx264 编码器已经安装。

如果使用 Heroku，你需要为应用程序添加一个 Buildpack：

`heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`

如果使用 Docker 镜像，ffmpeg 已经包含在内。

### Docker 部署

你现在可以使用 docker-compose 部署 Nazurin：`docker-compose up -d --build`。

## 变更

### 授权

- 添加 `ALLOW_ID` 以替换 `ADMIN_ID`

  : 你希望与其分享的用户 ID，以英文逗号分隔。

  : 例如：`ALLOW_ID = 12345,23456,34567`

  : 默认为空。

- 添加 `ADMIN_USERNAME` 以替换 `ALLOW_USERNAME`

  : 你希望与其分享的用户的用户名，不含 `@`，以英文逗号分隔。

  : 例如：`ALLOW_USERNAME = user1,user2,user3`

  : 默认为空。

- 添加 `ALLOW_GROUP` 以替换 `GROUP_ID`

  : 群组 ID 列表，以英文逗号分隔，其中的成员均可使用此机器人。

  : 例如：`ALLOW_GROUP = -12345,-23456`

- `ADMIN_ID`

  : 你仍然需要 `ADMIN_ID` 来接收错误报告和使用受限命令。

- 用户 ID 和用户名可同时使用

  : 虽然 v1 只支持用户 ID 和用户名其中之一，在 v2 中你可以同时使用。

### 存储

- 可配置选项 `STORAGE` 变更为以逗号（`,`）分隔的字符串

  : 例如：

      ```shell
      # v1
      STORAGE = ['Mega', 'GoogleDrive']

      # v2
      STORAGE = Mega,GoogleDrive
      ```

- 使用 `DOWNLOAD_DIR` 的本地存储现已成为独立的存储类型

  : 若要使用本地存储，在 `STORAGE` 中追加 `Local`，例如：`STORAGE = Local,Mega`

- Telegram 相册频道现已成为一种存储类型

  : 除了设定 `ALBUM_ID` 之外，还需要在 `STORAGE` 中追加 `Telegram`，例如：

      ```shell
      ALBUM_ID = -100123456
      STORAGE = Telegram,Mega
      ```

- 本地数据目录变更

  : 本地数据，包括收藏的图片（`STORAGE_DIR`）和临时文件（`TEMP_DIR`）已移动至应用根目录下的 `data` 目录。

  : 请在应用目录中创建一个名为 `data` 的新目录，并将 `STORAGE_DIR`（默认为 `Picutres`）和 `TEMP_DIR`（默认为 `temp`）移动至该目录。

## 改进

- 改进目录结构
- 切换到 asyncio 以获得更好的性能
- 触发频率限制时自动重试
- 更多的网络请求重试
