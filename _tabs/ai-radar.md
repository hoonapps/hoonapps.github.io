---
icon: fas fa-satellite-dish
order: 1
title: AI
---

# AI

AI 관련 글을 모아두는 카테고리 페이지입니다. 모델, 에이전트, RAG, MCP, 개발 도구,
오픈소스 실험처럼 새로 확인한 내용을 이곳에 정리합니다.

## 최근 AI 글

{% assign ai_posts = site.posts | where_exp: 'post', 'post.categories contains "AI"' %}

{% for post in ai_posts limit: 30 %}
- [{{ post.title }}]({{ post.url | relative_url }}) · {{ post.date | date: "%Y.%m.%d" }}
{% else %}
- 아직 AI 카테고리 글이 없습니다.
{% endfor %}

## 자동 수집 후보

`tools/ai_radar.py`가 수집한 후보는 글감 후보로만 사용합니다.

{% assign radar = site.data.ai_radar %}
{% assign candidates = radar.candidates | default: empty %}

{% for item in candidates limit: 10 %}
- [{{ item.name }}]({{ item.url }}) · {{ item.source }} · {{ item.verdict }}
{% else %}
- 아직 수집된 후보가 없습니다.
{% endfor %}
