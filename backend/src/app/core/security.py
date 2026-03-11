from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Dict, Optional, Tuple
from uuid import UUID

from src.app.config import settings
from src.app.core.errors import AuthenticationError


# 密码加密上下文 - 使用sha256_crypt，无需额外依赖，兼容性好
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码 - bcrypt只支持前72字节，自动截断"""
    # bcrypt只处理密码的前72字节，超过部分自动截断
    truncated_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(truncated_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希 - bcrypt只支持前72字节，自动截断"""
    # bcrypt只处理密码的前72字节，超过部分自动截断
    truncated_password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(truncated_password)


def create_access_token(user_id: UUID, expires_delta: Optional[timedelta] = None) -> Tuple[str, datetime]:
    """生成访问令牌"""
    to_encode: Dict[str, object] = {"sub": str(user_id)}
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return encoded_jwt, expire


def create_refresh_token(user_id: UUID, expires_delta: Optional[timedelta] = None) -> Tuple[str, datetime]:
    """生成刷新令牌"""
    to_encode: Dict[str, object] = {"sub": str(user_id)}
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return encoded_jwt, expire


def decode_token(token: str) -> Dict[str, object]:
    """解码并验证令牌"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise AuthenticationError("Invalid or expired token")


def get_user_id_from_token(token: str, token_type: str = "access") -> UUID:
    """从令牌中获取用户ID"""
    payload = decode_token(token)
    
    if payload.get("type") != token_type:
        raise AuthenticationError(f"Invalid token type, expected {token_type}")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")
    
    try:
        return UUID(user_id)
    except ValueError:
        raise AuthenticationError("Invalid user ID in token")
