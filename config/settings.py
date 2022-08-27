import os

SECRET_KEY = os.environ.get(
    'SECRET_KEY', ";G*S&*#TY()BOJ0f8y9Y()Hf0h)(HofiPskd)j){US)dhsaON){*DSf9huinbhfe97(&T9"
)
DEBUG = os.environ.get('DEBUG', True)
CORS_ALLOWED_HOSTS = os.environ.get('CORS_ALLOWED_HOSTS', 'http://127.0.0.1:8000').split(" ")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES = 60
