# Nazurin

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/5cbfed1b51a644b187ed5d9521a4ea95)](https://www.codacy.com/manual/y-young/nazurin?utm_source=github.com&utm_medium=referral&utm_content=y-young/nazurin&utm_campaign=Badge_Grade)
![](https://img.shields.io/badge/python->%3D%203.8-blue)
![](https://img.shields.io/badge/-Telegram-blue.svg?logo=telegram)

[Documentation](https://nazurin.readthedocs.io/) | [中文文档](https://nazurin.readthedocs.io/zh/)

小さな小さな賢将, a Telegram bot that helps you collect ACG illustrations from various sites.

## Architecture

![architecture.png](https://s2.loli.net/2022/09/10/mpW32BJqxajV7Sg.png)

## Features

- View/Download artwork from [various sites](#supported-sites)
- Add images to your collection via Telegram
- Store your collection in Telegram channels
- Store images on [multiple types](#supported-storage) of storage
- Store image metadata in [multiple types](#supported-databases) of database

### Supported Sites

|       Name        |              URL               | Commands | Collection |
| :---------------: | :----------------------------: | :------: | :--------: |
|       Pixiv       |    <https://www.pixiv.net/>    |    ✔     |     ✔      |
|     Danbooru      | <https://danbooru.donmai.us/>  |    ✔     |     ✔      |
|     Safebooru     | <https://safebooru.donmai.us/> |          |     ✔      |
|      yandere      |      <https://yande.re/>       |    ✔     |     ✔      |
|     Konachan      |    <https://konachan.com/>     |    ✔     |     ✔      |
|     Lolibooru     |    <https://lolibooru.moe/>    |          |     ✔      |
|     Zerochan      |  <https://www.zerochan.net/>   |    ✔     |     ✔      |
|     Gelbooru      |    <https://gelbooru.com/>     |          |     ✔      |
|      Twitter      |     <https://twitter.com/>     |    ✔     |     ✔      |
|    ArtStation     | <https://www.artstation.com/>  |          |     ✔      |
|     Wallhaven     |    <https://wallhaven.cc/>     |          |     ✔      |
| Bilibili Dynamics |   <https://t.bilibili.com/>    |          |     ✔      |
|       Weibo       |      <https://weibo.com/>      |          |     ✔      |
|    DeviantArt     | <https://www.deviantart.com/>  |          |     ✔      |
|      Lofter       |   <https://www.lofter.com/>    |          |     ✔      |
|   Kemono.party    |    <https://kemono.party/>     |          |     ✔      |
|      Bluesky      |      <https://bsky.app/>       |          |     ✔      |

### Supported Databases

|                           Driver                            |                             Usage                              | Config Value |                           Note                           |
| :---------------------------------------------------------: | :------------------------------------------------------------: | :----------: | :------------------------------------------------------: |
|     [TinyDB](https://tinydb.readthedocs.io/en/latest/)      |    [TinyDB](https://nazurin.readthedocs.io/database/tinydb)    |   `Local`    |                         Default                          |
| [Firestore](https://firebase.google.com/products/firestore) | [Firestore](https://nazurin.readthedocs.io/database/firestore) |  `Firebase`  |                                                          |
|             [MongoDB](https://www.mongodb.com/)             |   [MongoDB](https://nazurin.readthedocs.io/database/mongodb)   |   `Mongo`    | [MongoDB Atlas](https://www.mongodb.com/atlas) supported |
|       [Cloudant](https://www.ibm.com/cloud/cloudant)        |  [Cloudant](https://nazurin.readthedocs.io/database/cloudant)  |  `Cloudant`  |                                                          |

You can also implement your own database driver by creating a file under `database` folder, and set this option to the name of driver class.

### Supported Storage

|                                          Name                                           |                                Usage                                | Config Value  |    Note     |
| :-------------------------------------------------------------------------------------: | :-----------------------------------------------------------------: | :-----------: | :---------: |
|                                          Local                                          |        [Local](https://nazurin.readthedocs.io/storage/local)        |    `Local`    |   Default   |
|                            [Telegram](https://telegram.org/)                            |     [Telegram](https://nazurin.readthedocs.io/storage/telegram)     |  `Telegram`   | Added in v2 |
|                                [MEGA](https://mega.io/)                                 |         [MEGA](https://nazurin.readthedocs.io/storage/mega)         |    `Mega`     |             |
|                        [Google Drive](https://drive.google.com/)                        | [Google Drive](https://nazurin.readthedocs.io/storage/google-drive) | `GoogleDrive` |             |
| [OneDrive](https://www.microsoft.com/en-us/microsoft-365/onedrive/online-cloud-storage) |     [OneDrive](https://nazurin.readthedocs.io/storage/onedrive)     |  `OneDrive`   |             |
|                            [S3](https://aws.amazon.com/s3/)                             |           [S3](https://nazurin.readthedocs.io/storage/s3)           |     `S3`      |             |

## Configuration

For more information, see [Documentation](https://nazurin.readthedocs.io/getting-started/configuration/).

## Deploy

> For more deploy options, checkout [Documentation](https://nazurin.readthedocs.io/getting-started/deploy/).

### Manual

> Tips: You may comment out unused dependencies in `requirements.txt` before installation.

1.  Install dependencies: `pip install -r requirements.txt`
2.  Set the required environment variables or place them in `.env` file, you may refer to `.env.example` as an example
3.  Start the bot: `python -m nazurin`

### Docker

1.  Configure the options in `.env`
2.  Run `docker-compose up -d` to use the lastet pre-built Docker images. (Alternatively, you may build the image yourself: `docker-compose up -d --build`)

## Usage

Use `/help` command to get a list of available commands or help for a specific command, use `/set_commands` to set bot commands in command menu.

Some system commands are listed below:

- `/clear_cache` — Clear cache
- `/help [COMMAND]` — Get help of all commands or a specific command
- `/ping` — Pong
- `/set_commands` — Set commands
- `/start` — Get help

### How to update your collection

Send the bot a message with a link of [supported sites](#supported-sites), this message will be forwarded to `GALLERY` channel, the bot will then download the original images from the site, send the files to `ALBUM` channel, and finally store to your custom destinations.

> Tips: On mobile you can use the _share_ button in apps, as long as the final message contains a link.
