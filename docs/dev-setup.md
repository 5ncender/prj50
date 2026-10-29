# 노트북 개발 환경 설정

회사 MacBook Pro와 집 MacBook Air 모두 같은 절차로 설정한다. 노트북은 개발 전용이고, 예약 작업 실행과 운영 데이터는 서버가 맡는다.

## 1. 필요한 도구

- [uv](https://docs.astral.sh/uv/) (Python 3.12 자동 설치)
- Docker Desktop (개발용 Postgres)
- Git, Claude Code CLI
- Tailscale (서버 운영 DB를 읽기 전용으로 볼 때만, 서버 구축 이후)

## 2. 개인 GitHub 계정 분리 (회사 노트북에서 특히 중요)

**SSH 키**

```bash
ssh-keygen -t ed25519 -C "개인 이메일" -f ~/.ssh/id_ed25519_personal
```

`~/.ssh/config`에 추가:

```
Host github-personal
  HostName github.com
  IdentityFile ~/.ssh/id_ed25519_personal
  IdentitiesOnly yes
```

공개키(`~/.ssh/id_ed25519_personal.pub`)를 개인 GitHub 계정 → Settings → SSH keys에 등록.

**커밋 작성자**

`~/.gitconfig`에 추가 (프로젝트 폴더 경로는 노트북마다 맞게):

```
[includeIf "gitdir:~/Documents/prj50/"]
  path = ~/.gitconfig-personal
```

`~/.gitconfig-personal`:

```
[user]
  name = 개인 이름
  email = 개인 이메일
```

확인: 프로젝트 폴더에서 `git config user.email` → 개인 이메일이 나와야 한다.

**원격 저장소 주소**는 `git@github-personal:<개인계정>/prj50.git` 형식으로 쓴다.

> 회사 정책상 업무 장비에서 개인 GitHub 사용이 막혀 있거나 금지라면, 회사 노트북은 개발에서 빼고 집 노트북만 쓴다.

## 3. 프로젝트 설정

```bash
git clone git@github-personal:<개인계정>/prj50.git ~/Documents/prj50
cd ~/Documents/prj50
make setup      # 의존성 설치 + .env 생성
make db-up      # 개발용 Postgres (localhost:5433)
make migrate
make doctor     # DB·마이그레이션·Claude CLI가 ✅면 준비 완료 (외부 키 ⚠️는 정상)
make test
```

`.env`에는 **개발용 값만** 넣는다. 운영 키는 서버의 `.env`에만 둔다.

## 4. 두 노트북을 오갈 때

- 자리를 뜨기 전에 커밋·푸시, 다른 노트북에서 시작할 때 `git pull`
- 개발 DB는 노트북마다 따로다. 스키마는 `make migrate`로 맞추고, 데이터를 맞출 필요는 없다
- 의존성이 바뀌었으면 `uv sync`
