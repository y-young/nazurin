# Misskey Notes

From any Misskey instance.

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### MISSKEY_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Misskey`

Storage path for downloaded images.

### MISSKEY_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{id} - {filename} - {user[name]}({user[username]})`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "id": "<note id>",
  "createdAt": "2023-10-05T23:10:13.016Z",
  "userId": "<user id>",
  "user": {
    "id": "<user id>",
    "name": "<user display name>",
    "username": "<username>",
    "host": "<instance URL>"
  },
  "text": "<note texts>",
  "fileIds": ["<file id>"],
  "files": [
    {
      "id": "<file id>",
      "createdAt": "2023-10-05T23:10:16.445Z",
      "name": "<file name>",
      "type": "image/webp",
      "md5": "<file md5>",
      "size": 800000,
      "isSensitive": false,
      "properties": {
        "width": 2048,
        "height": 1969
      },
      "url": "<file URL>",
      "thumbnailUrl": "<thumbnail URL>"
    }
  ],
  "uri": "<URL from the original instance of this note>" // Only available when the note is from a remote instance.
}
```
