# Pixiv

<https://www.pixiv.net/>

## Configuration

!!! warning "Notice"

    Pixiv no longer supports username & password authorization from Feb 9, 2021. You'll have to obtain a refresh token in advance. (see [#9](https://github.com/y-young/nazurin/issues/9))

!!! warning "Notice"

    Since Pixiv access token and refresh token are cached in database, after switching account, you'll need to delete `pixiv` document in `nazurin` collection from the database.

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

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### PIXIV_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Pixiv`

Storage path for downloaded artworks.

### PIXIV_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{filename} - {title} - {user[name]}({user[id]})`

File name for downloaded artworks.

### Available Variables

_Only common used ones are listed._

```json
{
  "create_date": "Creation date",
  "series": "Series",
  "page_count": "Total image count",
  "height": "Height of first image",
  "total_view": "Total view count",
  "id": "Artwork ID",
  "title": "Artwork title",
  "width": "Width of first image",
  "type": "Artwork type, e.g. illust, manga",
  "tags": [
    {
      "name": "Tag name",
      "translated_name": "Translated tag name"
    }
  ],
  "user": {
    "account": "Illustrator username",
    "id": "Illustrator user ID",
    "name": "Illustrator name"
  },
  "total_bookmarks": "Total bookmark count",
  "filename": "Original filename without extension, e.g. 12345_p0",
  "page": "Single image position among all images, starting from 0"
}
```

## Ugoira support

To support Pixiv ugoira GIF preview (sent as MP4) in Telegram, you should have **ffmpeg** installed (already included in Docker image).

For more information, refer to <https://ffmpeg.org/>, make sure libx264 encoder is installed.

On Heroku, add a buildpack to your application:

`heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`
