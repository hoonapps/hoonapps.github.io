---
title: "Transactional Outbox: 이벤트 발행과 DB 트랜잭션 사이의 틈"
date: 2026-06-16 11:00:00 +0900
categories: [Backend, DeepDive]
tags: [backend, database, transaction, outbox, event-driven, message-queue]
---

서비스가 커지면 “DB에 저장하고 이벤트를 발행한다”는 코드가 자주 나온다. 주문을
저장한 뒤 결제 이벤트를 보내고, 사용자 가입을 저장한 뒤 환영 메일 이벤트를 보내는
식이다. 문제는 DB 트랜잭션과 메시지 브로커 발행이 같은 원자성 안에 있지 않다는
점이다.

## 흔한 코드

```ts
await dataSource.transaction(async manager => {
  const order = await manager.save(Order, command.toOrder());
  await eventBus.publish(new OrderCreatedEvent(order.id));
});
```

겉으로는 자연스럽지만 이 코드는 위험하다.

- DB 저장은 성공했는데 이벤트 발행이 실패할 수 있다.
- 이벤트 발행은 성공했는데 트랜잭션 commit이 실패할 수 있다.
- 네트워크 타임아웃 때문에 발행 성공 여부를 알 수 없을 수 있다.
- 재시도하면 중복 이벤트가 발생할 수 있다.

이 문제는 테스트 환경에서는 잘 드러나지 않고, 실제 운영에서 외부 시스템 장애나
브로커 지연이 생길 때 터진다.

## Outbox 패턴

Transactional Outbox의 핵심은 이벤트를 바로 브로커로 보내지 않고, 같은 DB
트랜잭션 안에서 outbox 테이블에 먼저 저장하는 것이다.

```ts
await dataSource.transaction(async manager => {
  const order = await manager.save(Order, command.toOrder());

  await manager.save(OutboxMessage, {
    id: randomUUID(),
    aggregateId: order.id,
    type: "OrderCreated",
    payload: JSON.stringify({ orderId: order.id }),
    status: "pending",
    createdAt: new Date()
  });
});
```

그 다음 별도의 publisher가 pending 메시지를 읽어 브로커에 발행하고, 성공하면
published 상태로 바꾼다.

## 이 방식의 장점

DB 저장과 이벤트 기록이 같은 트랜잭션에 들어간다. 따라서 “주문은 있는데 이벤트가
없는 상태”를 줄일 수 있다. 브로커가 잠시 죽어도 outbox 테이블에 메시지가 남아
있기 때문에 복구 후 다시 발행할 수 있다.

하지만 이 패턴도 공짜는 아니다.

## 운영에서 봐야 할 것

### 중복 발행

publisher가 브로커에 이벤트를 보낸 뒤 status 업데이트 전에 죽으면 같은 이벤트가
다시 발행될 수 있다. 그래서 consumer는 idempotent해야 한다. 이벤트 ID를 저장하고
이미 처리한 이벤트는 무시하는 방식이 필요하다.

### 순서

같은 aggregate의 이벤트 순서가 중요하다면 aggregateId와 sequence를 같이 저장해야
한다. 단순히 createdAt 정렬에 의존하면 clock, batch size, 병렬 publisher 때문에
순서가 흔들릴 수 있다.

### 적체

outbox는 장애를 흡수하지만 무한 버퍼가 아니다. publisher가 밀리면 테이블이 커지고
DB 부하가 증가한다. pending 개수, 가장 오래된 pending 시간, publish 실패율은
반드시 metric으로 봐야 한다.

### 보존 정책

published 메시지를 영원히 보관하면 테이블이 커진다. 하지만 너무 빨리 지우면 장애
분석이 어렵다. 서비스 성격에 따라 7일, 30일, 90일 같은 보존 정책을 정해야 한다.

## 결론

Transactional Outbox는 이벤트 기반 아키텍처를 시작할 때 반드시 검토해야 하는
패턴이다. 특히 “DB commit과 이벤트 발행이 같이 성공해야 한다”고 생각하는 코드가
있다면, 그 지점이 바로 outbox가 필요한 후보지다.

다만 outbox는 메시지 유실을 줄이는 패턴이지, 분산 시스템의 모든 문제를 없애는
마법이 아니다. 중복 처리, 순서, 적체, 보존 정책까지 같이 설계해야 운영 가능한
구조가 된다.
