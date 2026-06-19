---
title: "Enterprise AX Agent Platform 4단계: Tool Schema Registry와 Scope Check"
date: 2026-06-19 17:49:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, tool-registry, scope, governance, mcp, backend]
---

Agent가 외부 tool을 실행하려면 먼저 답해야 하는 질문이 있다.

```text
이 tool은 등록된 tool인가?
어떤 action type인가?
어떤 scope가 필요한가?
위험도는 어느 정도인가?
입력과 출력 schema는 무엇인가?
현재 사용자는 이 tool을 요청할 권한이 있는가?
```

지난 단계에서는 승인 요청과 replay를 만들었다.  
이번 단계에서는 그 앞단에 `Tool Schema Registry`와 `Scope Check`를 추가했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 왜 registry가 필요한가

Tool 이름을 문자열로만 다루면 운영 경계가 약해진다.

```text
workflow.request-change
internal-records.lookup
```

이 이름만으로는 알 수 없는 것이 많다.

- 읽기인지 쓰기인지
- 실행에 필요한 권한은 무엇인지
- 승인 대기가 필요한 위험도인지
- 입력 payload가 맞는지
- 비활성화된 tool은 아닌지

그래서 tool을 runtime 내부에 등록된 제품 리소스로 만들었다.

## ToolDefinition

이번 단계에서 추가한 모델은 `ToolDefinition`이다.

```text
ToolDefinition
  name
  action_type
  required_scope
  risk_level
  description
  input_schema
  output_schema
  enabled
```

현재 local registry에는 두 개의 tool이 있다.

| tool | action | required scope | risk |
| --- | --- | --- | --- |
| `internal-records.lookup` | `read` | `records:read` | low |
| `workflow.request-change` | `write` | `workflow:request` | high |

`workflow.request-change`는 scope가 있어도 바로 실행되지 않는다.  
risk level이 high이기 때문에 승인 대기로 전환된다.

## Scope Check

Agent 실행 요청에는 `actor_scopes`를 받는다.

```json
{
  "tenant_id": "default",
  "user_id": "operator-01",
  "scenario": "operations",
  "message": "정책 문서를 근거로 보고서 생성 요청을 처리해줘",
  "actor_scopes": ["records:read", "workflow:request"]
}
```

Tool Runtime은 registry에서 tool definition을 찾고 다음 순서로 검사한다.

```text
1. 등록된 tool인가
2. enabled 상태인가
3. 요청 action type이 definition과 일치하는가
4. actor_scopes에 required_scope가 있는가
5. risk_level에 따라 allowed / approval_required를 결정한다
```

scope가 없으면 `denied`가 된다.

```text
decision: denied
reason: 필요 scope가 없습니다: workflow:request
```

이 경우 승인 요청도 만들지 않는다.  
승인은 권한 없는 실행을 우회하는 통로가 아니기 때문이다.

## API

운영자가 registry를 볼 수 있도록 API도 추가했다.

```text
GET /v1/tools
```

응답 예시:

```json
[
  {
    "name": "workflow.request-change",
    "action_type": "write",
    "required_scope": "workflow:request",
    "risk_level": "high",
    "description": "외부 상태 변경이 필요한 workflow 요청을 생성한다.",
    "enabled": true
  }
]
```

이 API는 나중에 운영자 dashboard의 tool catalog 화면으로 이어질 수 있다.

## 실행 흐름 변화

이전 흐름:

```text
Agent -> Tool Runtime -> Policy -> Approval
```

이번 흐름:

```text
Agent
  -> Tool Request
  -> Tool Registry
  -> Scope Check
  -> Risk Policy
  -> Tool Execution
  -> Approval Request
  -> Audit Event
```

이제 Tool Runtime은 단순 실행기가 아니라 tool governance 계층이 됐다.

## 테스트

이번 단계에서 추가로 확인한 것:

- `/v1/tools`가 등록된 tool catalog를 반환한다.
- required scope가 있으면 high risk write tool이 approval request로 전환된다.
- required scope가 없으면 tool execution이 denied가 된다.
- denied tool execution은 approval request를 만들지 않는다.
- audit event에는 `tool.denied`가 남는다.

검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 6 passed
```

## 다음 단계

이제 MCP 서버를 붙일 준비가 됐다.

바로 MCP부터 만들 수도 있었지만, registry와 scope가 없는 MCP 연동은 운영 제품으로 약하다.  
다음 단계에서는 이 registry를 기준으로 MCP Streamable HTTP tool server를 분리할 수 있다.

다음 구현 후보:

1. MCP-compatible tool server boundary
2. tool schema export
3. external tool adapter
4. timeout/retry/fallback
5. operator dashboard

Tool을 연결하는 것보다 중요한 것은 어떤 tool을 어떤 권한과 위험도 안에서 실행하는지 제품 상태로 남기는 것이다.
