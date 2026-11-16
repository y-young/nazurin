# Kemono.party

<https://kemono.party/>, <https://kemono.su/>

<https://pawchive.pw/>, <https://pawchive.st/>

!!! note "Notice"

    Some posts are incompletely archived, i.e. the original files are not available while previews are. For these posts, images are downloaded from the preview thumbnails, and non-image files are skipped.

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### KEMONO_FILE_PATH

:material-lightbulb-on: Optional, defaults to `{site_name}/{service}/{username} ({user})/{title} ({id})`

Storage path for downloaded images.

### KEMONO_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{pretty_name}`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "id": "Post ID on the original platform, e.g. fanbox",
  "user": "User ID on the original platform, e.g. fanbox",
  "title": "",
  "added": "Time added on Kemono/Pawchive",
  "published": "Published time on original platform",
  "edited": "Time edited on Kemono/Pawchive, might be null",
  "filename": "Default filename provided by the website, without extension",
  "pretty_name": "Filename provided by author, with extension. If not provided, fallback to a UUID filename from the website",
  "site_name": "Site name, e.g. Kemono, Pawchive",
  "site": "Site identifier, e.g. kemono, pawchive"
}
```
