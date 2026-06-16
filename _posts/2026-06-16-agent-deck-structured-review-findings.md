---
title: "Agent Deck 7차 고도화: structured review findings"
date: 2026-06-16 17:01:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, review, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

Agent Deck dashboard에 filter와 export를 붙이면서 다음 병목이 보였다. review output을 표로
만드는 과정이 아직 agent가 쓴 자연어에 많이 기대고 있었다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`5f7aafe`](https://github.com/hoonapps/agent-deck/commit/5f7aafe)

## 이번 변경

`/review` prompt에 structured findings 형식을 추가했다.

```text
AGENT_DECK_FINDINGS_JSON
[
  {
    "severity": "high",
    "location": "src/app.js:42",
    "summary": "short actionable finding",
    "evidence": "why this matters"
  }
]
END_AGENT_DECK_FINDINGS_JSON
```

이 블록이 있으면 `agent-deck findings`, `/findings`, web dashboard export가 이 JSON을 먼저
읽는다. 블록이 없거나 JSON이 깨져 있으면 기존 자연어 parsing으로 fallback한다.

## 왜 JSON 블록인가

review 결과는 사람이 읽기 좋아야 하지만, 다시 쓰기 좋은 형태도 필요하다.

dashboard filter는 `severity`, `agent`, `location`, `summary`를 기준으로 움직인다. 이 값을
문장에서 추측하면 계속 애매한 케이스가 생긴다.

- `Blocking:`은 high로 보면 되지만 모든 agent가 같은 단어를 쓰지는 않는다.
- 파일 경로와 line number는 문장 중간에 섞인다.
- test gap과 bug가 한 bullet 안에 같이 들어갈 수 있다.
- 긴 설명이 붙으면 summary와 evidence의 경계가 흐려진다.

그래서 이번에는 agent output을 사람이 읽는 설명과 기계가 읽는 findings로 나눴다. 설명은
그대로 남기고, export는 구조화 블록을 우선 신뢰한다.

## transcript fence도 같이 정리

이번 작업에서 transcript 저장 방식도 손봤다.

기존에는 agent output을 항상 ` ```text ` fence 안에 넣었다. 그런데 agent가 Markdown code
block을 출력하면 transcript parser가 중간 fence를 닫는 fence로 착각할 수 있다.

이제 저장할 message 안에 triple backtick이 있으면 바깥 fence를 더 길게 만든다.

~~~text
````text
```js
console.log("nested fence");
```
````
~~~

작은 수정이지만 replay, findings, blog draft가 모두 transcript parser에 기대고 있어서 꽤
중요한 방어선이다.

## parser 순서

findings 추출 순서는 이렇게 바꿨다.

```text
1. AGENT_DECK_FINDINGS_JSON marker block 탐색
2. agent-deck-findings code fence 탐색
3. JSON array 또는 { findings: [...] } 정규화
4. severity alias 정리
5. 실패하면 기존 plain-text heuristic 사용
```

`blocker`, `blocking`, `critical`은 `high`로 정규화한다. `file`과 `line`이 따로 오면
`src/web.js:44` 같은 location으로 합친다.

## 검증

이번 변경은 parser와 transcript writer 양쪽을 테스트했다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

추가한 테스트:

- structured JSON block이 있으면 자연어 bullet을 중복 추출하지 않는다.
- `blocker` severity가 `high`로 정규화된다.
- `file` + `line`이 location으로 합쳐진다.
- agent output 안에 Markdown fence가 있어도 transcript가 다시 parse된다.

GitHub Actions CI도 통과했다.

## 다음

review findings가 안정되면 dashboard에서 다음 기능을 붙이기 쉬워진다.

- published/deferred session marker
- review finding별 처리 상태
- high severity만 모아 보는 inbox
- blog draft에 실제 변경 commit과 검증 명령 자동 포함

Agent AX 도구에서 transcript는 단순 로그가 아니다. agent가 남긴 판단을 다시 검증하고, 필요한
부분만 제품 지식으로 남기기 위한 원본 데이터다. 이번 structured findings는 그 원본 데이터를
조금 더 다루기 쉬운 형태로 만든 작업이다.
