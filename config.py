from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    telegram_bot_token: str
    database_url: str = "sqlite:///./journaling_bot.db"
    default_timezone: str = "UTC"
    default_schedule_times: str = "09:00,20:00"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    def get_schedule_times(self) -> list[str]:
        """Parse schedule times from comma-separated string."""
        return [time.strip() for time in self.default_schedule_times.split(",")]


settings = Settings()
