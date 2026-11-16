# Danbooru

<https://danbooru.donmai.us/>

## User-Agent

### DANBOORU_USER_ID

:material-lightbulb-on: Optional integer, unset by default

Your Danbooru user ID, included in the User-Agent for API requests and file downloads.
Find it in your profile URL: for `https://danbooru.donmai.us/users/12345`, the ID is `12345`.

An IP address with a bad reputation, combined with a missing user ID in the User-Agent,
may result in a Cloudflare ban. See the [Danbooru API wiki](https://danbooru.donmai.us/wiki_pages/help:api)
for User-Agent guidance.

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### DANBOORU_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Danbooru`

Storage path for downloaded images.

### DANBOORU_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{id} - {filename}`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "id": "ID",
  "created_at": "Created at",
  "uploader_id": "Uploader ID",
  "score": 10,
  "md5": "MD5",
  "rating": "s",
  "image_width": "Image width",
  "image_height": "Image height",
  "fav_count": 10,
  "file_ext": "png",
  "parent_id": null,
  "has_children": false,
  "approver_id": "Approver ID",
  "tag_count_general": 1,
  "tag_count_artist": 1,
  "tag_count_character": 1,
  "tag_count_copyright": 1,
  "file_size": "File size",
  "up_score": 10,
  "down_score": 0,
  "tag_count": 5,
  "updated_at": "Uploaded at",
  "pixiv_id": "Pixiv ID, may be null",
  "tag_count_meta": 1,
  "tag_string_character": "",
  "tag_string_copyright": "",
  "tag_string_artist": "",
  "tag_string_meta": "",
  "filename": "Human-friendly file name like that when downloading on website, consists of tags, without extension"
}
```
