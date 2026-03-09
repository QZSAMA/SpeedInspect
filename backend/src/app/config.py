from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, field_validator
from typing import List, Optional


class Settings(BaseSettings):
    """应用配置"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 应用配置
    APP_NAME: str = "SpeedInspect Backend"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    SECRET_KEY: SecretStr

    # 数据库配置
    DATABASE_URL: SecretStr
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 100

    # JWT配置
    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS配置
    CORS_ORIGINS: str = "http://localhost:3000"
    CORS_ALLOW_CREDENTIALS: bool = True

    # 对象存储配置
    STORAGE_TYPE: str = "local"
    STORAGE_ENDPOINT: Optional[str] = None
    STORAGE_ACCESS_KEY: Optional[SecretStr] = None
    STORAGE_SECRET_KEY: Optional[SecretStr] = None
    STORAGE_BUCKET: str = "speedinspect"
    STORAGE_REGION: str = "us-east-1"

    # LLM配置
    LLM_PROVIDER: str = "tongyi"
    LLM_API_KEY: Optional[SecretStr] = None
    LLM_MODEL: str = "qwen-vl-max"

    # 短信配置
    SMS_PROVIDER: Optional[str] = None
    SMS_ACCESS_KEY: Optional[SecretStr] = None
    SMS_SECRET_KEY: Optional[SecretStr] = None
    SMS_SIGN_NAME: Optional[str] = None
    SMS_TEMPLATE_CODE: Optional[str] = None

    # 限流配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v: str) -> List[str]:
        """解析CORS_ORIGINS为列表"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        """是否是开发环境"""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """是否是生产环境"""
        return self.ENVIRONMENT == "production"


settings = Settings()
