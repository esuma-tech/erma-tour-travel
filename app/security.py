import bcrypt
from itsdangerous import URLSafeSerializer, BadSignature

from .config import settings

serializer = URLSafeSerializer(settings.secret_key, salt="erma-admin-session")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def create_session_token(username: str) -> str:
    return serializer.dumps({"u": username})


def read_session_token(token: str) -> str | None:
    try:
        data = serializer.loads(token)
        return data.get("u")
    except BadSignature:
        return None
