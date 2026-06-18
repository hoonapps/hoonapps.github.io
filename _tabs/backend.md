---
icon: fas fa-server
order: 2
title: 백엔드
---

# 백엔드

백엔드 관련 글을 모아두는 페이지입니다.

## 최근 백엔드 글

{% assign backend_posts = site.posts | where_exp: 'post', 'post.categories contains "Backend" or post.categories contains "NestJS" or post.categories contains "Docker" or post.categories contains "DeepDive"' %}

{% for post in backend_posts limit: 30 %}
- [{{ post.title }}]({{ post.url | relative_url }}) · {{ post.date | date: "%Y.%m.%d" }} · {{ post.categories | join: " / " }}
{% else %}
- 아직 백엔드 카테고리 글이 없습니다.
{% endfor %}
