---
title: "Enterprise AX Agent Platform 6단계: Approval Reject와 닫힌 상태 전이"
date: 2026-06-19 19:08:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, approval, governance, audit, backend]
---

지난 단계까지는 쓰기성 tool call을 `approval_required`로 전환하고, 운영자가 승인하면 replay하는 흐름을 만들었다.

하지만 운영 제품에서는 승인만큼 반려도 중요하다.  
운영자가 실행하지 않기로 결정한 요청은 단순히 pending 목록에서 방치되면 안 된다.

이번 단계에서는 approval workflow에 `reject` 상태 전이를 추가했다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 문제

기존 상태 전이는 다음과 같았다.

```text
pending -> executed
```

이 구조에는 빈 부분이 있다.

```text
pending 상태의 요청을 실행하지 않기로 결정하면 어떻게 닫을 것인가?
반려 사유는 어디에 남길 것인가?
반려된 요청에 approve가 다시 들어오면 어떻게 할 것인가?
감사 이벤트는 어떻게 남길 것인가?
```

그래서 상태 전이를 다음처럼 확장했다.

```text
pending -> executed
pending -> rejected
```

`executed`와 `rejected`는 둘 다 닫힌 상태다.

## API

새 endpoint는 다음과 같다.

```text
POST /v1/approvals/{approval_id}/reject
```

요청:

```json
{
  "tenant_id": "default",
  "rejected_by": "operator-02",
  "reason": "요청 근거가 부족하여 실행하지 않습니다."
}
```

응답:

```json
{
  "status": "rejected",
  "approved_by": "operator-02",
  "replay_result": {
    "decision": "rejected",
    "rejected_by": "operator-02",
    "reason": "요청 근거가 부족하여 실행하지 않습니다."
  }
}
```

필드 이름은 기존 schema와의 호환을 위해 `approved_by`를 그대로 사용했다.  
의미상으로는 이 요청을 닫은 운영자다.

## 상태 전이 규칙

`ApprovalUseCase.reject()`는 다음 규칙을 따른다.

```text
1. approval request가 없으면 404
2. pending이 아니면 기존 상태 그대로 반환
3. pending이면 rejected로 변경
4. replay_result에 반려 결정과 사유 저장
5. approval.rejected audit event 기록
```

반려된 요청에 다시 approve가 들어와도 replay하지 않는다.

이 규칙은 승인 replay의 멱등성과 같은 방향이다.  
닫힌 요청은 다시 외부 상태 변경으로 이어지지 않아야 한다.

## 감사 이벤트

반려 시 다음 이벤트가 남는다.

```text
event_type: approval.rejected
resource_type: approval_request
payload:
  agent_run_id
  tool_execution_id
  tool_name
  reason
```

이제 운영자는 승인된 action뿐 아니라 실행하지 않기로 결정한 action도 추적할 수 있다.

## 테스트

이번 단계에서 추가한 테스트는 다음을 검증한다.

- 승인 대기 요청을 reject API로 반려할 수 있다.
- 반려된 요청은 pending 목록에서 사라진다.
- 반려된 요청의 `replay_result`에 사유가 남는다.
- 반려 후 approve를 호출해도 replay가 실행되지 않는다.
- 기존 API, MCP, tool runtime 테스트가 함께 통과한다.

검증 결과:

```text
make verify
ruff check .                       -> 통과
mypy apps --explicit-package-bases -> 통과
pytest                             -> 9 passed
```

## 다음 단계

승인 queue의 상태 전이는 이제 최소 운영 흐름을 갖췄다.

다음으로는 실행 안정성 쪽을 보강할 수 있다.

1. Tool Gateway timeout/retry/fallback
2. audit event export
3. operator dashboard
4. approval comment history
5. evaluation dataset과 회귀 테스트

Agent가 action을 제안하는 것보다 중요한 것은 그 action을 실행하거나 실행하지 않는 결정이 제품 상태로 남는 것이다.
