---
title: "Enterprise AX Agent Platform 10: 로컬 운영 검증 흐름"
date: 2026-06-20 00:10:00 +0900
categories: [Projects, AI]
tags: [ax, ai-agent, local-dev, testing, docker, backend]
description: "서버 실행, demo flow, regression eval, Docker build, Postgres migration 검증까지 로컬에서 반복 가능한 흐름으로 묶었다."
---

운영 가능한 백엔드는 로컬에서도 전체 흐름을 재현할 수 있어야 한다. 외부 서비스가 없으면 아무것도 확인하지 못하는 구조는 개발 속도와 품질을 동시에 떨어뜨린다.

저장소: [hoonapps/enterprise-ax-agent-platform](https://github.com/hoonapps/enterprise-ax-agent-platform)

## 기본 실행

로컬 기본 모드는 외부 DB 없이 동작한다.

```text
STORAGE_BACKEND=memory
VECTOR_BACKEND=local
```

실행 명령은 단순하게 유지했다.

```bash
make install
make dev
```

API 문서와 dashboard는 다음 주소에서 확인한다.

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/dashboard
```

## Demo Flow

서버를 띄우지 않고도 application use case를 직접 호출하는 demo flow를 둔다.

```bash
make demo
```

이 흐름은 다음을 한 번에 실행한다.

```text
sample document ingest
knowledge agent run
feedback
diagnostics
evidence bundle
run replay
approval-required action
scenario run
operations summary
```

HTTP 밖에서도 같은 domain model, policy, repository port, tool runtime을 사용한다. 그래서 demo flow는 별도 샘플 스크립트가 아니라 제품 실행 경로 검증에 가깝다.

## Verification Gate

기본 검증은 `make verify`로 묶었다.

```bash
make verify
```

포함되는 검증은 다음이다.

```text
ruff
mypy
pytest
regression evaluation
```

테스트는 API 단위뿐 아니라 use case, idempotency, approval, webhook dispatcher, scenario run, operations read model까지 포함한다.

## Docker와 Postgres

Docker Compose 모드에서는 Postgres와 Qdrant를 붙일 수 있다.

Postgres migration은 SQL 파일과 ledger로 관리한다.

```text
001_initial_schema.sql
002_tenant_rls.sql
003_agent_scenario_runs.sql
```

`003_agent_scenario_runs.sql`은 scenario run history를 저장하기 위한 테이블과 RLS 설정을 포함한다. 로컬 검증에서는 컨테이너 초기화 로그와 psql 조회로 table, owner, row-level security 상태를 확인했다.

## 품질 기준

현재 검증 기준은 다음 흐름을 통과해야 한다.

- API 서버가 boot 된다.
- dashboard JavaScript가 parse 된다.
- `make demo`가 scenario history까지 출력한다.
- `make verify`가 lint, type check, test, regression eval을 통과한다.
- Docker image가 build 된다.
- Postgres migration이 clean DB에 적용된다.

## 결과

이 단계에서 제품은 로컬 단독 실행, 검증, 컨테이너 실행, DB migration 확인까지 하나의 루프로 묶였다.

Agent 제품은 “서버가 뜬다”로 끝나지 않는다. 문서 적재부터 운영 summary까지 이어지는 실행 경로가 반복 가능해야 한다. 그래야 기능을 추가해도 운영 품질이 유지된다.
