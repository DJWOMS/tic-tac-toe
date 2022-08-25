import os

SECRET_KEY = os.environ.get(
    'SECRET_KEY', ";G*S&*#TY()BOJ0f8y9Y()Hf0h)(HofiPskd)j){US)dhsaON){*DSf9huinbhfe97(&T9"
)
print(SECRET_KEY)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES = 60
