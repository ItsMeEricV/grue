import os


class Config:
    TESTING: bool = False


class MainConfig(Config):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "default_user")
    POSTGRES_PW: str = os.getenv("POSTGRES_PW", "default_password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "default_db")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "your_google_client_id")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "your_google_client")
    GOOGLE_CALLBACK: str = os.getenv("GOOGLE_CALLBACK", "your_google_callback")

    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


class TestConfig(Config):
    TESTING: bool = True
    SECRET_KEY: str = "test"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "your_google_client_id")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "your_google_client")
    GOOGLE_CALLBACK: str = os.getenv("GOOGLE_CALLBACK", "your_google_callback")
