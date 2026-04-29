# API 명세

## 공통 사항

| 항목 | 값 |
|------|----|
| Base URL | `http://localhost:8000` |
| 인증 | 없음 |

---

## 1주차

### GET /health

서버가 정상 실행 중인지 확인합니다. 모든 주차에서 유지됩니다.

**Endpoint**
`GET /health`

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**

(없음)

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `status` | string | O | 서버 상태 | `"ok"` |

**Success Response Example**

```json
// 200 OK
{
  "status": "ok"
}
```

**Error Response Example**

```json
// 500 Internal Server Error
{ "detail": "Internal Server Error" }
```

---

### POST /summarize (1주차: 에코)

요청으로 받은 JSON을 그대로 되돌려 줍니다. 스키마 검증 없음.

**Endpoint**
`POST /summarize`

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `Content-Type` | string | O | 요청 데이터 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| (임의) | object | - | 임의 JSON | `{ "title": "...", "content": "..." }` |

**Request Example**

```json
{
  "title": "...",
  "content": "..."
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `received` | object | O | 받은 JSON 그대로 | `{ "title": "...", "content": "..." }` |
| `message` | string | O | 처리 결과 메시지 | `"echo ok"` |

**Success Response Example**

```json
// 200 OK
{
  "received": { "title": "...", "content": "..." },
  "message": "echo ok"
}
```

**Error Response Example**

```json
// 500 Internal Server Error
{ "detail": "Internal Server Error" }
```

---

## 2주차

### POST /summarize (2주차: 스키마 적용)

Request·Response 스키마를 적용합니다. 스키마를 만족하지 않는 요청은 422로 차단됩니다.

**Endpoint**
`POST /summarize`

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `Content-Type` | string | O | 요청 데이터 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `content_text` | string | O | 요약 대상 테크 블로그 전문 | `"FastAPI는 Python의 타입 힌트를 활용해..."` |
| `title` | string \| null | - | 글 제목 | `"FastAPI 완벽 가이드"` |
| `output_format` | `"json"` | O | 출력 형식. 현재 `"json"` 만 허용 | `"json"` |

**Request Example**

```json
{
  "content_text": "FastAPI는 Python의 타입 힌트를 활용해...",
  "title": "FastAPI 완벽 가이드",
  "output_format": "json"
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `summary` | string | O | 2~3문장 핵심 요약 | `"..."` |
| `key_points` | string[] | O | 핵심 포인트 목록 | `["...", "..."]` |
| `meta.prompt_version` | string | O | 프롬프트 버전 | `"v1.0"` |
| `meta.generated_at` | string | O | 생성 시각 (ISO 8601) | `"2024-01-15T10:30:00Z"` |

**Success Response Example**

```json
// 200 OK
{
  "summary": "...",
  "key_points": ["...", "..."],
  "meta": {
    "prompt_version": "v1.0",
    "generated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Response Example**

```json
// 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "content_text"],
      "msg": "Field required",
      "input": {}
    }
  ]
}

// 500 Internal Server Error
{ "detail": "Internal Server Error" }
```

---

## 3주차

### POST /summarize (3주차: DB 저장)

Request 스키마는 2주차와 동일합니다. 요약 생성 후 DB에 저장하며, 응답에 `id`가 추가됩니다.

**Endpoint**
`POST /summarize`

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `Content-Type` | string | O | 요청 데이터 형식 | `application/json` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `content_text` | string | O | 요약 대상 테크 블로그 전문 | `"FastAPI는 Python의 타입 힌트를 활용해..."` |
| `title` | string \| null | - | 글 제목 | `"FastAPI 완벽 가이드"` |
| `output_format` | `"json"` | O | 출력 형식. 현재 `"json"` 만 허용 | `"json"` |

**Request Example**

```json
{
  "content_text": "FastAPI는 Python의 타입 힌트를 활용해...",
  "title": "FastAPI 완벽 가이드",
  "output_format": "json"
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | O | 저장된 요약의 고유 번호 | `1` |
| `summary` | string | O | 2~3문장 핵심 요약 | `"..."` |
| `key_points` | string[] | O | 핵심 포인트 목록 | `["...", "..."]` |
| `meta.prompt_version` | string | O | 프롬프트 버전 | `"v1.0"` |
| `meta.generated_at` | string | O | 생성 시각 (ISO 8601) | `"2024-01-15T10:30:00Z"` |

**Success Response Example**

```json
// 200 OK
{
  "id": 1,
  "summary": "...",
  "key_points": ["...", "..."],
  "meta": {
    "prompt_version": "v1.0",
    "generated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Response Example**

```json
// 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "content_text"],
      "msg": "Field required",
      "input": {}
    }
  ]
}

// 500 Internal Server Error
{ "detail": "Internal Server Error" }
```

---

### GET /summaries (3주차)

저장된 요약 전체 목록을 최신순으로 조회합니다.

**Endpoint**
`GET /summaries`

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**

(없음)

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `[].id` | integer | O | 요약 고유 번호 | `1` |
| `[].title` | string \| null | O | 페이지에서 추출한 제목 | `"FastAPI 완벽 가이드"` |
| `[].created_at` | string | O | 저장된 시각 (ISO 8601) | `"2025-03-28T10:30:00Z"` |

**Success Response Example**

```json
// 200 OK
[
  { "id": 1, "title": "FastAPI 완벽 가이드", "created_at": "2025-03-28T10:30:00Z" },
  { "id": 2, "title": "Rust async runtime 변경점", "created_at": "2025-03-27T09:00:00Z" }
]
```

**Error Response Example**

```json
// 500 Internal Server Error
{ "detail": "Internal Server Error" }
```

---

### GET /summaries/{id} (3주차)

요약 한 건을 조회합니다.

**Endpoint**
`GET /summaries/{id}`

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | O | 조회할 요약의 고유 번호 | `1` |

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**

(없음)

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | O | 요약 고유 번호 | `1` |
| `title` | string \| null | O | 페이지에서 추출한 제목 | `"FastAPI 완벽 가이드"` |
| `content_text` | string | O | 크롤링한 본문 원문 | `"FastAPI는..."` |
| `summary` | string | O | 2~3문장 핵심 요약 | `"..."` |
| `key_points` | string[] | O | 핵심 포인트 목록 | `["...", "..."]` |
| `meta.prompt_version` | string | O | 프롬프트 버전 | `"v1.0"` |
| `meta.generated_at` | string | O | 생성 시각 (ISO 8601) | `"2025-03-28T10:30:00Z"` |
| `created_at` | string | O | 저장된 시각 (ISO 8601) | `"2025-03-28T10:30:00Z"` |

**Success Response Example**

```json
// 200 OK
{
  "id": 1,
  "title": "FastAPI 완벽 가이드",
  "content_text": "FastAPI는...",
  "summary": "...",
  "key_points": ["...", "..."],
  "meta": {
    "prompt_version": "v1.0",
    "generated_at": "2025-03-28T10:30:00Z"
  },
  "created_at": "2025-03-28T10:30:00Z"
}
```

**Error Response Example**

```json
// 404 Not Found
{ "detail": "Summary not found" }

// 500 Internal Server Error
{ "detail": "Internal Server Error" }
```

---

## 4주차

엔드포인트·Request·Response 스펙은 3주차와 동일합니다. 내부 코드 구조만 레이어로 분리됩니다.

- `GET /health` · `POST /summarize` · `GET /summaries` · `GET /summaries/{id}`

---

## 5주차

### POST /summarize (5주차: URL 입력으로 교체)

URL을 받아 서버가 직접 크롤링하고 본문을 추출한 뒤 요약합니다. 결과는 DB에 저장됩니다.

**Endpoint**
`POST /summarize`

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `Content-Type` | string | O | 요청 데이터 형식 | `application/x-www-form-urlencoded` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `url` | string | O | 요약할 테크 블로그 URL | `"https://fastapi.tiangolo.com/tutorial/"` |
| `output_format` | `"json"` | O | 출력 형식. 현재 `"json"` 만 허용 | `"json"` |

**Request Example**

```json
{
  "url": "https://fastapi.tiangolo.com/tutorial/",
  "output_format": "json"
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | O | 저장된 요약의 고유 번호 | `3` |
| `recommended_for` | string | O | 이런 분께 추천 | `"Python 웹 개발을 처음 시작하는 분"` |
| `difficulty` | `"초급"` \| `"중급"` \| `"고급"` | O | 글의 난이도 | `"초급"` |
| `read_time` | integer | O | 원문 읽기 예상 시간 (분) | `8` |
| `summary` | string | O | 2~3문장 핵심 요약 | `"..."` |
| `key_points` | string[] | O | 핵심 포인트 목록 | `["...", "..."]` |
| `meta.prompt_version` | string | O | 프롬프트 버전 | `"v2.0"` |
| `meta.generated_at` | string | O | 생성 시각 (ISO 8601) | `"2025-03-28T10:30:00Z"` |

**Success Response Example**

```json
// 200 OK
{
  "id": 3,
  "recommended_for": "Python 웹 개발을 처음 시작하는 분",
  "difficulty": "초급",
  "read_time": 8,
  "summary": "FastAPI는 Python의 타입 힌트를 기반으로 빠르게 API를 만들 수 있는 프레임워크입니다.",
  "key_points": [
    "자동 문서화 (Swagger UI)",
    "Pydantic으로 입력 검증",
    "비동기 지원"
  ],
  "meta": {
    "prompt_version": "v2.0",
    "generated_at": "2025-03-28T10:30:00Z"
  }
}
```

**Error Response Example**

```json
// 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "url"],
      "msg": "Field required",
      "input": {}
    }
  ]
}

// 500 Internal Server Error
{ "detail": "Internal Server Error" }
```

---

### POST /summarize/batch

여러 URL을 한꺼번에 받아 동시에 크롤링·요약합니다. 최대 10개. 일부 실패해도 전체 요청이 실패하지 않습니다.

**Endpoint**
`POST /summarize/batch`

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `Content-Type` | string | O | 요청 데이터 형식 | `application/x-www-form-urlencoded` |

**Request Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `urls` | string[] | O | URL 목록 (1~10개) | `["https://...", "https://..."]` |
| `output_format` | `"json"` | O | 출력 형식. 현재 `"json"` 만 허용 | `"json"` |

**Request Example**

```json
{
  "urls": [
    "https://blog.example.com/rust-async",
    "https://blog.example.com/postgresql-index",
    "https://blog.example.com/k8s-1-30"
  ],
  "output_format": "json"
}
```

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `results` | object[] | O | 성공한 요약 목록 | `[...]` |
| `results[].id` | integer | O | 요약 고유 번호 | `4` |
| `results[].recommended_for` | string | O | 이런 분께 추천 | `"..."` |
| `results[].difficulty` | string | O | 글의 난이도 | `"중급"` |
| `results[].read_time` | integer | O | 예상 읽기 시간 (분) | `12` |
| `results[].summary` | string | O | 핵심 요약 | `"..."` |
| `results[].key_points` | string[] | O | 핵심 포인트 목록 | `["...", "..."]` |
| `results[].meta.prompt_version` | string | O | 프롬프트 버전 | `"v2.0"` |
| `results[].meta.generated_at` | string | O | 생성 시각 (ISO 8601) | `"2025-03-28T10:31:00Z"` |
| `failed` | object[] | O | 실패한 항목 목록 | `[...]` |
| `failed[].url` | string | O | 실패한 URL | `"https://..."` |
| `failed[].error` | string | O | 실패 사유 | `"HTTP 403"` |

**Success Response Example**

```json
// 200 OK
{
  "results": [
    {
      "id": 4,
      "recommended_for": "Rust로 비동기 서버를 운영 중인 분",
      "difficulty": "중급",
      "read_time": 12,
      "summary": "Rust 1.80의 async 변경점과 마이그레이션 경험을 다룹니다.",
      "key_points": ["async fn in trait stable", "tokio 3.x 지원", "breaking change 2가지"],
      "meta": { "prompt_version": "v2.0", "generated_at": "2025-03-28T10:31:00Z" }
    },
    {
      "id": 5,
      "recommended_for": "SQL 쿼리 성능에 관심 있는 백엔드 개발자",
      "difficulty": "초급",
      "read_time": 8,
      "summary": "PostgreSQL 인덱스 전략과 실전 최적화 사례를 설명합니다.",
      "key_points": ["B-Tree vs GIN 선택 기준", "복합 인덱스 순서", "EXPLAIN ANALYZE 읽기"],
      "meta": { "prompt_version": "v2.0", "generated_at": "2025-03-28T10:31:00Z" }
    }
  ],
  "failed": [
    {
      "url": "https://blog.example.com/k8s-1-30",
      "error": "페이지를 가져올 수 없습니다 (HTTP 403)"
    }
  ]
}
```

**Error Response Example**

```json
// 422 Unprocessable Entity
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "urls"],
      "msg": "Field required",
      "input": {}
    }
  ]
}

// 500 Internal Server Error
{ "detail": "Internal Server Error" }
```

---

### GET /summaries (5주차)

저장된 요약 전체 목록을 최신순으로 조회합니다. 3주차 대비 `created_at` 대신 `url`이 반환됩니다.

**Endpoint**
`GET /summaries`

**Path Parameter**

(없음)

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**

(없음)

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `[].id` | integer | O | 요약 고유 번호 | `1` |
| `[].title` | string \| null | O | 페이지에서 추출한 제목. 추출 실패 시 null | `"FastAPI 완벽 가이드"` |
| `[].url` | string | O | 원본 URL | `"https://fastapi.tiangolo.com/tutorial/"` |

**Success Response Example**

```json
// 200 OK
[
  { "id": 1, "title": "FastAPI 완벽 가이드", "url": "https://fastapi.tiangolo.com/tutorial/" },
  { "id": 2, "title": "Rust async runtime 변경점", "url": "https://blog.example.com/rust-async" }
]
```

**Error Response Example**

```json
// 500 Internal Server Error
{ "detail": "Internal Server Error" }
```

---

### GET /summaries/{id} (5주차)

요약 한 건을 조회합니다. 3주차 대비 `url`, `recommended_for`, `difficulty`, `read_time`이 추가됩니다.

**Endpoint**
`GET /summaries/{id}`

**Path Parameter**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | O | 조회할 요약의 고유 번호 | `1` |

**Query Parameter**

(없음)

**Request Header**

(없음)

**Request Body**

(없음)

**Request Example**

(없음)

**Response Body**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | O | 요약 고유 번호 | `1` |
| `title` | string \| null | O | 페이지에서 추출한 제목. 추출 실패 시 null | `"FastAPI 완벽 가이드"` |
| `url` | string | O | 원본 URL | `"https://fastapi.tiangolo.com/tutorial/"` |
| `content_text` | string | O | 크롤링한 본문 원문 | `"FastAPI는..."` |
| `recommended_for` | string | O | 이런 분께 추천 | `"Python 웹 개발을 처음 시작하는 분"` |
| `difficulty` | string | O | 글의 난이도 | `"초급"` |
| `read_time` | integer | O | 예상 읽기 시간 (분) | `8` |
| `summary` | string | O | 2~3문장 핵심 요약 | `"..."` |
| `key_points` | string[] | O | 핵심 포인트 목록 | `["...", "..."]` |
| `meta.prompt_version` | string | O | 프롬프트 버전 | `"v2.0"` |
| `meta.generated_at` | string | O | 생성 시각 (ISO 8601) | `"2025-03-28T10:30:00Z"` |
| `created_at` | string | O | 저장된 시각 (ISO 8601) | `"2025-03-28T10:30:00Z"` |

**Success Response Example**

```json
// 200 OK
{
  "id": 1,
  "title": "FastAPI 완벽 가이드",
  "url": "https://fastapi.tiangolo.com/tutorial/",
  "content_text": "FastAPI는...",
  "recommended_for": "Python 웹 개발을 처음 시작하는 분",
  "difficulty": "초급",
  "read_time": 8,
  "summary": "...",
  "key_points": ["...", "..."],
  "meta": {
    "prompt_version": "v2.0",
    "generated_at": "2025-03-28T10:30:00Z"
  },
  "created_at": "2025-03-28T10:30:00Z"
}
```

**Error Response Example**

```json
// 404 Not Found
{ "detail": "Summary not found" }

// 500 Internal Server Error
{ "detail": "Internal Server Error" }
```
