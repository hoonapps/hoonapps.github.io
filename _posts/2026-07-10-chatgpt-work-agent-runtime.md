---
title: "AI Radar: ChatGPT Work가 보여준 업무 agent의 실행 경계"
date: 2026-07-10 17:15:00 +0900
categories: [AI, DeepDive]
tags: [ai, agent, chatgpt, openai, chatgpt-work, codex, plugins, sites, governance, backend, ax]
image: /assets/img/posts/2026/07/chatgpt-work-agent-runtime.png
---

2026년 7월 9일 OpenAI가 `ChatGPT Work`를 공개했다. 처음에는 또 하나의 ChatGPT 기능처럼 보일 수
있는데, 내가 보기에는 방향이 조금 다르다.

핵심은 "더 똑똑하게 답하는 챗봇"이 아니다. ChatGPT가 앱, 파일, 브라우저, 코드 작업, 문서 작성,
예약 실행까지 한 흐름 안에서 다루는 업무 agent runtime으로 이동하고 있다는 점이 중요하다.

## 본 자료

- OpenAI: [ChatGPT is now a partner for your most ambitious work](https://openai.com/index/chatgpt-for-your-most-ambitious-work/)
- OpenAI Help Center: [ChatGPT - Release Notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)
- ChatGPT Learn: [What's new](https://learn.chatgpt.com/docs/whats-new)

대표 이미지는 ChatGPT Learn의 What's new 페이지 이미지를 사용했다.

## 핵심 메모

OpenAI 설명 기준으로 ChatGPT Work는 앱과 파일을 넘나들며 action을 수행하고, 필요하면 몇 시간 동안
작업을 이어가며, 목표를 문서, 스프레드시트, 발표 자료, 리포트, Sites 같은 결과물로 만들 수 있다.

같이 공개된 흐름도 중요하다.

- ChatGPT desktop app 안에 Chat, Work, Codex가 같이 들어간다.
- Work는 권한을 받은 로컬 파일과 데스크톱 앱을 사용할 수 있다.
- 내장 브라우저로 웹 조사와 앱 작업을 이어갈 수 있다.
- App Directory는 Plugin Directory로 바뀐다.
- Scheduled Tasks는 한 번 실행, 반복 실행, 변경 감시 같은 작업을 맡는다.
- Sites는 대시보드, 내부 포털, 인터랙티브 리포트 같은 결과물을 만드는 public beta로 나온다.

이 조합을 보면 단순히 기능이 늘어난 게 아니다. agent가 어디까지 보고, 어디까지 실행하고, 어떤
결과물을 만들 수 있는지가 한 제품 안에서 다시 정리되고 있다.

## 왜 지금 중요한가

지금까지 AI 제품은 주로 입력창 중심으로 설명됐다.

```text
질문을 입력한다
모델이 답한다
사람이 다음 행동을 한다
```

ChatGPT Work가 밀고 있는 방향은 이 흐름과 다르다.

```text
목표를 준다
agent가 필요한 자료와 도구를 찾는다
중간 결과를 만들고 수정한다
중요한 action은 승인을 받는다
완성된 산출물을 남긴다
```

여기서 제품의 경쟁력은 답변 문장만으로 결정되지 않는다. 어떤 앱에 연결할 수 있는지, 권한을 어디까지
좁힐 수 있는지, 오래 걸리는 작업을 어떻게 유지하는지, 사람이 언제 개입하는지, 결과물을 어디에
남기는지가 더 중요해진다.

내 기준으로 이건 `agent UX`라기보다 `agent runtime` 문제에 가깝다.

## 백엔드 관점에서 보면

업무 agent가 실제 조직 안에 들어오려면 다음 구조가 필요하다.

- 사용자와 조직 단위의 identity
- 앱별 scoped permission
- 연결된 파일과 데이터의 boundary
- 오래 걸리는 작업을 위한 workflow state
- 예약 실행과 재시도 정책
- 중요한 action 앞의 approval gate
- 생성된 산출물의 versioning
- 실행 로그와 감사 로그
- 비용과 사용량 제한
- 네트워크와 브라우저 접근 제한

OpenAI도 enterprise 설명에서 admin control, Compliance API, browser와 network restriction, 중요한
action의 auto-review를 같이 언급한다. 이 부분이 빠지면 업무 agent는 편리한 자동화 도구가 아니라
통제하기 어려운 실행면이 된다.

특히 Plugin Directory가 중요해 보인다. 앞으로 agent 제품은 "모델이 무엇을 아는가"보다 "어떤
plugin을 어떤 권한으로 붙일 수 있는가"를 더 많이 따질 가능성이 크다.

## 조심할 지점

ChatGPT Work 같은 제품이 강해질수록 attack surface도 넓어진다.

로컬 파일, 데스크톱 앱, 브라우저, 이메일, 캘린더, CRM, 프로젝트 관리 도구가 한 agent에게 연결되면
편해지는 만큼 위험도 커진다. prompt injection, 과한 권한, 잘못된 예약 실행, 민감한 파일 접근,
외부 전송 같은 문제가 한꺼번에 엮일 수 있다.

그래서 업무 agent를 볼 때는 기능 데모보다 아래 질문을 먼저 보는 게 맞다.

```text
읽기 권한과 쓰기 권한이 분리되는가
승인이 필요한 action을 명확히 나눌 수 있는가
실행 로그가 사람이 추적 가능한 형태로 남는가
plugin별 권한을 회수할 수 있는가
예약 작업이 실패했을 때 재시도와 중단 기준이 있는가
민감한 데이터가 어떤 경로로 나가는지 볼 수 있는가
```

agent가 사람 대신 클릭하고 작성하고 제출할 수 있다면, 백엔드 시스템에서 말하는 auth, audit,
idempotency, rollback이 그대로 필요해진다.

## 판단

**Watch.**

ChatGPT Work는 단순한 기능 추가라기보다 업무 agent의 실행 경계를 제품으로 묶는 시도에 가깝다.
모델 성능이 계속 좋아지는 건 이제 기본값에 가까워지고 있다. 다음 경쟁은 agent가 실제 업무 환경에서
어디까지 안전하게 실행될 수 있는지로 넘어간다.

내가 앞으로 볼 지점은 세 가지다.

- Plugin Directory가 실제 업무 도구 연결의 표준 경로가 될 수 있는가
- Scheduled Tasks가 반복 업무 자동화의 기본 인터페이스가 될 수 있는가
- enterprise governance가 편의성과 충돌하지 않고 유지될 수 있는가

이 셋이 같이 굴러가면 ChatGPT는 답변 도구가 아니라 업무 실행 계층에 가까워진다. 반대로 권한, 감사,
승인 흐름이 애매하면 강력한 기능일수록 조직에서는 조심스럽게 볼 수밖에 없다.
