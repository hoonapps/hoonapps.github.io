---
title: "Enterprise AX Agent Platform 02: 문서 적재와 RAG 전략"
date: 2026-06-20 00:58:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, rag, retrieval, vector-db, backend]
description: "문서 적재, chunking, query classification, retrieval strategy, citation을 하나의 실행 경로로 묶었다."
---

RAG는 검색 API 하나로 끝나지 않는다. 운영 가능한 Agent에서는 문서가 어떻게 들어왔고, 어떤 chunk가 검색됐고, 답변이 어떤 근거를 사용했는지 남아야 한다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 적재 흐름

문서 적재는 다음 순서로 처리한다.

```text
POST /v1/documents/ingest
-> tenant 접근 검사
-> 문서 원본 저장
-> chunk 생성
-> 검색 index 반영
-> ontology read model 갱신
-> audit event 기록
```

chunking은 검색 품질을 위해 필요하지만, 운영 추적 관점에서는 더 중요한 역할이 있다. AgentRun에 citation을 남길 때 chunk id가 있어야 답변 근거를 다시 열 수 있다.

## Query Classification

사용자 질문은 같은 RAG 전략으로 처리하지 않는다.

```text
knowledge
summary
action
diagnostic
```

질문 유형이 다르면 필요한 retrieval 방식과 policy가 달라진다.

- 지식 질문은 근거 chunk와 citation이 중요하다.
- 요약 질문은 여러 chunk의 coverage가 중요하다.
- 실행 질문은 retrieval보다 tool runtime과 approval policy가 중요하다.
- 진단 질문은 trace와 audit event까지 같이 봐야 한다.

그래서 query classifier를 application layer에 두고, 이후 use case가 retrieval strategy와 policy guard를 선택하게 했다.

## Retrieval Strategy

검색 어댑터는 두 가지 모드를 둔다.

| 모드 | 목적 |
| --- | --- |
| local deterministic adapter | 외부 서비스 없이 로컬 테스트와 demo flow 재현 |
| Qdrant adapter | Vector DB 기반 검색으로 전환 가능한 경계 |

중요한 점은 use case가 특정 Vector DB SDK를 모르게 하는 것이다. application은 `KnowledgeSearchPort`만 호출하고, adapter가 local 또는 Qdrant로 바뀐다.

## Grounded Answer

답변 생성 결과에는 항상 근거를 포함한다.

```text
answer
citations[]
classification
retrieval_strategy
trace_steps[]
policy_decision
```

답변 텍스트가 좋아 보여도 citation이 없으면 운영 제품에서는 설명력이 부족하다. 그래서 answer와 citations를 분리하지 않고 AgentRun의 결과 모델에 함께 둔다.

## Preview와 Persisted Run

Agent 실행에는 preview와 persisted run을 나눴다.

```text
POST /v1/agents/runs/preview
POST /v1/agents/runs
```

preview는 실제 저장과 audit event를 만들지 않는다. 운영자는 정책이나 검색 결과를 확인할 수 있지만, 원장성 실행으로 기록하지 않는다. 반대로 persisted run은 trace, audit, feedback, replay, evidence bundle의 기준점이 된다.

## 결과

이 단계에서 RAG는 단순 검색 기능이 아니라 Agent 실행 모델 안으로 들어왔다.

- 문서 적재와 chunking
- 질문 유형별 retrieval strategy
- local/Qdrant adapter 교체 경계
- citation 포함 답변
- preview와 persisted run 분리
- AgentRun 중심의 실행 추적

이후 tool runtime을 붙여도 검색과 실행의 책임이 섞이지 않는 이유가 이 경계다.
