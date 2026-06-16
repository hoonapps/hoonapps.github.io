---
title: "Agent Deck 5차 고도화: 로컬 web dashboard"
date: 2026-06-16 16:40:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, dashboard, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

`agent-deck`는 터미널에서 agent 작업을 실행하고, transcript를 남기고, replay와 findings를
CLI로 확인하는 단계까지 왔다. 이번에는 그 기록을 브라우저에서 보는 로컬 dashboard를 붙였다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`56f1584`](https://github.com/hoonapps/agent-deck/commit/56f1584)

## 이번 목표

터미널은 실행에 강하다. 하지만 세션을 다시 읽고, 리뷰 결과를 표로 보고, 어떤 기록을
블로그로 정리할지 고르는 일은 브라우저 화면이 더 편하다.

그래서 이번 목표는 작게 잡았다.

- `.agent-deck/sessions` 목록을 웹에서 본다.
- 선택한 transcript의 replay timeline을 본다.
- review findings를 table로 본다.
- 같은 parser를 CLI와 web dashboard가 공유한다.
- 외부 서비스 없이 로컬에서만 띄운다.

## `agent-deck web`

새 명령은 이렇다.

```bash
agent-deck web --host 127.0.0.1 --port 4545
```

실행하면 로컬 HTTP 서버가 뜬다.

```text
Agent Deck dashboard: http://127.0.0.1:4545/
```

브라우저에서는 왼쪽에 session 목록, 오른쪽에 선택된 session detail을 보여준다.

detail 영역은 두 개로 나눴다.

- Replay: transcript를 compact timeline으로 표시
- Findings: review output에서 뽑은 severity, agent, location, summary table

## 구조

새 파일은 `src/web.js`다.

역할은 세 가지다.

- `createDashboardServer`: Node 기본 `http` 서버 생성
- `dashboardModel`: transcript 목록과 선택된 session detail 생성
- `startDashboard`: CLI에서 서버를 띄우는 얇은 wrapper

별도 web framework는 넣지 않았다. 지금 필요한 것은 제품용 웹앱이 아니라 로컬 session
browser다. dependency를 늘리기보다 Node 기본 모듈과 기존 parser를 재사용하는 쪽이 맞다.

## 안전한 파일 선택

dashboard는 transcript 디렉터리 안의 `.md` 파일만 다룬다.

session 선택은 파일명 basename으로 제한했다. 예를 들어 `/api/session?file=../review.md`처럼
들어와도 디렉터리 밖 파일을 읽지 않고 `review.md`로 정규화해서 매칭한다.

이 도구는 로컬 전용이지만, 파일을 읽는 기능은 처음부터 좁게 잡는 게 맞다.

## API

HTML 외에 작은 JSON endpoint도 있다.

```text
GET /api/sessions
GET /api/session?file=review.md
```

이 API는 나중에 dashboard를 더 키울 때 그대로 확장할 수 있다. 예를 들면 severity filter,
publish-ready flag, blog draft 생성 버튼 같은 기능을 붙일 수 있다.

## 검증

이번 변경은 테스트를 42개까지 늘렸다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

추가로 샘플 transcript를 만들어 실제 dashboard 서버를 띄우고 확인했다.

```text
GET /
GET /api/sessions
GET /api/session?file=../review.md
```

확인한 것:

- HTML에 session 목록이 렌더링된다.
- Replay 영역에 agent timeline이 나온다.
- Findings table에 `src/app.js:12` location이 표시된다.
- JSON API가 같은 데이터를 반환한다.
- package dry-run에 `src/web.js`가 포함된다.
- GitHub Actions CI가 통과한다.

## 다음

이제 `agent-deck`의 기록 루프는 터미널과 브라우저를 모두 갖췄다.

```text
TUI에서 agent 작업 실행
-> transcript 저장
-> CLI에서 replay/findings 확인
-> web dashboard에서 세션 탐색
-> blog draft로 정리
```

다음 단계는 dashboard 안에서 바로 filter와 export를 다루는 것이다.

- severity별 findings filter
- agent별 session filter
- publish-ready session 표시
- dashboard에서 findings/blog draft export

Agent AX 작업대는 단순히 agent를 호출하는 화면이 아니라, 실행 결과를 다시 읽고 검증하고
지식으로 남기는 도구여야 한다. 이번 dashboard는 그 읽기 계층의 시작이다.
