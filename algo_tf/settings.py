from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from algo_tf.domain.enums import Mode


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ALGO_TF_", extra="ignore")

    mode: Mode = Mode.REPLAY
    database_url: str = Field(default="sqlite:///./algo_tf.db")
    api_key: str = Field(default="dev-key")


settings = Settings()
