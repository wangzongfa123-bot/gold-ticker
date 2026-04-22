from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./gold_monitor.db"
    API_NINJAS_KEY: str = ""
    GOLD_API_KEY: str = ""
    FETCH_INTERVAL_SECONDS: int = 300
    DATA_RETENTION_DAYS: int = 90
    CORS_ORIGINS: list = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


settings = Settings()
