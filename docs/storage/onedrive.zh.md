# OneDrive

<https://www.microsoft.com/zh-cn/microsoft-365/onedrive/online-cloud-storage>

## 使用之前

要使用 OneDrive 存储，你需要完成以下两个步骤：

1.  在 Azure Active Directory (AAD) 中注册一个应用程序
2.  授权并获得 _Refresh Token_

这意味着你的账户必须同时拥有 OneDrive 和 Azure Active Directory 的使用权限，例如 Office 365 E5 订阅。

对于微软机构账户（工作或学校账户），可在 [此处](https://portal.office.com/account/?ref=MeControl#subscriptions) 查看订阅状态。

对于个人账户，你可能需要购买 Azure Active Directory 订阅。

## 使用指南

### 注册应用程序

1.  前往 Azure Active Directory -> [应用注册](https://go.microsoft.com/fwlink/?linkid=2083908)

2.  点击**新注册**

3.  输入注册信息：

    - 在**名称**一栏输入你希望使用的应用名称
    - 对于**受支持的帐户类型**，选择**任何组织目录(任何 Azure AD 目录 - 多租户)中的帐户和个人 Microsoft 帐户(例如，Skype、Xbox)**
    - 在**重定向 URI**（可选）一栏，添加以下 URI：`http://localhost:5000/getAToken`

4.  点击**注册**创建应用程序

5.  在应用**概要**页面，找到**应用程序(客户端) ID** 并记录

6.  在**证书和密码**页面，前往**客户端密码**标签页，点击**新客户端密码**：

    - 输入客户端密码说明或留空
    - 选择截止期限 **12 个月**或 **24 个月**
    - 点击**添加**按钮后将显示**客户端密码**，记录客户端密码

7.  在**API 权限**页面
    - 点击**添加权限**按钮
    - 选择 **Microsoft APIs** 标签页
    - 在 _常用 Microsoft APIs_ 板块，选择 **Microsoft Graph**
    - 在**委托的权限**板块，授予以下权限：**Files.Read**, **Files.ReadWrite**，必要时可使用搜索框
    - 点击**添加权限**

### 授权并获得 Refresh Token

在开始之前，你需要安装 `git`, `Python 3` 和一个浏览器。

1.  获取工具

    ```shell
    git clone https://github.com/y-young/ms-graph-token-tool.git
    ```

2.  运行工具

    ```shell
    pip install -r requirements.txt
    ```

    ```shell
    python start.py
    ```

3.  依照屏幕上的指引，输入**应用程序(客户端) ID** 和**客户端密码**

        Redirect URI: http://localhost:5000/getAToken
        Input Application ID: {输入应用程序(客户端) ID}
        Input Application Secret: {输入客户端密码}

4.  点击链接并在浏览器中完成授权

        Initiating authorization flow...
        Please open the following link in browser to complete authorization:
        https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=...
        Awaiting authorization...
        ======== Running on http://0.0.0.0:5000 ========
        (Press CTRL+C to quit)

5.  如果授权成功，你的 **Refresh Token** 将显示在最后一个页面上，记录 Refresh Token

## 配置

!!! warning "注意"

    由于 OneDrive 的 Access Token 和 Refresh Token 被缓存在数据库中，切换账号后，你需要从数据库中删除 `nazurin` 集合中的 `onedrive` 文档。

### STORAGE

追加 `OneDrive`，详见 [配置](../getting-started/configuration.zh.md/#storage)。

### OD_CLIENT

:material-exclamation-thick: 必需

从 AAD 中获取的**应用程序(客户端) ID**。

### OD_SECRET

:material-exclamation-thick: 必需

从 AAD 中获取的**客户端密码**。

### OD_RF_TOKEN

:material-exclamation-thick: 必需

在最后一步中获取的 **Refresh Token**。

!!! note "备注"

    此 Refresh Token 只用于初次授权，之后机器人将自动更新密钥。

!!! warning "注意"

    在启用两步验证后，你可能需要重新获取 Refresh Token。

（由 [@weremexii](https://github.com/weremexii/) 撰写）
