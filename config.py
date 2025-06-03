from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
    )

    DEBUG: bool = False
    BOT_TOKEN: str
    DOMAIN: str = 'localhost:8000'  # Base domain
    REDIS_HOST: str = 'localhost'  # Redis host
    REDIS_PORT: int = 6379  # Redis port
    REDIS_PASSWORD: str = ''  # Password for Redis connection
    ACCESS_TOKEN_LIFETIME: int = 3600  # Access token lifetime in seconds
    REFRESH_TOKEN_LIFETIME: int = 3600  # Refresh token lifetime in seconds

    SIGNATURE_AUTH_SECRET_KEY: str = ''  # Secret key for signature authentication

    OPENROUTER_API_KEY: str = ''  # API key for OpenRouter

    # Derived URLs
    @property
    def BASE_URL(self) -> str:
        return f"http://{self.DOMAIN}/"

    @property
    def API_V1_URL(self) -> str:
        return f"{self.BASE_URL}api/v1/"

    @property
    def USER_MANAGEMENT_API_V1(self) -> str:
        return f"{self.API_V1_URL}auth/"

    @property
    def USERS_API_URL(self) -> str:
        return f"{self.USER_MANAGEMENT_API_V1}users/"

    @property
    def AUTH_API_URL(self) -> str:
        return f"{self.API_V1_URL}auth/"

    @property
    def REDIS_URL(self):
        return (
            f"redis://:{settings.REDIS_PASSWORD}"
            f"@{settings.REDIS_HOST}:{settings.REDIS_PORT}/3"
        )


settings = Settings()
