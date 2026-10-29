# CLAUDE.md

개인 투자 리서치 자동화 시스템. **매매 자동화가 아니라** 정보 수집 → 양질의 정보 선별 → 분석 → 하루 30분 이내로 읽을 분량으로 전달하는 것이 목적이다.
전체 계획과 결정 근거는 [PLAN.md](PLAN.md)에 있다. 설계를 바꾸는 작업이면 PLAN.md도 함께 고친다.

## 언어

- 사용자와의 대화, 문서, 주석, docstring, CLI 출력, 커밋 메시지 본문은 **한국어**
- 코드 식별자(변수·함수·테이블·컬럼 이름)는 영어

## 운영 구조 (중요)

- **서버(서울 리전 VPS) 1대가 예약 작업 실행과 운영 데이터 저장을 모두 맡는다.** 노트북 2대(회사 MacBook Pro, 집 MacBook Air)는 개발 전용
- 노트북에서는 예약 작업을 등록하거나 운영 DB에 쓰지 않는다. 운영 DB 조회는 Tailscale + 읽기 전용 계정으로만
- 노트북 간 동기화 대상은 코드(Git)뿐. 데이터 파일을 iCloud·Dropbox로 동기화하지 않는다
- 운영 비밀값(Gmail 토큰, 포트폴리오, 구독 토큰)은 서버에만 둔다. 특히 회사 노트북에는 두지 않는다

## 명령어

```bash
make setup      # uv sync + .env 생성
make db-up      # 개발용 Postgres 기동 (localhost:5433, pgvector/pg17)
make migrate    # alembic upgrade head
make doctor     # 설정·DB·마이그레이션·Claude CLI·외부 키 점검
make test       # pytest (DB 테스트는 Postgres 없으면 건너뜀)
make lint       # ruff check + format --check
make fmt        # ruff 자동 수정
make db-shell   # psql
make db-reset   # 개발 DB 삭제 후 재생성
```

CLI는 `uv run invest <명령>`. 진입점은 `src/invest/cli.py`(Typer).

## 구조

```
src/invest/
  config.py       설정 (pydantic-settings, .env)
  db.py           SQLAlchemy 엔진 + 스키마 모델
  cli.py          CLI 명령
  collectors/     news, research, macro, market, filings — 소스별 수집기
  processing/     본문 추출, 중복 제거, 클러스터링, 점수, 요약
  analytics/      지표, 레짐·이상치, 자금흐름, 포트폴리오 리스크
  delivery/       Notion, Telegram
config/           sources.yaml(소스 레지스트리), interests.yaml(관심 프로파일)
prompts/          LLM 프롬프트 — 코드와 같이 버전 관리
migrations/       Alembic
deploy/           서버용 systemd 유닛·설정 스크립트
docs/             dev-setup.md(노트북 설정), adr/(설계 결정 기록)
data/             원본·Parquet (gitignore, 실데이터는 서버에만)
```

## 규칙

**데이터·DB**
- 스키마 변경은 `db.py` 모델 수정 + Alembic 마이그레이션으로만. DB에 직접 DDL을 치지 않는다
- 운영 데이터(메타데이터, 뉴스, 리포트, 공시, 실행 이력)는 Postgres, 시계열은 `data/parquet/` + DuckDB
- 수집 원본(HTML, PDF, JSON)은 가공 전에 `data/raw/{source}/{date}/`에 그대로 저장한다. 가공 로직을 바꿔도 재처리할 수 있어야 한다
- 수집기는 "마지막 성공 시각" 이후를 가져오는 따라잡기 방식으로 만든다 (서버 재시작 후 빈 구간 복구)
- 모든 예약 작업은 `job_runs`에 실행 이력을 남긴다

**LLM**
- 구독만 사용한다(API 종량제 없음). LLM 호출은 Claude Code 헤드리스(`claude -p`)이며, `llm_runner` 모듈을 통해서만 한다
- 기사마다 LLM을 부르지 않는다. 로컬 사전 필터로 후보를 줄인 뒤 묶어서 한 번에 호출한다. 데일리 브리프 기준 하루 2~3회가 목표
- 숫자(가격, 지표, 변동률)는 LLM이 만들지 않는다. 코드가 데이터에서 직접 넣고, LLM은 문장만 쓴다
- LLM이 쓴 요약에는 반드시 원문 링크를 붙인다
- 프롬프트는 코드 안에 하드코딩하지 않고 `prompts/`에 둔다

**수집 매너·저작권**
- robots.txt와 약관을 지키고 저빈도로 수집한다. 소스별 파서는 서로 격리해서 하나가 깨져도 나머지는 돈다
- 원문은 서버에 개인 보관만 한다. Notion에는 요약과 링크만 올린다

**비밀값**
- 환경변수는 모두 `INVEST_` 접두사를 쓴다 (사용자 셸에 다른 프로젝트의 `DATABASE_URL`이 export돼 있음)
- `.env`, 토큰, 자격증명 파일은 커밋하지 않는다(.gitignore). 새 키를 추가하면 `.env.example`과 `config.EXTERNAL_KEYS`에도 추가한다
- 로그와 CLI 출력에 키 값을 찍지 않는다. 설정 여부만 표시한다

## Git

- 개인 GitHub 계정의 비공개 저장소. 회사 계정과 SSH 키·커밋 작성자를 분리한다 (docs/dev-setup.md)
- 커밋·푸시는 사용자가 요청할 때만
