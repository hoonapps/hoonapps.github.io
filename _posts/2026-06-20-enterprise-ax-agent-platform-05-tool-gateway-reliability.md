---
title: "Enterprise AX Agent Platform 05: Tool Gateway 신뢰성"
date: 2026-06-20 00:05:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, reliability, retry, circuit-breaker, backend]
description: "외부 tool 호출에 timeout, retry, fallback, circuit breaker를 적용하고 gateway 상태를 운영 API로 노출했다."
---

Agent가 외부 tool을 호출하면 실패는 정상 상황이 된다. 외부 시스템은 느릴 수 있고, 일시적으로 실패할 수 있고, 같은 요청을 여러 worker가 처리하려 할 수도 있다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## Runtime과 Gateway 분리

Tool Runtime은 정책과 상태 전이를 담당한다. Tool Gateway는 외부 실행을 담당한다.

```text
Tool Runtime
  -> registry
  -> scope
  -> policy
  -> approval

Tool Gateway
  -> timeout
  -> retry
  -> fallback
  -> circuit breaker
  -> execution metadata
```

이 둘을 섞지 않았다. 정책 실패와 외부 실행 실패는 원인이 다르고 운영 대응도 다르다.

## Retry와 Fallback

일시 실패는 정해진 횟수만 재시도한다. 재시도 후에도 실패하면 fallback result를 반환한다.

fallback은 실패를 숨기는 장치가 아니다. AgentRun trace와 audit event에 실패 원인, attempt 수, fallback 여부를 남긴다.

```text
status: fallback
attempts: 2
error_code: gateway_timeout
```

운영자는 답변 텍스트만 보지 않고 gateway metadata를 함께 본다.

## Circuit Breaker

반복 실패가 일정 기준을 넘으면 circuit을 연다.

```text
closed -> open -> half_open -> closed
```

open 상태에서는 외부 호출을 즉시 차단한다. 회복 시간이 지나면 half-open에서 제한적으로 호출하고, 성공하면 closed로 복귀한다.

상태 조회 API도 둔다.

```text
GET /v1/tools/gateway/status
```

## Agent 실패와 Tool 실패 구분

외부 tool 실패가 항상 AgentRun 전체 실패는 아니다. 예를 들어 조회성 tool이 fallback을 반환했지만 문서 근거 답변은 생성할 수 있다면 run은 완료될 수 있다.

그래서 결과 모델을 다음처럼 나눴다.

```text
agent_run.status
tool_result.status
trace_step.status
audit_event.event_type
```

하나의 boolean으로 처리하지 않으면 운영 화면에서 정확한 원인을 보여줄 수 있다.

## 결과

이 단계에서 외부 실행은 단순 함수 호출이 아니라 신뢰성 계층을 가진 adapter가 됐다.

- timeout/retry/fallback wrapper
- circuit breaker 상태 전이
- gateway execution metadata
- gateway status API
- AgentRun trace와 audit event 연결

Agent 제품은 외부 시스템이 완벽하다는 가정 위에 설계하면 안 된다. 실패를 모델링해야 운영할 수 있다.
