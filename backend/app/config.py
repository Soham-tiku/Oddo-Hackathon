import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://stackit:stackitpass@localhost:5432/stackit_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me")
    # rate‑limit default (100 req / 15min)
    RATELIMIT_DEFAULT = "100/15minutes"
    JWT_ACCESS_TOKEN_EXPIRES = False 