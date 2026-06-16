---
title: "Agent Deck 8차 고도화: session status marker"
date: 2026-06-16 17:12:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, dashboard, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

Agent Deck dashboard가 세션을 보여주고, findings를 필터링하고, blog draft를 내려받는 단계까지
왔다. 이번에는 세션을 발행 큐로 다루기 위한 작은 상태 마커를 붙였다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`23b2685`](https://github.com/hoonapps/agent-deck/commit/23b2685)

## 이번 변경

dashboard에서 각 transcript session을 세 가지 상태로 표시할 수 있게 했다.

- `draft`
- `published`
- `deferred`

기본값은 `draft`다. 글로 정리한 세션은 `published`, 지금은 미뤄둘 세션은 `deferred`로 바꿀 수
있다. 세션 목록과 detail header 양쪽에 status badge가 나오고, detail 화면에서 버튼으로 상태를
바꾼다.

## 왜 필요한가

Agent Deck의 transcript는 계속 쌓인다. 하루에 agent 작업을 여러 번 돌리면 어떤 세션을 글로
정리했는지, 어떤 세션은 나중에 봐야 하는지 금방 흐려진다.

파일명만으로는 부족하다.

- review가 끝난 세션인지
- blog draft까지 뽑은 세션인지
- 이미 공개 글로 옮긴 세션인지
- 나중에 다시 볼 세션인지

이 상태가 dashboard에 남아야 작업 흐름이 끊기지 않는다.

## transcript는 건드리지 않는다

상태는 transcript Markdown 파일에 직접 쓰지 않았다. 대신 transcript directory 안에 sidecar
파일을 둔다.

```text
.agent-deck-session-state.json
```

형식은 단순하다.

```json
{
  "review.md": {
    "status": "published",
    "updatedAt": "2026-06-16T08:09:07.763Z"
  }
}
```

transcript는 원본 기록이고, marker는 dashboard의 작업 상태다. 둘을 섞지 않는 편이 나중에
export, replay, archive를 다루기 쉽다.

## API

새 endpoint를 추가했다.

```text
POST /api/session-state
```

요청 body:

```json
{
  "file": "review.md",
  "status": "published"
}
```

응답은 session 목록과 같은 형태로 맞췄다.

```json
{
  "name": "review.md",
  "status": "published",
  "statusUpdatedAt": "2026-06-16T08:09:07.763Z"
}
```

HTML form도 같은 저장 로직을 쓴다. 버튼을 누르면 상태를 저장하고 다시 선택된 session 화면으로
돌아온다.

## 검증

이번 변경은 dashboard 테스트를 45개까지 늘렸다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

추가로 로컬 dashboard 서버를 띄워 HTTP로 직접 확인했다.

```text
POST /api/session-state
GET /api/session?file=review.md
GET /api/sessions
```

확인한 것:

- 처음 상태는 `draft`다.
- `published`, `deferred` 상태가 sidecar JSON에 저장된다.
- GET API가 저장된 status를 다시 내려준다.
- sidecar 파일은 session 목록에 섞이지 않는다.
- transcript Markdown 파일은 rewrite하지 않는다.
- GitHub Actions CI가 통과한다.

in-app browser 연결은 현재 사용할 수 없어 화면 클릭 검증은 하지 못했다. 대신 HTML 렌더링,
JSON API, form 저장 경로를 테스트와 로컬 HTTP 호출로 확인했다.

## 다음

이제 dashboard는 단순 조회 화면에서 작은 publishing queue 역할을 하기 시작했다.

다음 후보는 finding 단위 상태다.

- accepted
- fixed
- ignored

session 단위로 발행 여부를 표시하고, finding 단위로 처리 여부를 남기면 agent review 결과가
더 이상 흩어지지 않는다. 실행 기록, 검증 기록, 발행 기록이 같은 도구 안에서 이어지는 형태가
Agent AX 작업대에 더 잘 맞는다.
