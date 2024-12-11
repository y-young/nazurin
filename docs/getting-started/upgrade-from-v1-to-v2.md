# Upgrade from v1 to v2

## Features

### Ignore items in image caption

You can set the bot to omit some fields when generating image captions.

Usage:

: Set `CAPTION_IGNORE` in environment variables, e.g.: `CAPTION_IGNORE = bookmarked`.

Default is none.

### Make the bot completely public

Set `IS_PUBLIC = true` to share your bot with everyone, default to `false`.

### API Server with Nazurin Extension

Nazurin now comes with a built-in API server, pairing with [Nazurin Extension](https://github.com/y-young/nazurin-extension), your desktop experience will be greatly improved.

### Docker Deployment

You can now deploy Nazurin with docker-compose using `docker-compose up -d --build`.

### Ugoira support

To support Pixiv ugoira GIF preview (sent as MP4) in Telegram, you should have **ffmpeg** installed.

For more information, refer to <https://ffmpeg.org/>, make sure libx264 encoder is installed.

On Heroku, add a buildpack to your application:

`heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`

If you're using the Docker image, ffmpeg is already included.

## Changes

### Authorization

- Add `ALLOW_ID` to replace `ADMIN_ID`

  : Set IDs of users with whom you want to share, separated by commas.

  : e.g.: `ALLOW_ID = 12345,23456,34567`

  : Default is none.

- Add `ADMIN_USERNAME` to replace `ALLOW_USERNAME`

  : Set usernames of users with whom you want to share, without `@`, separated by commas.

  : e.g.: `ALLOW_USERNAME = user1,user2,user3`

  : Default is none.

- `GROUP_ID` is renamed to `ALLOW_GROUP`

  : Set IDs of groups in which all members have access to this bot, separated by commas.

  : e.g.: `ALLOW_GROUP = -12345,-23456`

- `ADMIN_ID`

  : You still need `ADMIN_ID` in order to receive error reports and have access to some restricted commands.

- User IDs & usernames both works now

  : While v1 supports either user ID or username, you may use both in v2.

### Storage

- Configurable option `STORAGE` is now a string seperated by commas(`,`).

  : e.g.:

      ```shell
      # v1
      STORAGE = ['Mega', 'GoogleDrive']

      # v2
      STORAGE = Mega,GoogleDrive
      ```

- Local storage using `DOWNLOAD_DIR` is now an independent storage

  : To use local storage, append `Local` to `STORAGE`, e.g.: `STORAGE = Local,Mega`

- Telegram album channel is now a type of storage

  : Besides setting `ALBUM_ID`, append `Telegram` to `STORAGE`, e.g.:

      ```shell
      ALBUM_ID = -100123456
      STORAGE = Telegram,Mega
      ```

- Local storage destination changed

  : Local data including collection (`STORAGE_DIR`) and temporary files (`TEMP_DIR`) are moved to `data` folder at application root.

  : Please create a folder named `data` in the main folder, and move `STORAGE_DIR` (Default is `Picutres`), `TEMP_DIR` (Default is `temp`) into the folder.

## Enhancement

- Enhanced folder structure
- Switch to asyncio for better performance
- Retry when hitting flooding limits
- Retry for more network requests
