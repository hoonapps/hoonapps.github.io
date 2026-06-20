---
title: "Enterprise AX Agent Platform 06: Evaluation과 회귀 게이트"
date: 2026-06-20 00:06:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, evaluation, regression-test, ci, backend]
description: "Agent 답변 품질을 EvaluationRun으로 기록하고 expected facts 기반 회귀 평가를 CI gate로 연결했다."
---

Agent 제품은 답변을 생성하는 것만으로 끝나지 않는다. 검색 전략, chunking, policy, prompt, adapter를 바꾼 뒤에도 답변 품질이 유지되는지 측정해야 한다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## EvaluationRun

평가 실행은 별도 리소스로 만들었다.

```text
EvaluationRun
  id
  status
  cases[]
  average_score
  pass_rate
  created_at
```

각 case는 질문과 기대 사실을 가진다.

```text
question
expected_facts[]
minimum_score
```

답변이 기대 사실을 얼마나 포함하는지 측정하고, 전체 pass rate를 계산한다.

## API

평가 API는 다음 흐름을 제공한다.

```text
POST /v1/evaluations/runs
GET  /v1/evaluations/runs/{evaluation_run_id}
```

평가도 audit event를 남긴다. 품질 측정 결과가 운영 이벤트와 분리되면 나중에 어떤 변경 이후 품질이 떨어졌는지 추적하기 어렵다.

## Regression Dataset

CI에서 사용하는 dataset은 JSON으로 둔다.

```text
sample_documents
evaluation_cases
minimum_average_score
minimum_pass_rate
```

테스트는 샘플 문서를 적재하고 실제 use case를 호출한 뒤 점수를 검사한다. 단순 mock 테스트가 아니라 제품 실행 경로를 통과한다.

## Gate 기준

회귀 게이트는 두 가지를 본다.

```text
average_score
pass_rate
```

평균 점수만 보면 일부 case가 완전히 실패해도 묻힐 수 있다. pass rate만 보면 부분 품질 하락을 놓칠 수 있다. 그래서 둘을 같이 둔다.

## 운영 화면과 연결

평가 결과는 operations summary와 dashboard에서 볼 수 있게 했다.

운영자가 봐야 하는 것은 최신 평가가 성공했는지뿐 아니라, 최근 실행 품질이 어느 방향으로 움직이는지다. AgentRun feedback과 evaluation run을 함께 보면 실제 사용자 반응과 기준 dataset 품질을 분리해서 판단할 수 있다.

## 결과

이 단계에서 품질은 사람이 감으로 보는 결과물이 아니라 시스템 리소스가 됐다.

- EvaluationRun API
- expected facts scoring
- JSON regression dataset
- CI regression gate
- audit event 기록
- operations read model 연결

Agent 품질 관리는 모델 호출 뒤에 붙이는 리포트가 아니라 개발과 운영 경로 안에 들어가야 한다.
