# Nazurin

![](https://img.shields.io/badge/python->%3D%203.5-blue)
![](https://img.shields.io/badge/-Telegram-blue.svg?logo=telegram)

English | [中文](https://blog.gpx.moe/2020/07/20/nazurin/)

小さな小さな賢将, a Telegram bot which helps you collect ACG illustrations from various sites.

## Architecture

![architecture.png](https://i.loli.net/2020/07/29/sJB1HkgvwZ8mOez.png)

## Features

- View artwork from Pixiv/Danbooru/Yandere/Konachan
- Download artwork from the 4 sites above + Twitter
- Add images to collection via Telegram
- Store your collection in Telegram channels
- Upload images to [MEGA](https://mega.nz/)

## Deploy

### Deploy on Heroku

1. 'Deploy to Heroku' Button:

    [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

2. Manual deploy:

    Set all required environment variables on Heroku according to `config.py`(root directory & `/sites`), clone this repository and push to Heroku, everything should be working properly.

### Deploy on your own server

1. Install dependencies: `pip install -r requirements.txt`
2. Set the required environment variables
3. Start the bot: `python bot.py`

## Usage

Commands:

- `/pixiv <id>` - view pixiv artwork
- `/pixiv_download <id>` - download pixiv artwork
- `/danbooru <id>` - view danbooru post
- `/danbooru_download <id>` - download danbooru post
- `/yandere <id>` - view yandere post
- `/yandere_download <id>` - download yandere post
- `/konachan <id>` - view konachan post
- `/konachan_download <id>` - download konachan post
- `/bookmark <id>` - bookmark pixiv artwork(ADMIN ONLY)

Update your collection: send the bot a message with a link of Pixiv/Danbooru/Yandere/Konachan/Twitter, this message will be forwarded to `GALLERY` channel, the bot will then download the original images from the site, send the files to `ALBUM` channel, and finally upload to MEGA for backup.

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

Storage directory, can be local or remote, _must_ exists when using MEGA.

### ALBUM_ID

Telegram channel ID used for storing _files_.

### GALLERY_ID

Telegram channel ID used for storing _messages_, messages sent to bot and containing URL entities will be forwarded here for reviewing.

### ADMIN_ID

Telegram user ID(_not_ username) of the admin, Pixiv bookmark and collection update features are restricted to admin user.

> Tips: You can get your User ID & Channel ID via [@GetIDs Bot](https://t.me/getidsbot/)

### DATABASE

Type of database.

Default option (`Local`) uses `TinyDB` as local database, set to `Firebase` to use Firebase.

You can also implement your own database driver by creating a file under `database` folder, and set this option to the name of driver class.

### GOOGLE_APPLICATION_CREDENTIALS

Firebase SDK credentials, see [Firebase Documentation](https://firebase.google.com/docs/admin/setup#initialize_the_sdk).

You should create a Firestore collection named `nazurin` to store bot data, eg. Pixiv tokens.

For Heroku, you can copy the content of `service-account-file.json`.

### PIXIV_USER & PIXIV_PASS

Pixiv email or user id, and password.

### MEGA_USER & MEGA_PASS

MEGA login email and password.

## Roadmap

- [ ] Introduce plugin system and extract some functions
- [x] Support local database
- [ ] Thorough error handling
- [ ] Support more sites
- [ ] Support Pixiv ugoira
- [ ] Support Moebooru pools
- [ ] Reverse Image Search
- [ ] Provide more configurable options
