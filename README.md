# Nazurin

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5cbfed1b51a644b187ed5d9521a4ea95)](https://www.codacy.com/manual/y-young/nazurin?utm_source=github.com&utm_medium=referral&utm_content=y-young/nazurin&utm_campaign=Badge_Grade)
![](https://img.shields.io/badge/python->%3D%203.5-blue)
![](https://img.shields.io/badge/-Telegram-blue.svg?logo=telegram)

English | [中文](https://blog.gpx.moe/2020/07/20/nazurin/)

小さな小さな賢将, a Telegram bot which helps you collect ACG illustrations from various sites.

## Architecture

![architecture.png](https://i.loli.net/2020/07/29/sJB1HkgvwZ8mOez.png)

## Features

-   View/Download artwork from [various sites](#supported-sites)
-   Add images to your collection via Telegram
-   Store your collection in Telegram channels
-   Store images on local disk or [MEGA](https://mega.nz/)
-   Store image metadata in [multiple types](#database) of database

### Supported Sites

|        Name       |               URL              | Commands | Collection |
| :---------------: | :----------------------------: | :------: | :--------: |
|       Pixiv       |    <https://www.pixiv.net/>    |     ✔    |      ✔     |
|      Danbooru     |  <https://danbooru.donmai.us/> |     ✔    |      ✔     |
|     Safebooru     | <https://safebooru.donmai.us/> |          |      ✔     |
|      yandere      |       <https://yande.re/>      |     ✔    |      ✔     |
|      Konachan     |     <https://konachan.com/>    |     ✔    |      ✔     |
|     Lolibooru     |    <https://lolibooru.moe/>    |          |      ✔     |
|      Gelbooru     |     <https://gelbooru.com/>    |          |      ✔     |
|      Twitter      |     <https://twitter.com/>     |          |      ✔     |
| Bilibili Dynamics |    <https://t.bilibili.com/>   |          |      ✔     |

## Deploy

### Deploy on Heroku

1.  'Deploy to Heroku' Button:

    [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

> Tips: You can fork this repository, modify it to your needs, and use this button to deploy your own version.

2.  Manual deploy:

    Set all required environment variables on Heroku according to `config.py`(root directory & `/sites`), clone this repository and push to Heroku, everything should be working properly.

### Deploy on your own server

> Tips: You may comment out unused dependencies in `requirements.txt` before installation.

1.  Install dependencies: `pip install -r requirements.txt`
2.  Set the required environment variables
3.  Start the bot: `python bot.py`

## Usage

Commands:

-   `/ping` - pong
-   `/pixiv <id>` - view pixiv artwork
-   `/pixiv_download <id>` - download pixiv artwork
-   `/danbooru <id>` - view danbooru post
-   `/danbooru_download <id>` - download danbooru post
-   `/yandere <id>` - view yandere post
-   `/yandere_download <id>` - download yandere post
-   `/konachan <id>` - view konachan post
-   `/konachan_download <id>` - download konachan post
-   `/bookmark <id>` - bookmark pixiv artwork
-   `/clear_downloads` - clear download cache
-   `/help` - get help text

### How to update your collection

Send the bot a message with a link of [supported sites](#supported-sites), this message will be forwarded to `GALLERY` channel, the bot will then download the original images from the site, send the files to `ALBUM` channel, and finally store to your custom destination.

> Tips: On mobile you can use the _share_ button in apps, as long as the final message contains a link.

## Configuration

### ENV

The default option (`production`) uses Webhook mode, you can set to `development` to use polling mode.

### TOKEN

API token of your bot, can be obtained from [@BotFather](https://t.me/BotFather).

### WEBHOOK_URL

Webhook URL to be set for Telegram server.

### PORT

Webhook port, automatically set if on Heroku.

### STORAGE

String, evaluated to list.

Type of storage, default is `[]` which only uses `DOWNLOAD_DIR` as local storage. Set to `['Mega']` to use MEGA.

Implement other storage by creating a file under `storage` with a `store` function.

### DOWNLOAD_DIR

Local directory to store downloaded images, will be created if not exists.

### STORAGE_DIR

Storage directory, can be local or remote, will be created if not exists.

### ALBUM_ID

Telegram channel ID used for storing _files_.

### GALLERY_ID

Telegram channel ID used for storing _messages_, messages sent to bot and containing URL entities will be forwarded here for reviewing.

### ADMIN_ID

Telegram user ID(_not_ username) of the admin, bot functions are restricted to admin user.

> Tips:
>
> 1.  You can get your User ID & Channel ID via [@GetIDs Bot](https://t.me/getidsbot/)
> 2.  You need to add your bot to channel administrators

### DATABASE

Type of database.

Supported databases:

|   Driver  |                          URL                         |   Config   |           Note          |
| :-------: | :--------------------------------------------------: | :--------: | :---------------------: |
|   TinyDB  | <https://tinydb.readthedocs.io/en/stable/index.html> |   `Local`  |         Default         |
| Firestore |   <https://firebase.google.com/products/firestore>   | `Firebase` |                         |
|  MongoDB  |              <https://www.mongodb.com/>              |   `Mongo`  | MongoDB Atlas supported |
|  Cloudant |         <https://www.ibm.com/cloud/cloudant>         | `Cloudant` |                         |

You can also implement your own database driver by creating a file under `database` folder, and set this option to the name of driver class.

#### GOOGLE_APPLICATION_CREDENTIALS

Firebase SDK credentials, see [Firebase Documentation](https://firebase.google.com/docs/admin/setup#initialize_the_sdk).

For Heroku, you can copy the content of `service-account-file.json`.

#### MONGO_URI

MongoDB [connection string](https://docs.mongodb.com/manual/reference/connection-string/), _must_ specify database.

eg: `mongodb://username:password@localhost:27017/database`, default is `mongodb://localhost:27017/nazurin`.

#### CLOUDANT_USER & CLOUDANT_APIKEY & CLOUDANT_DB

Cloudant username, API key and database name, using IAM authentication, default database is `nazurin`.

### PIXIV_USER & PIXIV_PASS

Pixiv email or user id, and password.

### MEGA_USER & MEGA_PASS

MEGA login email and password.

## MEGA Encoding Issue

Due to unknown reasons, there're encoding issues with special filenames (e.g.:special or full-width characters) on MEGA. These filenames may be wrongly displayed on MEGA Android & iOS clients, and cannot be synced through MEGASync. However, MEGA Web client can handle these files correctly, so to solve this problem, do the following:

1.  Create a temporary directory and set `STORAGE_DIR` to it
2.  Periodically log into MEGA **Web** client
3.  **Copy** all files from temporary directory to archive directory (Do not use _move_)
4.  Delete files in temporary directory
5.  Problem solved

> Of course you can modify filename format to avoid this problem

## Roadmap

-   [x] Introduce plugin system and extract some functions
-   [x] Support local database
-   [ ] Thorough error handling
-   [ ] Support more sites
-   [x] Support Pixiv ugoira
-   [ ] Support Moebooru pools
-   [ ] Reverse Image Search
-   [ ] Provide more configurable options
