# API 명세

5주 차별로 API 계약이 확장됩니다. 이전 주차 엔드포인트는 하위 호환으로 유지됩니다.

> **API란?** 서버에 요청을 보내고 응답을 받을 수 있도록 정해 둔 규칙입니다. 어떤 주소로, 어떤 방식으로 보내야 하는지, 그리고 응답이 어떤 형태로 오는지를 미리 약속해 두는 것이라고 생각하시면 됩니다.

---

## 공통 사항

| 항목 | 값 | 설명 |
|------|-----|------|
| Base URL | `http://localhost:8000` | 서버가 실행되는 주소입니다. 모든 요청 앞에 붙습니다. |
| Content-Type | `application/json` | 요청·응답 데이터 형식이 JSON임을 명시합니다. |
| 인증 | 없음 | 커리큘럼 범위 밖입니다. |

### HTTP 메서드란?

요청의 목적을 표현하는 동사입니다. 이 프로젝트에서 쓰는 두 가지만 알면 됩니다.

| 메서드 | 언제 쓰나 |
|--------|-----------|
| `GET` | 데이터를 **조회**할 때 |
| `POST` | 데이터를 **생성·전송**할 때 |

### HTTP 상태 코드란?

서버가 응답할 때 "처리가 어떻게 됐는지"를 숫자로 알려 주는 코드입니다.

| 코드 | 의미 | 언제 발생하나 |
|------|------|--------------|
| 200 | OK | 요청이 정상 처리되었을 때 |
| 404 | Not Found | 찾는 데이터가 없을 때 (예: 없는 `id` 조회) |
| 422 | Unprocessable Entity | 요청 데이터가 규칙에 맞지 않을 때. FastAPI가 자동으로 반환합니다. |
| 500 | Internal Server Error | 서버 내부에서 예상치 못한 오류가 발생했을 때 |

---

## 1주차

### GET /health

서버가 정상 실행 중인지 확인하는 엔드포인트입니다. 모든 주차에서 유지됩니다.

> **엔드포인트란?** 특정 기능을 수행하는 서버의 주소(URL)입니다. `/health` 는 "서버 상태 확인"이라는 기능에 붙인 주소입니다.

**Endpoint**
`GET /health`

**Path Parameters**
없음

**Query Parameters**
없음

**Example Request**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response Fields**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `status` | string | - | 서버 상태 | `"ok"` |

**200 OK**
```json
{
  "status": "ok"
}
```

**Response Code**

| Code | Description |
|------|-------------|
| 200 | 정상 처리 |
| 500 | 서버 내부 오류 |

**Error Response**
```json
// 500
{ "detail": "Internal Server Error" }
```

---

### POST /summarize (1주차: 에코)

요청으로 받은 JSON을 그대로 되돌려 줍니다. LLM·DB 미사용. 스키마 검증 없음(임의 JSON 허용).

> **에코(echo)란?** 보낸 내용을 그대로 돌려 주는 것입니다. 지금은 AI 로직이 없고, "요청이 서버에 들어오고 응답이 나간다"는 흐름 자체를 확인하는 단계입니다.

**Endpoint**
`POST /summarize`

**Path Parameters**
없음

**Query Parameters**
없음

**Request Body (application/json)**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| (임의) | object | - | 임의 JSON | `{ "title": "...", "content": "..." }` |

**Example Request**
```http
POST /summarize HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "title": "...",
  "content": "..."
}
```

**Response Fields**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `received` | object | - | 받은 JSON 그대로 | `{ "title": "...", "content": "..." }` |
| `message` | string | - | 처리 결과 메시지 | `"echo ok"` |

**200 OK**
```json
{
  "received": { "title": "...", "content": "..." },
  "message": "echo ok"
}
```

**Response Code**

| Code | Description |
|------|-------------|
| 200 | 정상 처리 |
| 500 | 서버 내부 오류 |

**Error Response**
```json
// 500
{ "detail": "Internal Server Error" }
```

---

## 2주차

### POST /summarize (2주차: 스키마 적용)

Request·Response 스키마를 적용합니다. 스키마를 만족하지 않는 요청은 로직 실행 전에 422로 차단됩니다.

> **스키마(Schema)란?** "이 요청에는 어떤 필드가 있어야 하고, 각각 어떤 타입이어야 한다"는 규칙입니다. 계약서라고 생각하시면 됩니다.

**Endpoint**
`POST /summarize`

**Path Parameters**
없음

**Query Parameters**
없음

**Request Body (application/json)**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `content_text` | string | O | 요약 대상 테크 블로그 전문 | `"FastAPI는 Python의 타입 힌트를 활용해..."` |
| `title` | string \| null | - | 글 제목 (없으면 null) | `"FastAPI 완벽 가이드"` |
| `output_format` | `"json"` | O | 출력 형식. 현재 `"json"` 만 허용 | `"json"` |

**Example Request**
```http
POST /summarize HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "content_text": "FastAPI는 Python의 타입 힌트를 활용해...",
  "title": "FastAPI 완벽 가이드",
  "output_format": "json"
}
```

**Response Fields**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `summary` | string | - | 2~3문장 핵심 요약 | `"..."` |
| `key_points` | string[] | - | 핵심 포인트 목록 | `["...", "..."]` |
| `meta.prompt_version` | string | - | 어떤 버전의 프롬프트로 생성했는지 | `"v1.0"` |
| `meta.generated_at` | string | - | 생성 시각 (ISO 8601 형식) | `"2024-01-15T10:30:00Z"` |

**200 OK**
```json
{
  "summary": "...",
  "key_points": ["...", "..."],
  "meta": {
    "prompt_version": "v1.0",
    "generated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Response Code**

| Code | Description |
|------|-------------|
| 200 | 정상 처리 |
| 422 | 요청 데이터 오류 |
| 500 | 서버 내부 오류 |

**Error Response**
```json
// 422
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

// 500
{ "detail": "Internal Server Error" }
```

---

## 3주차

### POST /summarize (3주차: DB 저장)

2주차 Request·Response 스키마와 동일합니다. 요약 생성 후 DB에 저장하며, 응답에 `id` 가 추가됩니다.

> **`id`란?** DB에 저장된 각 레코드를 구분하는 고유 번호입니다. 나중에 이 번호로 특정 요약을 다시 꺼낼 수 있습니다.

**Endpoint**
`POST /summarize`

**Path Parameters**
없음

**Query Parameters**
없음

**Request Body (application/json)**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `content_text` | string | O | 요약 대상 테크 블로그 전문 | `"FastAPI는 Python의 타입 힌트를 활용해..."` |
| `title` | string \| null | - | 글 제목 (없으면 null) | `"FastAPI 완벽 가이드"` |
| `output_format` | `"json"` | O | 출력 형식. 현재 `"json"` 만 허용 | `"json"` |

**Example Request**
```http
POST /summarize HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "content_text": "FastAPI는 Python의 타입 힌트를 활용해...",
  "title": "FastAPI 완벽 가이드",
  "output_format": "json"
}
```

**Response Fields**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | - | 저장된 요약의 고유 번호 | `1` |
| `summary` | string | - | 2~3문장 핵심 요약 | `"..."` |
| `key_points` | string[] | - | 핵심 포인트 목록 | `["...", "..."]` |
| `meta.prompt_version` | string | - | 어떤 버전의 프롬프트로 생성했는지 | `"v1.0"` |
| `meta.generated_at` | string | - | 생성 시각 (ISO 8601 형식) | `"2024-01-15T10:30:00Z"` |

**200 OK**
```json
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

**Response Code**

| Code | Description |
|------|-------------|
| 200 | 정상 처리 |
| 422 | 요청 데이터 오류 |
| 500 | 서버 내부 오류 |

**Error Response**
```json
// 422
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

// 500
{ "detail": "Internal Server Error" }
```

---

### GET /summaries

저장된 요약 전체 목록을 최신순으로 조회합니다.

**Endpoint**
`GET /summaries`

**Path Parameters**
없음

**Query Parameters**
없음

**Example Request**
```http
GET /summaries HTTP/1.1
Host: localhost:8000
```

**Response Fields**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | - | 요약 고유 번호 | `1` |
| `title` | string \| null | - | 페이지에서 추출한 제목 | `"FastAPI 완벽 가이드"` |
| `url` | string | - | 원본 URL | `"https://fastapi.tiangolo.com/tutorial/"` |

**200 OK**
```json
[
  { "id": 1, "title": "FastAPI 완벽 가이드", "url": "https://fastapi.tiangolo.com/tutorial/" },
  { "id": 2, "title": "Rust async runtime 변경점", "url": "https://blog.example.com/rust-async" }
]
```

**Response Code**

| Code | Description |
|------|-------------|
| 200 | 정상 처리 |
| 500 | 서버 내부 오류 |

**Error Response**
```json
// 500
{ "detail": "Internal Server Error" }
```

---

### GET /summaries/{id}

요약 한 건을 조회합니다. `{id}` 자리에 조회할 요약 번호를 넣으면 됩니다.

> 예: `GET /summaries/1` → id가 1인 요약을 조회합니다.

**Endpoint**
`GET /summaries/{id}`

**Path Parameters**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | O | 조회할 요약의 고유 번호 | `1` |

**Query Parameters**
없음

**Example Request**
```http
GET /summaries/1 HTTP/1.1
Host: localhost:8000
```

**Response Fields**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | - | 요약 고유 번호 | `1` |
| `title` | string \| null | - | 페이지에서 추출한 제목 | `"FastAPI 완벽 가이드"` |
| `url` | string | - | 원본 URL | `"https://fastapi.tiangolo.com/tutorial/"` |
| `content_text` | string | - | 크롤링한 본문 원문 | `"FastAPI는..."` |
| `summary` | string | - | 2~3문장 핵심 요약 | `"..."` |
| `key_points` | array | - | 핵심 포인트 목록 | `[...]` |
| `meta` | object | - | prompt_version, generated_at 등 | `{ "prompt_version": "v2.0", "generated_at": "..." }` |
| `created_at` | string | - | 저장된 시각 | `"2025-03-28T10:30:00Z"` |

**200 OK**
```json
{
  "id": 1,
  "title": "FastAPI 완벽 가이드",
  "url": "https://fastapi.tiangolo.com/tutorial/",
  "content_text": "FastAPI는...",
  "summary": "...",
  "key_points": ["...", "..."],
  "meta": {
    "prompt_version": "v2.0",
    "generated_at": "2025-03-28T10:30:00Z"
  },
  "created_at": "2025-03-28T10:30:00Z"
}
```

**Response Code**

| Code | Description |
|------|-------------|
| 200 | 정상 처리 |
| 404 | 해당 id 없음 |
| 500 | 서버 내부 오류 |

**Error Response**
```json
// 404
{ "detail": "Summary not found" }

// 500
{ "detail": "Internal Server Error" }
```

---

## 4주차

엔드포인트·Request·Response 스펙은 3주차와 동일합니다. **외부에서 보이는 동작은 바뀌지 않고**, 내부 코드 구조만 레이어로 분리됩니다.

| 구분 | 3주차 | 4주차 |
|------|--------|--------|
| 요약 생성 | 더미 데이터 (LLM 미사용) | LangChain으로 실제 LLM 호출 |
| 로직 위치 | 컨트롤러 함수 안 | Service 레이어 |
| DB 접근 위치 | 컨트롤러 함수 안 | Repository 레이어 |
| 저장 조건 | 더미 응답 그대로 저장 | Pydantic 검증 통과분만 저장 |

**API 목록 (구조는 3주차와 동일)**

- **Endpoint** · **Description** · **Path Parameters** · **Query Parameters** · **Request Body** · **Example Request** · **Example Response** 형식으로 3주차 명세를 따릅니다.
- `GET /health` · `POST /summarize` · `GET /summaries` · `GET /summaries/{id}`

---

## 5주차

`SummaryRequest` 스키마가 교체됩니다. `content_text` + `title` 대신 `url` + `output_format`만 받습니다. 서버가 직접 URL을 크롤링해서 본문을 추출합니다. 배치 처리 엔드포인트도 추가됩니다.

> **왜 교체인가?** 실제 사용자는 텍스트를 복붙하지 않습니다. 링크를 공유합니다. `content_text`를 받는 설계 자체가 잘못된 가정이었습니다.

### 스키마 변경

#### SummaryRequest (교체)

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `url` | string | O | 요약할 테크 블로그 URL | `"https://..."` |
| `output_format` | `"json"` | O | 출력 형식. 현재 `"json"` 만 허용 | `"json"` |

#### SummaryResponse (기존 필드 유지 + 추가)

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `recommended_for` | string | - | 이런 분께 추천 | `"Rust로 비동기 서버를 운영 중인 분"` |
| `difficulty` | `"초급"` \| `"중급"` \| `"고급"` | - | 글의 난이도 | `"중급"` |
| `read_time` | integer | - | 원문 읽기 예상 시간 (분) | `12` |
| `summary` | string | - | 2~3문장 핵심 요약 | `"..."` |
| `key_points` | string[] | - | 핵심 포인트 목록 | `["...", "..."]` |
| `meta` | object | - | prompt_version, generated_at | `{ "prompt_version": "v2.0", ... }` |

#### SummaryListItem (변경)

`title`은 사용자 입력이 아닌 서버가 페이지에서 추출한 값입니다.

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | - | 요약 고유 번호 | `1` |
| `title` | string \| null | - | 페이지에서 추출한 제목. 추출 실패 시 null | `"FastAPI 완벽 가이드"` |
| `url` | string | - | 원본 URL | `"https://..."` |

#### BatchSummaryRequest (신규)

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `urls` | string[] | O | URL 목록 (1~10개) | `["https://...", "https://..."]` |
| `output_format` | `"json"` | O | 출력 형식 | `"json"` |

#### BatchSummaryResponse (신규)

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `results` | SummaryResponseWithId[] | - | 성공한 요약 목록 | `[...]` |
| `failed` | object[] | - | 실패한 항목 목록. 각 요소: `{ url, error }` | `[...]` |

> 배치 요청은 일부가 실패해도 전체가 실패하지 않습니다. 성공한 것은 `results`에, 실패한 것은 `failed`에 담겨 반환됩니다.

---

### POST /summarize (5주차: URL 입력으로 교체)

URL을 받아 서버가 직접 크롤링하고 본문을 추출한 뒤 요약합니다. 결과는 DB에 저장됩니다.

**Endpoint**
`POST /summarize`

**Path Parameters**
없음

**Query Parameters**
없음

**Request Body (application/json)**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `url` | string | O | 요약할 테크 블로그 URL | `"https://..."` |
| `output_format` | `"json"` | O | 출력 형식 | `"json"` |

**Example Request**
```http
POST /summarize HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "url": "https://fastapi.tiangolo.com/tutorial/",
  "output_format": "json"
}
```

**Response Fields**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `id` | integer | - | 저장된 요약의 고유 번호 | `3` |
| `recommended_for` | string | - | 이런 분께 추천 | `"Python 웹 개발을 처음 시작하는 분"` |
| `difficulty` | string | - | 글의 난이도 | `"초급"` |
| `read_time` | integer | - | 원문 읽기 예상 시간 (분) | `8` |
| `summary` | string | - | 2~3문장 핵심 요약 | `"..."` |
| `key_points` | string[] | - | 핵심 포인트 목록 | `["...", "..."]` |
| `meta.prompt_version` | string | - | 프롬프트 버전 | `"v2.0"` |
| `meta.generated_at` | string | - | 생성 시각 (ISO 8601) | `"2025-03-28T10:30:00Z"` |

**200 OK**
```json
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

**Response Code**

| Code | Description |
|------|-------------|
| 200 | 정상 처리 |
| 422 | 요청 데이터 오류 |
| 500 | URL 크롤링 실패 또는 서버 내부 오류 |

**Error Response**
```json
// 422
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

// 500
{ "detail": "Internal Server Error" }
```

---

### POST /summarize/batch

여러 URL을 한꺼번에 받아 동시에 크롤링·요약합니다. 최대 10개. 각 URL은 독립적으로 처리되며, 일부 실패해도 전체 요청이 실패하지 않습니다.

**Endpoint**
`POST /summarize/batch`

**Path Parameters**
없음

**Query Parameters**
없음

**Request Body (application/json)**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `urls` | string[] | O | URL 목록 (1~10개) | `["https://...", "https://..."]` |
| `output_format` | `"json"` | O | 출력 형식 | `"json"` |

**Example Request**
```http
POST /summarize/batch HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "urls": [
    "https://blog.example.com/rust-async",
    "https://blog.example.com/postgresql-index",
    "https://blog.example.com/k8s-1-30"
  ],
  "output_format": "json"
}
```

**Response Fields**

| Name | Type | Required | Description | Example |
|------|------|:--------:|-------------|---------|
| `results` | SummaryResponseWithId[] | - | 성공한 요약 목록 | `[...]` |
| `failed` | object[] | - | 실패한 항목 목록. 각 요소: `{ url, error }` | `[...]` |

**200 OK**
```json
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

**Response Code**

| Code | Description |
|------|-------------|
| 200 | 정상 처리 (일부 실패 포함 가능) |
| 422 | 요청 데이터 오류 |
| 500 | 서버 내부 오류 |

**Error Response**
```json
// 422
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

// 500
{ "detail": "Internal Server Error" }
```

---

**API 목록 (5주차 전체)**

- `GET /health` · `POST /summarize` · `GET /summaries` · `GET /summaries/{id}` (기존 유지)
- `POST /summarize/batch` (신규)
