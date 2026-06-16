---
title: "Agent Deck 13차 고도화: trend time window"
date: 2026-06-16 17:59:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, dashboard, review, trend, filter, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

trend filter를 붙이고 나니 다음 문제는 시간 범위였다. 전체 session을 다 훑으면 오래된 review까지
섞인다. 하루 작업을 볼 때는 오늘 작업만 보고 싶고, 흐름을 빠르게 볼 때는 최근 몇 개 session만
보고 싶다.

이번에는 Review Trends에 time window를 추가했다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`fe3b18f`](https://github.com/hoonapps/agent-deck/commit/fe3b18f)

## 이번 변경

`GET /api/trends`가 `window` query를 받게 했다.

```text
GET /api/trends?window=recent:1
GET /api/trends?window=today
GET /api/trends?window=since:2026-06-16
```

dashboard의 Review Trends form에도 Window select를 추가했다.

화면 preset:

- all
- today
- recent:5
- recent:10

API는 `recent:N`을 받아서 임의 개수도 처리한다.

## 계산 순서

이번 변경에서 중요한 건 filter 순서다.

```text
session list
-> time window 적용
-> window 안의 findings 추출
-> severity / agent / status filter 적용
-> trend group 계산
```

time window는 session 단위 filter다. finding filter보다 먼저 적용해야 한다.

## 응답 구조

window가 들어가면서 session count도 세 가지로 나눴다.

```json
{
  "total": 2,
  "sessions": 1,
  "scannedSessions": 2,
  "windowSessions": 1,
  "filters": {
    "window": "recent:1"
  }
}
```

각 값의 의미:

- `scannedSessions`: dashboard가 전체로 훑은 session 수
- `windowSessions`: time window 안에 남은 session 수
- `sessions`: 최종 finding filter까지 통과한 session 수

이렇게 나눠두면 나중에 “전체 session은 80개인데 최근 5개 중 2개 session에만 open finding이
있다” 같은 화면을 만들기 쉽다.

## 로컬 날짜 기준

처음에는 `since`를 ISO date 기준으로 잘랐다. 그런데 로컬 dashboard에서 `touch -t 202606160000`
같은 파일은 UTC로 보면 전날로 밀릴 수 있다.

dashboard는 사람이 로컬에서 보는 도구다. 그래서 `today`와 `since:YYYY-MM-DD`는 session
modifiedAt을 로컬 날짜 `YYYY-MM-DD`로 바꾼 뒤 비교하게 했다.

## 검증

테스트에서는 transcript 파일의 mtime을 고정했다.

```text
review.md    -> 2026-06-15
follow-up.md -> 2026-06-16
```

확인한 것:

- `window=recent:1`은 최신 session 하나만 본다.
- `window=since:2026-06-16`은 2026-06-16 session만 본다.
- `windowSessions`와 `scannedSessions`가 분리된다.
- Window select에서 `recent:5` selected 상태가 유지된다.
- session filter form과 finding status form이 `window` 값을 잃지 않는다.

실행한 검증:

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

로컬 HTTP로도 확인했다.

```text
GET /api/trends?window=recent:1
GET /api/trends?window=since:2026-06-16
```

확인한 응답:

```json
{
  "total": 2,
  "sessions": 1,
  "scanned": 2,
  "windowSessions": 1,
  "window": "since:2026-06-16"
}
```

## 다음

이제 Review Trends는 꽤 운영 화면에 가까워졌다.

```text
time window
severity / agent / status
location trend
status marker
session detail
```

다음 후보는 trend snapshot export다. daily standup이나 changelog에 붙일 수 있게 현재 trend
상태를 Markdown으로 뽑으면, dashboard에서 본 내용을 바로 기록으로 넘길 수 있다.
