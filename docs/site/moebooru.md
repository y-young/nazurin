# Moebooru

<https://yande.re/>

<https://konachan.com/>

<https://lolibooru.moe/>

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### MOEBOORU_FILE_PATH

:material-lightbulb-on: Optional, defaults to `{site_name}`

Storage path for downloaded images.

### MOEBOORU_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{filename}`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "id": "ID",
  "created_at": "Created at",
  "creator_id": "Creator ID",
  "author": "Uploader",
  "score": 133,
  "md5": "MD5",
  "file_size": "File size",
  "jpeg_width": 2048,
  "jpeg_height": 1520,
  "jpeg_file_size": "JPEG file size",
  "rating": "s",
  "has_children": false,
  "parent_id": null,
  "status": "active",
  "width": 2048,
  "height": 1520,
  "filename": "Original filename, without extension. Format may differ from site to site",
  "site_name": "Site name, e.g. Yandere",
  "site_url": "Site URL, e.g. yande.re"
}
```
