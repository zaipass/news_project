from redis import StrictRedis


class BaseConfig(object):
    # 开启调试模式
    DEBUG = True

    LOGGING_DEBUG = DEBUG
    # 秘钥
    SECRET_KEY = "SECRET_KEY"
    # redis 的参数
    REDIS_HOST = "localhost"

    REDIS_PORT = 6379

    # mysql 数据库的参数
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@localhost:3306/sql_day"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session 保存在Redis数据库中
    SESSION_TYPE = "redis"

    SESSION_USE_SIGNER = True

    SESSION_REDIS = StrictRedis(REDIS_HOST, REDIS_PORT)

    SESSION_PERMANENT = 60 * 60 * 24


class DevelopmentConfig(BaseConfig):
    pass


class ProductConfig(BaseConfig):
    pass


class TestConfig(BaseConfig):
    pass

configs = {
    "dev": DevelopmentConfig,
    "pro": ProductConfig,
    "test": TestConfig
}