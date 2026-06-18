---
icon: fas fa-code-branch
order: 3
title: 프로젝트
---

새로 만든 작업과 실험을 모아두는 페이지입니다.

## 최근 프로젝트 글

{% assign project_posts = site.posts | where_exp: 'post', 'post.categories contains "Projects"' %}

{% for post in project_posts limit: 30 %}
- [{{ post.title }}]({{ post.url | relative_url }}) · {{ post.date | date: "%Y.%m.%d" }}
{% else %}
- 아직 프로젝트 글이 없습니다.
{% endfor %}

## 기록할 내용

- 만들게 된 이유
- 사용한 기술
- 구현하면서 막힌 점
- 배포와 운영 메모
- 다음에 고칠 점
