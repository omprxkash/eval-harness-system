from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/eval_harness"
    REDIS_URL: str = "redis://localhost:6379/0"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ACTIVE_LLM_PROVIDER: str = "gemini"
    GEMINI_MODEL: str = "gemini-2.0-flash"
    OPENAI_MODEL: str = "gpt-4o"
    JUDGE_TEMPERATURE: float = 0.0

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
