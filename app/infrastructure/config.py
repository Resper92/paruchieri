from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    db_user: str
    db_password: str
    db_host: str
    db_name: str

    secret_key: str = "dev-secret-key-change-me"
    access_token_expire_minutes: int = 60 * 24

    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"


settings = Settings()
