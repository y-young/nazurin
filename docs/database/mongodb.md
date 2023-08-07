# MongoDB

<https://www.mongodb.com/>

You can run your own MongoDB server or use a cloud service, like [MongoDB Atlas](https://www.mongodb.com/atlas/database).

## Configuration

### DATABASE

Set to `Mongo`. For more information, see [Configuration](../getting-started/configuration.md/#database).

### MONGO_URI

:material-exclamation-thick: Required, defaults to `mongodb://localhost:27017/nazurin`

MongoDB [connection string](https://docs.mongodb.com/manual/reference/connection-string/), _must_ include database name.

e.g.: `mongodb://username:password@localhost:27017/database`
