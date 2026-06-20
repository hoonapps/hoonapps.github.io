---
title: "Enterprise AX Agent Platform: 운영 가능한 Agent 백엔드 설계 기록"
date: 2026-06-20 00:00:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, backend, architecture, rag, operations]
description: "사내 지식 검색, 업무 자동화, 정책 감사, 실행 추적을 하나의 흐름으로 묶은 Agent 백엔드 구현 기록이다."
---

LLM Agent를 제품으로 만들 때 가장 먼저 분리해야 하는 것은 모델 호출과 운영 책임이다.

질문에 답하는 기능만 있으면 데모는 된다. 하지만 실제 시스템에서는 다음 질문이 바로 따라온다.

```text
어떤 문서를 근거로 답했는가?
개인정보는 모델 context에 들어가기 전에 제거됐는가?
외부 tool 실행은 어떤 권한과 정책을 통과했는가?
승인, 반려, 재시도, 장애 격리는 어디에서 제어되는가?
운영자는 어떤 audit event와 trace로 실행을 재구성할 수 있는가?
```

이 문제를 풀기 위해 `Enterprise AX Agent Platform`을 만들었다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 제품 경계

이 시스템은 챗봇이 아니라 Agent 실행을 운영 가능한 백엔드 리소스로 다룬다.

```text
FastAPI / MCP / Dashboard / CLI
        |
        v
Application Use Case
        |
        v
Domain Model / Policy
        |
        v
Port Interface
        |
        v
Adapter: Postgres, Vector DB, Tool Gateway, Webhook, Observability
```

핵심은 외부 기술을 직접 비즈니스 규칙 안에 넣지 않는 것이다. LLM, Vector DB, workflow tool, storage backend는 바뀔 수 있다. 반대로 실행 정책, 감사 모델, 승인 상태, 평가 기준은 제품의 중심이므로 도메인과 use case에 둔다.

## 현재 구현 범위

구현은 로컬 단독 실행과 Postgres/Qdrant 연동 모드를 모두 지원한다.

| 영역 | 구현 |
| --- | --- |
| API | FastAPI REST API, MCP-compatible JSON-RPC boundary |
| RAG | 문서 적재, chunking, query classification, retrieval strategy, citation |
| Persistence | in-memory repository, Postgres repository, migration ledger |
| Vector Search | local deterministic adapter, Qdrant adapter |
| Policy | PII redaction, action risk policy, scope guard, tenant guard |
| Tool Runtime | tool schema registry, read/write action 분리, approval-required 전환 |
| Reliability | timeout, retry, fallback, circuit breaker |
| Audit | audit event, request id correlation, JSONL/CSV export |
| Integration | webhook subscription, delivery outbox, dispatcher, dead-letter 상태 |
| Operations | summary, usage, SLO, alerts, incident snapshot, dashboard |
| Evaluation | evaluation run, expected facts scoring, regression gate |
| Scenario | 운영 runbook catalog, scenario execution, persisted run history |

## 읽는 순서

각 글은 기능 추가 기록이 아니라 운영 가능한 Agent 백엔드를 만들기 위해 어떤 책임을 어디에 뒀는지 설명한다.

1. [01. 아키텍처와 DB 경계]({% post_url 2026-06-20-enterprise-ax-agent-platform-01-architecture-db %})
2. [02. 문서 적재와 RAG 전략]({% post_url 2026-06-20-enterprise-ax-agent-platform-02-rag-pipeline %})
3. [03. Tool Runtime과 MCP 경계]({% post_url 2026-06-20-enterprise-ax-agent-platform-03-tool-runtime-mcp %})
4. [04. 승인, 권한, 멱등성]({% post_url 2026-06-20-enterprise-ax-agent-platform-04-approval-security %})
5. [05. Tool Gateway 신뢰성]({% post_url 2026-06-20-enterprise-ax-agent-platform-05-tool-gateway-reliability %})
6. [06. Evaluation과 회귀 게이트]({% post_url 2026-06-20-enterprise-ax-agent-platform-06-evaluation-regression %})
7. [07. Audit Trail과 Webhook Outbox]({% post_url 2026-06-20-enterprise-ax-agent-platform-07-audit-webhook-outbox %})
8. [08. 운영 Read Model과 Dashboard]({% post_url 2026-06-20-enterprise-ax-agent-platform-08-operations-dashboard %})
9. [09. Ontology Graph와 Scenario Runbook]({% post_url 2026-06-20-enterprise-ax-agent-platform-09-ontology-scenario %})
10. [10. 로컬 운영 검증 흐름]({% post_url 2026-06-20-enterprise-ax-agent-platform-10-local-verification %})

## 설계 기준

이 제품을 만들면서 지킨 기준은 네 가지다.

- Agent 실행은 하나의 감사 가능한 리소스여야 한다.
- 외부 상태를 바꾸는 tool call은 정책과 승인을 통과해야 한다.
- 운영 품질은 사람이 화면에서 보는 지표와 CI에서 막는 회귀 평가로 함께 관리해야 한다.
- 로컬에서도 전체 흐름을 재현할 수 있어야 한다.

이 기준 때문에 API, DB, policy, adapter, dashboard가 한 흐름으로 묶인다. Agent 제품의 완성도는 답변 품질만으로 결정되지 않는다. 답변이 만들어지고 실행되고 추적되고 회귀 평가되는 전체 경로가 제품이다.
