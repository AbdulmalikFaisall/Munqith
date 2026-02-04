from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "munqith-backend"
    DEBUG: bool = True


settings = Settings()
