---
title: "Why 'localhost' Fails in Docker: Exploring Bridge Networks and Solutions"
date: 2024-11-29 11:00:00 +0900
categories: [Docker]
tags: [NestJS, Docker, Postgresql, bridge]
image: /assets/img/docker.png
---


# Introduction

In this post, we will discuss an issue related to connecting an application container and a PostgreSQL container via TypeORM using `docker-compose`. Specifically, the connection fails when the `host` is set to `localhost`. 

This is a common issue for Docker users, so let's dive into it.

Let's begin.

---

## Issue Description

As mentioned in the introduction, we attempted to run an application container and a PostgreSQL container using `docker-compose`. However, the error shown in the image below occurred:

![5-1](/assets/img/posts/24.11/5-1.png)

### Why does this happen?

The issue arises because `localhost` refers to the internal IP (`127.0.0.1`) of the container itself. This means that instead of pointing to the PostgreSQL container, it refers to the internal network of the application container.

**In short, PostgreSQL is not within the network space of the application container, causing the connection to fail.**

## Solution

The database host is managed through the `.env` file. As shown below, we can use either `172.17.0.1` or `host.docker.internal` as the `DB_HOST`.

![5-2](/assets/img/posts/24.11/5-2.png)

<br />

## Why do `172.17.0.1` and `host.docker.internal` work?

To understand this, consider the following flow of a network request sent by a Docker container:

**container(eth0) => veth => docker0(bridge) => Host Network Interface (eth0) → External Network**

The key component here is `docker0` (the bridge). Docker automatically creates a **bridge network** for containers.

<br />

#### What is a Bridge Network in Docker?

- **Container Communication**: Containers on the same bridge network can communicate with each other using container names.
- **Host Isolation**: The bridge network provides network isolation between the host and the containers.

Let’s verify if the bridge is created, whether the containers are connected to the same bridge, and explore the bridge details.

---

##### 1. Check the Network List

<br />

```bash
docker network ls
```
![5-3](/assets/img/posts/24.11/5-3.png)

As shown above, the created containers are part of the `DRIVER(bridge)` network.

<br />

##### 2. Bridge Network Details

<br />

```bash
docker network inspect bridge
```

```sh
[
    {
        "Name": "bridge",
        "Id": "7d3d8d77186a1f2dd28027ac25a178c87d0d432ecab2852b78086f68b6301696",
        "Created": "2024-11-29T01:57:46.973940286Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": null,
            "Config": [
                {
                    "Subnet": "172.17.0.0/16",
                    "Gateway": "172.17.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {},
        "Options": {
            "com.docker.network.bridge.default_bridge": "true",
            "com.docker.network.bridge.enable_icc": "true",
            "com.docker.network.bridge.enable_ip_masquerade": "true",
            "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
            "com.docker.network.bridge.name": "docker0",
            "com.docker.network.driver.mtu": "1500"
        },
        "Labels": {}
    }
]
```

The `Driver` is `bridge`, and the `Gateway` is `172.17.0.1`. This explains why `172.17.0.1` works. The bridge enables communication between containers, and its gateway address is `172.17.0.1`.

<br />

##### 3. Why does `host.docker.internal` work?

- `host.docker.internal` is a DNS name provided by Docker to access the host machine.
- It maps the host machine’s IP address, allowing containers to reference services running on the host.

You can test this by pinging `host.docker.internal` from within a container:

```bash
docker exec -it nestjs-app sh
ping host.docker.internal
```

![5-4](/assets/img/posts/24.11/5-4.png)

It maps to `192.168.65.254`, which explains why setting the `DB_HOST` to `192.168.65.254` also works.

---

# Conclusion

Today, we explored container connectivity in Docker. By diving deeper into this topic, we gained a better understanding of Docker's structure and communication principles. While there are still areas I need to study further, this is a step in the right direction.

I hope this post was helpful to you.

Thank you for reading, and happy blogging! 🚀

## References

- [Testing APP](https://github.com/hoonapps/Docker-bridge)
- [Docker](https://www.docker.com/)
- [Bridge network driver](https://docs.docker.com/engine/network/drivers/bridge/)
- [StackOverFlow](https://stackoverflow.com/questions/48546124/what-is-the-linux-equivalent-of-host-docker-internal)



<!-- In this post, 
docker-compose에서 애플리케이션 앱 컨테이너와 postgresql 컨테이너를 올리고 두개를 Typeorm 모듈을 통해 연결했는데 
host를 localhost로 연결했을때 실패한 이슈에 대해서 얘기하고자 합니다.

도커를 사용하는 사람들은 한번쯤은 겪어본 이슈일것 같아서 자세하게 파헤쳐 보겠습니다.

그럼 시작합니다.

---

## 이슈 내용

소개글에 있듯이 docker-compose를 통해서 도커에 애플리케이션 앱 컨테이너와 PostgreSQL 컨테이너를 올렸는데
이미지와 같은 에러가 났다.

![1](/assets/img/posts/24.11/241129_01.png)

### 왜 안될까?

당연하게도 localhost는 컨테이너 내부 IP (127.0.0.1)를 가리키므로 PostgreSQL 컨테이너가 아닌 애플리케이션 컨테이너의 내부 네트워크를 참조하기 때문이다.

**즉 PostgreSQL은 애플리케이션 컨테이너의 네트워크 공간에 없으므로 연결 실패.**

## 해결 방법

.env 파일에서 db host를 관리하는데

![2](/assets/img/posts/24.11/241129_02.png)

위 이미지처럼
DB_HOST에 172.17.0.1 과 host.docker.internal을 사용하면 된다.

<br />

## 172.17.0.1 과 host.docker.internal 은 왜 될까?

위에 이유를 알기 위해 앞서 도커 컨테이너가 네트워크 요청을 보내게 되면

**container(eth0) => veth => docker0(bridge) => Host Network Interface (eth0) → External Network**

이런 flow로 진행이돼

여기서 우리가 집중해야 되는곳은

docker0(bridge)야 도커는 기본적으로 컨테이터에서 **bridge** 네트워크가 자동적으로 생성이 돼

<br />

#### What is Bridge Network in Docker

- 컨테이너 간 통신: 같은 브리지 네트워크에 있는 컨테이너들은 컨테이너 이름을 통해 통신할 수 있습니다.
- 호스트 격리: 브리지 네트워크는 컨테이너와 호스트 간의 네트워크 격리를 제공합니다.

그럼 실제로 bridge가 생성이 됐는지 컨테이너들이 같은 bridge에 연결되어 있는지 확인해보고 bridge 상세 정보를 봐보자

---
<br />

##### 1. 네트워크 목록 확인하기
<br />

```bash
docker network ls
```
![3](/assets/img/posts/24.11/241129_03.png)

위 처럼 내가 만든 컨테이너가 DRIVER(bridge)에 들어가 있는것을 확인 할 수 있어

<br />

##### 2. Bridge 네트워크 상세 정보
<br />
```bash
docker network inspect bridge
```

```sh
[
    {
        "Name": "bridge",
        "Id": "7d3d8d77186a1f2dd28027ac25a178c87d0d432ecab2852b78086f68b6301696",
        "Created": "2024-11-29T01:57:46.973940286Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": null,
            "Config": [
                {
                    "Subnet": "172.17.0.0/16",
                    "Gateway": "172.17.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {},
        "Options": {
            "com.docker.network.bridge.default_bridge": "true",
            "com.docker.network.bridge.enable_icc": "true",
            "com.docker.network.bridge.enable_ip_masquerade": "true",
            "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
            "com.docker.network.bridge.name": "docker0",
            "com.docker.network.driver.mtu": "1500"
        },
        "Labels": {}
    }
]
```

위에서 보면 Driver: bridge 이고 Gateway가 172.17.0.1 이야

그래서 우리가 localhost는 안됐는데 172.17.0.1가 되는 이유가 여기에 있어
앞에 bridge에 설명한것처럼 컨테이너간의 통신을 bridge가 가능하게 해주는데 bridge의 gateway 주소가 172.17.0.1 이였기때문에

database_host를 172.17.0.1로 설정했을때 가능했던 이유였어.

<br />

##### 3. `host.docker.internal`는 왜 될까?

- Docker가 호스트 머신에 대한 접근을 위해 제공한 DNS 이름.
- 호스트 머신에 서비스를 참조하려면 호스트의 IP 주소를 알아야 하는데 `host.docker.internal`은 이런 상황에서 사용자를 대신해 호스트 머신의 IP 주소를 자동으로 매핑해주는 역할을 합니다.

실제로 컨테이너 안에서 host.docker.internal로 핑을 날려보면

```bash
docker exec -it nestjs-app sh
ping host.docker.internal
```

![3](/assets/img/posts/24.11/241129_04.png)

192.168.65.254로 매핑 되서 보내지는걸 볼 수 있어

그래서 host.docker.internal 뿐만아니라 database_host를 192.168.65.254로 설정해도 정상적으로 연결이 되는걸 확인 할 수 있어

---

# Conclusion

오늘은 도커 컨테이너간의 연결에 대해서 글을 써봤는데 개발 할때는 그냥 지나갔던 부분을
조금이나마 자세하게 알아봐서 도커의 구조와 통신원리를 알 수 있었어
내가 틀린부분도 있고 아직 전체적인 구조를 자세하게 모르지만 더 공부해야지!
이 글을 보고 여러분도 도움이 됐으면 좋겠다

Thank you for reading, and happy blogging! 🚀

## References

- [Testing APP](https://github.com/hoonapps/Docker-bridge)
- [Docker](https://www.docker.com/)
- [Bridge network driver](https://docs.docker.com/engine/network/drivers/bridge/)
- [StackOverFlow](https://stackoverflow.com/questions/48546124/what-is-the-linux-equivalent-of-host-docker-internal) -->
