from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://user:password@localhost:5432/reviews"
    redis_url: str = "redis://localhost:6379/0"
    sendgrid_api_key: str = ""
    brand_name: str = "Acme"
    port: int = 8000
    weekly_report_recipient: str = ""
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
