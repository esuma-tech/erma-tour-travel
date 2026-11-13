import bcrypt
from itsdangerous import URLSafeSerializer, BadSignature

from .config import settings

admin_serializer = URLSafeSerializer(settings.secret_key, salt="erma-admin-session")
user_serializer = URLSafeSerializer(settings.secret_key, salt="erma-user-session")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def create_session_token(username: str) -> str:
    return admin_serializer.dumps({"u": username})


def read_session_token(token: str) -> str | None:
    try:
        data = admin_serializer.loads(token)
        return data.get("u")
    except BadSignature:
        return None


def create_user_session_token(user_id: int) -> str:
    return user_serializer.dumps({"uid": user_id})


def read_user_session_token(token: str) -> int | None:
    try:
        data = user_serializer.loads(token)
        return data.get("uid")
    except BadSignature:
        return None
