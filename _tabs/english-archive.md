---
icon: fas fa-language
order: 7
title: 영문 아카이브
---

# 영문 아카이브

2024년에 영어로 작성했던 글은 삭제하지 않고 아카이브로 보존합니다. 앞으로의 기본
언어는 한국어지만, 기존 글은 당시의 학습 경로와 구현 기록을 보여주는 자료입니다.

## 보존한 글

{% for post in site.posts %}
  {% assign year = post.date | date: "%Y" %}
  {% if year < "2026" %}
- [{{ post.title }}]({{ post.url | relative_url }}) · {{ post.date | date: "%Y.%m.%d" }} · {{ post.categories | join: " / " }}
  {% endif %}
{% endfor %}

## Migration Policy

기존 영어 글은 그대로 둡니다. 다만 새 글에서 같은 주제를 다시 다룰 때는 단순 번역이
아니라 다음 기준으로 재작성합니다.

- 문제 상황을 한국어 실무 맥락으로 다시 설명
- 현재 사용 중인 버전과 도구 기준으로 재검증
- 운영 리스크와 대체재 추가
- 예전 글 링크를 하단에 reference로 연결
