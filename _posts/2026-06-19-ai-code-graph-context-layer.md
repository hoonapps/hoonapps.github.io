---
title: "AI Radar: code graph가 coding agent의 context layer가 되는 시점"
date: 2026-06-19 17:05:00 +0900
categories: [AI, OpenSource]
tags: [ai, agent, mcp, coding-agent, code-graph, open-source, backend, ax]
image: /assets/img/posts/2026/06/gortex-code-graph-agent-context.jpg
---

Threads에서 `Gortex`라는 오픈소스 도구를 봤다. 코드를 그래프로 인덱싱하고, 그 결과를 CLI, MCP
Server, Web UI로 노출하는 프로젝트다. 처음에는 또 하나의 MCP 도구처럼 보였는데, 조금 더 보면
요즘 coding agent가 어디에서 막히는지 꽤 잘 짚고 있다.

agent가 큰 코드베이스를 다룰 때의 병목은 단순히 모델이 약해서만 생기지 않는다. 필요한 파일을
찾기 위해 계속 grep하고, 파일을 읽고, 주변 맥락을 다시 읽고, 그 과정에서 context window를
소모한다. 그러면 비용도 늘지만 더 큰 문제는 판단 품질이 흔들린다는 점이다.

내가 보기에는 이 흐름이 "더 큰 context window"만으로 해결될 문제는 아니다. coding agent에는
파일 읽기보다 한 단계 위의 context layer가 필요하다.

## 본 자료

- Threads: [Gortex 소개 글](https://www.threads.com/@githubprojects/post/DZo3B_hlHC2/gortex-indexes-repositories-into-a-code-graph-and-exposes-it-via-cli-mcp-server/)
- GitHub: [zzet/gortex](https://github.com/zzet/gortex)
- 논문: [Codebase-Memory: Tree-Sitter-Based Knowledge Graphs for LLM Code Exploration via MCP](https://arxiv.org/abs/2603.27277)

대표 이미지는 Gortex README에 포함된 Web UI 그래프 이미지를 블로그용으로 압축했다.

## 핵심 메모

Gortex README 기준으로 이 프로젝트는 repository를 tree-sitter 기반으로 분석해서 함수, 클래스,
call chain, HTTP route, cross-service contract 같은 정보를 그래프로 만든다. 그리고 그 정보를
MCP tool, CLI, HTTP API, Web UI로 꺼내 쓸 수 있게 한다.

눈에 띄는 주장은 세 가지다.

- 257개 언어/grammar를 분석한다.
- 여러 repository를 하나의 graph로 다룬다.
- agent가 필요한 정보만 질의하게 해서 token 사용량을 크게 줄인다고 설명한다.

GitHub API로 확인한 기준으로는 2026년 6월 19일 현재 Go 기반 Apache-2.0 프로젝트이고, repository
설명에서도 "100% local"과 "up to 50x" token 절감을 전면에 둔다.

여기서 중요한 건 숫자 자체보다 방향이다. agent가 큰 repo에서 계속 파일을 통째로 읽는 방식은
오래 가기 어렵다. 결국 agent가 물어봐야 하는 질문은 이런 쪽으로 바뀐다.

```text
이 함수는 어디에서 호출되는가
이 API route를 바꾸면 어떤 client가 영향을 받는가
이 message topic의 producer와 consumer는 어디인가
이 변경이 test, docs, config 중 어디까지 번지는가
```

이 질문은 text search보다 graph query에 가깝다.

## 왜 지금 봐야 하나

최근 agent tooling은 MCP 연결 자체보다 "연결된 뒤에 무엇을 얼마나 정확히 줄 것인가"로 넘어가고
있다. MCP server를 붙이는 것은 이제 시작점에 가깝다. 문제는 tool 목록이 많아질수록 agent가 어떤
tool을 골라야 하는지, 어떤 context를 읽어야 하는지, 얼마나 좁게 읽어야 하는지가 어려워진다.

GitHub MCP Server 쪽에서도 과거에 tool 수와 token 사용량을 줄이는 이슈가 있었다. tool이 많으면
편해 보이지만, 실제로는 tool selection이 흔들리고 기본 context가 무거워진다. Gortex가 흥미로운
이유도 여기에 있다. "tool을 더 많이 붙이자"보다 "agent가 코드 구조를 질의할 수 있게 하자"에
가깝다.

논문 `Codebase-Memory`도 비슷한 문제를 다룬다. LLM coding agent가 반복적으로 파일을 읽고 검색하는
대신, tree-sitter 기반 knowledge graph를 MCP로 제공하면 token과 tool call을 줄이면서도 코드베이스
이해를 보조할 수 있다는 방향이다. Gortex는 그 흐름을 더 제품/도구 형태로 밀어붙인 사례로 볼 수
있다.

## 백엔드 관점에서 본 가치

백엔드 코드는 단일 파일보다 관계가 중요하다.

controller, service, repository, queue handler, scheduler, event producer, consumer, migration,
feature flag, env var가 따로 존재해도 실제 변경 영향은 연결을 타고 퍼진다. agent가 이 관계를
모르면 작은 수정도 위험해진다.

예를 들어 `OrderStatus` enum 하나를 바꾼다고 해도 실제로 봐야 하는 것은 enum 정의만이 아니다.

```text
API response schema
database column value
message payload
admin filter
batch job condition
external integration mapping
test fixture
```

사람은 경험으로 이 주변을 떠올린다. agent는 매번 찾아야 한다. 그래서 code graph가 잘 만들어져
있으면 agent에게 "읽어야 할 주변"을 좁혀주는 역할을 할 수 있다.

내 기준에서는 이게 coding agent의 context engineering이다. prompt를 잘 쓰는 문제가 아니라,
agent가 탐색할 수 있는 구조화된 지도를 만드는 문제다.

## 다만 조심할 지점

code graph가 만능은 아니다.

첫째, graph의 품질은 parser와 resolver 품질에 크게 의존한다. TypeScript, Go, Java처럼 구조가
명확한 코드는 상대적으로 유리하지만, 동적 import, reflection, runtime DI, framework magic이 많은
코드는 놓치는 연결이 생길 수 있다.

둘째, graph가 오래되면 더 위험하다. agent가 stale graph를 믿고 수정하면 실제 파일보다 잘못된
구조를 기준으로 판단할 수 있다. 그래서 live indexing, dirty buffer 반영, branch별 session 격리가
중요하다.

셋째, 보안 경계도 봐야 한다. Gortex는 local-first를 강조하지만, MCP로 노출되는 순간 어떤 tool이
어떤 path와 symbol을 읽을 수 있는지 정책이 필요하다. 특히 회사 코드베이스에서는 "agent가 읽을 수
있는 코드"와 "팀원이 볼 수 있는 코드"가 항상 같지 않다.

## 도구로 볼 때의 평가 기준

이런 도구를 볼 때는 "그래프가 예뻐 보이는가"보다 실제 작업에서 판단을 줄여주는지를 봐야 한다.

- 변경 영향 범위를 사람이 납득할 수 있게 보여주는가
- 관계를 찾기 위해 읽는 파일 수가 실제로 줄어드는가
- 틀린 연결과 확실한 연결을 구분해서 표시하는가
- 오래된 index나 누락된 context를 경고하는가
- MCP tool이 너무 많아져서 오히려 agent 선택을 흐리게 만들지는 않는가

code graph가 유용하려면 agent에게 더 많은 정보를 던지는 도구가 아니라, 읽어야 할 정보를 좁혀주는
도구여야 한다.

## 판단

**Watch.**

Gortex를 아직 로컬에서 직접 돌려보지는 않았다. 그래서 Adopt라고 쓰기는 이르다. 다만 Threads에서
보인 여러 agent 도구 중에서는 방향이 꽤 실전적이다. coding agent의 품질은 모델, prompt, MCP
연결만으로 결정되지 않는다. 큰 repo에서는 context를 어떻게 좁히고, 어떤 관계를 먼저 보여주느냐가
중요해진다.

다음에 직접 확인할 것은 네 가지다.

```text
1. NestJS/TypeScript repo에서 route-service-repository 관계를 얼마나 잘 잡는가
2. monorepo나 multi-repo에서 API contract 연결이 실제로 유용한가
3. Codex CLI/Claude Code와 붙였을 때 tool 호출이 과하게 늘지 않는가
4. graph가 틀렸을 때 agent가 잘못된 확신을 갖지 않게 만들 수 있는가
```

이 네 가지가 괜찮으면 code graph는 coding agent의 기본 context layer가 될 가능성이 있다.
