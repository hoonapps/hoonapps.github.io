---
title: "AI Radar: agent authorization이 제품 경계가 되는 시점"
date: 2026-06-17 14:50:00 +0900
categories: [AI, OpenSource]
tags: [ai, agent, mcp, authorization, security, llm, open-source, backend, ax]
image: /assets/img/posts/2026/06/arcade-secure-action-layer.png
---

AI agent 이야기는 보통 모델 성능, prompt, workflow builder에서 시작한다. 그런데 실제 서비스에
붙이려고 하면 질문이 바뀐다.

이 agent가 누구 권한으로, 어떤 도구를, 어느 범위까지 실행할 수 있는가.

오늘은 그 지점을 기준으로 Arcade.dev를 봤다. Arcade는 2026년 6월 15일에 Series A 6천만 달러
투자를 발표했고, 자신들을 production AI agent를 위한 secure action layer로 설명한다. 단순히
투자 소식이라서 본 것은 아니다. MCP가 agent와 tool을 연결하는 표준 흐름이 되면서, 이제 중요한
경계가 "연결"에서 "권한 있는 실행"으로 넘어가고 있다는 신호로 봤다.

## 본 자료

- 공식 발표: [Arcade Raises $60M to Become the Secure Action Layer Behind Every Production AI Agent](https://www.businesswire.com/news/home/20260615229631/en/Arcade-Raises-%2460M-to-Become-the-Secure-Action-Layer-Behind-Every-Production-AI-Agent)
- 제품 설명: [Arcade.dev](https://www.arcade.dev/)
- 오픈소스 framework: [ArcadeAI/arcade-mcp](https://github.com/arcadeai/arcade-mcp)

대표 이미지는 Arcade 공식 사이트의 Open Graph 이미지를 사용했다.

## 핵심 메모

Arcade가 잡고 있는 문제는 꽤 명확하다.

agent가 Slack, Gmail, GitHub, CRM, 내부 API 같은 tool을 호출하려면 인증 정보가 필요하다. 쉬운
방법은 service account나 넓은 token을 agent에게 주는 것이다. 하지만 이 방식은 운영 환경에서
바로 위험해진다.

- 사용자의 실제 권한과 agent의 실행 권한이 분리되지 않는다.
- 어떤 agent가 어떤 user를 대신해 어떤 resource에 접근했는지 추적하기 어렵다.
- prompt injection이나 잘못된 tool call이 발생했을 때 blast radius가 커진다.
- 보안 리뷰에서 "이 agent가 할 수 없는 일"을 증명하기 어렵다.

Arcade가 말하는 action layer는 이 사이에 runtime을 두는 방식이다. agent는 reasoning을 하고,
runtime은 인증, 권한, tool 실행, 감사 로그를 맡는다.

```text
LLM / Agent
-> MCP client
-> authorization runtime
-> tool / business system
```

이 구조에서 중요한 점은 token을 LLM이나 client에 그대로 노출하지 않는다는 것이다. `arcade-mcp`
README도 tool이 OAuth scope를 선언하면 Arcade가 인증, token refresh, call 단위 scoping을 처리하고,
client와 LLM은 secret 값을 보지 않는다고 설명한다.

## 왜 지금 봐야 하나

MCP 서버를 하나 붙이는 것은 이제 어렵지 않다. 문제는 그 다음이다.

agent가 읽기만 하는가, 쓰기도 하는가. 쓰기 작업이라면 user별 권한을 어떻게 확인하는가. tool
호출 실패를 재시도해도 되는가. 결제, 이메일 발송, DB 변경처럼 되돌리기 어려운 행동은 누가
승인하는가. 그리고 나중에 감사할 때 어떤 로그가 남는가.

백엔드 관점에서는 이게 낯선 문제가 아니다. 결국 기존 시스템에서도 오래 다뤄온 문제다.

- authentication
- authorization
- audit log
- policy enforcement
- secret management
- idempotency
- rollback boundary

다만 agent가 들어오면 이 경계가 더 중요해진다. 사람은 화면을 보고 멈추거나 확인을 요청할 수
있지만, agent는 목표를 달성하기 위해 여러 tool call을 빠르게 이어갈 수 있다. 그래서 agent
runtime에는 "무엇을 할 수 있는지"뿐 아니라 "무엇을 절대 할 수 없는지"가 코드와 정책으로
박혀 있어야 한다.

## 내 기준의 체크리스트

agent tool layer를 만들거나 고를 때 앞으로는 이 항목을 먼저 볼 생각이다.

| 항목 | 봐야 할 것 |
| --- | --- |
| Identity | agent가 user를 대신하는지, service account로 도는지 |
| Scope | tool call마다 필요한 권한을 좁힐 수 있는지 |
| Secret | token/API key가 LLM context로 새지 않는지 |
| Audit | 누가, 언제, 무엇을 실행했는지 남는지 |
| Policy | 실행 전후에 block/redact/approval을 걸 수 있는지 |
| Failure | 실패, 재시도, 중복 실행을 제어할 수 있는지 |

이 체크리스트를 통과하지 못하면 production agent라고 부르기 어렵다.

## open-source 관점

`arcade-mcp`는 Python으로 MCP server와 tool을 만드는 framework다. README 기준으로 decorator API,
authorized tool calling, vendor-neutral client 지원, eval, deploy 흐름을 제공한다.

내가 흥미롭게 본 부분은 "MCP server를 빨리 만들 수 있다"보다 "tool이 필요한 auth scope를 선언한다"는
쪽이다. agent 개발이 framework 경쟁에서 runtime/security 경쟁으로 넘어가면, tool 정의에 권한
정보가 붙는 방식은 점점 중요해질 가능성이 크다.

아직 직접 실행까지는 하지 않았다. 그래서 결론은 Adopt가 아니라 Watch다.

## 판단

**Watch.**

Arcade 자체를 바로 쓰자는 뜻은 아니다. 다만 agent product를 만들 때 "모델이 똑똑한가"보다 먼저
"action layer가 안전한가"를 봐야 한다는 신호로는 충분하다.

특히 다음 조건에 해당하면 이 흐름을 계속 봐야 한다.

- agent가 외부 SaaS나 내부 API에 쓰기 작업을 한다.
- user별 권한이 중요한 B2B 제품이다.
- MCP server를 직접 만들고 있다.
- 보안 리뷰를 통과해야 하는 agent workflow를 만들고 있다.
- tool call audit log가 제품 요구사항에 들어간다.

## 다음에 해볼 것

다음에는 `arcade-mcp`를 로컬에서 간단히 실행해보고 싶다.

확인할 것은 세 가지다.

```text
1. custom MCP tool을 얼마나 빨리 만들 수 있는가
2. auth scope 선언이 코드에서 어떻게 보이는가
3. 실패한 tool call과 audit log를 개발자가 어떻게 확인하는가
```

이 세 가지가 괜찮으면 Agent Deck 같은 로컬 agent cockpit에도 참고할 부분이 있다. 지금 만든
preflight와 model 선택은 agent 실행 전 단계의 안정성이고, 다음 경계는 agent가 실행하는 action의
권한과 기록이다.
