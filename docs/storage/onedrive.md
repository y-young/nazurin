# OneDrive

<https://www.microsoft.com/en-us/microsoft-365/onedrive/online-cloud-storage>

## Before Use

To use OneDrive storage, you have to do the following two steps:

1.  Register an app in Azure Active Directory (AAD)
2.  Authorization and get a _Refresh Token_

That means that you must have an account with **both** OneDrive and Azure Active Directory access, for example, Office 365 E5 Subscription.

For Microsoft organization account (work or school account), you can check your subscription status [here](https://portal.office.com/account/?ref=MeControl#subscriptions).

For personal Microsoft account, you may need to purchase Azure Active Directory subscription.

## Instructions

### Register an App

1.  Go to Azure Active Directory -> [App registrations](https://go.microsoft.com/fwlink/?linkid=2083908)

2.  Click **New registration**

3.  Enter the registration information:

    - In the **Name** field, enter the application name you like
    - For **Supported account types**, select **Accounts in any organizational directory and personal Microsoft accounts**
    - In the **Redirect URI** (optional) field, add the following redirect URI: `http://localhost:5000/getAToken`

4.  Click **Register** to create the application

5.  On the app **Overview** page, find the **Application(client) ID** value and note it down

6.  On the **Certificates & secrets** page, go to **Client secrets** section, click **New client secret**:

    - Input a key description or just leave it blank
    - Select a key duration of either **In 1 year** or **In 2 years**
    - When you press the **Add** button, the **Client Secret** will be displayed, please note it down

7.  On the **API permissions** page
    - Click **Add a permission** button
    - Select **Microsoft APIs** tab
    - In the _Commonly used Microsoft APIs_ section, choose **Microsoft Graph**
    - In the **Delegated permissions** section, grant the following permissions: **Files.Read**, **Files.ReadWrite**. Use the search box if necessary.
    - Click **Add permissions**

### Authorization and Get Refresh Token

Before you start, you'll need to install `git`, `Python 3` and a browser.

1.  Get the tool

    ```shell
    git clone https://github.com/y-young/ms-graph-token-tool.git
    ```

2.  Run the tool

    ```shell
    pip install -r requirements.txt
    ```

    ```shell
    python start.py
    ```

3.  Follow the instructions on the screen, enter your **Application(client) ID** and **Client Secret**

        Redirect URI: http://localhost:5000/getAToken
        Input Application ID: {Enter Your Application(client) ID}
        Input Application Secret: {Enter Your Client Secret}

4.  Click the link and finish authorization in browser

        Initiating authorization flow...
        Please open the following link in browser to complete authorization:
        https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=...
        Awaiting authorization...
        ======== Running on http://0.0.0.0:5000 ========
        (Press CTRL+C to quit)

5.  Once succeeded, your **Refresh Token** will be displayed on the final page, please note it down

## Configuration

!!! warning "Notice"

    Since OneDrive access token and refresh token are cached in database, after switching account, you'll need to delete `onedrive` document in `nazurin` collection from the database.

### STORAGE

Append `OneDrive`. For more information, see [Configuration](../getting-started/configuration.md/#storage).

### OD_CLIENT

:material-exclamation-thick: Required

The **Application(client) ID** from AAD.

### OD_SECRET

:material-exclamation-thick: Required

The **Client Secret** from AAD.

### OD_RF_TOKEN

:material-exclamation-thick: Required

The **Refresh Token** you got in the final step.

!!! note

    This refresh token is only for first-time authorization, after which the bot will update the tokens automatically.

!!! warning "Attention"

    After enabling Two-factor Authentication, you may need to retrieve your refresh token again.

(By [@weremexii](https://github.com/weremexii/))
