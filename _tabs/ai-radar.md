---
icon: fas fa-satellite-dish
order: 1
title: AI 레이더
---

# AI 레이더

AI 레이더는 매일 새로 등장하는 AI 기술을 수집하고, 개발자 관점에서 쓸 만한지
판단하는 공간입니다. 자동 수집 결과는 “후보”일 뿐이고, 최종 채택 판단은 직접
실행한 뒤에만 내립니다.

{% assign radar = site.data.ai_radar %}
{% assign candidates = radar.candidates | default: empty %}

<section class="radar-overview" aria-label="AI Radar status">
  <div>
    <span>Generated</span>
    <strong>{{ radar.generated_at | default: "manual" }}</strong>
  </div>
  <div>
    <span>Window</span>
    <strong>{{ radar.window_days | default: 7 }} days</strong>
  </div>
  <div>
    <span>Candidates</span>
    <strong>{{ candidates.size }}</strong>
  </div>
</section>

## 오늘의 후보

<div class="radar-board">
  {% for item in candidates limit: 12 %}
    <article class="radar-card">
      <div class="radar-card-head">
        <span class="radar-source">{{ item.source }}</span>
        <span class="radar-verdict verdict-{{ item.verdict | downcase }}">{{ item.verdict }}</span>
      </div>
      <h2><a href="{{ item.url }}" target="_blank" rel="noopener noreferrer">{{ item.name }}</a></h2>
      <p>{{ item.summary }}</p>
      <dl>
        <div>
          <dt>Score</dt>
          <dd>{{ item.score }}</dd>
        </div>
        <div>
          <dt>Stars</dt>
          <dd>{{ item.stars }}</dd>
        </div>
      </dl>
      <p class="radar-reason">{{ item.reason }}</p>
      <div class="radar-tags">
        {% for tag in item.tags limit: 6 %}
          <span>{{ tag }}</span>
        {% endfor %}
      </div>
    </article>
  {% else %}
    <p>아직 수집된 후보가 없습니다. `python tools/ai_radar.py --write-data`를 실행하세요.</p>
  {% endfor %}
</div>

## 수집 채널

<div class="radar-sources">
  {% for source in radar.sources %}
    <section>
      <h2>{{ source.name }}</h2>
      <p>{{ source.signal }}</p>
      {% if source.url and source.url != "" %}
        <a href="{{ source.url }}" target="_blank" rel="noopener noreferrer">source</a>
      {% endif %}
    </section>
  {% endfor %}
</div>

## 판단 기준

<div class="radar-criteria">
  <section>
    <h2>문제 적합성</h2>
    <p>이 도구가 정말 새로운 문제를 해결하는가?</p>
  </section>
  <section>
    <h2>실행 가능성</h2>
    <p>30분 안에 로컬 또는 샌드박스에서 돌릴 수 있는가?</p>
  </section>
  <section>
    <h2>운영성</h2>
    <p>인증, 비용, 모니터링, 장애 대응이 가능한가?</p>
  </section>
  <section>
    <h2>확장성</h2>
    <p>팀/서비스 규모가 커져도 구조가 버티는가?</p>
  </section>
  <section>
    <h2>대체 가능성</h2>
    <p>기존 도구보다 명확히 나은 지점이 있는가?</p>
  </section>
</div>

## 수동 인박스

{% for entry in radar.manual_inbox %}
- **{{ entry.title }}** · {{ entry.status }}  
  {{ entry.note }}
{% else %}
- 수동 인박스가 비어 있습니다.
{% endfor %}

## 최근 AI 글

{% assign ai_posts = site.posts | where_exp: 'post', 'post.categories contains "AI"' %}

{% for post in ai_posts limit: 20 %}
- [{{ post.title }}]({{ post.url | relative_url }}) · {{ post.date | date: "%Y.%m.%d" }}
{% else %}
- 곧 첫 AI Radar 글이 올라옵니다.
{% endfor %}
