---
title: "[NestJS] Publishing a Custom Class Validator as an NPM Package"
date: 2024-11-25 10:00:00 +0900
categories: [NestJS]
tags: [NestJS, Github, npm, class-validator]
image: /assets/img/Nest.js.png
---

In this post, I will share the process of creating and publishing a custom class validator as an NPM package for validating user data in various projects, particularly in Korean contexts like user registration. This stems from the necessity to streamline data validation in such projects.

You can check out the open-source package on [GitHub](https://github.com/hoonapps/kr-validators) and participate in its development! :D

---

## Introducing My NPM Package: [kr-validators](https://www.npmjs.com/package/kr-validators)

Install it in your NestJS project using the following command:

```bash
npm i kr-validators
```

---

## Step 1: Create a Project

Open **Git Bash** and run the following commands:  

```bash
npx @nestjs/cli new kr-validators
cd kr-validators
```

---

## Step 2: Create a Library

Run the commands below to set up your library:

```bash
npm i class-validator
npx nest generate library validation
```

This will create a `libs/validation` folder, where you can write your custom decorators.

---

## Step 3: Implementing a Decorator

Here’s how to create a decorator for validating Korean resident registration numbers:

Create a file `libs/validation/src/decorators/is-resident-id-number.decorator.ts` and write the following:

```typescript
import {
  registerDecorator,
  ValidationOptions,
  ValidatorConstraint,
  ValidatorConstraintInterface,
} from 'class-validator';

@ValidatorConstraint({ async: false })
export class IsResidentIdNumberConstraint
  implements ValidatorConstraintInterface
{
  validate(value: string): boolean {
    // 1. Check if the number is 13 digits long
    if (!value || value.length !== 13) return false;

    // 2. Multiply the first 12 digits by their weights and sum them
    const weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5];
    const digits = value.split('').map(Number);
    const checkSum = weights.reduce(
      (sum, weight, index) => sum + weight * digits[index],
      0,
    );
    // 3. Calculate the check digit
    const checkDigit = (11 - (checkSum % 11)) % 10;

    // 4. Compare the calculated check digit with the 13th digit
    return checkDigit === digits[12];
  }

  defaultMessage(): string {
    return 'Invalid Resident ID number';
  }
}

export function IsResidentIDNumber(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsResidentIdNumberConstraint,
    });
  };
}
```

- Korean resident registration numbers are 13 digits long. We first check the length.
- Multiply the first 12 digits by a predefined weight array and sum the results.
- Divide the sum by 11 and calculate the remainder, subtract it from 11, and get the remainder when divided by 10.
- If this matches the last digit of the number, the validation is successful.

---

## Step 4: Module and Barrel Setup

1. Module Setup

Edit `libs/validation/src/validation.module.ts` as follows:

```typescript
import { Module } from '@nestjs/common';
import { IsResidentIDNumber } from './decorators/is-resident-id-number.decorator';

@Module({
  providers: [IsResidentIDNumber],
})
export class ValidationModule {}
```

2. Barrel Setup

Edit `libs/validation/src/index.ts` to export the necessary decorators:

```typescript
export * from './decorators/is-resident-id-number.decorator';
export * from './validation.module';
```

---

## Step 5: Build and Publish the Package

1. Log in to NPM:

```bash
npm login
```

2. Build the Library:

```bash
npm run build:libs
```

3. Publish the Package:

```bash
npm publish
```

---

# Conclusion

While this example only includes validation for resident registration numbers, I’ve also added validators for phone numbers, business numbers, card numbers, emails, and postal codes. Without these validators, developers often need to implement such checks directly in business logic for each project, which can be repetitive and inefficient.

This package addresses that need and makes validation reusable and efficient across projects. I plan to update it further, so feel free to contribute!

Thank you for reading, and happy blogging! 🚀

## References

- [NPM Package](https://www.npmjs.com/package/kr-validators)
- [GitHub Repository](https://github.com/hoonapps/kr-validators)
- [Test Repository](https://github.com/hoonapps/kr-validators-test)





<!-- ---
title: "[NestJS] Publishing a Custom Class Validator as an NPM Package"
date: 2024-11-25 10:00:00 +0900
categories: [NestJS]
tags: [NestJS, Github, npm, class-validator]
image: /assets/img/Nest.js.png
---

# [NestJS] Publishing a Custom Class Validator as an NPM Package

In this post, 한국에서 회원가입 할때 유저 정보를 받는 다양한 프로젝트에서 데이터의 유효성 검증을 하는것을 더욱 편리하게 사용하고 싶다는 필요성을 느껴서 
nestjs 프로젝트를 만들고 NPM 패키지로 배포하는 과정을 담았어.  
오픈소스로 배포했으니 [here](https://github.com/hoonapps/kr-validators) 들어가서 많이 참여해줘 :D

---

## 우선 내가 만든 NPM 패키지는 [kr-validators](https://www.npmjs.com/package/kr-validators) 이거야

```bash
npm i kr-vaildators
```

nestjs 프로젝트에서 위 command로 설치하면 돼 😀

---

## Step 1: Create a project

Open **Git Bash** and run the following command:  

```bash
npx @nestjs/cli new kr-validators
cd kr-validators
```

---

## Step 2: Create a library

아래 커맨드를 따라해서 실행 시켜줘

```bash
npm i class-validator
npx nest generate library validation
```

그러면 `libs/validation` 폴더가 생성이되며, 이 안에 커스텀 데코레이터를 작성하게 됩니다.

---

## Step 3: 데코레이터 구현

한국 주민등록 번호에 대해서 유효성 검사 데코레이터를 설명할게

`libs/validation/src/decorators/is-resident-id-number.decorator.ts` 파일을 생성하고 아래 내용을 작성합니다.

```typescript
import {
  registerDecorator,
  ValidationOptions,
  ValidatorConstraint,
  ValidatorConstraintInterface,
} from 'class-validator';

@ValidatorConstraint({ async: false })
export class IsResidentIdNumberConstraint
  implements ValidatorConstraintInterface
{
  validate(value: string): boolean {
    // 1. 13자리 체크
    if (!value || value.length !== 13) return false;

    // 2. 주민번호 앞 12자리와 가중치를 곱해서 더한다.
    const weights = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5];
    const digits = value.split('').map(Number);
    const checkSum = weights.reduce(
      (sum, weight, index) => sum + weight * digits[index],
      0,
    );
    // 3. 합계를 11로 나눈 나머지를 11에서 빼준값을 10으로 나눠서 나머지를 구한다.
    const checkDigit = (11 - (checkSum % 11)) % 10;

    // 4. 주민번호 마지막 번호랑 위에서 구한 나머지랑 비교해서 일치하면 유효 성공
    return checkDigit === digits[12];
  }

  defaultMessage(): string {
    return 'Invalid Resident ID number';
  }
}

export function IsResidentIDNumber(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsResidentIdNumberConstraint,
    });
  };
}

```
- 한국 주민등록 번호는 총 13자리로 구성이 되어있어. 그래서 13자리 체크를 먼저해주고
- 주민번호 앞 12자리와 **weights** 변수에 배열을 순서대로 곱해주고 모두 더해줘
- 합계를 11로 나누고 그 나머지를 다시 11에서 빼주고 다시 10으로 나눠서 나머지를 구해줘
- 위에서 구한 값이랑 주민번호 마지막 숫자랑 일치하면 유효성 검사 성공이야

---

## Step 4: Module 및 Barrel 설정

1. Module 설정

`libs/validation/src/validation.module.ts`를 수정합니다.

```typescript
import { Module } from '@nestjs/common';
import { IsResidentIDNumber } from './decorators/is-resident-id-number.decorator';

@Module({
  providers: [IsResidentIDNumber],
})
export class ValidationModule {}
```

2. Barrel 설정

`libs/validation/src/index.ts`를 수정하여 필요한 데코레이터를 export합니다.

```typescript
export * from './decorators/is-resident-id-number.decorator';
export * from './validation.module';
```

---

## Step 5: 패키지 빌드 및 배포

1. NPM 로그인

```bash
npm login
```

2. 라이브러리 빌드

```bash
npm run build:libs
```

3. 배포

```bash
npm publish
```


# 마무리

위에 주민등록번호 유효성 검사만 작성했지만 phone numbers, business numbers, card numbers, emails, and postal codes 의 유효성 검사도 만들었고
위 유효성 검사가 없었으면 비지니스 로직에서 해당 유효성 검사 처리하는 것을 프로젝트 마다 만들어야 돼.
그래서 나는 더욱 이 패키지가 필요하다고 생각했고 그래서 만들었어.
앞으로 더 추가해야 되는 부분이 있으면 업데이트 할거야!
되게 간단하게 NPM 패키지를 만들어서 배포했으니 여러분들도 같이 많이 참여 해줬으면 좋겠습니다.

Thank you for reading, and happy blogging! 🚀

## 참고

- `https://www.npmjs.com/package/kr-validators`
- `https://github.com/hoonapps/kr-validators`
- `https://github.com/hoonapps/kr-validators-test`
 -->
