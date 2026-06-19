---
title: "Enterprise AX Agent Platform 01: 아키텍처와 DB 경계"
date: 2026-06-20 00:59:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, backend, architecture, database, fastapi]
description: "Agent 실행을 운영 리소스로 다루기 위해 FastAPI, use case, domain policy, repository adapter를 분리했다."
---

Agent 백엔드의 첫 번째 설계 문제는 모델이 아니다. 어떤 책임을 API, application, domain, adapter 중 어디에 둘 것인가가 먼저다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

Agent 실행을 단순 함수 호출로 두지 않고 다음 리소스로 분해했다.

```text
Document
DocumentChunk
AgentRun
TraceStep
ToolDefinition
ToolRequest
ApprovalRequest
AuditEvent
EvaluationRun
WebhookDelivery
AgentScenarioRun
```

이렇게 나누면 운영자가 답해야 하는 질문을 데이터로 다룰 수 있다.

- 어떤 문서 chunk가 답변 근거가 됐는가
- 어떤 policy decision이 실행을 막거나 통과시켰는가
- 어떤 tool call이 승인 대기 상태가 됐는가
- 어떤 audit event가 외부 webhook delivery로 이어졌는가
- 어떤 scenario run이 실제 운영 흐름을 검증했는가

## 계층 구조

구조는 헥사고날 아키텍처에 가깝게 잡았다.

```text
apps/api/routers
  HTTP schema, status code, dependency

apps/api/application
  use case orchestration, port interface

apps/api/domain
  model, policy, status transition

apps/api/adapters
  Postgres, local storage, vector search, tool gateway, webhook client
```

라우터는 요청과 응답만 책임진다. 실행 순서와 정책 판단은 use case와 domain으로 내려간다. Postgres, Qdrant, webhook, tool gateway는 port 뒤에 둔다.

## DB 설계 방향

Postgres schema는 운영 추적을 기준으로 잡았다.

```text
tenants
documents
document_chunks
agent_runs
agent_trace_steps
approvals
audit_events
webhook_subscriptions
webhook_deliveries
idempotency_records
schema_migrations
agent_scenario_runs
```

Vector DB에는 검색을 위한 embedding/chunk 참조를 둔다. 원장성 데이터는 Postgres에 둔다. Agent 실행을 나중에 재구성하려면 run, trace, approval, audit, webhook 상태가 관계형 데이터로 남아야 한다.

## Migration Ledger

DB migration은 단순 SQL 파일 적용으로 끝내지 않았다.

`schema_migrations` ledger를 두고 다음 값을 저장한다.

```text
version
filename
checksum
applied_at
```

운영 API에서는 migration 상태도 조회한다. 적용된 migration, pending migration, checksum mismatch를 구분해야 로컬과 배포 환경의 schema drift를 설명할 수 있다.

## Multi Tenant 경계

tenant는 단순 metadata가 아니라 접근 경계다.

API key credential은 다음 두 축으로 평가된다.

```text
무엇을 할 수 있는가 -> scope
어디에 할 수 있는가 -> tenant_id
```

Postgres 모드에서는 row-level security 검증 스크립트까지 둔다. Agent 시스템은 데이터 경계가 느슨하면 검색 결과와 audit event가 동시에 오염된다. 그래서 tenant filter는 API 계층의 편의 기능이 아니라 저장소 계층의 설계 조건으로 둔다.

## 결과

이 단계의 산출물은 기능 하나가 아니라 제품의 뼈대다.

- 외부 기술 교체가 가능한 port 구조
- in-memory와 Postgres를 같은 use case에서 쓰는 repository adapter
- migration 상태를 운영 지표로 노출하는 DB 설계
- tenant와 scope를 함께 다루는 보안 경계

이 구조가 있어야 이후 RAG, tool runtime, audit, dashboard가 서로 엉키지 않는다.
