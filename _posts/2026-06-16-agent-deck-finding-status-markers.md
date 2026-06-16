---
title: "Agent Deck 9차 고도화: finding status marker"
date: 2026-06-16 17:22:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, dashboard, review, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

직전 단계에서 session 단위 status를 붙였다. 이번에는 한 단계 더 내려가서 review finding
단위의 처리 상태를 dashboard에 붙였다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`dc0fab6`](https://github.com/hoonapps/agent-deck/commit/dc0fab6)

## 이번 변경

각 review finding에 네 가지 상태를 둘 수 있게 했다.

- `open`
- `accepted`
- `fixed`
- `ignored`

기본값은 `open`이다. review에서 나온 항목을 바로 고칠지, 받아들일지, 이미 처리했는지,
무시할지 dashboard에서 표시할 수 있다.

## 왜 finding 단위인가

session status만으로는 부족하다.

하나의 review session 안에는 여러 finding이 섞인다.

- 바로 고쳐야 하는 blocker
- 맞는 지적이지만 나중에 처리할 항목
- 이미 다른 커밋에서 해결된 항목
- 맥락상 받아들이지 않는 항목

세션 전체를 `published`로 바꿔도 finding 하나하나의 처리 상태는 남지 않는다. 그래서 이번에는
세션이 아니라 finding을 작업 단위로 보기 시작했다.

## 안정적인 key

화면에 보이는 `#1`, `#2`는 읽기에는 좋지만 저장 key로 쓰기에는 약하다. transcript에 finding이
하나 추가되면 번호가 밀릴 수 있다.

그래서 상태 저장에는 finding fingerprint를 쓴다.

```text
agent
severity
location
summary
```

이 값을 묶어서 짧은 hash key로 만든다. 화면에서는 여전히 번호를 보여주지만, sidecar JSON에는
fingerprint key로 저장한다.

## sidecar 구조 확장

상태는 기존 `.agent-deck-session-state.json`에 같이 저장한다.

```json
{
  "review.md": {
    "status": "draft",
    "updatedAt": "",
    "findings": {
      "d64c54e690f7": {
        "status": "accepted",
        "updatedAt": "2026-06-16T08:19:04.384Z"
      }
    }
  }
}
```

transcript Markdown은 그대로 둔다. 원본 기록과 작업 상태를 분리하는 원칙은 session marker와
같다.

## API와 filter

새 endpoint를 추가했다.

```text
POST /api/finding-state
```

요청 body:

```json
{
  "file": "review.md",
  "finding": "d64c54e690f7",
  "status": "fixed"
}
```

dashboard filter에도 status를 추가했다.

```text
GET /api/session?file=review.md&status=fixed
GET /export/findings?file=review.md&status=fixed
```

이제 `high` severity만 보거나, 특정 agent가 남긴 finding만 보거나, 아직 `open`인 항목만 따로
볼 수 있다.

## 검증

이번 변경은 dashboard 테스트를 46개까지 늘렸다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

로컬 HTTP 호출로도 확인했다.

```text
POST /api/finding-state
GET /api/session?file=review.md&status=accepted
GET /export/findings?file=review.md&status=fixed
```

확인한 것:

- finding key가 안정적인 hash 형태로 내려온다.
- 처음 상태는 `open`이다.
- `accepted`, `fixed`, `ignored` 상태를 sidecar JSON에 저장한다.
- status filter가 JSON API와 findings export에 적용된다.
- session status와 finding status가 같은 sidecar 안에서 공존한다.
- GitHub Actions CI가 통과한다.

in-app browser 연결은 이번에도 사용할 수 없었다. 화면 클릭 검증은 하지 못했고, HTML 렌더링,
API, form 저장 경로를 테스트와 로컬 HTTP 호출로 확인했다.

## 다음

이제 Agent Deck dashboard는 단순히 transcript를 읽는 화면이 아니다.

```text
session: draft / published / deferred
finding: open / accepted / fixed / ignored
```

다음으로는 `open high` finding만 모아보는 review inbox가 좋아 보인다. agent review가 많아질수록
중요한 것은 더 많은 출력을 받는 것이 아니라, 아직 처리되지 않은 중요한 항목을 놓치지 않는
것이다.
