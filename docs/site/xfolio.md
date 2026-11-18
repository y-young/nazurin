# Xfolio

<https://xfolio.jp/>

## Configuration

### XFOLIO_SESSION

:material-lightbulb-on: Optional

Value of the `xfolio_session` cookie from a logged-in browser session (valid for 30 days on a rolling basis).

- **Without `XFOLIO_SESSION`**: Works out-of-the-box for public portfolios using the public display images (`assets.xfolio.jp`, WebP up to 1200px height).
- **With `XFOLIO_SESSION`**:
  - Unlocks full-scale original images (`user_asset.php` via `fullscale_image`, automatically detecting original PNG/JPEG/WebP format) with automatic fallback to `assets.xfolio.jp` when full-scale viewing is disabled by the creator.
  - Accesses portfolios that have bot protection (`reCAPTCHA`) enabled for logged-out visitors.
  - Enables automatic bookmarking (favoriting) and liking when collecting works.

### XFOLIO_BOOKMARK

:material-lightbulb-on: Optional, defaults to `True`

Whether to automatically bookmark (add to favorites) the work when `XFOLIO_SESSION` is configured.

### XFOLIO_LIKE

:material-lightbulb-on: Optional, defaults to `True`

Whether to automatically like the work when `XFOLIO_SESSION` is configured.

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### XFOLIO_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Xfolio`

Storage path for downloaded images.

### XFOLIO_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{id}_{index} - {title} - {user[name]}({user[code]})`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "id": "Work ID",
  "title": "Work title",
  "description": "Work description",
  "url": "Canonical work URL",
  "user": {
    "id": "Creator ID",
    "user_id": "User ID",
    "code": "Creator portfolio code",
    "name": "Creator display name",
    "profile": "Creator profile description",
    "url": "Creator portfolio URL"
  },
  "tags": ["Tag 1", "Tag 2"],
  "series": {
    "id": "Series ID",
    "title": "Series title",
    "url": "Series URL"
  },
  "likes_num": "Number of likes",
  "favorites_num": "Number of favorites",
  "filename": "Original file name, without extension",
  "image_id": "Full-scale image ID (if available when logged in)",
  "index": "Image index",
  "extension": "Extension, with leading dot"
}
```
