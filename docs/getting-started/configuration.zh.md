# 配置

Nazurin 有以下两种配置方式可选：

- 直接设置环境变量
- 以 `.env.example` 为模板，修改后重命名为 `.env`

## ENV

:material-lightbulb-on: 可选，默认为 `production`

默认选项（`production`）使用 Webhook 模式，你可以设置为 `development` 以使用轮询模式。

## TOKEN

:material-exclamation-thick: 必需

机器人的 API 密钥，可从 [@BotFather](https://t.me/BotFather) 获取。

## WEBHOOK_URL

:material-exclamation-thick: 如使用 Webhook 模式则必需

发送到 Telegram 服务器的 Webhook URL，机器人的服务器应能通过此 URL 访问，应以 `/` 结尾，例如 `https://xxx.fly.dev/`。

## HOST

:material-exclamation-thick: 如使用 Webhook 模式则必需

要绑定到的主机地址，默认为 `0.0.0.0`。使用反向代理时请设置为 `127.0.0.1`。

如在 Docker 容器中部署，建议使用 [容器网络](https://docs.docker.com/config/containers/container-networking/#published-ports)。

## PORT

:material-exclamation-thick: 如使用 Webhook 模式则必需

Webhook 端口，使用 Heroku 时自动设定。

如在 Docker 容器中部署，建议使用 [容器网络](https://docs.docker.com/config/containers/container-networking/#published-ports)。

## DATABASE

:material-exclamation-thick: 必需，默认为 `Local`

数据库类型，例如 `Mongo`。

支持的数据库：

--8<-- "docs/includes/database.zh.md"

你也可以实现你自己的数据库驱动，只需在 `database` 文件夹下创建一个文件，并将此选项设置为驱动的类名。

## STORAGE

:material-exclamation-thick: 必需，默认为 `Local`

存储类型列表，以英文逗号分隔，例如 `Local,OneDrive`。

支持的存储：

--8<-- "docs/includes/storage.zh.md"

可通过在 `storage` 文件夹下创建文件并编写 `store` 方法来实现其他的存储类型。

_在 v2 中变更。_

## STORAGE_DIR

:material-lightbulb-on: 可选，默认为 `Pictures`

本地或远程存储的目录路径，如不存在则自动创建。

## GALLERY_ID

:material-lightbulb-on: 可选

用于存储**信息**的 Telegram 频道 ID，含有链接的信息将被转发到此处以便之后查阅。

!!! tip "提示"

    你需要将机器人设置为频道管理员。

## ADMIN_ID

:material-exclamation-thick: 必需

管理员用户的 Telegram 用户 ID（**不是**用户名），机器人的一些功能仅限管理员用户使用。

## IS_PUBLIC

:material-lightbulb-on: 可选，默认为 `false`

是否将机器人公开，如果设置为 `true`，则任何人都可使用此机器人。

_在 v2 中新增。_

## ALLOW_ID

:material-lightbulb-on: 可选

!!! warning "注意"

    当 `IS_PUBLIC` 设置为 `true` 时，此选项无效。

允许使用此机器人的 Telegram 用户 ID（_不是_ 用户名），以英文逗号分隔。

例如：

```bash
export ALLOW_ID=111111 # 单一用户
export ALLOW_ID=111111,222222,333333 # 多个用户
```

!!! tip "提示"

    可使用 [@GetIDs Bot](https://t.me/getidsbot/) 获取用户 ID 和频道 ID。

_在 v2 中变更。_

## ALLOW_USERNAME

:material-lightbulb-on: 可选

!!! warning "注意"

    当 `IS_PUBLIC` 设置为 `true` 时，此选项无效。

允许使用此机器人的 Telegram 用户的用户名，以英文逗号分隔。

_在 v2 中变更。_

## ALLOW_GROUP

:material-lightbulb-on: 可选

!!! warning "注意"

    当 `IS_PUBLIC` 设置为 `true` 时，此选项无效。

Telegram 群组 ID，以英文逗号分隔。这些群组中的用户能够在**群聊中**使用机器人。

_在 v2 中变更。_

!!! abstract "关于权限控制"

    1. 如果 `IS_PUBLIC=true`，允许所有访问
    2. `ALLOW_ID`、`ALLOW_USERNAME` 和 `ADMIN_ID` 中的用户可以在私聊中使用机器人
    3. `ALLOW_GROUP` 中的用户可以在指定的群聊中使用机器人

    更多信息请查看 [`nazurin/middleware.py`](https://github.com/y-young/nazurin/blob/master/nazurin/middleware.py)。

## RETRIES

:material-lightbulb-on: 可选，默认为 `5`

网络请求的重试次数。

_在 v2 中新增。_

## TIMEOUT

:material-lightbulb-on: 可选，默认为 `20`

请求超时时间，以秒为单位。

## DOWNLOAD_CHUNK_SIZE

:material-lightbulb-on: 可选，默认为 `4096`

写入下载文件时的块大小，以字节为单位。

_在 v2.6.0 中新增。_

## MAX_PARALLEL_DOWNLOAD

:material-lightbulb-on: 可选，默认为 `5`

同时下载的最大文件数。

_在 v2.7.0 中新增。_

## MAX_PARALLEL_UPLOAD

:material-lightbulb-on: 可选，默认为 `5`

同时上传的最大文件数。

_在 v2.7.0 中新增。_

## HTTP_PROXY

:material-lightbulb-on: 可选，默认遵循环境变量

网络请求的代理 URL，例如 `http://127.0.0.1:7890`，将遵循你的环境变量设置。

## CAPTION_IGNORE

:material-lightbulb-on: 可选，默认为空

图片说明中要忽略的条目，以英文逗号分隔，如 `bookmarked`。

_在 v2 中新增。_

## CLEANUP_INTERVAL

:material-lightbulb-on: 可选，默认为 `7`

临时目录清理的间隔时间，单位为天。每次清理时将删除访问时间在一天前的文件。设置为 `0` 时将禁用自动清理。

_在 v2.4.1 中新增。_
