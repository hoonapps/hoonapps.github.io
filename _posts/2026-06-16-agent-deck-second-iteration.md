---
title: "Agent Deck 2차 고도화: 상태바, 리뷰 레인, 세션 export"
date: 2026-06-16 15:55:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, tui, developer-tools, ax]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

이전 글에서 `agent-deck`를 "여러 AI 코딩 에이전트를 한 터미널에서 조율하는 도구"로
정리했다. 오늘은 바로 한 단계 더 밀었다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`7b7d0d8`](https://github.com/hoonapps/agent-deck/commit/7b7d0d8)

## 이번 목표

처음 버전은 여러 agent pane을 한 화면에 두고 메시지를 라우팅하는 데 집중했다. 그런데
실제로 매일 쓰려면 부족한 부분이 바로 보인다.

- 지금 어떤 agent가 일하는 중인지 한눈에 보여야 한다.
- agent가 멈추면 사람이 직접 눈치채기 전에 끊을 수 있어야 한다.
- 리뷰 요청은 매번 손으로 프롬프트를 다시 쓰지 않아야 한다.
- 세션이 끝나면 작업 기록을 바로 export할 수 있어야 한다.
- 터미널 화면이 기능만 있는 게 아니라 cockpit처럼 보여야 한다.

그래서 이번에는 `status`, `timeout`, `review`, `export`, `TUI polish`를 한 번에 넣었다.

## 1. 상태가 보이는 agent pane

이제 각 agent process는 내부 상태를 가진다.

```text
idle
running
failed
timeout
stopped
```

TUI에서는 header와 pane label에 상태가 보인다. pane border도 상태에 따라 색이 바뀐다.
`running`은 노란색, `idle`은 녹색, `timeout`이나 `failed`는 빨간색 계열로 보이게 했다.

작은 변화지만 중요하다. 여러 agent를 동시에 쓰면 "누가 아직 일하고 있지?"를 계속
확인하게 된다. 상태가 화면에 고정되어 있으면 사람이 관리해야 하는 맥락이 줄어든다.

## 2. `/status`

상태를 더 자세히 보고 싶을 때는 `/status`를 쓴다.

```text
/status
```

출력에는 agent별 state, turn count, 마지막 exit code 또는 signal, 마지막 실행 시간이
들어간다.

이건 나중에 agent run을 job처럼 다루기 위한 기초다. agent도 결국 하나의 작업 단위라서
상태, 시작 시각, 종료 결과, duration이 있어야 한다.

## 3. `turnTimeoutMs`

turn mode agent가 오래 멈춰 있으면 자동으로 끊을 수 있게 했다.

```json
{
  "turnTimeoutMs": 300000,
  "agents": [
    {
      "id": "codex",
      "command": "codex",
      "turnTimeoutMs": 120000
    }
  ]
}
```

top-level timeout을 기본값으로 두고, agent별로 override할 수 있다. `0`을 주면 timeout을
끄는 방식이다.

AI agent는 가끔 응답을 오래 붙잡는다. 특히 CLI wrapper를 쓰면 provider 쪽 문제인지,
로컬 command 문제인지, 단순히 모델이 오래 생각하는지 바로 알기 어렵다. timeout은 이
불확실성을 운영 가능한 형태로 자르는 장치다.

## 4. role preset

agent마다 역할을 붙일 수 있게 했다.

```json
{
  "rolePresets": {
    "reviewer": "Find correctness, regression, test, and security issues first."
  },
  "agents": [
    {
      "id": "claude",
      "command": "claude",
      "role": "reviewer"
    }
  ]
}
```

역할은 메시지 앞에 자동으로 들어간다. 매번 "너는 reviewer야" 같은 프롬프트를 반복하지
않아도 된다.

이 구조는 앞으로 `implementer`, `tester`, `architect`, `researcher` 같은 lane으로
확장하기 좋다.

## 5. `/review`

리뷰 요청은 별도 명령으로 뺐다.

```text
/review inspect the current diff and list blocking issues first
```

`reviewAgents`에 지정한 agent들에게 reviewer prompt를 보낸다. 설정이 없으면 reviewer
role을 가진 agent, 또는 Codex/Claude를 기본 후보로 본다.

내가 원하는 방향은 이거다.

```text
/co 구현해줘
/test
/review 이 diff에서 blocking issue만 찾아줘
/export decisions
```

즉, 구현 agent와 리뷰 agent를 같은 터미널에서 역할 분리해서 쓰는 흐름이다.

## 6. `/export`

세션이 끝나면 Markdown summary를 뽑을 수 있다.

```text
/export decisions
```

그러면 transcript 옆에 이런 파일이 생긴다.

```text
.agent-deck/sessions/<session>-decisions.md
```

export에는 user prompt 수, agent output 수, test event 수, 최근 context가 들어간다.
지금은 단순 summary지만, 나중에는 이걸 바로 블로그 초안이나 작업 보고서로 바꿀 수 있다.

이 기능은 내가 블로그를 꾸준히 쓰기 위한 핵심 연결점이다. agent와 작업한 기록을 남기고,
그걸 다시 글로 정리하는 루프를 만들 수 있다.

## 7. 터미널 디자인 polish

이번에 TUI 화면도 손봤다.

- header에 agent 상태를 색상으로 표시
- pane label에 `[idle]`, `[running]`, `[timeout]` 표시
- 상태별 pane border 색상
- 입력창 위에 고정 command hint bar 추가
- focused composer border 색상 정리

터미널 도구도 디자인이 중요하다. 특히 매일 보는 도구라면 기능만 되는 것보다 지금 어디에
있는지, 무엇을 할 수 있는지, 어떤 상태인지 바로 읽혀야 한다.

## 검증

이번 변경은 테스트를 같이 늘렸다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
npm pack --dry-run
```

현재 기준:

- 테스트 24개 통과
- lint 통과
- demo config validation 통과
- npm tarball에 docs/example/source 포함 확인
- GitHub Actions CI 통과

## 다음 단계

아직 더 할 일이 많다.

- `/timeout <agent> <ms>`처럼 TUI 안에서 timeout 변경
- transcript pause/redaction
- 3개 이상 agent layout
- review 결과를 findings table로 구조화
- `blog-from-transcript`로 export를 블로그 초안으로 변환
- local web dashboard 버전

하지만 오늘 변화로 `agent-deck`는 단순한 멀티 pane TUI에서 조금 더 실제 작업용 cockpit에
가까워졌다.

내가 만들고 싶은 건 거대한 AI IDE가 아니다. 매일 쓰는 터미널에서 여러 agent를 안전하게
부르고, 멈추고, 검증하고, 기록하는 작은 AX 작업대다.
