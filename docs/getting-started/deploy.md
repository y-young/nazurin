# Deploy

## Deploy on your own server

### Manual

!!! tip

    You may comment out unused dependencies in `requirements.txt` before installation.

1.  Install dependencies: `pip install -r requirements.txt`
2.  Set the required environment variables or place them in `.env` file, you may refer to `.env.example` as an example
3.  Start the bot: `python -m nazurin`

### Docker

1.  Configure the options in `.env`
2.  Run `docker-compose up -d` to use the lastet pre-built Docker images.

    (Alternatively, you may build the image yourself: `docker-compose up -d --build`)

## Deploy on Fly.io

!!! note

    The 256MB free RAM on fly.io is not enough to run ffmpeg conversion (Pixiv ugoira to MP4), scaling to 512MB should work but will introduce extra costs.

### Fresh Setup

1. Install flyctl, sign up and sign in, refer to <https://fly.io/docs/hands-on/install-flyctl/>
2. Run `fly launch --copy-config --image ghcr.io/y-young/nazurin:latest`, enter required information and skip deployment

   - It's recommended to choose a **hard-to-guess name** for your application to improve security, you may use a generated name if you wish
   - It's recommended to locate your app in **European regions** since the Telegram bot API server is said to be in Netherlands. Also, this helps to reduce outbound bandwidth to Asia since the free quota is smaller than North America/Europe (30GB vs 100GB).
   - We choose **not to deploy** the app at this time because we haven't set the environment variables and the app will throw errors at startup

   ```
   > fly launch --copy-config --image ghcr.io/y-young/nazurin:latest
   An existing fly.toml file was found for app nazurin
   Creating app in /nazurin
   Using image ghcr.io/y-young/nazurin:latest
   ? App Name (leave blank to use an auto-generated name): {Your Application Name}
   Automatically selected personal organization: {Your Organization Name}
   ? Select region: ams (Amsterdam, Netherlands)
   Created app nazurin in organization personal
   Wrote config file fly.toml
   ? Would you like to set up a Postgresql database now? No
   ? Would you like to deploy now? No
   Your app is ready. Deploy with `flyctl deploy`
   ```

3. Update configuration in `.env`, referring to `.env.example` as an example. The webhook URL should look like `https://xxx.fly.dev/`, and you don't have to specify a port since it's already setup in `fly.toml`
4. Run `python ./tools/set_fly_secrets.py` to setup the environment variables as secrets on fly.io
5. Run `fly deploy` to deploy the app, check the logs to see if there's any error

### Migrate from Heroku

1. Install flyctl, sign up and sign in, refer to <https://fly.io/docs/hands-on/install-flyctl/>
2. Use this tool to migrate your app: <https://fly.io/launch/heroku>
3. Run `fly config save` to save your configuration file locally for future operations
4. Update the port and webhook URL: `fly secrets set PORT=8080 WEBHOOK_URL=https://YOUR_APP_NAME.fly.dev/`
5. The application should restart automatically, check the logs to see if there's any error

## Deploy on Heroku

!!! warning "Caution"

    Starting November 28, 2022, Heroku will stop offering free product plans and plan to start shutting down free dynos and data services
    (<https://blog.heroku.com/next-chapter>), and we'll take Heroku support as a low priority.

### “Deploy to Heroku” Button

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

!!! tip

    You can fork this repository, modify it to your needs, and use this button to deploy your own version.

### Manual

Set all required environment variables on Heroku according to [Configuration Guide](./configuration.md), clone this repository and push to Heroku, everything should be working properly.
