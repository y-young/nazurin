# Configuration

To configure options, you have the following ways:

- Directly set envrionment variables
- Use `.env.example` as a template, modify the values and rename it to `.env`

## ENV

:material-lightbulb-on: Optional, defaults to `production`

The default option (`production`) uses Webhook mode, you can set to `development` to use polling mode.

## TOKEN

:material-exclamation-thick: Required

API token of your bot, can be obtained from [@BotFather](https://t.me/BotFather).

## WEBHOOK_URL

:material-exclamation-thick: Required if using webhook mode

Webhook URL to be set for Telegram server, the bot server should be accessible on this URL, should end with `/`, e.g. `https://xxx.fly.dev/`.

## HOST

:material-exclamation-thick: Required if using webhook mode

The host to bind to, defaults to `0.0.0.0`. Set to `127.0.0.1` if you are using a reverse proxy.

If you are using Docker, configure [container networking](https://docs.docker.com/config/containers/container-networking/#published-ports) instead.

## PORT

:material-exclamation-thick: Required if using webhook mode

Webhook port, automatically set if on Heroku.

If you are using Docker, configure [container networking](https://docs.docker.com/config/containers/container-networking/#published-ports) instead.

## DATABASE

:material-exclamation-thick: Required, defaults to `Local`

Type of database, e.g. `Mongo`.

Supported databases:

--8<-- "docs/includes/database.md"

You can also implement your own database driver by creating a file under `database` folder, and set this option to the name of driver class.

## STORAGE

:material-exclamation-thick: Required, defaults to `Local`

List of storage types, separated by commas, e.g. `Local,OneDrive`.

Supported storage:

--8<-- "docs/includes/storage.md"

Implement other storage by creating a file under `storage` folder with a `store` method.

_Changed in v2._

## STORAGE_DIR

:material-lightbulb-on: Optional, defaults to `Pictures`

Directory path in local storage or remote, will be created if not exists.

## GALLERY_ID

:material-lightbulb-on: Optional

Telegram channel ID used for storing _messages_, messages containing links sent to bot will be forwarded here for reviewing.

!!! tip

    You need to add your bot to channel administrators.

## ADMIN_ID

:material-exclamation-thick: Required

Telegram user ID (_not_ username) of the admin user, some bot functions are restricted to the admin user.

## IS_PUBLIC

:material-lightbulb-on: Optional, defaults to `false`

Whether to make this bot public, when set to `true`, everyone can use the bot.

_Added in v2._

## ALLOW_ID

:material-lightbulb-on: Optional

!!! warning "Attention"

    When `IS_PUBLIC` is `true`, this option will be ignored.

Telegram ID (_not_ username) of the users allowed to use this bot, separated by commas.

e.g.:

```bash
export ALLOW_ID=111111 # single user
export ALLOW_ID=111111,222222,333333 # multiple users
```

!!! tip

    You can get your User ID & Channel ID via [@GetIDs Bot](https://t.me/getidsbot/).

_Changed in v2._

## ALLOW_USERNAME

:material-lightbulb-on: Optional

!!! warning "Attention"

    When `IS_PUBLIC` is `true`, this option will be ignored.

Telegram username of the users allowed to use this bot, separated by commas.

_Changed in v2._

## ALLOW_GROUP

:material-lightbulb-on: Optional

!!! warning "Attention"

    When `IS_PUBLIC` is `true`, this option will be ignored.

Telegram group ID, separated by commas. Users in these groups will be able to use the bot **in group chat**.

_Changed in v2._

!!! abstract "About access control"

    1. Allow all if `IS_PUBLIC=true`
    2. User in `ALLOW_ID` or `ALLOW_USERNAME` or `ADMIN_ID` can access the bot via private chat
    3. User in `ALLOW_GROUP` can access via specified group chat

    For more information, see [`nazurin/middleware.py`](https://github.com/y-young/nazurin/blob/master/nazurin/middleware.py).

## RETRIES

:material-lightbulb-on: Optional, defaults to `5`

Number of attempts to retry on network related operations.

_Added in v2._

## TIMEOUT

:material-lightbulb-on: Optional, defaults to `20`

Request timeout in seconds.

## DOWNLOAD_CHUNK_SIZE

:material-lightbulb-on: Optional, defaults to `4096`

Chunk size when writing downloaded files, in bytes.

_Added in v2.6.0._

## MAX_PARALLEL_DOWNLOAD

:material-lightbulb-on: Optional, defaults to `5`

Maximum number of parallel downloads.

_Added in v2.7.0._

## MAX_PARALLEL_UPLOAD

:material-lightbulb-on: Optional, defaults to `5`

Maximum number of parallel uploads.

_Added in v2.7.0._

## HTTP_PROXY

:material-lightbulb-on: Optional, defaults to your environment

Proxy URL for network requests, e.g. `http://127.0.0.1:7890`, will follow your environment.

## CAPTION_IGNORE

:material-lightbulb-on: Optional, defaults to none

Items to ignore in image caption, separated by commas, e.g. `bookmarked`.

_Added in v2._

## CLEANUP_INTERVAL

:material-lightbulb-on: Optional, defaults to `7`

Temporary directory cleanup interval, in days. Files whose access time is older than 1 day will be deleted during cleanup. Automatic cleanup will be disabled if set to `0`.

_Added in v2.4.1._
