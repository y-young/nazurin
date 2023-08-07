# MEGA

<https://mega.io/>

## 配置

!!! warning "注意"

    由于登录凭据被缓存在数据库中，切换 MEGA 账号后，你需要从数据库中删除 `nazurin` 集合中的 `mega` 文档。

### STORAGE

追加 `Mega`，详见 [配置](../getting-started/configuration.zh.md/#storage)。

### MEGA_USER

:material-exclamation-thick: 必需

登录电子邮件地址。

### MEGA_PASS

:material-exclamation-thick: 必需

登录密码。

## 编码问题

由于未知原因，MEGA 中的特殊文件名（例如特殊字符和全角字符）会出现编码问题，
这些文件名可能在 Android 和 iOS 客户端中显示不正常，且无法使用 MEGASync 同步。
但是 MEGA 网页客户端能够正确处理这些文件，因此如需解决此问题，请遵循以下步骤：

1.  创建一个临时文件夹并设置为 `STORAGE_DIR`
2.  定期登录 MEGA **网页**客户端
3.  从临时文件夹**复制**所有文件到归档文件夹（切勿使用 _剪切_）
4.  在临时文件夹中删除原文件
5.  问题解决

!!! tip "提示"

    当然，你也可以通过修改文件名的格式来规避此问题。
