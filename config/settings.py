import os
from pathlib import Path
from urllib.parse import parse_qsl, urlparse

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY is not configured.")


DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"


ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]


database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is not configured.")


postgres_url = urlparse(database_url)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": postgres_url.path.lstrip("/"),
        "USER": postgres_url.username,
        "PASSWORD": postgres_url.password,
        "HOST": postgres_url.hostname,
        "PORT": postgres_url.port or 5432,
        "OPTIONS": dict(parse_qsl(postgres_url.query)),
    }
}