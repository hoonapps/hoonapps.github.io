---
icon: fas fa-server
order: 2
title: 백엔드 코어
---

# 백엔드 코어

이 탭은 단순 프레임워크 사용법이 아니라 백엔드 시스템의 실패 지점을 깊게 정리하는
읽기 경로입니다. 좋은 백엔드 글은 “어떻게 쓰는가”보다 “어디서 깨지는가”를 설명해야
합니다.

{% assign tracks = site.data.engineering_tracks %}

## 핵심 트랙

<div class="track-grid">
  {% for track in tracks.backend_core %}
    <section>
      <span>{{ track.status }}</span>
      <h2>{{ track.name }}</h2>
      <p>{{ track.description }}</p>
    </section>
  {% endfor %}
</div>

## AI 시스템과 만나는 지점

<div class="track-grid">
  {% for track in tracks.ai_systems %}
    <section>
      <span>{{ track.status }}</span>
      <h2>{{ track.name }}</h2>
      <p>{{ track.description }}</p>
    </section>
  {% endfor %}
</div>

## 추천 읽기 순서

<div class="reading-path">
  {% for item in tracks.reading_order %}
    <a href="{{ item.url | relative_url }}">
      <span>{{ forloop.index }}</span>
      <strong>{{ item.title }}</strong>
      <em>{{ item.area }}</em>
    </a>
  {% endfor %}
</div>

## 최근 백엔드 글

{% assign backend_posts = site.posts | where_exp: 'post', 'post.categories contains "Backend"' %}
{% assign deep_posts = site.posts | where_exp: 'post', 'post.categories contains "DeepDive"' %}
{% assign core_posts = backend_posts | concat: deep_posts | uniq %}

{% for post in core_posts limit: 30 %}
- [{{ post.title }}]({{ post.url | relative_url }}) · {{ post.date | date: "%Y.%m.%d" }}
{% else %}
- 곧 첫 Backend Core 글이 올라옵니다.
{% endfor %}

## 앞으로 채울 주제

- DB isolation level과 lost update
- idempotency key 설계
- Redis lock의 안전성과 Redlock 논쟁
- queue backpressure와 retry storm
- Postgres index bloat와 autovacuum
- OpenTelemetry trace 설계
- LLM tool calling 백엔드 권한 경계
- Agent sandbox와 audit log
