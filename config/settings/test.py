from .base import *  # noqa: F403
from .base import BASE_DIR

DEBUG = True
SECRET_KEY = "test-secret-key"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
STUDENT_EMAIL_DOMAINS = ["st.ug.edu.gh"]
LECTURER_EMAIL_DOMAINS = ["ug.edu.gh"]
STATICFILES_DIRS = [BASE_DIR / "static"]
