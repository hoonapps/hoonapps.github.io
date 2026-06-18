---
icon: fas fa-satellite-dish
order: 1
title: AI
---

AI 관련 글을 모아두는 페이지입니다.

## 최근 AI 글

{% assign ai_posts = site.posts | where_exp: 'post', 'post.categories contains "AI"' %}

{% for post in ai_posts limit: 30 %}
- [{{ post.title }}]({{ post.url | relative_url }}) · {{ post.date | date: "%Y.%m.%d" }}
{% else %}
- 아직 AI 카테고리 글이 없습니다.
{% endfor %}
