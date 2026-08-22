---
title: "AI Radar: Copilot이 보여준 공유 agent 작업 공간"
date: 2026-08-22 13:45:00 +0900
categories: [AI, DeepDive]
tags: [ai, agent, github-copilot, slack, microsoft-teams, collaboration, cloud-agent, pull-request, governance, backend, ax]
image: /assets/img/posts/2026/08/copilot-shared-agentic-work.jpg
---

GitHub가 2026년 8월 21일에 Slack과 Microsoft Teams 안에서 Copilot cloud agent를 쓰는 흐름을 공개했다.
처음 보면 "Copilot을 메신저에서도 부를 수 있다" 정도로 보일 수 있다. 그런데 내가 보기에는 포인트가
조금 다르다.

coding agent가 개인 IDE 안의 비공개 도우미에서, 팀이 같이 보고 조정하는 공유 작업 세션으로 이동하고
있다.

## 본 자료

- GitHub Changelog: [The new GitHub Copilot experience in Slack](https://github.blog/changelog/2026-08-21-the-new-github-copilot-experience-in-slack/)
- GitHub Changelog: [Shared agentic work with GitHub Copilot in Microsoft Teams](https://github.blog/changelog/2026-08-21-shared-agentic-work-with-github-copilot-in-microsoft-teams/)
- GitHub Changelog: [Agent Plugins 1.0 in VS Code, Copilot CLI, and the Copilot app](https://github.blog/changelog/2026-08-12-agent-plugins-1-0-in-vs-code-copilot-cli-and-the-copilot-app/)
- GitHub Changelog: [MCP allowlists in enterprise managed settings](https://github.blog/changelog/2026-08-06-mcp-allowlists-in-enterprise-managed-settings/)

대표 이미지는 GitHub Changelog의 Copilot Slack 공개 글 이미지를 사용했다.

## 핵심 메모

Slack에서는 `@GitHub`를 DM, 채널, thread에서 부르면 agent session을 시작할 수 있다. GitHub 설명 기준으로
Copilot은 대화 내용과 허용된 GitHub context를 사용해서 코드 질문에 답하고, bug report를 triage하고,
issue를 만들거나 label을 붙이고, failure를 조사하고, secure cloud sandbox에서 변경을 구현하고 검증한 뒤
pull request까지 열 수 있다.

Microsoft Teams 쪽도 비슷하다. channel, thread, direct message에서 `@GitHub`를 부르면 Copilot cloud
agent session이 시작되고, conversation 안의 사람들이 질문을 추가하거나 context를 더 넣거나 작업 방향을
조정할 수 있다. repository write access가 있는 사람은 Copilot에게 변경 작업을 맡길 수 있다.

중요한 건 agent가 Slack이나 Teams에 갇히지 않는다는 점이다.

```text
Slack / Teams 대화
-> Copilot cloud agent session
-> secure cloud sandbox
-> artifact / diff / preview
-> pull request
-> terminal, Copilot app, IDE에서 이어서 작업
```

이 흐름은 coding agent의 시작점이 IDE만이 아니라 팀 대화가 될 수 있다는 뜻이다.

## 왜 지금 중요한가

개발팀의 실제 의사결정은 IDE 안에서만 일어나지 않는다.

장애 대응은 Slack thread에서 시작될 수 있고, 회의 중에 나온 action item은 Teams chat에 남는다. 제품
기획의 작은 변경도 issue보다 먼저 대화로 흘러간다. 지금까지는 사람이 그 대화를 읽고, issue로 옮기고,
브랜치를 만들고, 구현하고, PR을 열었다.

Copilot의 이번 흐름은 그 중간 구간을 agent에게 넘기려는 시도다.

```text
대화에서 문제 발견
-> agent에게 조사 지시
-> 팀이 같은 thread에서 진행 상황 확인
-> 필요한 context 추가
-> agent가 PR 생성
-> 사람이 review와 merge 판단
```

개인 agent와 다른 점은 투명성이다. 한 사람이 로컬에서 agent에게 일을 시키면 prompt, 판단, 중간 결과가
개인 작업 공간에 묻히기 쉽다. 반대로 channel이나 thread에서 agent session이 열리면 팀이 같은 흐름을
본다. 누가 어떤 지시를 넣었고, agent가 어떤 방향으로 작업 중인지, 어디서 멈춰야 하는지 공유된다.

이건 단순 협업 UX가 아니라 운영 방식의 변화에 가깝다.

## 백엔드 관점에서 보면

공유 agent session을 제품으로 만들려면 백엔드는 꽤 많은 상태를 관리해야 한다.

- conversation id
- 참가자 identity
- repository permission
- session owner와 steering 권한
- cloud sandbox lifecycle
- tool call log
- diff와 artifact version
- PR attribution identity
- budget과 usage limit
- approval rule
- audit trail

특히 권한 경계가 중요하다. Slack channel에 있는 사람이 모두 repository write access를 갖는 것은 아니다.
Teams 대화에 참여했다고 해서 agent에게 merge 권한을 줄 수도 없다. 그래서 대화 권한과 GitHub 권한을
분리해서 봐야 한다.

```text
conversation participant
!= repository collaborator
!= agent session controller
!= PR approver
```

이 네 가지를 섞으면 운영 사고가 난다.

GitHub가 별도 approval을 언급한 것도 이 지점 때문이다. Slack integration identity나 Microsoft Teams
Copilot integration identity가 만든 PR에 대해 repository administrator가 추가 승인을 요구할 수 있다.
팀은 빠르게 움직일 수 있지만, agent가 만든 코드가 사람 검토 없이 바로 들어가면 안 된다.

## Agent Plugins와 같이 보면

8월 12일 공개된 Agent Plugins 1.0도 같이 봐야 한다. GitHub는 Agent Plugins 1.0을 VS Code, Copilot
CLI, GitHub Copilot SDK, Copilot app에서 generally available로 열었다. 하나의 plugin package가 skill과
MCP server 설정을 담고, 여러 compatible agent client에서 쓸 수 있는 구조다.

이 흐름을 Slack/Teams와 합치면 그림이 더 선명해진다.

```text
collaboration surface
-> shared agent session
-> plugin / MCP capability
-> cloud sandbox execution
-> PR and review workflow
-> managed settings and allowlist
```

agent가 팀 대화에서 바로 실행되려면 tool을 아무거나 붙일 수 없다. 어떤 plugin이 설치 가능한지, 어떤
MCP server가 허용되는지, 어떤 marketplace를 신뢰할지 조직 정책이 필요하다. GitHub가 enterprise managed
settings와 MCP allowlist를 같이 밀고 있는 이유도 여기에 있다.

agent가 IDE 밖으로 나오면 governance도 IDE 밖으로 나와야 한다.

## 조심할 지점

공유 agent 작업은 편하지만, 실패하면 더 시끄럽다.

개인 IDE에서 잘못된 변경을 만들면 한 사람의 local branch에서 끝날 수 있다. 하지만 Slack/Teams thread에서
agent가 잘못된 방향으로 움직이면 여러 사람이 그 흐름을 보고, 중간에 잘못된 context를 추가하고, PR까지
만들 수 있다.

그래서 필요한 질문은 이쪽이다.

```text
누가 agent session을 시작할 수 있는가
누가 방향을 바꿀 수 있는가
누가 stop할 수 있는가
어떤 대화 내용이 code context로 들어가는가
agent가 만든 artifact는 어디에 남는가
PR attribution은 누구에게 붙는가
budget 초과나 sandbox 실패는 어떻게 보이는가
```

이 질문을 제품이 명확히 다뤄야 한다. 그렇지 않으면 shared agent session은 협업 도구가 아니라 noisy
automation이 된다.

## 판단

**Watch.**

Copilot의 Slack/Teams 통합은 메신저 bot 추가가 아니다. coding agent가 팀의 대화, 권한, 예산, review
흐름 안으로 들어오는 장면이다.

내가 앞으로 볼 지점은 세 가지다.

- shared agent session에서 steering 권한과 repository 권한이 얼마나 잘 분리되는가
- Slack/Teams에서 시작한 작업이 IDE, CLI, PR review로 얼마나 자연스럽게 이어지는가
- Agent Plugins, MCP allowlist, managed settings가 실제 조직 정책으로 버틸 수 있는가

agent가 개인 생산성 도구에 머무를 때는 좋은 답변과 빠른 수정이 중요했다. 팀 협업 공간으로 들어오면
이야기가 달라진다. 이제 중요한 건 agent가 일을 잘하는 것뿐 아니라, 그 일이 팀이 볼 수 있고 멈출 수
있고 검토할 수 있는 흐름으로 남는지다.
