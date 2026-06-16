---
title: "Agent Deck 11차 고도화: review trends"
date: 2026-06-16 17:38:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, dashboard, review, trend, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

Review Inbox를 붙이고 나니 다음으로 필요한 화면이 보였다. 지금 당장 처리해야 하는 high
finding을 보는 것도 중요하지만, 같은 위치에서 문제가 반복되는지도 봐야 한다.

이번에는 dashboard에 cross-session review trend를 추가했다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`b9f0c4a`](https://github.com/hoonapps/agent-deck/commit/b9f0c4a)

## 이번 변경

dashboard 상단에 Review Trends 패널을 추가했다.

trend는 저장된 transcript session 전체에서 review findings를 읽고 아래 기준으로 묶는다.

- location
- agent
- severity
- status

가장 중요한 표는 location 기준이다. 같은 파일과 라인에서 finding이 반복되면 dashboard 첫
화면에서 바로 보인다.

## API

새 endpoint를 추가했다.

```text
GET /api/trends
```

응답은 dashboard가 그대로 사용할 수 있는 derived view다.

```json
{
  "total": 3,
  "sessions": 2,
  "locations": [
    {
      "label": "src/app.js:12",
      "count": 2,
      "high": 2,
      "open": 2,
      "sessions": 2
    }
  ],
  "agents": [
    {
      "label": "codex",
      "count": 2
    }
  ]
}
```

여기서 중요한 점은 별도 trend 파일을 만들지 않는다는 것이다. transcript와
`.agent-deck-session-state.json`만 읽어서 매번 계산한다.

## 화면

Review Inbox 아래에 Review Trends 패널이 나온다.

상단에는 severity, status, agent 분포를 pill 형태로 보여준다. 아래 표에는 반복 location을
정렬해서 보여준다.

정렬 기준은 일부러 open 항목을 먼저 보게 했다.

```text
open count
-> high count
-> total count
-> location name
```

review dashboard에서 가장 먼저 보고 싶은 것은 이미 끝난 지적보다 아직 남아 있는 반복 문제다.

## 테스트 fixture

이번 테스트에는 두 개의 transcript를 넣었다.

첫 번째 session에는 plain text review finding이 있고, 두 번째 session에는
`AGENT_DECK_FINDINGS_JSON` block이 있다. 둘 다 `src/app.js:12`를 가리키게 만들어서 trend가
실제로 session을 가로질러 묶는지 확인했다.

확인한 값:

- 전체 finding 수
- session 수
- 반복 location의 count
- high/open count
- agent별 count
- dashboard HTML의 Review Trends 렌더링
- `GET /api/trends` 응답

## 검증

이번 변경은 아래 명령으로 확인했다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

로컬 dashboard도 띄워서 직접 HTTP로 확인했다.

```text
GET /api/trends
GET /
```

확인한 응답:

```json
{
  "total": 3,
  "sessions": 2,
  "top": {
    "label": "src/app.js:12",
    "count": 2,
    "high": 2,
    "open": 2,
    "sessions": 2
  }
}
```

in-app browser는 이번에도 `iab` 세션이 없어 붙지 않았다. 대신 테스트, 로컬 API, dashboard
HTML 문자열, GitHub Actions CI로 확인했다.

## 다음

이제 dashboard 상단은 이렇게 흐른다.

```text
Review Inbox
Review Trends
Session list
Session detail
```

다음에는 trend filter를 넣고 싶다. 최근 N개 session만 보기, 특정 agent만 보기, unresolved만
보기 정도가 들어가면 review dashboard가 단순 조회 화면에서 운영 화면에 더 가까워진다.
