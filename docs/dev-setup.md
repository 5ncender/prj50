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

`~/.ssh/config`의 **맨 위**에 추가:

```
Host github-personal
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_personal
  IdentitiesOnly yes
```

> 맨 위에 두는 이유: `Host *` 블록에 회사 키가 `IdentityFile`로 지정돼 있으면, SSH는 설정 파일에 나온 순서대로 키를 시도한다. 개인 블록이 아래에 있으면 회사 키가 먼저 쓰여 회사 계정으로 인증될 수 있다.

공개키를 개인 GitHub 계정에 등록 (**브라우저가 개인 계정으로 로그인돼 있는지 먼저 확인**):

```bash
pbcopy < ~/.ssh/id_ed25519_personal.pub
```

https://github.com/settings/keys → New SSH key → Title에 기기 이름(예: `MacBook Air (집)`) → Key에 붙여넣기 → Add SSH key.

키에 passphrase를 걸었다면 키체인에 한 번 저장:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519_personal
```

확인: `ssh -T git@github-personal` → `Hi 5ncender!`가 나와야 한다. 회사 계정 이름이 나오면 설정 순서나 키 등록 계정을 다시 확인.

**커밋 작성자**

`~/.gitconfig`에 추가 (프로젝트 폴더 경로는 노트북마다 맞게):

```
[includeIf "gitdir:~/Documents/prj50/"]
  path = ~/.gitconfig-personal
```

`~/.gitconfig-personal`:

```
[user]
  name = 5ncender
  email = 113486668+5ncender@users.noreply.github.com
```

확인: 프로젝트 폴더에서 `git config user.email` → noreply 주소가 나와야 한다. 다른 폴더에서는 기존 회사 설정이 그대로 쓰인다.

**원격 저장소 주소**는 `git@github-personal:5ncender/prj50.git` (clone도 이 주소로).

> 회사 정책상 업무 장비에서 개인 GitHub 사용이 막혀 있거나 금지라면, 회사 노트북은 개발에서 빼고 집 노트북만 쓴다.

## 3. 프로젝트 설정

```bash
git clone git@github-personal:5ncender/prj50.git ~/Documents/prj50
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
