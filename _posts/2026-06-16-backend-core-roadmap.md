---
title: "Backend Core 로드맵: 사용법을 넘어 실패 지점까지 가는 글쓰기"
date: 2026-06-16 13:00:00 +0900
categories: [Backend, DeepDive]
tags: [backend, architecture, database, observability, systems]
pin: true
---

백엔드 글은 프레임워크 사용법에서 멈추기 쉽다. 컨트롤러를 만들고, ORM을 붙이고,
Docker로 띄우는 글은 필요하지만 그 자체로 깊이를 만들지는 못한다. 실무에서 중요한
질문은 보통 그 다음에 나온다.

- 트랜잭션은 정확히 어디까지 보장하는가?
- 장애가 나면 중복 요청은 어떻게 처리되는가?
- 큐가 밀릴 때 시스템은 어떻게 느려지는가?
- 캐시가 틀렸을 때 데이터 정합성은 어떻게 복구되는가?
- 로그는 많은데 왜 장애 원인을 못 찾는가?

앞으로 Backend Core 글은 이 질문들을 기준으로 쓴다.

## 1. 데이터 정합성

가장 먼저 볼 축은 데이터 정합성이다. 백엔드 시스템은 결국 상태를 바꾸는 시스템이고,
상태 변경에는 항상 경계가 있다.

다룰 주제:

- isolation level과 lost update
- optimistic lock과 pessimistic lock
- idempotency key
- transactional outbox
- exactly-once라는 표현의 함정
- event ordering과 deduplication

좋은 글의 기준은 “이 패턴을 쓰세요”가 아니라 “이 패턴을 써도 남는 실패 모드는
무엇인가”까지 가는 것이다.

## 2. 성능과 확장

성능 글은 benchmark 숫자보다 병목을 찾는 과정이 중요하다. 같은 API라도 병목은
DB, lock, network, serialization, GC, 외부 API 중 어디에서든 생길 수 있다.

다룰 주제:

- Postgres index와 query plan
- connection pool starvation
- N+1과 batch loading
- Redis cache invalidation
- queue backpressure
- retry storm
- load balancing 알고리즘의 실제 차이

성능 글은 반드시 측정 기준을 남긴다. latency p50/p95/p99, throughput, error rate,
CPU, memory, DB wait event를 같이 봐야 한다.

## 3. 운영과 관측성

서비스는 배포된 뒤부터 진짜 백엔드가 된다. 운영 글은 코드보다 시스템의 가시성을
다룬다.

다룰 주제:

- structured logging
- OpenTelemetry trace 설계
- metric cardinality
- alert fatigue
- SLO와 error budget
- 장애 대응 runbook
- 배포 rollback 기준

관측성의 목표는 예쁜 대시보드가 아니다. 장애가 났을 때 원인을 좁히는 시간을
줄이는 것이다.

## 4. AI 시스템의 백엔드

AI 기능도 결국 백엔드 시스템 위에서 돈다. 모델 호출 하나를 붙이는 것은 쉽지만,
실제 제품에 넣으려면 다른 문제가 생긴다.

다룰 주제:

- tool calling 권한 경계
- agent sandbox
- prompt/version 관리
- LLM request tracing
- cost guardrail
- fallback model
- RAG freshness와 eval
- human-in-the-loop workflow

AI 시스템에서 가장 위험한 지점은 모델이 틀리는 것만이 아니다. 권한이 넓은 도구를
잘못 호출하거나, 비용이 폭증하거나, 사용자의 데이터를 불필요하게 외부로 보내는
것도 같은 수준의 문제다.

## 운영 원칙

Backend Core 글은 앞으로 다음 형식을 따른다.

1. 문제 상황을 먼저 제시한다.
2. 내부 동작을 설명한다.
3. 최소 재현 코드를 넣는다.
4. 운영에서 터지는 지점을 적는다.
5. 대안과 trade-off를 비교한다.
6. 언제 쓰고 언제 피할지 결론을 낸다.

이 로드맵은 블로그의 기준선이다. 새 글이 이 기준에 못 미치면 짧은 노트로 남기고,
기준을 통과하는 주제만 Deep Dive로 올린다.
