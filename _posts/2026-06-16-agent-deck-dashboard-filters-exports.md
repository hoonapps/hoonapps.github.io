---
title: "Agent Deck 6차 고도화: dashboard filter와 export"
date: 2026-06-16 16:49:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, dashboard, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

이전 단계에서 `agent-deck web`으로 세션을 브라우저에서 볼 수 있게 만들었다. 이번에는
dashboard를 읽기 화면에서 작업 화면에 조금 더 가깝게 만들었다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`c1fee23`](https://github.com/hoonapps/agent-deck/commit/c1fee23)

## 이번 변경

dashboard에 세 가지를 추가했다.

- severity filter
- agent filter
- findings/blog draft download

이제 review findings가 많은 세션에서도 `high`, `medium`, 특정 agent 기준으로 좁혀 볼 수
있다. 선택된 필터는 query string으로 남기기 때문에 새로고침하거나 링크를 공유해도 같은
상태를 다시 볼 수 있다.

## findings download

dashboard에서 필터를 적용한 뒤 바로 Markdown findings를 받을 수 있다.

```text
/export/findings?file=review.md&severity=high
```

이 endpoint는 파일을 자동으로 쓰지 않는다. 선택된 transcript와 filter를 기준으로 Markdown을
생성해서 download response로 내려준다. dashboard browsing은 기본적으로 read-only여야 하기
때문이다.

## blog draft download

같은 화면에서 blog draft도 받을 수 있다.

```text
/export/blog?file=review.md
```

초안 문구도 조정했다. generated draft에 남아 있던 제3자 관점의 표현을 `내가 보낸 요청`으로
바꿨다. 앞으로 generated draft도 공개 글의 문체 기준을 따라가야 한다.

## API 응답 정리

수동 검증 중 `/api/session`이 내부용 `path`, `markdown`까지 JSON으로 내려주는 것을 확인했다.
로컬 도구라도 API 응답에는 필요한 데이터만 내보내는 편이 맞다.

그래서 HTML 렌더링과 export 내부에서는 원문을 쓰되, JSON API에서는 raw markdown과 로컬 경로를
제외하도록 바꿨다.

## 검증

이번 변경은 기존 dashboard 테스트를 확장해서 확인했다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

추가로 샘플 transcript로 실제 dashboard 서버를 띄워 확인했다.

```text
GET /?session=review.md&severity=medium&agent=codex
GET /api/session?file=review.md&severity=medium&agent=codex
GET /export/findings?file=review.md&severity=high
GET /export/blog?file=review.md
```

확인한 것:

- filter select box가 선택 상태를 유지한다.
- filtered findings table에는 선택된 agent/severity 결과만 나온다.
- JSON API는 raw markdown과 local path를 내보내지 않는다.
- findings download는 필터된 Markdown만 생성한다.
- blog draft download는 `내가 보낸 요청` 기준으로 생성된다.
- GitHub Actions CI가 통과한다.

## 다음

dashboard가 이제 세션을 보기만 하는 화면에서 결과를 정리하는 화면으로 이동하고 있다.

남은 후보는 이렇다.

- publish-ready session marker
- dashboard 안에서 published/deferred 표시
- structured JSON review findings
- TUI replay mode

agent 작업대에서 중요한 것은 실행보다 기록의 재사용성이다. 필터와 export는 그 기록을 다시
작업 가능한 형태로 만드는 작은 계층이다.
