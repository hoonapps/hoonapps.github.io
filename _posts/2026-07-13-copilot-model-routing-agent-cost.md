---
title: "AI Radar: Copilot 모델 선택이 보여준 agent 비용 구조"
date: 2026-07-13 09:55:00 +0900
categories: [AI, DeepDive]
tags: [ai, agent, github-copilot, openai, gpt-5-6, model-routing, coding-agent, cost, backend, ax]
image: /assets/img/posts/2026/07/copilot-model-routing-agent-cost.png
---

GitHub Copilot에 OpenAI `GPT-5.6` 계열이 들어왔다. Sol, Terra, Luna 세 가지 모델로 나뉘고,
Copilot 안에서 작업 성격에 맞춰 고를 수 있는 형태다.

처음 보면 모델 라인업이 하나 더 늘어난 소식처럼 보인다. 그런데 내가 보기에는 이 변화의 핵심은
모델 이름이 아니다. coding agent를 운영할 때 이제 "어떤 모델이 제일 좋은가"보다 "어떤 작업에 어떤
모델을 태울 것인가"가 더 중요해지고 있다는 점이다.

## 본 자료

- GitHub Changelog: [OpenAI's GPT-5.6 Sol, Terra, and Luna are now available in GitHub Copilot](https://github.blog/changelog/2026-07-09-openais-gpt-5-6-sol-terra-and-luna-are-now-available-in-github-copilot/)
- GitHub Changelog: [Copilot Agent is now available in JetBrains AI Assistant](https://github.blog/changelog/2026-06-30-copilot-agent-is-now-available-in-jetbrains-ai-assistant/)
- GitHub Changelog: [Ask Copilot for a repository overview](https://github.blog/changelog/2026-07-09-ask-copilot-for-a-repository-overview/)

대표 이미지는 GitHub Changelog의 Copilot 이미지를 사용했다.

## 핵심 메모

GitHub 설명 기준으로 GPT-5.6 계열은 세 가지로 나뉜다.

- `Sol`: 큰 코드베이스, 복잡한 추론, 오래 도는 agent 작업
- `Terra`: 일반적인 interactive coding과 agentic coding의 기본 선택지
- `Luna`: 작고 빠른 작업을 위한 경량, 저비용 선택지

모델은 VS Code, Visual Studio, Copilot CLI, GitHub Copilot cloud agent, GitHub Copilot app,
github.com, 모바일, JetBrains, Xcode, Eclipse 같은 여러 표면에 들어간다. Business와 Enterprise
관리자는 Copilot settings에서 GPT-5.6 모델 정책을 켜야 하고, 기본값은 off다.

같은 시기에 GitHub는 JetBrains AI Assistant 안에서도 Copilot을 agent picker의 first-class option으로
올렸다. IDE 안에서 모델을 고르고 reasoning depth를 조절하며, 멀티스텝 작업을 넘기는 흐름이 점점
명확해지고 있다.

## 왜 지금 중요한가

coding agent는 한 가지 작업만 하지 않는다.

```text
저장소 훑기
버그 위치 추적
테스트 작성
작은 리팩터링
큰 구조 변경
리뷰 코멘트 반영
문서와 README 정리
명령 실행 후 실패 원인 분석
```

이 작업들을 전부 같은 모델에 태우는 건 편하지만 비싸고, 반대로 전부 경량 모델에 태우면 긴 작업에서
맥이 끊긴다. 그래서 실제 제품에서는 model routing이 중요해진다.

내 기준으로 Copilot의 Sol/Terra/Luna 구분은 모델 성능표보다 운영 구조에 더 가깝다.

```text
task intent
-> context size
-> expected runtime
-> risk level
-> budget
-> model choice
-> execution policy
```

좋은 coding agent 제품은 매번 이 판단을 직접 하지 않아도 되게 만들어야 한다. 그래도 중요한 순간에는
모델과 reasoning depth를 직접 조절할 수 있어야 한다. 자동 라우팅과 수동 선택이 같이 필요하다.

## 백엔드 관점에서 보면

모델 라우팅은 UI 옵션이 아니라 서버 구조 문제다.

agent platform을 만든다면 최소한 이런 데이터가 필요하다.

- 요청의 작업 유형
- repo 크기와 context 크기
- 예상 tool call 수
- 예상 실행 시간
- 사용자의 plan과 조직 정책
- 작업의 위험도
- 실패했을 때 재시도 가능성
- 산출물의 검증 방식
- 실제 token, tool, runtime 비용

이 정보가 쌓여야 다음 요청에서 더 나은 라우팅을 할 수 있다. 예를 들어 "README 요약"은 경량 모델로
충분할 수 있고, "숨은 race condition을 테스트까지 포함해서 고쳐라"는 더 강한 모델과 긴 실행 시간이
필요할 수 있다.

여기서 중요한 건 모델 라우팅이 곧 비용 통제라는 점이다. agent는 한 번의 답변보다 훨씬 많은 context,
tool call, 재시도, 검증 단계를 소비한다. 조직 단위로 쓰기 시작하면 모델 선택은 개발자 취향이 아니라
budget policy가 된다.

## 제품 관점에서 보면

GitHub가 "모델 picker"를 여러 개발 표면에 넣는 건 자연스럽다. 개발자는 이미 IDE, CLI, 웹, 모바일,
cloud agent를 오가며 일한다. 같은 Copilot이라도 표면마다 작업 성격이 다르다.

- IDE에서는 코드 편집과 테스트 실행이 중심이다.
- CLI에서는 명령 실행과 로컬 환경 해석이 중요하다.
- github.com에서는 repository overview, PR review, issue 탐색이 자연스럽다.
- cloud agent에서는 오래 걸리는 작업 위임이 핵심이다.

같은 모델 목록이라도 각 표면에서 기본값은 달라져야 한다. 작은 수정은 빠르게, 큰 변경은 깊게, 위험한
작업은 승인과 로그를 남기는 쪽으로 가야 한다.

## 조심할 지점

모델 선택지가 늘어나면 좋아 보이지만, 제품이 정리하지 못하면 사용자는 피곤해진다.

```text
이 작업은 Sol인가 Terra인가
Luna로 돌렸다가 실패하면 다시 Sol로 돌려야 하나
reasoning depth를 올리면 비용이 얼마나 늘어나나
조직 정책에서 막힌 모델은 왜 막혔나
실패한 작업은 모델 문제인가 context 문제인가 tool 문제인가
```

이 질문에 답하지 못하면 모델 picker는 힘이 아니라 노이즈가 된다. agent 제품은 선택지를 보여주는 데서
끝나면 안 되고, 선택의 이유와 결과를 기록해야 한다.

특히 enterprise에서는 기본 off 정책이 중요하다. 새 모델이 들어올 때마다 자동으로 켜지는 구조보다,
관리자가 비용과 데이터 경계를 보고 켤 수 있는 구조가 더 현실적이다.

## 판단

**Watch.**

Copilot의 GPT-5.6 Sol/Terra/Luna 공개는 모델 성능 경쟁의 또 다른 장면이기도 하지만, 더 크게 보면
coding agent의 비용 구조가 드러나는 장면이다.

앞으로 볼 지점은 세 가지다.

- Copilot이 작업 유형에 따라 모델을 얼마나 잘 추천하는가
- 조직 단위 budget과 model policy가 얼마나 세밀하게 잡히는가
- 실패한 agent 작업을 모델, context, tool, policy 중 어디 문제로 분류할 수 있는가

coding agent가 더 오래, 더 깊게 일할수록 모델 라우팅은 선택 기능이 아니라 기본 인프라가 된다. 좋은
모델 하나를 고르는 시대에서, 작업마다 맞는 실행 경로를 고르는 시대로 가고 있다.
