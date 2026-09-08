from .base import *  # noqa: F403
from .base import env

DEBUG = False

SECRET_KEY = env("SECRET_KEY")

if DEBUG:
    raise RuntimeError("DEBUG must be False in production.")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must be set in production.")

CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
