# Google Drive

<https://drive.google.com/>

## 使用之前

Google Drive 在以下任一条件下可完美工作：

- `STORAGE_DIR` 的大小不超过 **15GB**
- `STORAGE_DIR` 是**团队共享盘**中的文件夹

Google Drive 驱动使用 _服务账号_ 访问云端硬盘。由于 Google API 的限制，所上传文件的拥有者为服务账号，且根据共享文件夹规则，共享文件夹中的文件将占用拥有者的存储空间，除非共享文件夹位于团队共享盘中。

因此，如果你使用**个人云端硬盘**中的共享文件夹，受服务账号的配额所限，文件总大小最多为 15GB；但如果使用**团队共享盘**，则无需担心。

## 使用指南

1.  登录 [GCP 控制台](https://console.cloud.google.com/)
2.  启用 Google Drive API（<https://developers.google.com/drive/api/v3/enable-drive-api#enable_the_drive_api>）
3.  创建一个服务账号并下载密钥文件（<https://cloud.google.com/iam/docs/creating-managing-service-account-keys#iam-service-account-keys-create-console>），
    如果之前已有 Firebase 的服务账号也可重复使用
4.  手动在云端硬盘中创建一个文件夹（个人或团队共享盘）
5.  将文件夹共享给之前创建的服务账号，并给予编辑者权限
6.  设置所有必需的环境变量

## 配置

### STORAGE

追加 `GoogleDrive`，详见 [配置](../getting-started/configuration.zh.md/#storage)。

### GD_FOLDER

:material-exclamation-thick: 必需

`STORAGE_DIR` 在云端硬盘中的文件夹 ID。

进入文件夹并从 URL 中获取，例如：`https://drive.google.com/drive/u/1/folders/{FOLDER_ID}`

### GD_CREDENTIALS or GOOGLE_APPLICATION_CREDENTIALS

:material-exclamation-thick: 必需

密钥文件路径或内容。

`GD_CREDENTIALS` 的优先级高于 `GOOGLE_APPLICATION_CREDENTIALS`，如果没有配置 `GD_CREDENTIALS` 则使用 `GOOGLE_APPLICATION_CREDENTIALS`。

!!! tip "提示"

    如果你同时使用 [Firestore](../database/firestore.zh.md) 数据库并已配置了 `GOOGLE_APPLICATION_CREDENTIALS`，则无需任何操作 :)
