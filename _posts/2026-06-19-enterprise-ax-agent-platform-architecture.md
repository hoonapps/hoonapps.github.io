---
title: "Enterprise AX Agent Platform 1단계: 운영 가능한 Agent 백엔드의 경계 잡기"
date: 2026-06-19 17:00:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, fastapi, rag, backend, architecture, database, llmops]
---

LLM Agent를 업무에 붙이는 일은 모델 호출보다 백엔드 경계 설계가 더 어렵다.

질문은 금방 만들 수 있다.

```text
이 문서 요약해줘.
장애 리스크 알려줘.
이 요청 처리해줘.
```

하지만 운영 제품으로 만들려면 질문이 달라진다.

- 어떤 문서를 근거로 답했는가
- 개인정보는 LLM context에 들어가기 전에 제거됐는가
- 이 Agent가 어떤 권한으로 tool을 실행하는가
- 삭제, 결제, 송금 같은 위험 작업은 어디에서 막는가
- 실패한 실행을 운영자가 나중에 재구성할 수 있는가
- Vector DB와 업무 원장의 책임은 어떻게 나누는가

이 문제를 풀기 위해 `Enterprise AX Agent Platform`을 만들기 시작했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 제품 목표

목표는 챗봇이 아니다.  
사내 지식 검색, 업무 자동화, 정책 감사, 실행 추적을 하나의 흐름으로 묶는 Agent 실행 플랫폼이다.

```text
Document Ingestion
-> Retrieval Strategy
-> Policy Guard
-> Grounded Answer
-> Tool Runtime
-> Audit Event
```

1단계에서는 모든 기능을 크게 만들기보다, 운영 가능한 제품으로 커질 수 있는 경계를 먼저 잡았다.

## 1단계 구현 범위

현재 구현한 기능은 다음과 같다.

- FastAPI 기반 REST API
- 문서 적재 API
- 문서 chunking
- 로컬 deterministic 검색 어댑터
- Qdrant Vector DB 어댑터
- Postgres Repository 어댑터
- 질문 유형 분류
- 질문 유형별 RAG 전략 선택
- 근거 기반 답변 생성
- 개인정보 마스킹 정책
- 위험 action 승인 차단 정책
- Agent 실행 trace
- 감사 이벤트 기록
- Docker Compose 기반 로컬 인프라
- ruff, mypy, pytest, GitHub Actions CI

기본 실행은 외부 서비스 없이 동작한다.  
운영형 로컬 모드에서는 Postgres와 Qdrant로 전환할 수 있다.

## 아키텍처

구조는 헥사고날 아키텍처로 잡았다.

```text
FastAPI / n8n / MCP / CLI
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
Adapter: Postgres, Vector DB, LLM, Tool Runtime, Observability
```

LLM 제품을 만들 때 피하고 싶은 구조가 있다.

```text
router 안에서 prompt 만들고,
SDK 호출하고,
vector search 하고,
정책 판단하고,
응답까지 조립하는 구조
```

이 방식은 처음에는 빠르지만 운영 경계가 흐려진다.  
그래서 이번 프로젝트에서는 다음처럼 책임을 나눴다.

| 계층 | 책임 |
| --- | --- |
| Domain | 문서, 청크, Agent 실행, 정책 판단 |
| Application | 문서 적재, 검색, Agent 실행 유스케이스 |
| Adapter | 메모리 저장소, Postgres, 로컬 검색, Qdrant |
| Router | FastAPI 입출력 |

중요한 것은 기술 이름이 아니라 교체 경계다.  
Vector DB, LLM provider, workflow tool이 바뀌어도 업무 정책과 실행 흐름은 유지돼야 한다.

## DB 설계

MVP라도 데이터 모델은 운영 기준으로 잡았다.

```text
tenants
  ├─ users
  ├─ documents
  │    └─ document_chunks
  ├─ agent_runs
  │    ├─ retrieval_events
  │    ├─ tool_calls
  │    └─ agent_messages
  ├─ evaluation_runs
  │    └─ evaluation_cases
  └─ audit_events
```

핵심 판단은 RDB와 Vector DB의 책임 분리다.

| 저장소 | 책임 |
| --- | --- |
| Postgres | 업무 원장, 문서 메타데이터, 실행 이력, 감사 이벤트 |
| Vector DB | 유사도 검색용 임베딩 인덱스 |

Vector DB는 source of truth가 아니다.  
임베딩 모델이 바뀌거나 인덱스가 깨지면 `document_chunks`를 기준으로 다시 만들 수 있어야 한다.

## 정책과 감사로그

Agent가 단순히 답변만 한다면 위험이 작다.  
하지만 업무 시스템을 조회하고 실행하기 시작하면 정책이 제품의 핵심 기능이 된다.

현재 정책은 작지만 명확하다.

- 이메일, 전화번호, 주민등록번호 패턴 마스킹
- 삭제, 송금, 결제, 퇴사처리 같은 위험 action 차단
- 차단된 요청도 감사 이벤트로 기록
- 답변에는 citation과 trace 포함

이 설계의 목적은 Agent가 무엇을 할 수 있는지보다, 무엇을 하면 안 되는지를 코드로 표현하는 것이다.

## 운영형 저장소 전환

처음에는 메모리 저장소와 로컬 검색으로 동작한다.

```text
STORAGE_BACKEND=memory
VECTOR_BACKEND=local
```

운영형 로컬 인프라에서는 설정만 바꾼다.

```text
STORAGE_BACKEND=postgres
VECTOR_BACKEND=qdrant
```

Postgres는 `db/migrations`의 schema로 시작하고, Qdrant collection은 어댑터가 필요 시 생성한다.  
이렇게 만든 이유는 실행 편의성과 운영 구조를 동시에 가져가기 위해서다.

## 검증

검증은 하나의 명령으로 묶었다.

```bash
make verify
```

검증 항목:

- `ruff check .`
- `mypy apps --explicit-package-bases`
- `pytest`

Agent 제품은 LLM 응답이 그럴듯한지만 봐서는 안 된다.  
정책, 데이터 모델, API 경계, adapter 교체 가능성, 테스트 가능성이 같이 검증돼야 한다.

## 다음 단계

다음 단계는 기능을 크게 늘리는 것이 아니라 운영 경계를 더 구체화하는 것이다.

1. MCP Streamable HTTP 서버
2. tool schema와 권한 scope
3. tool call audit
4. timeout/retry/fallback
5. evaluation dataset과 regression test
6. n8n/Slack 승인 플로우
7. 운영자 dashboard

이 프로젝트는 LLM을 호출하는 코드를 모아둔 레포가 아니라, Agent를 업무 시스템으로 운영하기 위한 백엔드 제품으로 키워갈 생각이다.
