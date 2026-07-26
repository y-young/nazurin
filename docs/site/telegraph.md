# Telegraph

<https://telegra.ph/>, <https://graph.org/>

Nazurin archives Telegraph pages through the official `getPage/<path>` API with `return_content=true`. Browser automation is not required.

Each page is stored as a directory containing the original API response, an offline HTML article, and downloaded images:

```text
Telegraph/
└── <sanitized-title> (<12-char-path-hash>)/
    ├── article.html
    ├── page.json
    └── assets/
        ├── 001.jpg
        ├── 002.png
        └── ...
```

- `article.html` preserves the supported text structure and references downloaded images using relative paths.
- `page.json` contains the complete response returned by the Telegraph API.
- Images are numbered in document order. If an image cannot be downloaded, the HTML keeps its original URL as a clickable link, so numbering may contain gaps. Videos and iframe content are not downloaded; their links are preserved.

## Customizing Storage Path

For more information, refer to [Customizing Storage Path & File Name](./index.md/#customizing-storage-path--file-name).

### TELEGRAPH_FILE_PATH

:material-lightbulb-on: Optional, defaults to `Telegraph/{archive_name}`

### Available Variables

```json
{
  "archive_name": "Sanitized page title followed by a stable 12-character path hash",
  "title": "Page title returned by Telegraph",
  "path": "Normalized Telegraph page path",
  "path_hash": "First 12 characters of the SHA-256 hash of the page path"
}
```
