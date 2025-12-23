# Gelbooru

<https://gelbooru.com/>

## Configuration

### Authentication

To mitigate abusive behavior, Gelbooru occasionally requires authentication to access the API and throttle access to the API, see [Gelbooru API Documentation](https://gelbooru.com/index.php?page=wiki&s=view&id=18780).

To obtain the API key and User ID, create an account on Gelbooru and find the API access credentials in [account settings](https://gelbooru.com/index.php?page=account&s=options).

#### GELBOORU_API_KEY

:material-lightbulb-on: Optional

API key for Gelbooru.

#### GELBOORU_USER_ID

:material-lightbulb-on: Optional

User ID for Gelbooru.

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### GELBOORU_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Gelbooru`

Storage path for downloaded images.

### GELBOORU_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{id}`

File name for downloaded images.

### Available Variables

_Only common used ones are listed._

```json
{
  "id": "ID",
  "created_at": "Creation date",
  "score": 3,
  "width": 900,
  "height": 1800,
  "md5": "MD5",
  "rating": "general",
  "owner": "danbooru",
  "creator_id": "Creator ID",
  "parent_id": 0,
  "title": ""
}
```
