---
title: "Agent Deck: 여러 AI 코딩 에이전트를 한 터미널에서 조율하기"
date: 2026-06-16 15:10:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, codex, claude, tui, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-terminal-workspace.png
---

`agent-deck`는 내가 로컬에서 여러 AI 코딩 에이전트를 한 터미널 안에서 조율하려고
만든 TUI 도구다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

## 왜 만들었나

AI 코딩 에이전트를 실제 작업에 쓰다 보면 한 가지 문제가 반복된다.

Codex는 Codex 터미널에서 돌고, Claude는 Claude 터미널에서 돌고, 테스트는 또 다른
터미널에서 돌린다. 그러다 보면 사람이 중간에서 계속 내용을 복사하고, 어느 에이전트가
어떤 맥락을 알고 있는지 기억해야 한다.

`agent-deck`의 목적은 단순하다.

- Codex, Claude 같은 CLI 에이전트를 한 화면에서 본다.
- `/co`, `/cl`, `/all`, `/to` 같은 명령으로 메시지를 라우팅한다.
- 대화와 테스트 결과를 Markdown transcript로 남긴다.
- 최근 대화 히스토리를 다음 agent turn에 주입해서 다른 에이전트가 중간에 합류할 수 있게 한다.
- `F10`이나 `/test`로 테스트를 바로 실행한다.

즉, 모델 API를 감싸는 제품이 아니라 내가 이미 쓰는 CLI들을 한 작업대에 올려두는 도구다.

## 현재 구조

구성은 작게 가져갔다.

| 영역 | 파일 | 역할 |
| --- | --- | --- |
| CLI | `bin/agent-deck.js` | `agent-deck`, `doctor`, `init`, `validate` 실행 |
| 설정 | `src/config.js` | config 로드, agent 정규화, 모델 override 처리 |
| TUI | `src/app.js` | pane, composer, history, activity 렌더링 |
| Agent process | `src/agent.js` | turn mode child process, interactive PTY 실행 |
| Transcript | `src/transcript.js` | Markdown 세션 로그와 공유 히스토리 생성 |
| Git/Test | `src/git.js` | git status, test command 실행 |

기본 모드는 `turn`이다. Codex는 `codex exec`, Claude는 `claude --print`로 호출해서
provider CLI의 불필요한 상태 메시지보다 `You:`와 최종 답변만 보이게 만든다.

필요하면 `interactive` mode도 쓸 수 있다. 이 경우 provider의 원래 터미널 UI를 그대로
PTY 안에서 실행한다.

## 이번에 고도화한 것

오늘은 단순 README 정리가 아니라 실제 사용 전에 실패를 빨리 발견할 수 있게 만드는 쪽을
보강했다.

### 1. 문서를 분리했다

README 하나에 모든 걸 넣지 않고 `docs/`로 나눴다.

- `docs/CONFIGURATION.md`: 설정 스키마, 모델 우선순위, turn/interactive mode
- `docs/ARCHITECTURE.md`: 내부 구성과 메시지 흐름
- `docs/WORKFLOWS.md`: 실제 사용 패턴
- `docs/ROADMAP.md`: 다음 고도화 방향

이 도구는 앞으로 내가 직접 계속 쓸 가능성이 높다. 그래서 설치법보다 중요한 건
"어떤 작업 흐름에 맞는 도구인가"를 문서에 남기는 것이다.

### 2. `agent-deck validate`를 추가했다

TUI를 열기 전에 설정만 검증할 수 있게 했다.

```bash
agent-deck validate --config examples/agent-deck.config.json
```

성공하면 workspace와 agent 목록을 보여준다. CI나 로컬 세션 시작 전에 빠르게 확인하기 좋다.

### 3. agent id와 alias 충돌을 막았다

이전에는 alias가 충돌해도 실행 후 라우팅 단계에서 애매하게 동작할 수 있었다. 이제는
시작 시점에 막는다.

예를 들어 두 agent가 같은 alias를 쓰면 바로 실패한다.

```text
Alias "agent" is used by both "alpha" and "beta"
```

AI 에이전트 조율 도구에서 라우팅이 애매하면 치명적이다. `/co`라고 쳤는데 다른 agent로
가거나, `/to reviewer`가 잘못 해석되면 도구를 믿기 어렵다.

### 4. alias 자동 생성 정책을 고쳤다

이번 검증 과정에서 실제 버그도 하나 잡았다.

`echo-a`, `echo-b` 같은 demo agent가 있을 때, 명시 alias를 줬는데도 내부에서 둘 다
자동 축약 alias `ec`를 추가할 수 있었다. 그래서 demo config가 새 validation에서 실패했다.

정책을 바꿨다.

- `aliases`를 명시하면 그 alias와 전체 `id`만 사용한다.
- 명시 alias가 없을 때만 기본 축약 alias를 만든다.

작은 변경이지만, 도구 라우팅의 예측 가능성을 높이는 쪽이다.

### 5. 테스트를 늘렸다

기존 config 테스트에 더해 CLI 테스트를 추가했다.

- `agent-deck validate`가 TUI를 열지 않고 config를 검증하는지
- invalid config가 실패하는지
- duplicate id/alias를 잡는지
- `maxHistoryChars`가 양의 정수인지
- 명시 alias 정책이 의도대로 동작하는지

현재 기준으로 로컬과 GitHub Actions 모두 통과했다.

```text
npm test
npm run lint
```

## 내가 생각하는 사용 방식

`agent-deck`는 에이전트에게 모든 걸 맡기는 도구가 아니다. 오히려 사람이 작업 경계와
검증 기준을 잡고, 여러 agent를 역할별로 쓰기 위한 도구다.

예를 들면 이런 식이다.

```text
/co 현재 diff를 correctness와 test 관점에서 리뷰해줘.
/cl 같은 diff를 제품/사용성 리스크 관점에서 봐줘.
/test
/all 둘의 의견을 바탕으로 지금 적용할 항목과 보류할 항목을 나눠줘.
```

내가 앞으로 AX 엔지니어로 가려면 중요한 능력은 "AI를 많이 쓰는 것"이 아니라
"AI 작업 단위를 설계하고 검증하는 것"이라고 본다. `agent-deck`는 그 작업 방식을 실험하기
좋은 작은 도구다.

## 다음에 붙이고 싶은 것

다음 고도화 후보는 이렇다.

- turn mode timeout
- agent 상태 표시: idle, running, failed, last exit code
- transcript 일시 정지와 마지막 entry redaction
- 3개 이상 agent를 위한 layout 개선
- `validate`를 CI 예제로 문서화
- Codex-only, Claude-only, local-model config 예제 추가
- asciinema나 screenshot demo 추가

지금은 아직 early working release다. 하지만 방향은 분명하다.

`agent-deck`는 거대한 agent platform이 아니라, 로컬 개발자가 여러 AI 코딩 에이전트를
더 안전하고 재현 가능하게 조율하기 위한 작은 cockpit이다.
