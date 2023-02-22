# Twitter

<https://twitter.com/>

## Customizing Storage Path & File Name

For more information, refer to [Customizing Storage Path & File Name](../#customizing-storage-path--file-name).

### TWITTER_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Twitter`

Storage path for downloaded images or videos.

### TWITTER_FILE_NAME

:material-lightbulb-on: Optional, defaults to `{id_str}_{index} - {user[name]}({user[id_str]})`

File name for downloaded images or videos.

### Available Variables

_Only common used ones are listed._

```json
{
  "lang": "Tweet language, e.g. ja",
  "favorite_count": 4814,
  "possibly_sensitive": false,
  "created_at": "Creation date",
  "id_str": "Tweet ID",
  "user": {
    "id_str": "User ID",
    "name": "User name",
    "screen_name": "User handle"
  },
  "photos": [
    {
      "width": "Width",
      "height": "Height"
    }
  ],
  "filename": "Original filename in twimg.com URL, without extension",
  "index": "Photo or video index in a tweet"
}
```
