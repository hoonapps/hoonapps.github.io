---
title: "Enterprise AX Agent Platform 09: Ontology Graph와 Scenario Runbook"
date: 2026-06-20 00:51:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, ontology, scenario, runbook, backend]
description: "문서 metadata에서 ontology graph read model을 만들고 운영 시나리오를 실행 가능한 runbook으로 모델링했다."
---

Agent 운영은 개별 질문만으로 설명되지 않는다. 문서가 어떤 개념과 연결되는지, 실제 운영 상황에서 여러 단계가 제대로 이어지는지도 볼 수 있어야 한다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## Ontology Graph

문서 적재 과정에서 ontology graph read model을 업데이트한다.

```text
Document
  -> metadata
  -> concepts
  -> OntologyNode
  -> OntologyEdge
```

API는 다음과 같다.

```text
GET /v1/ontology/graph
```

RAG 검색은 질문에 맞는 chunk를 찾는 데 강하다. ontology graph는 운영자가 문서 집합의 구조를 볼 때 유용하다.

- 어떤 문서가 internal 분류인가
- 어떤 업무 개념이 자주 등장하는가
- 특정 문서가 어떤 metadata와 연결되는가
- 같은 개념을 공유하는 문서가 무엇인가

## Read Model로 둔 이유

ontology graph는 쓰기 원장이 아니라 조회 모델이다.

문서 원본과 chunk는 별도 저장소에 남고, graph는 운영 탐색과 설명을 위해 계산된다. 이 구분을 두면 graph 생성 방식이 바뀌어도 문서 원장이 흔들리지 않는다.

## Scenario Runbook

운영 검증은 단일 API 호출로 끝나지 않는다. 그래서 scenario를 별도 리소스로 만들었다.

```text
AgentScenarioDefinition
  id
  title
  steps[]

AgentScenarioRunResult
  scenario_id
  step_results[]
  succeeded
  started_at
  finished_at
```

기본 시나리오는 두 가지다.

```text
release-readiness
incident-triage
```

## Scenario API

API는 catalog, detail, run history를 나눴다.

```text
GET  /v1/scenarios
GET  /v1/scenarios/runs
GET  /v1/scenarios/{scenario_id}
POST /v1/scenarios/{scenario_id}/run
```

scenario run 결과는 Postgres 모드에서 `agent_scenario_runs` 테이블에 저장된다. dashboard는 최신 실행과 최근 history를 함께 보여준다.

## Runbook이 필요한 이유

운영자가 보고 싶은 것은 “API가 살아 있다”가 아니다.

```text
문서 검색이 된다.
정책이 적용된다.
승인 필요한 작업이 pending으로 간다.
evaluation 품질이 기준을 넘는다.
audit와 operations summary에 반영된다.
```

이 흐름을 scenario runbook으로 만들면 배포 전 검증과 장애 대응 검증을 같은 모델로 다룰 수 있다.

## 결과

이 단계에서 시스템은 개별 기능 목록을 넘어 운영 시나리오를 실행할 수 있게 됐다.

- ontology graph read model
- scenario catalog
- scenario execution API
- persisted scenario run history
- dashboard scenario panel
- release readiness와 incident triage 흐름

Agent 백엔드의 완성도는 endpoint 수가 아니라 여러 기능이 운영 흐름으로 이어지는지에서 드러난다.
