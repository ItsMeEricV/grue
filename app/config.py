import os

class Config:
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'default_user')
    POSTGRES_PW = os.getenv('POSTGRES_PW', 'default_password')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'default_db')

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PW}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False