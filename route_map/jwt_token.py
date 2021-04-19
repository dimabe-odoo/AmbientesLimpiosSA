import jwt
import datetime
from .api_env import secret, algorithm


def generate_token(user_id):
    payload = {
        'iat': datetime.datetime.utcnow(),
        'sub': user_id,
    }
    token = jwt.encode(
        payload,
        secret,
        algorithm=algorithm
    )
    return token


def decode_token(token):
    return jwt.decode(
        token,
        secret,
        algorithms=[algorithm]
    )
