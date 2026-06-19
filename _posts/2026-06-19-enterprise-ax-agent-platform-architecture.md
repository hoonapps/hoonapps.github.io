---
title: "Enterprise AX Agent Platform 1단계: 한국 대기업 AX 포트폴리오를 백엔드 시스템으로 설계하기"
date: 2026-06-19 17:00:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, fastapi, rag, backend, architecture, database, portfolio, llmops]
---

AX Engineer, AI Agent Engineer 공고를 보면 공통점이 있다.  
모델을 직접 학습하는 역할보다, LLM과 Agent 도구를 기업 업무 시스템에 안전하게 붙이고 운영 가능한 형태로 만드는 역할이 빠르게 늘고 있다.

그래서 새 포트폴리오 프로젝트를 하나 만들었다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

이번 프로젝트의 목표는 챗봇 데모가 아니다.

```text
기업 업무 시스템에 LLM Agent를 안전하게 연결하고,
RAG·권한·감사로그·평가·운영 안정성을 갖춘 백엔드 플랫폼으로 설계한다.
```

내가 보여주고 싶은 포지션은 명확하다.

- AI 모델 연구자가 아니라 AX/Agent 백엔드 엔지니어
- 프롬프트만 만지는 사람이 아니라 시스템 경계를 설계하는 개발자
- RAG 데모가 아니라 운영 가능한 Agent 실행 플랫폼을 만드는 사람

## 왜 통합 플랫폼인가

처음에는 회사별 프로젝트를 따로 만들 생각을 했다.  
현대오토에버용 MCP 프로젝트, LG CNS용 A-RAG 프로젝트, 무신사용 n8n 자동화 프로젝트처럼 나누는 방식이다.

하지만 공고를 겹쳐보면 공통 코어가 있다.

- Python
- FastAPI 또는 API 서버
- RAG
- Vector DB
- Agent orchestration
- Tool calling
- 업무 시스템 연동
- 권한/보안/감사로그
- 평가/관측성

그래서 구조를 이렇게 잡았다.

```text
공통 AX Agent Platform
  ├─ 현대오토에버: MCP + A2A + 지식그래프
  ├─ LG CNS: Agentic RAG + 평가
  ├─ 삼성SDS: RAG 전략 라우팅 + 거버넌스
  ├─ 무신사: n8n/iPaaS 업무 자동화
  ├─ SK AX: LLMOps + 관측성 + fallback
  └─ 금융/제조: 마스킹 + 승인 + 감사로그
```

코어는 하나로 만들고, 회사별 시나리오를 얹는 방식이다.

## 1단계 구현 범위

첫 단계는 작게 잡았다. 하지만 구조는 작게 잡지 않았다.

현재 구현한 것:

- FastAPI 기반 REST API
- 문서 적재 API
- 문서 chunking
- 로컬 deterministic 검색 어댑터
- 질문 유형 분류
- 질문 유형별 RAG 전략 선택
- 근거 기반 답변 생성
- 개인정보 마스킹 정책
- 위험 action 승인 차단 정책
- Agent 실행 trace
- 감사 이벤트 기록
- Postgres 기준 DB 설계 SQL
- 헥사고날 아키텍처 기반 코드 구조
- pytest, ruff, mypy, GitHub Actions CI

외부 LLM API key 없이도 로컬에서 돌아가게 했다.  
이유는 명확하다. 포트폴리오는 보는 사람이 바로 실행하고 검증할 수 있어야 한다.

## 아키텍처 판단

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

LLM Agent 프로젝트에서 흔한 실수는 라우터, 프롬프트, SDK 호출, 벡터 검색, 정책 판단을 한 파일에 몰아넣는 것이다.  
그 방식은 빠르게 보이지만, 기업 시스템으로 설명하기 어렵다.

이 프로젝트에서는 다음 경계를 분리했다.

| 계층 | 책임 |
| --- | --- |
| Domain | 문서, 청크, Agent 실행, 정책 판단 |
| Application | 문서 적재, 검색, Agent 실행 유스케이스 |
| Adapter | 메모리 저장소, 로컬 검색, 이후 Postgres/Qdrant/MCP |
| Router | FastAPI 입출력 |

면접에서 설명해야 할 것은 “LangChain을 썼다”가 아니라 “외부 기술이 바뀌어도 업무 정책과 실행 흐름이 흔들리지 않는다”는 점이다.

## DB 설계

MVP는 메모리 저장소로 동작하지만, 기준 DB는 Postgres로 설계했다.

핵심 테이블은 다음과 같다.

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

중요한 판단은 RDB와 Vector DB의 책임 분리다.

| 저장소 | 책임 |
| --- | --- |
| Postgres | 업무 원장, 문서 메타데이터, 실행 이력, 감사 이벤트 |
| Vector DB | 유사도 검색용 임베딩 인덱스 |

Vector DB는 source of truth가 아니다.  
임베딩 모델이 바뀌면 `document_chunks`를 기준으로 다시 색인할 수 있어야 한다.

## 정책과 감사로그

기업형 Agent에서 중요한 질문은 이것이다.

> 이 Agent가 누구 권한으로, 어떤 도구를, 어디까지 실행할 수 있는가?

그래서 1단계부터 정책 경계를 넣었다.

- 이메일, 전화번호, 주민등록번호 패턴 마스킹
- 삭제, 송금, 결제, 퇴사처리 같은 위험 action 차단
- 차단된 실행도 감사 이벤트로 기록
- 답변에는 citation과 trace 포함

이건 삼성SDS, 금융권, SK AX 같은 곳에 특히 중요하다.  
Agent가 할 수 있는 일보다, Agent가 하면 안 되는 일을 어떻게 막는지가 실무에서는 더 중요하다.

## 검증

현재 검증 명령은 하나로 묶었다.

```bash
make verify
```

검증 항목:

- `ruff check .`
- `mypy apps --explicit-package-bases`
- `pytest`

현재 결과:

```text
All checks passed
Success: no issues found
3 passed
```

## 다음 단계

다음 단계는 기능을 무작정 늘리는 것이 아니라, 회사별 공고에 맞는 확장 축을 하나씩 구현하는 것이다.

1. Qdrant 연동
2. Postgres repository 구현
3. LangGraph 기반 Agent graph 적용
4. MCP Streamable HTTP 서버
5. n8n workflow 연동
6. 평가 데이터셋과 regression test
7. 회사별 시나리오 README 작성

이 프로젝트는 앞으로 내 AX 포트폴리오의 중심 레포가 된다.  
목표는 “LLM을 써봤다”가 아니라 “기업형 Agent 백엔드를 설계하고 운영 가능한 구조로 만들 수 있다”를 증명하는 것이다.
