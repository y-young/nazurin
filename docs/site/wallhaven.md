# Wallhaven

<https://wallhaven.cc/>

## Configuration

### WALLHAVEN_API_KEY

:material-lightbulb-on: Optional, required to view NSFW wallpapers according to [API Documentation](https://wallhaven.cc/help/api#wallpapers)

Wallhaven API key, can be found in [Account settings](https://wallhaven.cc/settings/account).

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### WALLHAVEN_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Wallhaven`

Storage path for downloaded wallpapers.

### WALLHAVEN_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{id}`

File name for downloaded wallpapers.

### Available Variables

_Only common used ones are listed._

```json
{
  "id": "Wallpaper ID",
  "uploader": {
    "username": "Uploader username",
    "group": "Uploader group, e.g. User"
  },
  "views": "View count",
  "favorites": "Favorite count",
  "purity": "Purity, e.g. sfw",
  "category": "Category, e.g. anime",
  "dimension_x": "Width",
  "dimension_y": "Height",
  "resolution": "Resolution, e.g. 1920x1080",
  "ratio": "Aspect ratio",
  "file_size": "File size in bytes",
  "file_type": "File type, e.g. image/png",
  "created_at": "Creation date",
  "colors": ["Color palettes"],
  "tags": [
    {
      "id": "Tag ID",
      "name": "Tag name",
      "alias": "Tag alias",
      "category_id": "Tag category ID",
      "category": "Tag category",
      "purity": "Tag purity, e.g. sfw"
    }
  ]
}
```
