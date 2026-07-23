---
title: "AI Radar: Palantir FDE가 보여준 현장 배치형 엔지니어링 모델"
date: 2026-07-23 10:34:00 +0900
categories: [AI, DeepDive]
tags: [ai, agent, palantir, fde, forward-deployed-engineer, ontology, foundry, aip, enterprise, backend, ax]
image: /assets/img/posts/2026/07/palantir-fde-operating-model.svg
---

Palantir의 `FDE`, 즉 Forward Deployed Engineer는 요즘 AI 회사들이 다시 꺼내는 개념이다. OpenAI,
Anthropic, 여러 enterprise AI 회사들이 고객 현장에 엔지니어를 붙여 실제 업무에 맞게 AI를 배포하려는
흐름과 연결된다.

FDE는 언어가 아니다. 단순 직무명으로만 보기에도 부족하다. 내가 보기에는 Palantir가 만든 핵심은
"현장 문제를 제품 구조로 되돌리는 엔지니어링 운영 모델"에 가깝다.

## 본 자료

- Palantir Docs: [AI FDE overview](https://www.palantir.com/docs/foundry/ai-fde/overview)
- Palantir Blog: [Dev versus Delta: Demystifying engineering roles at Palantir](https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87)
- Palantir Job: [Forward Deployed AI Engineer](https://jobs.lever.co/palantir/636fc05c-d348-4a06-be51-597cb9e07488)
- Palantir Blog: [How Palantir Foundry's Ontology Deploys Data Science to the Front Line](https://blog.palantir.com/how-palantir-foundrys-ontology-deploys-data-science-to-the-front-line-7a9679bdfd01)

대표 이미지는 FDE 운영 모델을 기준으로 직접 정리한 다이어그램이다.

## 핵심 메모

Palantir는 전통적으로 Software Engineer를 `Dev`, Forward Deployed Software Engineer를 `Delta`라고
부른다. Palantir 설명에 따르면 Dev는 Foundry와 Gotham 같은 플랫폼 컴포넌트를 만들고, Delta는 특정
고객의 기술적 성과를 만들기 위해 플랫폼을 배포하고 커스터마이즈한다.

여기서 중요한 구분은 이 문장이다.

```text
Dev: one capability, many customers
Delta: one customer, many capabilities
```

FDE는 고객 옆에서 요구사항을 듣고 티켓을 전달하는 역할이 아니다. 고객의 실제 데이터, 실제 운영,
실제 제약 안에서 작동하는 소프트웨어를 만든다. Palantir의 Forward Deployed AI Engineer 채용 설명도
비슷하다. Gen AI 전략과 구현을 같이 맡고, end-to-end workflow를 만들고, production까지 가져가며,
현장에서 배운 내용을 AIP 제품군으로 되돌린다고 설명한다.

이게 FDE 개념의 핵심이다.

```text
고객 현장
-> 작동하는 workflow
-> 반복되는 패턴 발견
-> platform capability로 흡수
-> 다음 배포가 빨라짐
```

## 왜 지금 중요한가

AI 제품은 데모가 쉽다. 실제 업무 배포는 어렵다.

기업 안에는 오래된 시스템, 엉킨 권한, 불완전한 데이터, 문서화되지 않은 업무 규칙, 부서별 예외가
같이 있다. 그래서 API만 열어주거나 챗봇만 붙인다고 업무가 바뀌지 않는다.

FDE 모델은 이 현실을 정면으로 인정한다.

```text
고객의 문제를 추상화하기 전에 먼저 들어간다
현장에서 작동하는 것을 만든다
반복되는 부분만 제품으로 승격한다
제품팀은 현장의 거친 패턴을 플랫폼 기능으로 다듬는다
```

이 구조는 AI agent 시대에 더 중요해진다. agent는 단순 UI보다 더 많은 것을 요구한다. 데이터 접근,
tool 권한, 승인 흐름, 업무 지식, 실패 처리, 감사 로그까지 모두 엮인다. 이걸 고객이 스스로 알아서
붙이길 기다리면 대부분 production까지 가지 못한다.

## Ontology와 연결해서 보면

Palantir의 FDE 모델은 Ontology와 같이 봐야 한다. Foundry Ontology는 조직의 entity, relationship,
process, event를 한 곳에 묶고, 실제 action과 연결하려는 구조다.

Ontology 글에서 Palantir는 데이터 과학자가 모델을 만들고 끝나는 게 아니라, 어떤 업무 의사결정에
모델이 쓰이는지 보고, 결과와 피드백까지 닫힌 루프로 연결할 수 있다고 설명한다.

이건 FDE가 현장에서 하는 일과 잘 맞는다.

- 어떤 데이터가 중요한지 찾는다.
- 누가 실제 의사결정을 하는지 파악한다.
- 모델이나 workflow가 어디에 붙어야 하는지 정한다.
- 사용되지 않는 이유를 관찰한다.
- 다시 Ontology와 application layer를 수정한다.

즉 FDE는 고객 맞춤 코드를 무한히 찍어내는 사람이 아니라, 현장의 업무 구조를 Ontology와 제품 구조로
번역하는 사람에 가깝다.

## AI FDE가 의미하는 것

재밌는 건 Palantir가 이제 `AI FDE`라는 제품 개념도 문서화했다는 점이다. Palantir Docs 기준으로 AI
FDE는 자연어 요청을 Foundry operation으로 바꾸고, data transformation, code repository 관리,
ontology 생성과 수정, build 실행 같은 작업을 수행하는 interactive agent다.

여기서 중요한 부분은 권한과 context다. AI FDE는 기존 사용자 권한을 따른다. 모델, tool, data 범위를
선택할 수 있고, 필요한 capability만 열어줄 수 있다. 기본 상태에서는 최소 context로 시작하고, 필요한
dataset, folder, documentation을 추가하면서 context를 확장한다.

또 closed-loop operation도 언급된다.

```text
action 실행
-> 결과 관찰
-> 다음 action 결정
-> preview, CI, function test로 검증
-> branch proposal 또는 pull request로 리뷰
```

이건 사람이 하던 FDE의 일부를 agent runtime으로 옮기는 방향이다. 사람 FDE가 사라진다는 뜻은 아니다.
오히려 반대에 가깝다. 현장의 문제를 이해하고, 어디까지 자동화할지 판단하고, 조직 안에 production
workflow로 심는 역할은 더 중요해진다.

## 백엔드 관점에서 보면

FDE 모델을 제품으로 만들려면 백엔드에는 이런 구조가 필요하다.

- 고객별 workspace와 tenant boundary
- system connector와 data permission
- workflow definition
- ontology version
- action permission과 approval rule
- deployment history
- field feedback
- support ticket과 incident
- evaluation case
- product backlog로 승격되는 pattern

FDE가 현장에서 만든 해결책이 개인기에서 끝나면 scaling이 안 된다. 반대로 모든 고객 문제를 처음부터
범용 제품으로 만들려고 하면 속도가 안 난다.

그래서 중간 계층이 필요하다.

```text
field patch
-> reusable workflow
-> ontology pattern
-> product primitive
-> platform capability
```

이 흐름이 있어야 현장 배치형 엔지니어링이 컨설팅으로 끝나지 않고 제품 회사의 학습 루프가 된다.

## 조심할 지점

FDE 모델에는 분명한 위험도 있다.

고객별로 너무 많은 예외를 만들면 기술 부채가 커진다. 현장 엔지니어가 너무 강하면 제품팀이 방향을
잃을 수 있다. 반대로 제품팀이 현장 피드백을 흡수하지 못하면 FDE는 고급 SI처럼 보이기 쉽다.

그래서 FDE 모델의 성패는 사람을 고객 옆에 배치하는 것만으로 결정되지 않는다.

```text
현장 해결책을 어떻게 제품 primitive로 바꾸는가
고객별 custom code를 어디까지 허용하는가
반복 패턴을 누가 수집하고 정리하는가
platform team이 field feedback을 얼마나 빠르게 흡수하는가
고객별 배포가 audit, versioning, rollback을 갖는가
```

이 질문에 답하지 못하면 FDE는 제품 전략이 아니라 비싼 구현 인력이 된다.

## 판단

**Watch.**

Palantir의 FDE 개념은 AI 시대에 다시 중요해지고 있다. 이유는 간단하다. AI agent는 enterprise 안에서
그냥 설치되는 물건이 아니라, 실제 업무 흐름에 맞춰 배치되고 운영되어야 하는 시스템이기 때문이다.

내가 앞으로 볼 지점은 세 가지다.

- 사람 FDE와 AI FDE가 어떻게 역할을 나눌 것인가
- field feedback이 Ontology, AIP, Foundry 같은 platform capability로 얼마나 빨리 흡수되는가
- OpenAI 같은 AI 회사들이 이 모델을 단순 고객 지원이 아니라 제품 학습 루프로 만들 수 있는가

FDE의 본질은 고객 옆에 앉는 것이 아니다. 현실의 업무를 소프트웨어 구조로 번역하고, 그 과정에서
반복되는 패턴을 플랫폼으로 되돌리는 것이다. AI agent가 enterprise로 들어갈수록 이 모델은 더 자주
소환될 가능성이 크다.
