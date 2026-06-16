---
title: "Agent Deck 14차 고도화: trend snapshot export"
date: 2026-06-16 18:08:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, dashboard, review, trend, export, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

Review Trends가 시간 범위와 filter를 갖추고 나니, 다음은 기록으로 넘기는 일이었다. dashboard에서
본 내용을 다시 손으로 정리하면 흐름이 끊긴다. 현재 trend 상태를 그대로 Markdown으로 뽑을 수
있어야 한다.

이번에는 trend snapshot export를 추가했다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`14a51a9`](https://github.com/hoonapps/agent-deck/commit/14a51a9)

## 이번 변경

새 export endpoint를 추가했다.

```text
GET /export/trends
```

기존 trend query를 그대로 받는다.

```text
GET /export/trends?window=recent:1
GET /export/trends?window=today&status=open
GET /export/trends?agent=codex&severity=high
```

dashboard의 Review Trends form에는 `Download trend` 링크를 붙였다. 화면에서 적용한 filter와
time window 그대로 Markdown snapshot을 내려받는다.

## Markdown 형식

export 결과는 이런 형태다.

```md
# Agent Deck Review Trends

- Generated: 2026-06-16T09:07:13.982Z
- Findings: 2
- Sessions with findings: 1
- Window sessions: 1
- Scanned sessions: 2
- Filters: window=recent:1, severity=all, agent=all, status=all

## Locations

| Location | Total | High | Open | Sessions |
| --- | ---: | ---: | ---: | ---: |
| src/app.js:12 | 1 | 1 | 1 | 1 |
```

그 아래에는 severity, status, agent별 count도 붙는다.

```md
## Severity

- high: 1
- low: 1

## Status

- open: 2

## Agents

- codex: 2
```

## 구현 방향

별도 snapshot 파일은 만들지 않았다. `/api/trends`와 같은 derived read model을 쓰고, 응답만
Markdown으로 바꾼다.

```text
reviewTrends(...)
-> formatTrendMarkdown(...)
-> sendMarkdown(...)
```

이렇게 해두면 dashboard 화면, JSON API, Markdown export가 같은 계산 결과를 공유한다.

## 왜 필요한가

agent review를 계속 돌리면 dashboard 안에서는 상태가 보인다. 그런데 하루가 끝나면 따로 남길
요약이 필요하다.

예를 들면 이런 곳에 바로 붙일 수 있다.

- daily standup
- changelog draft
- blog 작업 로그
- PR summary
- 다음 agent run의 context

trend snapshot은 dashboard에서 보는 운영 상태를 외부 기록으로 넘기는 최소 단위다.

## 검증

이번 변경은 아래 명령으로 확인했다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

로컬 dashboard도 띄워서 직접 확인했다.

```text
GET /export/trends?window=recent:1
GET /?session=review.md&window=recent:1
```

확인한 것:

- `Download trend` 링크가 렌더링된다.
- 링크가 현재 filter query를 유지한다.
- Markdown에 finding/session/window/scanned count가 들어간다.
- location table이 들어간다.
- severity/status/agent count가 들어간다.
- `window=recent:1` 결과에 오래된 session finding이 섞이지 않는다.

## 다음

다음 후보는 trend comparison이다.

지금은 현재 window의 snapshot을 뽑는다. 다음에는 `recent:5`와 그 이전 5개 session을 비교해서
open finding이 줄었는지, 어떤 agent에서 반복 finding이 늘었는지 볼 수 있게 만들고 싶다.
