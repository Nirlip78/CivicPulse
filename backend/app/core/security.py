import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm import Session
from backend.app.core.config import ACCESS_TOKEN_MINUTES, SECRET_KEY
from backend.app.database.session import get_db
from backend.app.models import User

bearer_scheme = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)

def verify_password(password: str, stored: str) -> bool:
    return pbkdf2_sha256.verify(password, stored)

def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()

def create_access_token(user: User) -> str:
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64(json.dumps({"sub": str(user.id), "role": user.role, "exp": int((datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_MINUTES)).timestamp())}, separators=(",", ":")).encode())
    signature = _b64(hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: Session = Depends(get_db)) -> User:
    error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token")
    if credentials is None:
        raise error
    try:
        header, payload, signature = credentials.credentials.split(".")
        expected = _b64(hmac.new(SECRET_KEY.encode(), f"{header}.{payload}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(expected, signature): raise ValueError
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        if int(data["exp"]) < int(datetime.now(timezone.utc).timestamp()): raise ValueError
        user = db.get(User, int(data["sub"]))
        if user is None: raise ValueError
        return user
    except (ValueError, KeyError, json.JSONDecodeError):
        raise error

def require_admin(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user
