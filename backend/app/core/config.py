from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str = "cambia-esto-en-produccion-usa-una-clave-segura-de-64-caracteres"
    DATABASE_URL: str = "sqlite:///./gestivoryx.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    APP_PORT: int = 3000
    ALLOWED_ORIGINS: str = "*"

    @property
    def cors_origins(self) -> list[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()

_DEFAULT_KEY = "cambia-esto-en-produccion-usa-una-clave-segura-de-64-caracteres"
if settings.SECRET_KEY == _DEFAULT_KEY:
    import warnings
    warnings.warn(
        "⚠️  SECRET_KEY uses the default insecure value. "
        "Set a strong random key in your .env file before deploying to production.",
        stacklevel=1,
    )
