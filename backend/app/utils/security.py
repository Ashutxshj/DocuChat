from jose import JWTError, jwt

from app.utils.config import get_settings


def decode_token(token: str) -> str | None:
    settings = get_settings()
    if not settings.jwt_secret_key:
        return None

    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None

    subject = payload.get("sub")
    return str(subject) if subject else None
