# Hoonapps Lab Content Operating System

이 문서는 블로그를 “가끔 쓰는 개발 일기”가 아니라 지속적으로 누적되는 기술 연구소로
운영하기 위한 기준이다.

## Editorial Position

Hoonapps Lab은 AI 시대의 백엔드 엔지니어링을 한국어로 검증하는 공간이다. 글은
뉴스 요약보다 직접 실행한 결과, 운영 리스크, 설계 판단을 우선한다.

## Core Categories

| Category | Role |
| --- | --- |
| AI | 모델, 에이전트, MCP, RAG, 로컬 LLM, 개발 도구 |
| Backend | DB, 트랜잭션, 큐, 캐시, 네트워크, 관측성 |
| DeepDive | 한 개념을 내부 동작과 운영 관점까지 파는 장문 |
| OpenSource | 새 도구를 설치하고 코드/운영성/보안 경계를 검증 |
| Projects | 실제 작업의 설계 결정, 실패 기록, 배포 기록 |

## Weekly Rhythm

| Cadence | Output | Scope |
| --- | --- | --- |
| Daily | AI Radar | 후보 1개 이상 검토, Adopt/Watch/Skip 판단 |
| Weekly | Backend Deep Dive | 실무에서 터지는 깊은 주제 1개 |
| Weekly | Open Source Lab | 직접 실행한 도구 리뷰 1개 |
| Monthly | Project Review | 진행 중인 프로젝트의 아키텍처/운영 회고 |

## AI Radar Workflow

1. `python tools/ai_radar.py --write-data`로 후보를 수집한다.
2. `/ai-radar/`에서 후보를 훑고 하나를 고른다.
3. 공식 문서, README, 라이선스, 최근 commit, issue를 확인한다.
4. 가능하면 로컬에서 실행한다.
5. `docs/templates/ai-radar.md`를 기준으로 글을 작성한다.
6. 결론은 `Adopt`, `Watch`, `Skip` 중 하나로 끝낸다.

자동 수집 결과는 후보일 뿐이다. 실행 전에는 `Adopt`를 쓰지 않는다.

## Quality Bar

좋은 글은 다음 중 최소 두 가지를 포함해야 한다.

- 직접 실행한 명령, 코드, 설정
- 실패한 지점과 원인
- 운영 환경에서 생길 비용, 보안, 장애 리스크
- 대체재와 비교한 선택 이유
- 나중에 다시 검증할 수 있는 근거 링크

## Publishing Checklist

- 제목이 문제 또는 판단을 드러내는가?
- 카테고리와 태그가 기존 체계와 맞는가?
- 코드 블록 안의 `{{ }}`는 Liquid와 충돌하지 않는가?
- 외부 링크는 공식 문서나 원 저장소를 우선했는가?
- 결론이 모호하지 않은가?
- `bundle exec jekyll build`가 통과하는가?
