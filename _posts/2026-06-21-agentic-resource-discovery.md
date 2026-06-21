---
title: "AI Radar: ARD가 agent 생태계의 discovery layer가 되는 시점"
date: 2026-06-21 22:45:00 +0900
categories: [AI, DeepDive]
tags: [ai, agent, ard, mcp, a2a, skills, discovery, governance, backend, ax]
image: /assets/img/posts/2026/06/ard-agentic-resource-discovery.jpg
---

이번 주에 `Agentic Resource Discovery`, 줄여서 ARD가 공개됐다. GitHub, Google, Hugging Face,
Microsoft 쪽에서 같은 날 관련 글과 구현을 내놓았다. 처음 보면 또 하나의 agent 표준처럼 보이지만,
내가 보기에는 MCP 다음에 자연스럽게 나오는 문제를 건드린다.

MCP는 agent가 tool을 호출하는 표준 경로를 만들었다. A2A는 agent끼리 통신하는 흐름을 잡고 있다.
Skills는 agent에게 특정 작업 방식을 주입하는 포맷으로 자리 잡고 있다. 그런데 이 셋은 공통된 전제를
갖고 있다.

어떤 tool, agent, skill을 써야 하는지는 이미 사람이 알고 있다는 전제다.

실제 운영에서는 이 전제가 금방 깨진다. tool이 많아질수록 agent에게 모든 것을 미리 붙일 수 없고,
모든 tool 설명을 context에 넣을 수도 없다. 그래서 다음 병목은 연결이 아니라 discovery다.

## 본 자료

- GitHub Changelog: [Agent finder for GitHub Copilot now available](https://github.blog/changelog/2026-06-17-agent-finder-for-github-copilot-now-available/)
- Google Developers Blog: [Announcing the Agentic Resource Discovery specification](https://developers.googleblog.com/announcing-the-agentic-resource-discovery-specification/)
- Hugging Face Blog: [Agentic Resource Discovery: Let agents search](https://huggingface.co/blog/agentic-resource-discovery-launch)
- GitHub: [ards-project/ard-spec](https://github.com/ards-project/ard-spec)

대표 이미지는 Google Developers Blog의 ARD 글 이미지를 사용했다.

## 핵심 메모

ARD는 agentic resource를 cataloging, searching, discovering하기 위한 draft specification이다.
ARD spec 저장소는 MCP server, A2A agent card, Skill, API 같은 callable service를 federated
discovery service 네트워크에서 찾는 표준이라고 설명한다. 2026년 6월 21일 기준 상태는 v0.9 draft다.

GitHub는 이 흐름을 `Agent finder`로 Copilot에 붙였다. GitHub Changelog 기준으로 agent finder는
MCP server, skill, canvas, agent, tool을 미리 전부 연결하지 않고, task 설명을 기준으로 사용할 수
있는 resource index를 검색한다. 그리고 ranked match를 돌려준다.

Hugging Face는 `Discover Tool`을 reference implementation으로 소개했다. Hub에 있는 Skills, ML
application, MCP server를 ARD catalog entry로 검색할 수 있게 하는 방향이다.

Google 글에서 내가 중요하게 본 문장은 세 질문이다.

```text
어디에 필요한 capability가 있는가
어떤 capability를 실제로 써야 하는가
그 capability가 안전한지 어떻게 검증하는가
```

이 세 질문이 ARD의 핵심이다. 단순 검색이 아니라 discovery, ranking, verification을 같이 다룬다.

## 왜 지금 중요한가

agent 개발은 지금 너무 쉽게 tool을 붙이는 방향으로 흐르고 있다. MCP server 하나를 추가하고,
internal API 하나를 열고, 문서 검색 tool 하나를 붙이는 일은 어렵지 않다. 문제는 그 다음이다.

tool이 10개일 때는 사람이 관리할 수 있다. 100개가 되면 agent에게 모두 설명하는 순간 context가
무거워진다. 1,000개가 되면 어떤 tool이 최신인지, 누가 관리하는지, 어떤 권한으로 호출해야 하는지
추적하기 어렵다.

그래서 ARD가 말하는 registry 모델은 꽤 현실적이다.

```text
publisher
-> catalog manifest
-> registry / discovery service
-> agent query
-> ranked resource
-> connection / execution
```

agent가 모든 tool을 들고 다니는 대신, 필요한 순간에 찾고, 검증하고, 연결하는 쪽으로 간다. 이건
검색 UX 문제가 아니라 agent runtime 구조 문제에 가깝다.

## 백엔드 관점에서 보면

백엔드에서는 이미 비슷한 문제를 여러 번 겪었다.

- service discovery
- API gateway
- package registry
- plugin marketplace
- internal developer portal
- feature flag registry
- secret and policy management

ARD는 이 흐름을 agent resource 쪽으로 가져온다. 차이는 agent가 검색 결과를 보고 실제 action까지
이어갈 수 있다는 점이다. 그래서 일반적인 service discovery보다 위험도가 높다.

예를 들어 운영 장애를 분석하는 agent가 있다고 하자. 이 agent는 observability tool, deployment
history, runbook, incident ticket, feature flag, customer support log를 찾아야 할 수 있다. 여기서
중요한 건 "찾을 수 있다"가 아니다.

```text
어떤 registry를 신뢰할 것인가
어떤 resource를 노출할 것인가
어떤 resource는 읽기만 허용할 것인가
누가 publish한 capability인지 검증할 것인가
연결 후 실행 권한은 어디서 제한할 것인가
실행 로그와 감사 로그는 어디에 남길 것인가
```

이 질문을 빼면 discovery는 곧 attack surface가 된다.

## MCP와의 관계

MCP와 ARD는 경쟁 관계라기보다 층이 다르다.

MCP는 tool call을 어떻게 할지에 가깝다. ARD는 그 tool을 어떻게 찾고, 어떤 catalog에서 가져오고,
어떤 metadata를 보고 신뢰할지를 다룬다.

내 기준으로는 이렇게 나눠서 보는 게 편하다.

| 층 | 질문 |
| --- | --- |
| ARD | 어떤 resource를 찾아야 하는가 |
| MCP / A2A / API | 찾은 resource를 어떻게 호출할 것인가 |
| Auth runtime | 누구 권한으로 어디까지 실행할 것인가 |
| Audit / policy | 실행을 어떻게 기록하고 제한할 것인가 |

ARD만으로 production agent가 안전해지지는 않는다. 하지만 resource discovery를 표준화하면, 그 위에
policy와 governance를 얹을 자리가 생긴다.

## 내가 볼 지점

ARD에서 가장 중요한 건 "검색이 된다"가 아니라 "검증 가능한 검색이 된다"다.

agent가 어떤 tool을 찾았다고 해서 바로 연결하면 안 된다. 최소한 publisher identity, catalog
signature, version, permission, data boundary, compliance metadata 같은 정보가 같이 따라와야 한다.
그리고 enterprise 환경에서는 public registry보다 private registry가 더 중요해질 가능성이 크다.

내가 앞으로 볼 지점은 다섯 가지다.

- `ai-catalog.json` 같은 manifest가 실제로 얼마나 작성하기 쉬운가
- private registry와 allowlist가 운영하기 쉬운가
- resource ranking이 LLM prompt보다 안정적인가
- 잘못된 catalog나 악성 resource를 어떻게 걸러내는가
- discovery와 execution 권한이 분리되는가

특히 마지막이 중요하다. 찾는 것과 실행하는 것은 다른 권한이어야 한다. 검색은 넓게 하더라도 실행은
좁게 가야 한다.

## 판단

**Watch.**

ARD는 아직 draft spec이다. 바로 production에 넣을 단계라고 보기는 이르다. 하지만 방향은 중요하다.
agent 생태계가 커질수록 문제는 "어떤 tool을 만들 수 있는가"에서 "어떤 tool을 안전하게 찾고 붙일 수
있는가"로 이동한다.

MCP가 agent tool 호출의 연결면을 만들었다면, ARD는 그 앞단의 discovery layer를 잡으려는 시도다.
둘이 같이 자리 잡으면 agent runtime은 다음 구조에 가까워질 수 있다.

```text
task intent
-> resource discovery
-> trust / policy check
-> scoped connection
-> tool execution
-> audit log
```

이 흐름이 제대로 잡히면 agent는 더 많은 tool을 들고 다니는 방식에서 벗어날 수 있다. 필요한 것을
찾고, 검증하고, 좁은 권한으로 연결하는 쪽이 production에 더 가깝다.
