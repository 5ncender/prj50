import pytest
from sqlalchemy import text
from typer.testing import CliRunner

from invest.cli import app
from invest.config import Settings
from invest.db import get_engine

runner = CliRunner()


def _db_available() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("select 1"))
        return True
    except Exception:
        return False


def test_unprefixed_shell_vars_are_ignored(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgres://other-project/db")
    settings = Settings(_env_file=None)
    assert "other-project" not in settings.database_url


def test_help_lists_doctor():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "doctor" in result.output


def test_empty_env_values_are_treated_as_unset(monkeypatch):
    monkeypatch.setenv("INVEST_FRED_API_KEY", "")
    monkeypatch.setenv("INVEST_GOOGLE_CREDENTIALS_FILE", "")
    settings = Settings(_env_file=None)
    assert settings.fred_api_key is None
    assert settings.google_credentials_file is None


@pytest.mark.db
@pytest.mark.skipif(not _db_available(), reason="개발용 Postgres 없음 (make db-up)")
def test_doctor_passes_against_dev_db():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0, result.output
    assert "마이그레이션" in result.output
