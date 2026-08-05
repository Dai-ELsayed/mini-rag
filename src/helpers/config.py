from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    AAP_NAME: str
    APP_VERSION: str
    OPEN_API_KEY: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULTE_CHUNK_SIZE: int

    class config:
        env_file: ".env"

def get_settings():
    return Settings()
