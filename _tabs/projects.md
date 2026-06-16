---
icon: fas fa-code-branch
order: 3
title: 프로젝트
---

# 프로젝트

프로젝트 탭은 결과물 홍보보다 작업 기록에 가깝습니다. 무엇을 만들었는지뿐 아니라
왜 그렇게 설계했는지, 어떤 선택지를 버렸는지, 어디에서 실패했는지를 남깁니다.

## 기록 방식

- 문제 정의와 목표
- 아키텍처 결정 기록
- 핵심 구현과 코드 링크
- 운영/배포/모니터링 메모
- 실패한 접근과 다음 작업

## 진행 중인 축

| 축 | 설명 |
| --- | --- |
| AI-enabled Backend | AI 에이전트와 백엔드 워크플로를 결합하는 실험 |
| Developer Tools | 개발자가 매일 쓰는 자동화, 문서화, 배포 도구 |
| Product Lab | 실제 사용자에게 줄 수 있는 작은 제품 실험 |
| Systems Notes | 성능, 장애, 데이터 흐름을 검증한 기록 |

## 최근 프로젝트 글

{% assign project_posts = site.posts | where_exp: 'post', 'post.categories contains "Projects"' %}

{% for post in project_posts limit: 20 %}
- [{{ post.title }}]({{ post.url | relative_url }}) · {{ post.date | date: "%Y.%m.%d" }}
{% else %}
- 곧 첫 프로젝트 로그가 올라옵니다.
{% endfor %}
