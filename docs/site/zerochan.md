# Zerochan

<https://www.zerochan.net/>

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### ZEROCHAN_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Zerochan`

Storage path for downloaded images.

### ZEROCHAN_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{id} - {name}`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "id": "ID",
  "name": "Post name",
  "created_at": "Creation date",
  "image_width": "2480",
  "image_height": "1500",
  "file_ext": "png",
  "file_size": "File size",
  "uploader": "Uploader",
  "filename": "Original filename, without extension"
}
```
