"""환경 설정. 값은 .env 또는 환경변수에서 읽는다."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # 접두사 INVEST_: 셸에 다른 프로젝트의 DATABASE_URL 등이 export돼 있어도 섞이지 않게
    model_config = SettingsConfigDict(
        env_prefix="INVEST_",
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    env: Literal["dev", "prod"] = "dev"
    database_url: str = "postgresql+psycopg://invest:invest@localhost:5433/invest"
    data_dir: Path = PROJECT_ROOT / "data"

    # 외부 서비스 키 — 비어 있으면 None으로 취급
    fred_api_key: SecretStr | None = None
    ecos_api_key: SecretStr | None = None
    dart_api_key: SecretStr | None = None
    naver_client_id: SecretStr | None = None
    naver_client_secret: SecretStr | None = None
    notion_token: SecretStr | None = None
    telegram_bot_token: SecretStr | None = None
    telegram_chat_id: str | None = None
    sec_user_agent: str | None = None
    google_credentials_file: Path | None = None
    healthchecks_url: str | None = None


# doctor가 설정 여부를 점검하는 외부 서비스 항목 (표시 이름, 필드명)
EXTERNAL_KEYS: list[tuple[str, str]] = [
    ("FRED", "fred_api_key"),
    ("한국은행 ECOS", "ecos_api_key"),
    ("OpenDART", "dart_api_key"),
    ("네이버 검색 ID", "naver_client_id"),
    ("네이버 검색 Secret", "naver_client_secret"),
    ("Notion", "notion_token"),
    ("Telegram 봇", "telegram_bot_token"),
    ("Telegram chat", "telegram_chat_id"),
    ("SEC User-Agent", "sec_user_agent"),
    ("Google OAuth", "google_credentials_file"),
    ("healthchecks.io", "healthchecks_url"),
]


@lru_cache
def get_settings() -> Settings:
    return Settings()
