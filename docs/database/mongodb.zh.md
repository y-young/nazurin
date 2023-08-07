# MongoDB

<https://www.mongodb.com/>

你可以自行搭建 MongoDB 服务器或使用云服务，例如 [MongoDB Atlas](https://www.mongodb.com/atlas/database)。

## 配置

### DATABASE

设置为 `Mongo`，详见 [配置](../getting-started/configuration.zh.md/#database)。

### MONGO_URI

:material-exclamation-thick: 必需，默认为 `mongodb://localhost:27017/nazurin`

MongoDB [连接字符串](https://docs.mongodb.com/manual/reference/connection-string/)，**必须**包含数据库名称。

例如：`mongodb://username:password@localhost:27017/database`
