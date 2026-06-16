---
icon: fas fa-server
order: 2
title: 백엔드
---

# 백엔드

백엔드 관련 글을 모아두는 카테고리 페이지입니다. NestJS, Docker, 데이터베이스,
트랜잭션, 큐, 캐시, 네트워크, 운영 이슈를 정리합니다.

## 최근 백엔드 글

{% assign backend_posts = site.posts | where_exp: 'post', 'post.categories contains "Backend" or post.categories contains "NestJS" or post.categories contains "Docker" or post.categories contains "DeepDive"' %}

{% for post in backend_posts limit: 30 %}
- [{{ post.title }}]({{ post.url | relative_url }}) · {{ post.date | date: "%Y.%m.%d" }} · {{ post.categories | join: " / " }}
{% else %}
- 아직 백엔드 카테고리 글이 없습니다.
{% endfor %}

## 앞으로 정리할 주제

- 트랜잭션과 격리 수준
- 메시지 큐와 재시도
- 캐시와 동시성
- Docker와 배포
- 관측성, 로그, 트레이싱
- 백엔드에서 AI 도구를 붙일 때의 구조
