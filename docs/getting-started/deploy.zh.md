# 部署

## 自建服务器

### 手动部署

!!! tip "提示"

    你可以在安装前注释掉 `requirements.txt` 中不需要的依赖。

1.  安装依赖：`pip install -r requirements.txt`
2.  在 `.env` 中设置所需的环境变量，可参照 `.env.example`
3.  启动：`python -m nazurin`

### Docker

1.  在 `.env` 中设置所需的环境变量
2.  执行 `docker-compose up -d` 使用最新的预构建 Docker 镜像启动机器人

    （或者，你也可以自己构建 Docker 镜像：`docker-compose up -d --build`）

## 部署在 Fly.io 上

!!! note "注意"

    Fly.io 的 256MB 免费内存不足以运行 ffmpeg 转换（Pixiv ugoira 动图到 MP4），提升到 512MB 应能正常工作，但这会带来额外的费用开销。

### 全新部署

1. 安装 flyctl，注册并登录，参考 <https://fly.io/docs/hands-on/install-flyctl/>
2. 执行 `fly launch --copy-config --image ghcr.io/y-young/nazurin:latest`，输入所需信息并跳过部署阶段

   - 建议使用**不易被猜测到的名称**作为应用名称以提升安全性，你也可以使用自动生成的应用名称
   - 建议将应用部署在**欧洲区域**，因为 Telegram 机器人 API 服务器据说位于荷兰。同时这也有利于减少到亚洲的出口流量，毕竟亚洲流量的免费配额小于北美及欧洲（30GB 与 100GB）。
   - 我们选择暂时**不部署**应用，因为此时还没有设置环境变量，应用在启动时会抛出异常

     ```
     > fly launch --copy-config --image ghcr.io/y-young/nazurin:latest
     An existing fly.toml file was found for app nazurin
     Creating app in /nazurin
     Using image ghcr.io/y-young/nazurin:latest
     ? App Name (leave blank to use an auto-generated name): {你的应用名称}
     Automatically selected personal organization: {你的机构名称}
     ? Select region: ams (Amsterdam, Netherlands)
     Created app nazurin in organization personal
     Wrote config file fly.toml
     ? Would you like to set up a Postgresql database now? No
     ? Would you like to deploy now? No
     Your app is ready. Deploy with `flyctl deploy`
     ```

3. 在 `.env` 中更新配置，参照 `.env.example`。Webhook URL 应类似 `https://xxx.fly.dev/`，不需要指定端口，因为在 `fly.toml` 中已经设置
4. 执行 `python ./tools/set_fly_secrets.py` 将环境变量设置为 fly.io 上的 Secrets
5. 执行 `fly deploy` 部署应用，检查日志中有无报错

### 从 Heroku 迁移

1. 安装 flyctl，注册并登录，参考 <https://fly.io/docs/hands-on/install-flyctl/>
2. 使用此工具迁移你的应用程序：<https://fly.io/launch/heroku>
3. 执行 `fly config save` 将配置文件保存到本地以便之后使用
4. 更新端口和 Webhook URL：`fly secrets set PORT=8080 WEBHOOK_URL=https://你的应用名称.fly.dev/`
5. 应用程序应当会自动重启，检查日志中有无报错

## 部署在 Heroku 上

!!! warning "注意"

    从 2022 年 11 月 28 日起，Heroku 将停止供应免费产品，并计划关停免费 Dyno 和数据服务
    （<https://blog.heroku.com/next-chapter>），我们将把对 Heroku 的支持降为低优先级。

### “部署到 Heroku” 按钮

[![部署](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

!!! tip "提示"

    你也可以 Fork 这个仓库，根据你的需要修改代码，并用此按钮部署你修改过的版本。

### 手动部署

根据 [配置指南](./configuration.zh.md) 在 Heroku 上设置所有必需的环境变量，克隆这个仓库并推送到 Heroku，应用程序应当能正常工作。
