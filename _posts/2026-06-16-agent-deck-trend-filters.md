---
title: "Agent Deck 12차 고도화: trend filter"
date: 2026-06-16 17:47:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, dashboard, review, trend, filter, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

Review Trends를 붙이고 나니 전체 집계만 보는 화면은 금방 한계가 생긴다. review가 쌓일수록
필요한 질문은 더 좁아진다.

```text
codex가 남긴 open finding만 보고 싶다
high severity만 보고 싶다
fixed 처리한 finding은 trend에서 빼고 싶다
```

이번에는 trend에도 `severity`, `agent`, `status` filter를 붙였다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`817031b`](https://github.com/hoonapps/agent-deck/commit/817031b)

## 이번 변경

`GET /api/trends`가 session detail과 같은 query filter를 받게 했다.

```text
GET /api/trends?agent=codex&status=open
GET /api/trends?severity=high
GET /api/trends?status=fixed
```

dashboard의 Review Trends 패널에도 filter form을 추가했다.

필터 항목:

- severity
- agent
- status

이제 trend panel과 selected session detail이 같은 query context를 공유한다. 예를 들어
`agent=codex&status=open`을 걸면 상단 trend도 codex의 open finding만 보고, 아래 session
detail도 같은 기준으로 좁혀진다.

## 응답 구조

filtered trend는 적용한 filter와 전체 scan 범위를 같이 내려준다.

```json
{
  "total": 3,
  "sessions": 2,
  "scannedSessions": 2,
  "filters": {
    "severity": "all",
    "agent": "codex",
    "status": "open"
  },
  "agents": [
    {
      "label": "codex",
      "count": 3
    }
  ]
}
```

`sessions`는 filter 결과에 실제로 걸린 session 수다. `scannedSessions`는 dashboard가 훑은 전체
session 수다. 둘을 분리해 두면 “전체 20개 session 중 3개 session에만 open finding이 남았다”는
식의 화면으로 확장하기 좋다.

## 상태 변경과 trend

finding status를 `fixed`로 바꾸면 trend 결과도 바로 바뀐다. 새 파일을 저장하지 않고
`.agent-deck-session-state.json`의 status marker와 transcript findings를 합쳐서 다시 계산한다.

이번 테스트에서는 high finding 하나를 `fixed`로 바꾼 뒤 아래를 확인했다.

- `GET /api/trends?status=open`
- `GET /api/trends?status=fixed`

open trend에서는 남은 open finding만 보이고, fixed trend에서는 방금 처리한 finding만 보인다.

## 화면

Review Trends 패널에 `Apply trend`, `Reset trend` control을 넣었다.

`agent=codex&status=open`을 적용하면 HTML에서 select 상태도 유지된다.

```html
<option value="codex" selected>codex</option>
<option value="open" selected>open</option>
```

작은 변화지만 dashboard를 실제로 계속 켜놓고 쓰려면 이런 상태 유지가 중요하다.

## 검증

이번 변경은 아래 명령으로 확인했다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

로컬 dashboard HTTP도 확인했다.

```text
GET /api/trends?agent=codex&status=open
GET /?session=review.md&agent=codex&status=open
```

확인한 값:

- filtered trend total
- filtered session count
- scanned session count
- selected filter state
- Review Trends HTML
- GitHub Actions CI

브라우저 연결 도구는 이번에도 쓸 수 없었다. 대신 API 응답, HTML 문자열, unit test, CI로 확인했다.

## 다음

이제 trend는 전체 집계와 좁혀 보기까지 된다.

다음 후보는 time window다. 최근 N개 session, 오늘 session, 특정 날짜 이후 session을 볼 수 있으면
review dashboard가 하루 작업 흐름을 정리하는 데 더 가까워진다.
