---
title: "Enterprise AX Agent Platform 2단계: Tool Runtime과 승인 경계"
date: 2026-06-19 17:20:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, tool-runtime, governance, audit-log, backend, llmops]
---

Agent가 문서를 검색하고 답변하는 것까지는 비교적 단순하다.  
제품 경계가 어려워지는 지점은 Agent가 외부 시스템을 실행하려고 할 때다.

예를 들어 사용자가 이렇게 요청했다고 하자.

```text
정책 문서를 근거로 보고서 생성 요청을 처리해줘.
```

이 요청은 두 가지로 나뉜다.

- 근거 문서를 검색하고 실행안을 작성하는 일
- 외부 workflow나 업무 시스템에 상태 변경을 만드는 일

두 일을 같은 LLM 응답 안에 섞으면 위험하다.  
그래서 2단계에서는 Agent 추론과 외부 실행 사이에 `Tool Runtime`을 넣었다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 목표

이번 단계의 목표는 tool을 많이 붙이는 것이 아니다.  
tool 실행 경계를 제품 상태로 만드는 것이다.

```text
Agent Reasoning
  -> Tool Request
  -> Tool Policy
  -> Tool Runtime
  -> Tool Execution
  -> Audit Event
```

Agent가 외부 시스템을 바로 변경하지 않고, 정책 결정 결과를 남기도록 만들었다.

## 도메인 모델

새로 추가한 핵심 모델은 세 가지다.

```text
ToolRequest
ToolExecution
ToolDecision
```

`ToolRequest`는 Agent가 실행하고 싶은 표준화된 도구 요청이다.

```text
name: workflow.request-change
action_type: write
risk_level: high
input_payload: {...}
```

`ToolExecution`은 실제 runtime 판단 결과다.

```text
tool_name: workflow.request-change
action_type: write
decision: approval_required
status: pending_approval
```

중요한 점은 실행 결과가 문자열 로그가 아니라 도메인 객체라는 것이다.  
그래야 API 응답, 감사 이벤트, DB 저장, 운영자 화면으로 같은 정보를 흘릴 수 있다.

## 정책

현재 정책은 작게 시작했다.

| action type | 기본 정책 |
| --- | --- |
| `read` | 허용 |
| `approval` | 허용 |
| `write` + low risk | 허용 |
| `write` + medium/high risk | 승인 대기 |
| unknown | 거부 |

쓰기성 작업은 자동 실행하지 않고 `approval_required`로 남긴다.  
이건 제품 기본값이다. Agent가 좋은 답변을 했더라도 외부 상태 변경은 별도 경계를 지나야 한다.

## 실행 흐름

Agent 실행 흐름은 이렇게 바뀌었다.

```text
POST /v1/agents/runs
  -> 개인정보 마스킹
  -> 질문 유형 분류
  -> 검색 전략 선택
  -> 정책 사전 검사
  -> 문서 검색
  -> Tool Runtime 판단
  -> 근거 기반 답변 생성
  -> Agent 실행 저장
  -> Tool 감사 이벤트 저장
```

질문 유형이 `action`이 아니면 tool runtime은 skip된다.  
질문 유형이 `action`이면 요청 문장을 표준 tool request로 바꾼다.

현재 로컬 runtime은 두 가지 요청으로 정규화한다.

| 조건 | tool |
| --- | --- |
| 조회/확인/search/get | `internal-records.lookup` |
| 그 외 action | `workflow.request-change` |

## API 응답

이제 Agent 실행 응답에는 `tool_executions`가 포함된다.

```json
{
  "status": "succeeded",
  "query_type": "action",
  "tool_executions": [
    {
      "tool_name": "workflow.request-change",
      "action_type": "write",
      "decision": "approval_required",
      "status": "pending_approval",
      "reason": "외부 상태를 변경하는 작업은 승인 대기 상태로 전환합니다."
    }
  ]
}
```

실행이 차단된 것이 아니라, 답변은 생성하고 외부 상태 변경만 승인 대기로 남긴다.  
이 차이가 중요하다. 사용자는 실행안을 받을 수 있고, 운영자는 승인 경계를 볼 수 있다.

## 감사 이벤트

Tool Runtime 결과는 감사 이벤트로도 남는다.

```text
event_type: tool.approval_required
resource_type: tool_call
payload:
  tool_name: workflow.request-change
  action_type: write
  status: pending_approval
```

나중에 운영자 dashboard를 만들면 이 이벤트를 기준으로 승인 대기 목록, 거부 목록, 실패 목록을 만들 수 있다.

## 테스트

이번 단계에서 테스트도 추가했다.

- action 질의가 tool execution을 생성하는지
- 쓰기성 tool이 `approval_required`가 되는지
- `tool.approval_required` 감사 이벤트가 남는지
- API 응답에 `tool_executions`가 포함되는지

검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 5 passed
```

## 다음 단계

다음에는 이 local runtime을 실제 tool server 경계로 확장할 생각이다.

1. MCP Streamable HTTP 서버
2. tool schema registry
3. tool별 required scope
4. 승인 요청 API
5. 승인 후 실행 replay
6. tool call idempotency

Agent 제품에서 중요한 것은 tool을 많이 붙이는 것이 아니다.  
어떤 tool을 어떤 권한으로, 어떤 감사 경계 안에서 실행했는지 남기는 것이다.
