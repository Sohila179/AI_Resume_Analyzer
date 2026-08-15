from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_TITLE: str
    APP_VERSION: str
    APP_DESCRIPTION: str
    DATABASE_URL:str
    SECRET_KEY: str
    HF_API_TOKEN: str
    HF_MODEL: str
    model_config = SettingsConfigDict(env_file=".env")