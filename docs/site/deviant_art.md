# DeviantArt

<https://www.deviantart.com/ >

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### DEVIANT_ART_FILE_PATH

:material-lightbulb-on: Optional, defaults to `DeviantArt`

Storage path for downloaded images.

### DEVIANT_ART_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{title} - {deviationId}`

File name for downloaded images.

### DEVIANT_ART_DOWNLOAD_NAME

:material-lightbulb-on: Optional, defaults to `{title} - {deviationId} - {prettyName}`

Name for download files.

### Available Variables

_Only common used ones are listed._

```json
{
  "deviationId": "Deviation ID",
  "type": "image",
  "typeId": 1,
  "title": "Title",
  "publishedTime": "Published time",
  "author": {
    "userId": "User ID",
    "useridUuid": "User UUID",
    "username": "Username"
  },
  "stats": {
    "comments": 51,
    "favourites": 202,
    "views": 1058,
    "downloads": 0
  },
  "media": {
    "prettyName": "Human-friendly file name"
  },
  "extended": {
    "deviationUuid": "Deviation UUID",
    "originalFile": {
      "type": "original",
      "width": "Width",
      "height": "Height",
      "filesize": "File size"
    }
  },
  "filename": "Default filename (UUID), without extension"
}
```
