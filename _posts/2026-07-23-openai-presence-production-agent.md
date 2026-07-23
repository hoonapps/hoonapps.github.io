---
title: "AI Radar: OpenAI Presence가 보여준 production agent 운영 방식"
date: 2026-07-23 10:20:00 +0900
categories: [AI, DeepDive]
tags: [ai, agent, openai, presence, enterprise, production-agent, evaluation, guardrails, escalation, backend, ax]
image: /assets/img/posts/2026/07/openai-presence-production-agent.svg
---

OpenAI가 2026년 7월 22일 `OpenAI Presence`를 공개했다. 설명만 보면 voice agent와 chat agent를
기업에 붙여주는 제품처럼 보인다. 그런데 내가 보기에는 조금 더 중요한 신호가 있다.

이제 agent 제품의 중심이 "모델을 제공한다"에서 "운영 가능한 업무 단위를 같이 배포한다"로 넘어가고
있다. 모델, 지식 연결, 권한, 정책, 평가, 에스컬레이션, 개선 루프가 한 묶음으로 팔리기 시작한 것이다.

## 본 자료

- OpenAI: [Introducing OpenAI Presence](https://openai.com/index/introducing-openai-presence/)
- OpenAI: [Safety and alignment in an era of long-horizon models](https://openai.com/index/safety-alignment-long-horizon-models/)
- OpenAI: [OpenAI and Hugging Face partner to address security incident during model evaluation](https://openai.com/index/hugging-face-model-evaluation-security-incident/)

대표 이미지는 Presence의 production agent 구조를 기준으로 직접 정리한 다이어그램이다.

## 핵심 메모

OpenAI는 Presence를 customer workflow와 internal workflow에 AI agent를 넣기 위한 enterprise product로
설명한다. 현재는 voice와 chat agent를 지원하고, 고객 지원, outbound sales, 고위험 내부 업무 같은
흐름이 먼저 언급됐다.

중요한 구성 요소는 아래 쪽이다.

- policies and standard operating procedures
- guardrails
- approved actions
- simulations
- evaluation tools
- escalation rules
- Codex-powered improvement process

이 목록을 보면 Presence는 단순한 챗봇 배포 도구가 아니다. 특정 업무를 정하고, 필요한 지식과 시스템만
연결하고, 어떤 action이 허용되는지 정하고, 언제 사람에게 넘겨야 하는지 운영 규칙을 잡는 제품에
가깝다.

OpenAI는 자사 영어 전화 지원 채널에서도 Presence를 쓰고 있다고 밝혔다. 공개 수치 기준으로는 inbound
issue의 75%를 사람 도움 없이 해결하고, Codex 기반 개선 루프를 통해 human handoff를 10일 만에 15%
포인트 줄였다고 한다.

## 왜 지금 중요한가

agent를 production에 넣을 때 가장 어려운 부분은 데모가 아니다.

```text
한 번 잘 대답한다
-> 매일 들어오는 예외를 처리한다
-> 정책 변경을 따라간다
-> 잘못된 action을 막는다
-> 사람이 맡아야 할 순간을 구분한다
-> 운영 로그를 보고 계속 고친다
```

Presence가 건드리는 지점은 이 반복 구간이다. 기업 업무는 항상 예외가 있고, 정책이 바뀌고, 시스템
연동이 늘어난다. 그래서 agent가 production에서 살아남으려면 모델 성능만으로는 부족하다.

내 기준으로 Presence의 핵심은 `agent deployment`가 아니라 `agent operations`다.

```text
workflow
-> scoped knowledge
-> scoped system access
-> policy
-> simulation
-> evaluation
-> launch
-> session review
-> approved rollout
```

이 흐름이 있어야 agent를 계속 운영할 수 있다.

## 백엔드 관점에서 보면

Presence 같은 제품을 직접 만든다고 생각하면, 백엔드는 다음 데이터를 반드시 들고 있어야 한다.

- 업무별 agent definition
- 연결된 knowledge source와 system connector
- action별 permission
- approval rule
- escalation condition
- simulation case
- evaluation result
- production session log
- incident와 handoff reason
- agent version과 rollout history

특히 `agent version`이 중요하다. 정책 하나를 바꿨을 때도 실제로는 agent의 동작이 바뀐다. 그러면
이전 버전과 새 버전을 비교해야 하고, simulation을 다시 돌려야 하고, 일부 채널에만 먼저 배포하는
controlled rollout이 필요하다.

이건 LLM prompt를 수정하는 일이 아니라 production system을 배포하는 일에 가깝다.

## 안전 관점에서 보면

OpenAI가 며칠 전 공개한 long-horizon model 글과 Hugging Face 보안 사고 글을 같이 보면 방향이 더
선명해진다. 오래 실행되는 agent는 단일 action만 검사해서는 부족하다. 여러 단계가 모이면 원래 허용하지
않은 결과로 이어질 수 있다.

그래서 Presence에서 말하는 simulations, graders, guardrails, escalation은 부가 기능이 아니다.
production agent의 기본 안전장치다.

내가 볼 때 필요한 질문은 이쪽이다.

```text
이 action은 어느 업무에서만 허용되는가
이 agent는 어떤 데이터에만 접근하는가
언제 사람 승인으로 넘어가는가
실패한 대화는 어떤 evaluation case로 남는가
정책 변경 후 기존 session replay를 돌릴 수 있는가
새 버전은 어디까지 rollout됐는가
```

이 질문에 답할 수 있어야 agent가 조직 안에서 오래 돌아갈 수 있다.

## 판단

**Watch.**

OpenAI Presence는 self-serve SaaS라기보다 eligible enterprise customers를 위한 limited general
availability 제품이다. OpenAI Forward Deployed Engineers와 systems integrator가 같이 붙는 구조라서,
당장 모든 팀이 직접 써볼 수 있는 물건은 아니다.

하지만 방향은 중요하다. 앞으로 agent 제품은 "우리 모델이 더 똑똑하다"만으로 설명되기 어렵다. 실제
업무에 들어가려면 정책, 승인, 평가, 로그, 개선 루프까지 묶어서 보여줘야 한다.

내가 앞으로 볼 지점은 세 가지다.

- Presence의 evaluation과 simulation 구조가 얼마나 일반화되는가
- Codex 기반 개선 루프가 운영팀의 변경 관리와 잘 맞는가
- agent versioning, rollout, audit이 독립 제품처럼 드러나는가

agent 시대의 백엔드는 모델 호출 서버가 아니라 운영 가능한 실행 시스템에 가까워지고 있다. Presence는
그 방향을 꽤 노골적으로 보여주는 제품이다.
