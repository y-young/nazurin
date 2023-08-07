# 图源

图源是图片的来源，在收到命令或图片收藏请求时，Nazurin 从图源网站查询信息并获取图片。

目前支持的图源：

--8<-- "docs/includes/site.zh.md"

## 自定义存储路径和文件名

Nazurin 自 v2.3.0 起支持自定义存储路径和文件名，你可以为每个图源分别配置，下面介绍通用的规则。

支持此功能的图源插件将提供两个配置选项：

- 存储目录路径（例如 [`PIXIV_FILE_PATH`](pixiv.zh.md/#pixiv_file_path)），相对于 [`STORAGE_DIR`](../getting-started/configuration.zh.md/#storage_dir)
- 文件名（例如 [`PIXIV_FILE_NAME`](pixiv.zh.md/#pixiv_file_name)）

对于每个选项，它的值是使用 Python [格式字符串语法](https://docs.python.org/zh-cn/3/library/string.html#format-string-syntax) 的一个模板字符串。

每个图源插件都提供了不同的模板变量，你可以像 `{variable_name}` 这样使用。例如，Pixiv 图源插件提供了 `title` 变量，对应作品的标题，如果将 `PIXIV_FILE_NAME` 设置为 `{title}`，则文件名将会是作品的标题。注意文件扩展名会自动附加，因此不需要包含在模板中。

如果你想要使用嵌套在数组或对象中的变量，需要使用 `[]` 来访问它，例如，对于一个如下所示的变量 `user`：

```json
{
  "account": "username",
  "id": 12345,
  "name": "Nick Name"
}
```

模板 `{user[account]}` 将产生 `username`，模板 `{user[name]} ({user[id]})` 将产生 `Nick Name (12345)`，依此类推。

图源插件可能会提供表示日期或时间的变量，此时可以使用 [格式代码](https://docs.python.org/zh-cn/3/library/datetime.html#strftime-and-strptime-format-codes) 来格式化它们，例如，`{date:%Y-%m-%d}` 将产生 `2023-02-22`，`{date:%Y}` 将产生 `2023`。默认的时间日期格式为 `%Y-%m-%d %H:%M:%S`，它将产生类似 `2023-02-22 12:34:56` 的字符串。

以下是一些使用 Pixiv 图源的例子，仅供参考：

- 按画师用户名划分目录：`PIXIV_FILE_PATH = Pixiv/{user[account]}`
- 按创建年份和日期划分目录：`PIXIV_FILE_PATH = Pixiv/{create_date:%Y}/{create_date:%m}`
- 按文件类型（后缀名）分类：`PIXIV_FILE_PATH = Pixiv/{extension}`
- 将文件命名为 `id - page`：`PIXIV_FILE_NAME = {id} - {page}`
- 在文件名中包含作品标题和画师名：`PIXIV_FILE_NAME = {title} ({user[name]})`

!!! warning "注意"

    - 文件名中可以包含 Unicode 字符（如 emoji），但类似 `/` 的无效字符将会被替换
    - 留意可能发生改变的属性，如用户的昵称，这有可能会破坏你的目录结构
    - 你有责任确保同一目录下的文件名不会重复，否则重名的文件可能会被覆盖，例如使用用户名作为文件名就不是一个好主意
