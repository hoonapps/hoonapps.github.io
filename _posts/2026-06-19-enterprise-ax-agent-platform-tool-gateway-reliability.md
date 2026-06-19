---
title: "Enterprise AX Agent Platform 7단계: Tool Gateway Reliability"
date: 2026-06-19 19:42:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, reliability, retry, fallback, backend]
---

Agent가 외부 tool을 호출하기 시작하면 다음 문제가 바로 생긴다.

```text
외부 시스템이 느리면?
일시적으로 실패하면?
재시도는 어디에서 제어할 것인가?
최종 실패는 Agent 실행 전체 실패로 볼 것인가?
운영자는 실패 원인을 어디에서 볼 것인가?
```

지난 단계까지는 tool registry, scope check, MCP-compatible boundary, approval workflow를 만들었다.  
이번 단계에서는 Tool Gateway에 실행 안정성 계층을 추가했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 설계 방향

안정성 정책을 `LocalToolRuntime` 안에 직접 넣지 않았다.

Runtime의 책임은 다음에 가깝다.

```text
tool 등록 여부 확인
required scope 확인
risk level 판단
approval_required 전환
tool execution 생성
```

반면 timeout, retry, fallback은 외부 호출 어댑터의 공통 관심사다.

그래서 별도 wrapper를 만들었다.

```text
ToolRuntime
  -> ResilientToolGateway
  -> LocalToolGateway
```

`ResilientToolGateway`는 `ToolGatewayPort`를 구현하면서 내부 gateway를 감싼다.

## ResilientToolGateway

새 wrapper의 정책은 단순하다.

```text
1. gateway를 호출한다.
2. 예외가 발생하면 attempt 실패로 기록한다.
3. timeout을 넘으면 attempt 실패로 간주한다.
4. max_attempts까지 재시도한다.
5. 모두 실패하면 fallback 결과를 반환한다.
```

생성자는 다음 옵션을 받는다.

```text
inner
max_attempts
timeout_ms
fallback_enabled
```

현재 컨테이너에서는 `LocalToolGateway`를 감싸서 사용한다.

```text
ResilientToolGateway(inner=LocalToolGateway())
```

나중에 HTTP API, MCP client, workflow engine adapter를 붙여도 같은 wrapper를 적용할 수 있다.

## Gateway Metadata

이번 단계에서 `ToolGatewayResult`에 운영 metadata를 추가했다.

```text
attempts
elapsed_ms
fallback_used
error_message
```

Runtime은 이 값을 tool execution의 `output_payload._gateway`에 넣는다.

예시:

```json
{
  "result": "fallback_result",
  "source": "internal-records.lookup",
  "_gateway": {
    "attempts": 2,
    "elapsed_ms": 34,
    "fallback_used": true,
    "error_message": "ConnectionError: gateway unavailable"
  }
}
```

이제 운영자는 tool call이 성공했는지뿐 아니라 몇 번 시도했는지, fallback이 사용됐는지, 마지막 오류가 무엇인지 볼 수 있다.

## 실패 격리

중요한 점은 gateway 실패가 Agent 프로세스 전체 실패로 번지지 않는다는 것이다.

조회성 tool에서 외부 시스템이 모두 실패하면 결과는 `degraded`가 된다.

```text
decision: allowed
status: degraded
output_payload.result: fallback_result
```

정책상 허용된 실행이지만 외부 시스템 품질이 낮아진 상태를 별도로 표현한다.  
이 차이는 운영에서 중요하다.

```text
denied   -> 정책상 실행 불가
failed   -> fallback 없이 실행 실패
degraded -> fallback으로 응답 가능
```

## 테스트

이번 단계에서는 테스트용 gateway를 두 개 만들었다.

```text
FailsOnceGateway
AlwaysFailsGateway
```

검증한 내용:

- 첫 번째 호출이 실패하면 retry 후 성공한다.
- retry 횟수가 tool execution metadata에 남는다.
- 모든 attempt가 실패하면 fallback result를 반환한다.
- fallback 사용 여부와 error message가 metadata에 남는다.
- 기존 Agent/API/MCP/Approval 테스트가 함께 통과한다.

검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 11 passed
```

## 다음 단계

Tool Gateway의 최소 안정성은 들어갔다.

다음으로는 품질 평가와 운영 화면 쪽으로 확장할 수 있다.

1. evaluation dataset과 regression test
2. audit event export
3. operator dashboard
4. tool latency metric aggregation
5. approval comment history

Agent 제품에서 중요한 것은 성공 케이스만 만드는 것이 아니다.  
실패, 지연, fallback 같은 나쁜 상태도 제품 언어로 표현해야 운영할 수 있다.
