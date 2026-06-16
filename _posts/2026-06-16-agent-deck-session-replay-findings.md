---
title: "Agent Deck 4차 고도화: 세션 replay와 리뷰 findings table"
date: 2026-06-16 16:29:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, transcript, review, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

직전 글에서 다음으로 볼 항목을 이렇게 적었다.

- review 결과를 findings table로 구조화
- transcript replay와 session browser
- `agent-deck-web` dashboard

이번에는 앞의 두 개를 먼저 닫았다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`e713975`](https://github.com/hoonapps/agent-deck/commit/e713975)

## 왜 replay가 필요한가

Agent 작업은 한 번 실행하고 끝나는 것이 아니다. 어떤 요청을 했고, 어떤 agent가 답했고,
어디서 테스트를 돌렸고, 어떤 리뷰가 나왔는지를 다시 읽을 수 있어야 한다.

기존 transcript는 Markdown 원본으로 남았다. 사람이 열어보면 읽을 수 있지만, 매번 긴 파일을
스크롤하는 것은 불편하다. 그래서 CLI에서 바로 compact timeline으로 보는 기능을 넣었다.

```bash
agent-deck replay .agent-deck/sessions/session.md --limit 40
```

출력은 이런 식이다.

```text
2026-06-16T00:01:00.000Z  YOU -> review -> claude  blocking issue 찾아줘
2026-06-16T00:02:00.000Z  CLAUDE                  - Blocking: src/app.js:12...
```

이 기능은 나중에 TUI 안에서 session replay를 만들기 위한 첫 단계다. 지금은 CLI지만,
parser와 formatter를 공용으로 빼두었기 때문에 같은 로직을 TUI나 web dashboard에서도
재사용할 수 있다.

## session browser

저장된 transcript 목록도 CLI에서 볼 수 있게 했다.

```bash
agent-deck sessions
```

출력에는 수정 시각, 파일 크기, 파일명이 나온다.

```text
2026-06-16T07:28:23.676Z      292  review.md
```

작아 보이지만 중요하다. agent 작업을 매일 남기기 시작하면 `.agent-deck/sessions` 아래에
파일이 계속 쌓인다. "오늘 어떤 세션을 글로 정리하지?"를 고르려면 목록과 replay가 먼저다.

## review findings table

이전에는 `/review`로 리뷰 요청을 보낸 뒤, agent 응답을 사람이 읽고 판단했다. 이번에는
그 리뷰 출력을 Markdown table로 뽑는 기능을 추가했다.

TUI 안에서는 이렇게 쓴다.

```text
/findings review-table
```

세션이 끝난 뒤 CLI로도 만들 수 있다.

```bash
agent-deck findings .agent-deck/sessions/session.md --out findings.md
```

출력 파일은 이런 형태다.

```markdown
| # | Severity | Agent | Location | Summary | Evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | high | claude | src/app.js:12 | Blocking: ... | review: ... |
```

지금은 heuristic 기반이다. review output에서 bullet, numbered item, `Blocking`, `Missing`,
`Regression`, 파일 경로 같은 패턴을 찾아 findings row로 바꾼다. 완벽한 정적 분석기가
아니라, agent 리뷰를 사람이 검토하기 좋은 표로 바꾸는 첫 단계다.

다음 단계는 reviewer에게 JSON schema로 findings를 내게 하고, 그 구조를 그대로 import하는
방식이다. 하지만 처음부터 엄격한 schema로 가면 기존 transcript를 활용하기 어렵다. 그래서
이번에는 사람이 이미 받은 review output에서도 동작하는 방향을 택했다.

## 공용 transcript parser

이번 작업에서 `src/transcript-tools.js`를 새로 만들었다.

담당하는 일은 네 가지다.

- transcript Markdown parsing
- session file listing
- compact replay formatting
- review findings extraction

기존 `blog` 기능도 이 parser를 쓰도록 바꿨다. 이제 blog draft, replay, findings가 같은
transcript 해석 규칙을 공유한다.

이 구조가 중요한 이유는 다음 작업 때문이다. `agent-deck-web`을 만들면 같은 transcript를
웹에서 읽고, findings를 table로 보고, blog draft까지 이어가야 한다. parser가 CLI 안에
갇혀 있으면 다시 뜯어내야 한다.

## 검증

이번 변경은 테스트를 40개까지 늘렸다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

추가로 임시 transcript를 만들어서 실제 CLI smoke도 확인했다.

```text
agent-deck sessions
agent-deck replay
agent-deck findings
```

결과:

- 테스트 40개 통과
- lint 통과
- config validation 통과
- CLI smoke 통과
- npm tarball dry-run 통과
- GitHub Actions CI 통과

## 다음

이제 transcript 루프는 조금 더 단단해졌다.

```text
작업 실행
-> transcript 저장
-> replay로 흐름 확인
-> findings로 리뷰 결과 구조화
-> blog draft 생성
-> 블로그에 정리
```

다음은 자연스럽게 `agent-deck-web`이다. 터미널에서 실행하고, 웹 dashboard에서 세션과
findings를 읽고, publish 후보를 고르는 흐름까지 가면 내가 원하는 AX 작업대에 가까워진다.

Agent AX 엔지니어에게 필요한 것은 "모델에게 물어보기"가 아니라, agent가 만든 작업 기록을
검증 가능한 시스템으로 남기는 일이다. 이번 변경은 그 기록 시스템 쪽으로 간 작은 전진이다.
