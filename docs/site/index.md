# Site

Site is the source of images, when receiving a command or image collection request, Nazurin querys the site and fetch the images.

Currently supported sites:

--8<-- "docs/includes/site.md"

## Customizing Storage Path & File Name

Nazurin supports customizing storage path and file name since v2.3.0, you can configure it respectively for each site, but we'll explain the general rule here.

For sites supporting this feature, it'll provide two configuration options:

- Directory path (e.g. [`PIXIV_FILE_PATH`](pixiv.md/#pixiv_file_path)), relative to [`STORAGE_DIR`](../getting-started/configuration.md/#storage_dir)
- File name (e.g. [`PIXIV_FILE_NAME`](pixiv.md/#pixiv_file_name))

For each option, the value is a template string using Python's [Format String Syntax](https://docs.python.org/3/library/string.html#format-string-syntax).

Each site have different template variables available, you can use the variables as `{variable_name}`. For instance, Pixiv site plugin provides variable `title` denoting the title of the artwork, and if you set `PIXIV_FILE_NAME` to `{title}`, the file name will be the title of the artwork. Note that the file extension is automatically appended, you don't have to include it in the template, but every site will provide an `extension` variable in case you need it.

If you want to use a variable nested in an array or object, use `[]` to access it, e.g. for a variable `user` like this:

```json
{
  "account": "username",
  "id": 12345,
  "name": "Nick Name"
}
```

Template `{user[account]}` will produce `username`, and `{user[name]} ({user[id]})` will produce `Nick Name (12345)`, etc.

Sites may provide variables that are date or time, you can use the [Format Codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) to format them, e.g. `{date:%Y-%m-%d}` will produce `2023-02-22`, `{date:%Y}` will produce `2023`. The default format is `%Y-%m-%d %H:%M:%S`, which produces strings like `2023-02-22 12:34:56`.

Here're some examples of Pixiv for you to get started:

- Categorize by illustrator username: `PIXIV_FILE_PATH = Pixiv/{user[account]}`
- Categorize by creation date: `PIXIV_FILE_PATH = Pixiv/{create_date:%Y}/{create_date:%m}`
- Categorize by file type (extension): `PIXIV_FILE_PATH = Pixiv/{extension}`
- Name the image like `id - page`: `PIXIV_FILE_NAME = {id} - {page}`
- Include artwork title and illustrator name in file name: `PIXIV_FILE_NAME = {title} ({user[name]})`

!!! warning "Notice"

    - Unicode characters is supported in file name (like emoji), but invalid characters like `/` will be replaced
    - Be careful of things that can change, like the display name of an user, this may break your file structure
    - It's your duty to ensure the file names in the same directory are unique, otherwise the files will be overwritten, e.g. using username as file name is not a good idea
