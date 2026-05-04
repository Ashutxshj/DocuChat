from fastapi import Header, HTTPException

from app.utils.security import decode_token


async def get_current_user_id(
    authorization: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        user_id = decode_token(authorization.split(" ", 1)[1].strip())
        if user_id:
            return user_id
        raise HTTPException(status_code=401, detail="Invalid access token")

    return x_user_id or "anonymous"
