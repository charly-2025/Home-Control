from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    MYSQL_HOST: str
    MYSQL_PORT: int

    MYSQL_DATABASE: str

    MYSQL_USER: str
    MYSQL_PASSWORD: str

    MYSQL_ROOT_PASSWORD: str

    SECRET_KEY: str

    API_HOST: str
    API_PORT: int


settings = Settings()