---
title: "Agent Deck 10차 고도화: review inbox"
date: 2026-06-16 17:28:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, dashboard, review, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

finding 단위 상태를 붙이고 나니 다음 문제가 바로 보였다. 중요한 review 항목은 세션 안에
묻히면 안 된다. 이번에는 dashboard 상단에 `open high` finding만 모아보는 Review Inbox를
붙였다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`5eb2087`](https://github.com/hoonapps/agent-deck/commit/5eb2087)

## 이번 변경

dashboard 상단에 Review Inbox 영역을 추가했다.

이 영역은 저장된 모든 transcript session을 훑고, 아래 조건에 맞는 finding만 모은다.

```text
severity = high
status = open
```

session detail을 열기 전에 지금 당장 봐야 하는 review item이 있는지 먼저 확인할 수 있다.

## 왜 inbox인가

agent review가 많아지면 문제는 출력 부족이 아니다. 오히려 중요한 지적이 여러 session에
흩어지는 것이 문제다.

예를 들어 하루 동안 여러 작업을 하면 이런 상태가 된다.

- dashboard 기능 구현 review
- parser 변경 review
- blog export review
- packaging review

각 세션 안에는 high, medium, low finding이 섞인다. 이미 fixed 처리한 항목도 있고, 아직 open인
항목도 있다.

이때 필요한 화면은 전체 로그가 아니라 아직 처리되지 않은 high severity 목록이다.

## API

새 endpoint를 추가했다.

```text
GET /api/inbox
```

응답은 단순하다.

```json
{
  "count": 1,
  "sessions": 1,
  "findings": [
    {
      "session": "review.md",
      "severity": "high",
      "status": "open",
      "key": "d64c54e690f7"
    }
  ]
}
```

inbox는 별도 데이터를 저장하지 않는다. `.agent-deck-session-state.json`에 저장된 finding
status와 transcript에서 추출한 findings를 합쳐서 만든 read model이다.

## 화면

dashboard 첫 화면에서 topbar 아래에 Review Inbox가 나온다.

표시하는 값:

- session
- finding status button
- agent
- location
- summary

session 이름을 누르면 해당 session으로 이동하면서 `severity=high`, `status=open` filter가
적용된다. inbox 안에서도 finding 상태를 바꿀 수 있고, fixed로 바꾸면 다음 조회부터 inbox에서
빠진다.

## 검증

이번 변경은 dashboard 테스트를 유지하면서 inbox 검증을 추가했다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

로컬 HTTP 호출로도 확인했다.

```text
GET /api/inbox
POST /api/finding-state
GET /api/inbox
```

확인한 것:

- 처음에는 `open high` finding이 inbox에 나온다.
- finding을 `fixed`로 바꾸면 inbox count가 0이 된다.
- dashboard HTML에 Review Inbox와 count가 렌더링된다.
- `GET /api/inbox`는 여러 session을 훑어 derived view를 만든다.
- GitHub Actions CI가 통과한다.

in-app browser는 이번에도 사용할 수 없어서 화면 클릭 검증은 하지 못했다. 대신 HTML 렌더링,
API 응답, 상태 변경 후 inbox 감소를 테스트와 로컬 HTTP 호출로 확인했다.

## 다음

이제 dashboard의 읽기 흐름은 꽤 명확해졌다.

```text
Review Inbox
-> session detail
-> finding status
-> findings/blog export
-> blog post
```

다음 후보는 cross-session review trend summary다. 예를 들어 최근 세션에서 반복되는 위치,
자주 나오는 severity, 아직 open인 agent별 finding 수를 볼 수 있으면 agent review 품질을 더
잘 조절할 수 있다.
