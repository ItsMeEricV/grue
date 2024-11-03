import os


class Config(object):
    Testing = False


class MainConfig(Config):
    SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "default_user")
    POSTGRES_PW = os.getenv("POSTGRES_PW", "default_password")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "default_db")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your_google_client_id")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your_google_client")
    GOOGLE_CALLBACK = os.getenv("GOOGLE_CALLBACK", "your_google_callback")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "your_google_client_id")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "your_google_client")
    GOOGLE_CALLBACK = os.getenv("GOOGLE_CALLBACK", "your_google_callback")
