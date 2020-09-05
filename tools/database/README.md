# Database Helper

[English](#possible-uses) \| [中文](#用途)

## Possible Uses

-   Search for files collected in earlier versions, write their metadata to database (migrate to newer version)
-   Make sure that the metadata of every file is stored in database (database integrity check)
-   Build a metadata database from your local files (archive/management)

## Usage

1.  Setting up local environment, eg: install dependencies, configure envrionment variables
2.  In current directory, execute `python helper.py`
3.  Enter directory path to scan, ending with a slash or backslash, eg: `/data/images/`
4.  Enter skipped site names, all supported sites are: `['pixiv', 'danbooru', 'yandere', 'konachan', 'lolibooru', 'zerochan', 'twitter', 'bilibili']`
5.  When scan completed, check 'no match' and error files in output, manually handle these files

## 用途

-   将老版本收集的图片信息存入数据库以便迁移到新版本
-   确保每一个文件的信息都已存入数据库（检查数据库完整性）
-   建立本地收藏数据库，用于归档或管理

## 使用方法

1.  搭建本地环境，如安装依赖和设定环境变量
2.  在当前目录下，执行 `python helper.py`
3.  输入要扫描的目录路径，以斜杠或反斜杠结尾，如 `/data/images/`
4.  输入要跳过的来源名称，支持以下来源：`['pixiv', 'danbooru', 'yandere', 'konachan', 'lolibooru', 'zerochan', 'twitter', 'bilibili']`
5.  扫描结束后，查看输出的 'no match' 和 error 文件列表，手动进行处理
