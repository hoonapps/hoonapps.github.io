---
title: "Agent Deck 3차 고도화: transcript 제어와 블로그 초안 루프"
date: 2026-06-16 16:15:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, tui, transcript, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-polished-tui.png
---

이전 글의 마지막에 `agent-deck` 다음 작업으로 적어둔 항목들이 있었다.

- TUI 안에서 timeout 변경
- transcript pause/redaction
- 3개 이상 agent layout
- `blog-from-transcript`
- 터미널 cockpit polish

이번 커밋에서 이 묶음을 실제로 넣었다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋: [`66e2f1d`](https://github.com/hoonapps/agent-deck/commit/66e2f1d)

## 왜 transcript 제어가 먼저였나

Agent 작업을 블로그에 남기려면 기록이 있어야 한다. 그런데 모든 기록을 그대로 남기면
공개하기 어렵다.

작업 중에는 민감한 파일명, 로컬 경로, 아직 정리되지 않은 판단, 실패한 실험이 섞인다.
그래서 "기록한다"와 "공개한다" 사이에 제어 장치가 필요했다.

이번에 추가한 명령은 세 가지다.

```text
/record off
/record on
/redact-last
```

`/record off`는 transcript 기록을 잠깐 멈춘다. `/record on`은 다시 켠다.
`/redact-last`는 가장 마지막 transcript record를 제거하고 파일을 다시 쓴다.

이건 단순 편의 기능이 아니다. 앞으로 agent와 만든 작업을 매일 블로그에 남기려면,
기록을 안전하게 다루는 습관이 먼저 있어야 한다.

## runtime timeout

기존에는 config에서만 timeout을 정할 수 있었다.

```json
{
  "turnTimeoutMs": 300000
}
```

이번에는 실행 중에도 바꿀 수 있게 했다.

```text
/timeout codex 120000
```

Agent를 실제로 돌리면 작업마다 기다릴 수 있는 시간이 다르다. 짧은 리뷰는 2분이면 충분하고,
큰 리팩터링 검토는 5분 이상 볼 수도 있다. timeout은 config에만 있으면 운영 도구가 아니라
초기 설정값에 가깝다. TUI 안에서 바꿀 수 있어야 작업 흐름에 맞는다.

## 3개 이상 agent layout

이전 TUI는 사실상 2개 agent에 맞춰져 있었다. 이제 agent가 3개 이상이면 2열 grid로 배치한다.

```text
1 agent  -> 1 x 1
2 agents -> 1 x 2
3 agents -> 2 x 2
4 agents -> 2 x 2
```

아직 완성형은 아니다. 다음에는 keyboard focus 이동과 lane 개념을 붙여야 한다.
하지만 최소한 Codex, Claude, local model, shell agent 같은 조합을 한 화면에 놓을 수 있는
기초는 생겼다.

## blog draft CLI

이번에 가장 중요한 연결은 이 명령이다.

```bash
agent-deck blog .agent-deck/sessions/session.md --out draft.md --title "Agent Deck 작업 기록"
```

transcript를 읽어서 한국어 블로그 초안으로 바꾼다. 지금은 완성 글을 자동 작성하는 기능이
아니라, publish 전에 사람이 정리할 수 있는 skeleton을 만든다.

초안에는 이런 정보가 들어간다.

- 내가 보낸 요청 수
- agent 응답 수
- 테스트/검증 이벤트 수
- 최근 작업 흐름
- 정리할 체크리스트

내가 원하는 루프는 이거다.

```text
agent-deck로 작업
-> transcript 저장
-> 민감한 record pause/redact
-> blog draft 생성
-> 사람이 결론과 검증 결과를 정리
-> 블로그에 공개
```

AI 시대의 블로그는 단순 회고가 아니라 작업 로그와 검증 결과를 연결하는 곳이 되어야 한다.

## 터미널 cockpit polish

이번 TUI는 기능만 추가하지 않고 화면도 같이 다듬었다. 터미널 도구도 매일 보는 화면이면
상태가 잘 읽히고, 손에 익는 구성이어야 한다.

- 상단 2줄 header
- active agent 표시
- `record:on`, `record:paused` 상태 표시
- agent별 `IDLE`, `RUNNING`, `FAILED`, `TIMEOUT`, `STOPPED` 배지
- active pane marker
- 짧은 command hint bar
- 입력창 label에 현재 route 표시
- activity log 포맷 정리

터미널 도구도 매일 보면 제품이다. 특히 agent를 여러 개 돌릴 때는 "예쁜 화면"보다
"상태를 빨리 읽을 수 있는 화면"이 중요하다. 그래서 장식보다 active route, record 상태,
agent state를 먼저 보이게 했다.

## 검증

이번 변경은 테스트도 같이 늘렸다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
npm pack --dry-run
```

결과:

- 테스트 32개 통과
- lint 통과
- demo config validation 통과
- real agent config validation 통과
- npm tarball dry-run 통과
- GitHub Actions CI 통과

## 다음

`agent-deck`는 이제 단순한 멀티 pane TUI에서 조금 더 "agent 작업대"에 가까워졌다.

다음에 볼 것은 세 가지다.

- review 결과를 findings table로 구조화
- transcript replay와 session browser
- `agent-deck-web`처럼 터미널 밖에서 보는 dashboard

내가 가고 싶은 방향은 명확하다. Agent AX 엔지니어는 모델을 호출하는 사람이 아니라,
agent 작업 단위를 설계하고, 실행 환경을 만들고, 검증 가능한 기록으로 남기는 사람이다.

`agent-deck`는 그 방향으로 가기 위한 내 첫 번째 로컬 도구다.
