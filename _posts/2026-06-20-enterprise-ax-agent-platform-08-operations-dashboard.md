---
title: "Enterprise AX Agent Platform 08: 운영 Read Model과 Dashboard"
date: 2026-06-20 00:52:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, operations, dashboard, read-model, backend]
description: "운영자가 봐야 하는 지표를 summary, usage, SLO, alerts, incident snapshot API와 dashboard로 묶었다."
---

운영 화면은 API를 예쁘게 감싸는 일이 아니다. 먼저 어떤 데이터를 운영자가 봐야 하는지 정해야 한다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## Read Model

운영 API는 쓰기 모델과 분리된 read model로 설계했다.

```text
GET /v1/operations/summary
GET /v1/operations/usage
GET /v1/operations/slo
GET /v1/operations/alerts
GET /v1/operations/incidents/snapshot
GET /v1/operations/feedback/summary
GET /v1/operations/migrations/status
```

처음부터 별도 집계 테이블을 만들지는 않았다. 현재 규모에서는 repository에 있는 run, audit, approval, webhook, evaluation 데이터를 읽어 summary를 계산한다. 필요해지면 같은 API 계약 뒤에서 materialized read model로 바꿀 수 있다.

## Summary

summary는 운영자의 첫 화면에 필요한 데이터를 모은다.

```text
total_runs
successful_runs
approval_pending
policy_blocks
tool_failures
latest_evaluation
webhook_delivery_status
```

Agent 실행 품질과 외부 연동 상태를 같은 화면에서 봐야 한다. 답변은 성공했지만 webhook delivery가 dead-letter로 쌓이는 상황도 운영 이슈다.

## SLO와 Alerts

SLO API는 latency, success rate, fallback rate 같은 값을 계산한다.

alerts API는 임계치를 넘은 상태를 운영자가 바로 볼 수 있게 한다.

```text
evaluation_pass_rate_drop
tool_gateway_failure_rate_high
webhook_dead_letter_exists
approval_queue_backlog
```

alert는 단순 문자열이 아니라 원인과 관련 metric을 포함한다. 그래야 dashboard에서 클릭 가능한 운영 단위로 다룰 수 있다.

## Incident Snapshot

incident snapshot은 현재 시스템 상태를 한 번에 설명하기 위한 API다.

```text
alerts
slo
recent_failed_runs
pending_approvals
failed_webhook_deliveries
recommended_actions
```

장애 상황에서는 여러 API를 사람이 직접 조합할 시간이 없다. snapshot은 운영자가 가장 먼저 열어보는 데이터 묶음이다.

## Dashboard

`GET /dashboard`는 별도 프론트엔드 빌드 없이 FastAPI에서 제공하는 운영 콘솔이다.

화면에는 다음 패널을 둔다.

- operations summary
- SLO와 alerts
- approval queue
- tool catalog와 gateway status
- recent agent runs
- audit events
- webhook deliveries
- scenario runbooks

## 결과

이 단계에서 운영자는 curl이 아니라 화면과 read model로 시스템 상태를 볼 수 있게 됐다.

- operations summary API
- usage quota와 사용량 API
- SLO 계산
- alerts
- incident snapshot
- migration status
- operator dashboard

운영 화면은 부가 기능이 아니다. Agent가 업무 시스템이 되는 순간 read model은 제품의 핵심 API가 된다.
