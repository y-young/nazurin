# ArtStation

<https://www.artstation.com/>

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### ARTSTATION_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Artstation`

Storage path for downloaded artworks.

### ARTSTATION_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{title} ({hash_id}) - {filename}`

File name for downloaded artworks.

### Available Variables

_Only common used ones are listed._

```json
{
  "tags": ["Tag"],
  "assets": [
    {
      "id": "Image ID",
      "title": "Title",
      "width": 3840,
      "height": 2160,
      "position": "Image position"
    }
  ],
  "asset": "Current image asset",
  "user": {
    "id": "User ID",
    "username": "Username",
    "headline": "Headline",
    "full_name": "Full name"
  },
  "medium": {
    "name": "Medium name, e.g. Digital 2D",
    "id": "Medium ID"
  },
  "categories": [
    {
      "name": "Category name",
      "id": "Category ID"
    }
  ],
  "id": "Artwork ID",
  "user_id": "User ID",
  "title": "Title",
  "created_at": "Created at",
  "updated_at": "Updated at",
  "views_count": 0,
  "likes_count": 0,
  "comments_count": 0,
  "editor_pick": false,
  "adult_content": false,
  "slug": "URL slug name",
  "hash_id": "URL hash ID",
  "index": "Current image index",
  "filename": "Original filename"
}
```
