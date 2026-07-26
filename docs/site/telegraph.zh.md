# Telegraph

<https://telegra.ph/>，<https://graph.org/>

Nazurin 通过 Telegraph 官方 `getPage/<path>` API 并设置 `return_content=true` 来归档页面，不需要浏览器自动化。

每个页面以独立目录保存，其中包含原始 API 响应、可离线阅读的 HTML 文章和下载的图片：

```text
Telegraph/
└── <清理后的标题> (<12 位 path hash>)/
    ├── article.html
    ├── page.json
    └── assets/
        ├── 001.jpg
        ├── 002.png
        └── ...
```

- `article.html` 保留支持的正文结构，并使用相对路径引用已下载图片。
- `page.json` 保存 Telegraph API 返回的完整响应。
- 图片按照正文中的出现顺序编号。图片下载失败时，HTML 会保留其原始 URL 作为可点击链接，因此编号可能出现空缺。视频和 iframe 内容不会下载，将保留链接。

## 自定义存储路径

更多信息请查阅 [自定义存储路径和文件名](./index.zh.md/#customizing-storage-path--file-name)。

### TELEGRAPH_FILE_PATH

:material-lightbulb-on: 可选，默认为 `Telegraph/{archive_name}`


### 可用变量

```json
{
  "archive_name": "清理后的页面标题和稳定的 12 位 path hash",
  "title": "Telegraph 返回的页面标题",
  "path": "规范化后的 Telegraph page path",
  "path_hash": "page path 的 SHA-256 哈希前 12 位"
}
```
