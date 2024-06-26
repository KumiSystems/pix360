from django.urls import reverse_lazy

from pathlib import Path

from autosecretkey import AutoSecretKey

import pix360core

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ASK = AutoSecretKey(BASE_DIR / "settings.ini", template=BASE_DIR / "settings.dist.ini")
CONFIG = ASK.config

SECRET_KEY = ASK.secret_key
DEBUG = CONFIG.getboolean("PIX360", "Debug", fallback=False)
ALLOWED_HOSTS = [
    h.strip() for h in CONFIG.get("PIX360", "Hosts", fallback="localhost").split(",")
]
CSRF_TRUSTED_ORIGINS = [f"https://{h}" for h in ALLOWED_HOSTS]

SECURE_PROXY_SSL_HEADER_NAME = CONFIG.get(
    "KEYLOG", "SSLHeaderName", fallback="HTTP_X_FORWARDED_PROTO"
)
SECURE_PROXY_SSL_HEADER_VALUE = CONFIG.get("KEYLOG", "SSLHeaderValue", fallback="https")
SECURE_PROXY_SSL_HEADER = (SECURE_PROXY_SSL_HEADER_NAME, SECURE_PROXY_SSL_HEADER_VALUE)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pix360core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "pix360.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "pix360.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if (dbtype := "MySQL") in CONFIG or (dbtype := "MariaDB") in CONFIG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": CONFIG.get(dbtype, "Database"),
            "USER": CONFIG.get(dbtype, "Username"),
            "PASSWORD": CONFIG.get(dbtype, "Password"),
            "HOST": CONFIG.get(dbtype, "Host", fallback="localhost"),
            "PORT": CONFIG.getint(dbtype, "Port", fallback=3306),
        }
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_USER_MODEL = "pix360core.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

if "OIDC" in CONFIG:
    AUTHENTICATION_BACKENDS = [
        "pix360core.backends.OIDCBackend",
    ]

    LOGIN_URL = reverse_lazy("oidc_authentication_init")

    OIDC_NAME = CONFIG.get("OIDC", "Name", fallback="OIDC")
    OIDC_RP_CLIENT_ID = CONFIG["OIDC"]["ClientID"]
    OIDC_RP_CLIENT_SECRET = CONFIG["OIDC"]["ClientSecret"]
    OIDC_OP_JWKS_ENDPOINT = CONFIG["OIDC"]["JWKS"]
    OIDC_OP_AUTHORIZATION_ENDPOINT = CONFIG["OIDC"]["Authorization"]
    OIDC_OP_TOKEN_ENDPOINT = CONFIG["OIDC"]["Token"]
    OIDC_OP_USER_ENDPOINT = CONFIG["OIDC"]["UserInfo"]
    OIDC_CREATE_USER = CONFIG.getboolean("OIDC", "CreateUsers", fallback=False)
    OIDC_RP_SIGN_ALGO = CONFIG.get("OIDC", "Algorithm", fallback="RS256")

    if expiry := CONFIG.getint("OIDC", "SessionValidity", fallback=0):
        MIDDLEWARE.append("mozilla_django_oidc.middleware.SessionRefresh")
        OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = expiry * 60

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = None if DEBUG else CONFIG.get("PIX360", "StaticRoot", fallback=None)

CORE_STATIC_DIR = Path(pix360core.__file__).parent / "static"

STATICFILES_DIRS = []

# Settings for uploaded files

MEDIA_URL = "/media/"
MEDIA_ROOT = CONFIG.get("PIX360", "MediaRoot", fallback=BASE_DIR / "media")

if "S3" in CONFIG:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"
    AWS_ACCESS_KEY_ID = CONFIG.get("S3", "AccessKey")
    AWS_SECRET_ACCESS_KEY = CONFIG.get("S3", "SecretKey")
    AWS_STORAGE_BUCKET_NAME = CONFIG.get("S3", "Bucket")
    AWS_S3_ENDPOINT_URL = CONFIG.get("S3", "Endpoint")

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
