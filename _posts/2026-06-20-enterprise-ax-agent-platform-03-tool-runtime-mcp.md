---
title: "Enterprise AX Agent Platform 03: Tool Runtime과 MCP 경계"
date: 2026-06-20 00:03:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, tool-runtime, mcp, json-rpc, backend]
description: "Agent 추론과 외부 tool 실행 사이에 registry, scope, policy, audit를 통과하는 runtime 경계를 만들었다."
---

Agent가 외부 시스템을 호출하는 순간부터 답변 생성과 실행을 분리해야 한다. 같은 LLM 응답 안에서 판단과 실행을 섞으면 승인, 감사, 재시도, 권한 제어를 놓치기 쉽다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## Tool Definition

tool은 코드 함수가 아니라 등록된 schema로 다룬다.

```text
name
description
input_schema
output_schema
action_type
risk_level
required_scopes[]
```

Agent가 어떤 tool을 부를 수 있는지, 그 tool이 조회성인지 쓰기성인지, 어떤 권한이 필요한지를 registry에서 먼저 결정한다.

## Runtime 흐름

Tool Runtime은 다음 순서로 동작한다.

```text
tool request
-> registry lookup
-> required scope check
-> risk policy evaluation
-> read action immediate execution
-> write action approval_required transition
-> audit event append
```

쓰기성 action은 바로 실행하지 않는다. approval request를 만들고 `approval_required` 상태를 반환한다. 이 상태 전이는 Agent 답변 실패가 아니라 정상적인 운영 제어 결과다.

## MCP-Compatible Boundary

외부 클라이언트가 같은 runtime을 사용할 수 있도록 `/mcp` JSON-RPC endpoint를 추가했다.

```text
POST /mcp

tools/list
tools/call
```

여기서 중요한 점은 MCP endpoint가 별도 실행 경로가 아니라는 것이다. MCP로 들어온 tool call도 동일하게 registry, scope, risk policy, approval, audit 경로를 지난다.

```text
MCP Client
  -> JSON-RPC Router
  -> ToolCallUseCase
  -> ToolRuntimePort
  -> Policy / Approval / Audit
```

## Audit와 Trace

tool call 결과는 AgentRun trace와 audit event 양쪽에 남긴다.

trace는 한 실행 안에서 어떤 일이 일어났는지 보여준다. audit event는 시스템 전체에서 누가 무엇을 시도했고 어떤 정책 결과가 나왔는지 보여준다. 두 기록의 목적이 다르므로 둘 다 필요하다.

## 결과

이 단계의 핵심은 tool 실행을 Agent 내부 구현 세부사항으로 두지 않았다는 점이다.

- tool schema registry
- required scope check
- read/write action 분리
- approval-required 상태 전이
- MCP-compatible JSON-RPC endpoint
- AgentRun trace와 audit event 기록

이 경계가 있어야 다음 단계에서 승인, 반려, 멱등성, gateway 신뢰성을 독립적으로 붙일 수 있다.
