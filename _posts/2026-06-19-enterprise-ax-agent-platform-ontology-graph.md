---
title: "Enterprise AX Agent Platform 16단계: Ontology Graph Read Model"
date: 2026-06-19 22:58:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, ontology, knowledge-graph, backend]
---

RAG 검색은 질문에 맞는 문서 조각을 찾는 데 강하다.

하지만 운영자가 항상 질문만 하는 것은 아니다.

```text
어떤 문서가 internal 분류인가?
어떤 metadata가 자주 등장하는가?
어떤 개념들이 같이 나타나는가?
특정 문서가 어떤 업무 개념과 연결되는가?
```

이번 단계에서는 문서 적재 흐름에 ontology graph read model을 추가했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

새 API는 다음이다.

```text
GET /v1/ontology/graph
```

응답은 node와 edge로 구성된다.

```text
OntologyNode
OntologyEdge
OntologyGraph
```

## Ingestion Flow

문서 적재 use case는 이제 두 개의 read model을 업데이트한다.

```text
Document
  -> TextChunker
  -> VectorSearchPort
  -> OntologyExtractor
  -> OntologyRepositoryPort
```

Vector index는 검색을 위한 파생 데이터다.
Ontology graph는 문서와 개념의 관계를 조회하기 위한 read model이다.

둘을 분리해야 한다.

```text
Vector DB      -> 유사도 검색
Ontology graph -> 업무 개념 탐색
```

## Node

node는 네 종류로 시작했다.

```text
document
classification
metadata
concept
```

예를 들면 다음과 같다.

```text
document:ax-governance-playbook
classification:internal
metadata:domain=enterprise-ax
concept:audit
concept:approval
```

## Edge

edge는 관계를 표현한다.

```text
classified_as
has_metadata
mentions
co_occurs_with
```

문서가 internal 분류라면 다음 edge가 생긴다.

```text
document -> classified_as -> classification
```

문서가 audit와 approval을 같이 언급하면 다음 edge가 생긴다.

```text
concept:audit -> co_occurs_with -> concept:approval
```

## Extractor

현재 extractor는 결정론적 규칙 기반이다.

이 선택은 의도적이다.

```text
테스트가 재현 가능해야 한다.
초기 graph 구조를 안정적으로 검증해야 한다.
나중에 LLM entity extraction으로 교체할 수 있어야 한다.
```

LLM extractor를 넣더라도 repository port와 API 계약은 유지된다.

## Repository

repository는 두 구현을 가진다.

```text
InMemoryOntologyRepository
PostgresOntologyRepository
```

Postgres에는 다음 테이블을 둔다.

```text
ontology_nodes
ontology_edges
```

node와 edge는 evidence count를 가진다.
같은 개념이나 관계가 반복 등장하면 count가 증가한다.

## 테스트

테스트는 문서를 적재한 뒤 graph API를 호출한다.

확인하는 것:

```text
document node가 생성된다.
classification node가 생성된다.
metadata node가 생성된다.
concept node가 생성된다.
edge가 생성된다.
tenant scope가 적용된다.
```

## 다음 단계

지식 구조를 조회할 수 있게 되면 다음은 외부 workflow 연동이다.

Agent 시스템 내부에서 audit event만 남기는 것으로는 부족하다.
외부 자동화로 이벤트를 보내되, Agent 실행 경로와 외부 장애를 분리해야 한다.

다음 단계에서는 webhook outbox를 만든다.
