---
title: "Enterprise AX Agent Platform 15단계: Tenant-Scoped API Keys"
date: 2026-06-19 22:38:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, multi-tenant, security, backend]
---

API scope만으로는 충분하지 않다.

같은 `documents:read` 권한이라도 어떤 tenant의 문서를 읽을 수 있는지가 더 중요하다.

이번 단계에서는 API key credential에 tenant scope를 추가했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

권한 모델을 두 축으로 나눈다.

```text
무엇을 할 수 있는가 -> scope
어디에 할 수 있는가 -> tenant
```

예시는 다음과 같다.

```text
ops-key:operator-01:documents:read|agents:run@default
```

이 key는 `default` tenant에서만 지정된 scope를 사용할 수 있다.

tenant 목록은 `|`로 여러 개를 줄 수 있다.

```text
ops-key:operator-01:documents:read@default|sandbox
```

tenant를 생략하면 모든 tenant 접근을 허용한다.
하지만 운영형 설정에서는 명시하는 쪽이 안전하다.

## AuthPrincipal

인증 결과는 `AuthPrincipal`로 표현한다.

```text
actor_id
scopes
tenant_ids
```

router는 scope check를 먼저 통과한 뒤 tenant access를 확인한다.

```text
require_scopes("agents:run")
require_tenant_access(auth, request.tenant_id)
```

이 순서를 두는 이유는 오류 의미를 명확히 하기 위해서다.

```text
scope 부족        -> 기능 권한 없음
tenant 접근 불가  -> 데이터 경계 위반
```

## 적용 지점

tenant check는 request body, query parameter, JSON-RPC params에 모두 적용했다.

```text
REST body tenant_id
REST query tenant_id
MCP params tenant_id
```

MCP boundary도 예외가 아니다.

Agent tool 호출은 내부적으로 강한 권한을 가질 수 있으므로, JSON-RPC 요청의 tenant도 같은
guard를 통과해야 한다.

## Multi-Tenant 사고 방지

tenant guard의 목적은 복잡한 권한 시스템을 만드는 것이 아니다.

운영 사고를 줄이는 것이다.

```text
잘못된 API key로 다른 tenant 데이터 조회
자동화 스크립트의 tenant_id 오입력
MCP tool call의 tenant boundary 누락
```

이런 문제는 기능이 커질수록 발견하기 어렵다.

그래서 초기 단계에서 모든 router에 같은 guard 패턴을 넣었다.

## 테스트

테스트는 다음을 확인한다.

```text
tenant가 맞으면 요청이 통과한다.
tenant가 다르면 403이다.
tenant 제한이 없는 key는 통과한다.
MCP 요청도 tenant guard를 통과한다.
```

여기서 중요한 테스트는 MCP tenant denial이다.
일반 REST endpoint만 막고 MCP boundary를 열어두면 권한 모델이 깨지기 때문이다.

## 다음 단계

권한과 tenant 경계를 만든 뒤에는 지식 구조를 볼 수 있어야 한다.

RAG 검색은 문서 조각을 찾는 데 좋다.
하지만 운영자는 문서, 분류, 개념 사이의 관계를 보고 싶어한다.

다음 단계에서는 ontology graph read model을 추가한다.
