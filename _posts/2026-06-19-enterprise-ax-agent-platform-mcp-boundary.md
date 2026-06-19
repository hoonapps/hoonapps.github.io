---
title: "Enterprise AX Agent Platform 5단계: MCP-Compatible Tool Boundary"
date: 2026-06-19 18:36:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, mcp, json-rpc, tool-runtime, backend]
---

이번 단계에서는 Agent 내부에 있던 tool 실행 흐름을 외부 클라이언트가 호출할 수 있는 boundary로 분리했다.

핵심은 단순히 `/mcp` 엔드포인트를 추가하는 것이 아니다.  
외부에서 tool을 호출해도 기존 runtime의 registry, scope, risk policy, audit, approval 흐름을 그대로 타게 만드는 것이다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 구현한 것

이번 단계에서 추가한 기능은 세 가지다.

```text
1. Tool Gateway Port
2. ToolCallUseCase
3. MCP-compatible JSON-RPC endpoint
```

기존 `LocalToolRuntime`은 policy decision과 로컬 실행 결과 생성을 함께 맡고 있었다.  
이 구조에서는 나중에 MCP, 사내 API, workflow engine을 붙일 때 실행 책임이 섞이기 쉽다.

그래서 다음처럼 역할을 나눴다.

```text
ToolCallUseCase
  -> ToolRegistry
  -> ToolRuntime
  -> ToolPolicy
  -> ToolGatewayPort
  -> LocalToolGateway
```

Runtime은 실행 가능 여부를 판단하고, Gateway는 실제 실행 어댑터 역할을 맡는다.

## Tool Gateway

새로 추가한 포트는 `ToolGatewayPort`다.

```text
invoke(request, definition) -> ToolGatewayResult
replay(approval) -> ToolGatewayResult
```

이 포트를 둔 이유는 명확하다.

- Runtime은 등록 여부, required scope, risk level, approval decision만 담당한다.
- Gateway는 외부 시스템 호출, timeout, retry, fallback을 담당할 수 있다.
- 지금은 `LocalToolGateway`지만 이후 HTTP/MCP/workflow adapter로 교체할 수 있다.

즉, tool 실행을 제품 내부 정책 계층과 외부 호출 계층으로 분리했다.

## ToolCallUseCase

MCP endpoint에서 tool을 바로 runtime에 넘기지 않았다.

외부 클라이언트 호출도 제품의 use case로 처리해야 한다.

`ToolCallUseCase`는 다음을 담당한다.

- tool registry 조회
- input schema required field 검사
- actor scope 전달
- runtime 실행
- AgentRun 생성
- AuditEvent 기록
- approval_required 결과의 ApprovalRequest 생성

이렇게 해야 `/mcp`로 들어온 호출도 운영 이력에서 빠지지 않는다.

## JSON-RPC Endpoint

새 endpoint는 다음 하나다.

```text
POST /mcp
```

지원하는 method는 세 가지다.

```text
initialize
tools/list
tools/call
```

`tools/list`는 registry에 등록된 tool을 MCP 형태로 반환한다.

```json
{
  "name": "workflow.request-change",
  "description": "외부 상태 변경이 필요한 workflow 요청을 생성한다.",
  "inputSchema": {
    "type": "object",
    "required": ["request"]
  },
  "_meta": {
    "required_scope": "workflow:request",
    "risk_level": "high",
    "enabled": true
  }
}
```

`tools/call`은 다음처럼 호출한다.

```json
{
  "jsonrpc": "2.0",
  "id": "call-1",
  "method": "tools/call",
  "params": {
    "tenant_id": "default",
    "actor_id": "operator-01",
    "actor_scopes": ["records:read"],
    "name": "internal-records.lookup",
    "arguments": {
      "query": "최근 승인 대기 업무 조회"
    }
  }
}
```

응답에는 MCP의 `content`와 함께 제품 내부에서 쓰기 좋은 `structuredContent`를 같이 넣었다.

```json
{
  "structuredContent": {
    "tool_execution_id": "...",
    "tool_name": "internal-records.lookup",
    "decision": "allowed",
    "status": "succeeded"
  },
  "isError": false
}
```

## 승인 경계

중요한 부분은 쓰기성 tool이다.

`workflow.request-change`는 `workflow:request` scope가 없으면 `denied`가 된다.  
scope가 있더라도 risk level이 high이므로 즉시 실행하지 않고 `approval_required`가 된다.

이때 `ToolCallUseCase`는 `ApprovalRequest`를 생성한다.

```text
MCP client
  -> tools/call
  -> ToolCallUseCase
  -> ToolRuntime
  -> approval_required
  -> ApprovalRequest
  -> AuditEvent
```

외부 tool 호출이 들어와도 승인 queue와 audit trail에서 빠지지 않는다.

## 테스트

이번 단계에서 추가한 테스트는 다음을 검증한다.

- `/mcp initialize`가 server capability를 반환한다.
- `/mcp tools/list`가 registry tool 목록을 반환한다.
- 조회성 tool call은 scope가 있으면 `allowed`로 실행된다.
- 쓰기성 tool call은 scope가 없으면 `denied`가 된다.
- 쓰기성 high-risk tool call은 scope가 있어도 `approval_required`가 된다.
- MCP에서 생성된 approval request가 pending 목록에 나타난다.

검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 8 passed
```

## 다음 단계

이제 tool boundary는 제품 안에 들어왔다.

다음으로 중요한 것은 실행 안정성이다.

후보는 다음과 같다.

1. Tool Gateway timeout/retry/fallback
2. approval reject API
3. operator dashboard
4. audit event export
5. evaluation dataset과 회귀 테스트

지금 구조에서는 이 기능들이 자연스럽게 들어갈 위치가 있다.  
그 점이 이번 단계의 가장 중요한 결과다.
