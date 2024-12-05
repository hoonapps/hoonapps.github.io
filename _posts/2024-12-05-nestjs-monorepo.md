---
title: "[Nestjs] Setting Up a NestJS Monorepo with Docker"
date: 2024-12-05 21:00:00 +0900
categories: [NestJS]
tags: [NestJS, Docker, monorepo]
image: /assets/img/Nest.js.png
---


# Introduction

In this post, I will introduce how to set up a monorepo in NestJS and configure it with Docker for real-time development.
<!-- In this post, nestjs에서 monorepo 세팅하는 방법과 도커에 올려서 실시간 작업 하는 방법에 대해서 소개하겠습니다. -->

Let's begin!

---

## What is Monorepo?

A Monorepo (short for "monolithic repository") is a single version-controlled repository that holds the code for multiple projects,
which may or may not be related to one another. 
Instead of having separate repositories for each project, a monorepo combines them into one.


### Step: 1. Install the NestJS CLI.

```bash
npm install -g @nestjs/cli
```

### Step: 2. Create a new Monorepo project.

```bash
nest new nestjs-monorepo-docker
cd nestjs-monorepo-docker
```

### Step: 3. Set Up the Monorepo

I will create the `admin` and `user` apps, along with the `entity` and `common` libraries for shared use.
<!-- 저는 admin과 user앱을 만들고 같이 사용할 entity, common 을 추가 하겠습니다. -->

- `apps/admin`: Admin app
- `apps/user`: User app
- `libs/common`: For shared utilities, interceptors, filters, etc.
- `libs/entity`: For shared entity definitions (e.g., when using TypeORM)

<!-- - `apps/admin` : 어드민 앱
- `apps/user` : 유저 앱
- `libs/common`: 공통 유틸, 인터셉터, 필터 등 작성
- `libs/entity`: 공통 Entity 정의 (예: typeorm 사용 시) -->

- Use the NestJS CLI to add the admin, user, common, and entity modules.
```bash
nest generate app admin
nest generate app user
nest generate lib common
nest generate lib entity
```

- Final Folder Structure Example:
```go
nestjs-monorepo-docker
├── apps
│   ├── admin    
│   └── user
├── libs
│   ├── common
│   └── entity
├── docker-compose.yml
├── package.json
└── tsconfig.json
```

### Step: 4. Remove Unnecessary Folders and Modify nest-cli.json

At this step, there will be a total of three folders inside the apps directory: admin, user, and nestjs-monorepo-docker. You can delete the nestjs-monorepo-docker folder.

- Modify `nest-cli.json`

In this file, change the `sourceRoot to src` and remove any settings related to nestjs-monorepo-docker under projects.

<!-- 이 스텝까지오면 apps 안에 폴더가 총 3개가 될 것입니다.
admin, user, nestjs-monorepo-docker 폴더가 존재 할텐데 
nestjs-monorepo-docker는 지워주시면 됩니다.

- `nest-cli.json` 수정

위 파일에서 sourceRoot는 src로 변경해주고 projects의 nestjs-monorepo-docker 관련 설정들은 지워주시면 됩니다. -->

- Example

```typescript
{
  "$schema": "https://json.schemastore.org/nest-cli",
  "collection": "@nestjs/schematics",
  "sourceRoot": "src",
  "monorepo": true,
  "projects": {
    "admin": {
      "type": "application",
      "root": "apps/admin",
      "entryFile": "main",
      "sourceRoot": "apps/admin/src",
      "compilerOptions": {
        "tsConfigPath": "apps/admin/tsconfig.app.json"
      }
    },
    "user": {
      "type": "application",
      "root": "apps/user",
      "entryFile": "main",
      "sourceRoot": "apps/user/src",
      "compilerOptions": {
        "tsConfigPath": "apps/user/tsconfig.app.json"
      }
    },
    "common": {
      "type": "library",
      "root": "libs/common",
      "entryFile": "index",
      "sourceRoot": "libs/common/src",
      "compilerOptions": {
        "tsConfigPath": "libs/common/tsconfig.lib.json"
      }
    },
    "entity": {
      "type": "library",
      "root": "libs/entity",
      "entryFile": "index",
      "sourceRoot": "libs/entity/src",
      "compilerOptions": {
        "tsConfigPath": "libs/entity/tsconfig.lib.json"
      }
    }
  }
}
```

### Step: 5. Write the Dockerfile and modify the package.json.

- `apps/admin/Dockerfile`

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN yarn install

COPY . .

RUN yarn build:admin

CMD ["yarn", "start:admin"]
```
The user Dockerfile can be set up similarly, but replace admin with user.
<!-- 유저 Dockerfile은 위와 같이하고 admin을 user로 변경 해주시면 됩니다. -->


- Add the following scripts to `package.json`:

```typescript
"scripts":{
    "start:user": "nest start user --watch",
    "start:admin": "nest start admin --watch",
    "build:user": "nest build user",
    "build:admin": "nest build admin",
  }
```

### Step: 6. Write the docker-compose.yml 

```yml
services:
  admin:
    build:
      context: .
      dockerfile: apps/admin/Dockerfile
    ports:
      - '3001:3000'
    volumes:
      - .:/app
      - /app/node_modules
    command: yarn start:admin
    depends_on:
      - db

  user:
    build:
      context: .
      dockerfile: apps/user/Dockerfile
    ports:
      - '3000:3000'
    volumes:
      - .:/app
      - /app/node_modules
    command: yarn start:user
    depends_on:
      - db

  db:
    image: postgres:15
    ports:
      - '5432:5432'
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:

```

### Step: 7. Run Docker Compose

```bash
docker-compose up --build
```

1. Check the Connect PostgreSQL
- `postgresql`: http://localhost:5432
2. Check the NestJS App
- `user`: http://localhost:3000
- `admin`: http://localhost:3001



# Conclusion


Today, I worked on setting up a NestJS project as a monorepo, deploying it to Docker, and configuring it for real-time code builds.

A monorepo structure makes development more convenient by enabling the use of shared modules and a common database, which improves reusability and simplifies code management.

I hope you can use this sample app as a foundation to create your own amazing projects!

<!-- 오늘은 nestjs 프로젝트를 monorepo로 구성하고 docker에 올리고 실시간 코드 빌드를 위한 설정들을 해봤습니다.
모노레포는 공동 모듈, 공동 DB를 사용함으로써 재사용성을 높이고 코드 관리를 용이하게 해주는 점이 개발하는데 있어서 편리하게 해주는것 같습니다.
이 샘플 앱을 가지고 여러분만의 프로젝트를 잘 만드시길 바라겠습니다. -->

Thank you for reading, and happy blogging! 🚀

## References

- [Nestjs Document](https://docs.nestjs.com/cli/monorepo)
- [Sample Github](https://github.com/hoonapps/sample-nestjs-monorepo-docker)


