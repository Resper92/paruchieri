from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

ALGORITHM = "HS256"


class BcryptPasswordHasher:
    """Infrastructure adapter for the PasswordHasher port."""

    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


class JwtTokenService:
    """Infrastructure adapter for the TokenService port."""

    def __init__(self, secret_key: str, expire_minutes: int) -> None:
        self._secret_key = secret_key
        self._expire_minutes = expire_minutes

    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expire_minutes)
        return jwt.encode({"sub": subject, "exp": expire}, self._secret_key, algorithm=ALGORITHM)

    def decode_subject(self, token: str) -> str:
        payload = jwt.decode(token, self._secret_key, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if subject is None:
            raise jwt.InvalidTokenError("Token is missing a subject")
        return subject
