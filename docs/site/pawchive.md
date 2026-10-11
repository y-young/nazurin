# Pawchive

<https://pawchive.pw/>, <https://pawchive.st/>

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### PAWCHIVE_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Pawchive/{service}/{username} ({user})/{title} ({id})`

Storage path for downloaded images.

### PAWCHIVE_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{pretty_name}`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "id": "Post ID on the original platform, e.g. fanbox",
  "user": "User ID on the original platform, e.g. fanbox",
  "title": "",
  "added": "Time added on Pawchive",
  "published": "Published time on original platform",
  "edited": "Time edited on Pawchive, might be null",
  "filename": "Default filename provided by Pawchive, without extension",
  "pretty_name": "Filename provided by author, with extension. If not provided, fallback to a UUID filename from Pawchive"
}
```
