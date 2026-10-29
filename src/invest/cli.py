"""invest CLI 진입점."""

import shutil
import subprocess
import unicodedata
from dataclasses import dataclass
from typing import Literal

import typer
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import text

from invest.config import EXTERNAL_KEYS, PROJECT_ROOT, get_settings
from invest.db import get_engine

app = typer.Typer(help="개인 투자 리서치 자동화 CLI", no_args_is_help=True)


@app.callback()
def main() -> None:
    """개인 투자 리서치 자동화 CLI."""


@dataclass
class Check:
    name: str
    level: Literal["ok", "warn", "fail"]
    detail: str


def _display_width(s: str) -> int:
    """터미널 표시 폭. 한글 등 전각 문자는 2칸으로 센다."""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in s)


def _check_database() -> Check:
    try:
        with get_engine().connect() as conn:
            version = conn.execute(text("show server_version")).scalar_one()
            extensions = set(conn.execute(text("select extname from pg_extension")).scalars())
    except Exception as exc:
        return Check("DB 연결", "fail", f"{type(exc).__name__}: {exc}".splitlines()[0])
    missing = ", ".join(sorted({"vector", "pg_trgm"} - extensions))
    if missing:
        return Check("DB 연결", "warn", f"Postgres {version}, 확장 없음: {missing}")
    return Check("DB 연결", "ok", f"Postgres {version}, vector·pg_trgm 사용 가능")


def _check_migrations() -> Check:
    head = ScriptDirectory.from_config(Config(str(PROJECT_ROOT / "alembic.ini"))).get_current_head()
    try:
        with get_engine().connect() as conn:
            current = MigrationContext.configure(conn).get_current_revision()
    except Exception:
        return Check("마이그레이션", "fail", "DB에 연결할 수 없음")
    if current != head:
        return Check("마이그레이션", "fail", f"현재 {current}, 최신 {head} → make migrate")
    return Check("마이그레이션", "ok", f"최신 ({head})")


def _check_claude_cli() -> Check:
    if shutil.which("claude") is None:
        return Check("Claude Code CLI", "fail", "claude 명령을 찾을 수 없음")
    result = subprocess.run(
        ["claude", "--version"], capture_output=True, text=True, timeout=30, check=False
    )
    return Check("Claude Code CLI", "ok", result.stdout.strip() or "설치됨")


def _check_external_keys() -> list[Check]:
    settings = get_settings()
    return [
        Check(label, "ok", "설정됨") if getattr(settings, field) else Check(label, "warn", "미설정")
        for label, field in EXTERNAL_KEYS
    ]


@app.command()
def doctor() -> None:
    """설정·DB·외부 도구 연결 상태를 점검한다. 실패 항목이 있으면 종료 코드 1."""
    settings = get_settings()
    typer.echo(f"환경: {settings.env}\n")

    checks = [_check_database(), _check_migrations(), _check_claude_cli(), *_check_external_keys()]
    icons = {"ok": "✅", "warn": "⚠️ ", "fail": "❌"}
    width = max(_display_width(c.name) for c in checks)
    for c in checks:
        padding = " " * (width - _display_width(c.name))
        typer.echo(f"{icons[c.level]} {c.name}{padding}  {c.detail}")

    if any(c.level == "fail" for c in checks):
        raise typer.Exit(code=1)
