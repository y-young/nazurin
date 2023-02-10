# Pixiv

<https://www.pixiv.net/>

## Configuration

!!! warning "Notice"

    Pixiv no longer supports username & password authorization from Feb 9, 2021. You'll have to obtain a refresh token in advance. (see [#9](https://github.com/y-young/nazurin/issues/9))

### PIXIV_TOKEN

:material-exclamation-thick: Required unless Nazurin has cached one in your database

Your **refresh** token, you may use this [tool](https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde) to get one.

### PIXIV_MIRROR

:material-lightbulb-on: Optional, defaults to `i.pximg.net`, i.e. official image server

Image proxy when **viewing** artworks, introduced to help Telegram server get the image stably, **downloading** artworks still uses Pixiv server.

Will replace `i.pximg.net` in returned image URL.

e.g.: `i.pixiv.cat`

### PIXIV_TRANSLATION

:material-lightbulb-on: Optional

Language for possible tag translation, if translated name is unavailable, original name is used.

Use original name if not set, configured value will be set as `Accept-Language` in headers.

Example: `zh-CN`, `en-US`

### PIXIV_BOOKMARK_PRIVACY

:material-lightbulb-on: Optional, defaults to `public`

Bookmark visibility, `public` or `private`.

## Ugoira support

To support Pixiv ugoira GIF preview (sent as MP4) in Telegram, you should have **ffmpeg** installed (already included in Docker image).

For more information, refer to <https://ffmpeg.org/>, make sure libx264 encoder is installed.

On Heroku, add a buildpack to your application:

`heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`
