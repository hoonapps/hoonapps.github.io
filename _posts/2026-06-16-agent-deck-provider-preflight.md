---
title: "Agent Deck 15차 고도화: provider preflight"
date: 2026-06-16 18:31:00 +0900
categories: [Projects, AI]
tags: [agent-deck, ai, agent, cli, tui, codex, claude, auth, model, ax, developer-tools]
image: /assets/img/posts/2026/06/agent-deck-terminal-workspace.png
---

터미널 화면을 다듬다 보니, 먼저 막히는 지점은 색이나 layout이 아니었다. TUI가 뜬 뒤에 Codex가
바로 실패하면 화면이 아무리 좋아도 첫 경험이 망가진다. 특히 모델 이름이 현재 계정에서 지원되지
않거나, provider 로그인이 빠져 있으면 agent pane은 시작하자마자 error log로 채워진다.

그래서 이번에는 Agent Deck에 provider preflight를 넣었다.

저장소: [hoonapps/agent-deck](https://github.com/hoonapps/agent-deck)

이번 커밋:

- [`fe94fa4`](https://github.com/hoonapps/agent-deck/commit/fe94fa4) provider preflight
- [`531b496`](https://github.com/hoonapps/agent-deck/commit/531b496) CI Node 24 update

## 이번 변경

TUI가 열리기 전에 짧은 준비 검사를 먼저 돌린다.

```text
Agent Deck preflight
- codex: Codex logged in
- claude: Claude logged in
```

이미 로그인되어 있으면 그대로 통과한다. 로그인이 없으면 어떤 명령을 실행해야 하는지 보여주고,
interactive terminal에서는 바로 로그인 명령을 시작할지 묻는다.

```text
codex login
claude auth login
```

모델도 시작 전에 고를 수 있게 했다.

```bash
node ./bin/agent-deck.js --select-models
```

provider 기본 모델을 그대로 쓰거나, `gpt-5-codex`, `sonnet` 같은 후보를 고르거나, 직접 모델명을
입력할 수 있다. 계정마다 지원 모델이 다를 수 있으니 기본 config에서는 모델 pin을 제거했다.

## 왜 이렇게 바꿨나

Agent Deck은 브라우저 dashboard가 아니라 터미널 cockpit이 먼저다. 터미널에서 바로 agent를
다뤄야 하는데, 시작 후에야 로그인 문제를 발견하면 흐름이 끊긴다.

이번 변경으로 시작 순서가 이렇게 바뀌었다.

```text
CLI 확인
-> 로그인 상태 확인
-> 필요하면 로그인
-> 필요하면 모델 선택
-> TUI 실행
```

이제 실패가 TUI 안에서 갑자기 터지는 대신, TUI가 뜨기 전에 정리된다.

## 터미널 화면 쪽 정리

첫 화면의 header와 status bar도 조금 손봤다.

- route hint를 `/co /cl`처럼 더 분명하게 표시한다.
- agent 수, reviewer 수, model pin 수를 header에 보여준다.
- pane title에 role을 같이 표시한다.
- 시작 log에 어떤 명령부터 쓰면 되는지 남긴다.

사용 흐름은 이렇다.

```bash
cd /Users/kimyanghoon/Desktop/dev/agent-deck
node ./bin/agent-deck.js --select-models
```

데모만 보고 싶으면 provider 로그인이 필요 없는 echo config를 쓰면 된다.

```bash
node ./bin/agent-deck.js --config examples/demo.config.json
```

## 검증

이번 변경은 아래로 확인했다.

```text
npm test
npm run lint
node ./bin/agent-deck.js validate --config examples/demo.config.json
node ./bin/agent-deck.js validate --config examples/agent-deck.config.json
node ./bin/agent-deck.js setup --config examples/agent-deck.config.json --select-models
npm pack --dry-run
```

로컬에서는 Codex와 Claude가 둘 다 로그인 상태로 잡혔다. 그래서 preflight는 로그인 명령을 띄우지
않고 통과했다.

GitHub Actions도 Node 24 기준으로 올렸다. `actions/checkout@v5`, `actions/setup-node@v6` 조합으로
CI를 다시 돌렸고 성공했다.

## 다음

이제 남은 건 실제 TUI의 조작감이다. 다음에는 모델 선택을 단순 prompt가 아니라 더 편한 terminal
picker처럼 만들고, agent pane이 실패했을 때 원인과 다음 행동을 더 짧게 보여주는 쪽을 볼 생각이다.
