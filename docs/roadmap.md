# 5주 개발 로드맵

전체 흐름은 하나입니다. 각 주차는 앞 주차의 문제를 해결하면서 자연스럽게 이어집니다.

> 요청을 받는다 → 입력을 규격에 맞게 강제한다 → 내부 로직으로 처리한다 → 결과를 규격에 맞게 반환한다 → 저장하고 다시 꺼낸다 → 구조를 나눠서 확장한다 → 동시에 여러 요청을 처리한다

---

## 전체 흐름 요약

아래 표만 먼저 훑어 보시면, 5주가 어떤 질문에 답하면서 쌓여 가는지 한눈에 보실 수 있습니다.


| 주차  | 핵심 질문                          | 추가되는 것                               | 다음 주로 넘어가는 이유              |
| --- | ------------------------------ | ------------------------------------ | -------------------------- |
| 1주차 | 요청이 들어오고 응답이 나가는가?             | FastAPI 에코 서버                        | 아무 JSON이나 받는 것은 시스템이 아닙니다  |
| 2주차 | 계약을 코드로 고정할 수 있는가?             | Pydantic Request/Response 스키마        | 이 결과는 다시 꺼내야 하므로 저장이 필요합니다 |
| 3주차 | 지나가는 값을 관리 가능한 상태로 만들 수 있는가?   | SQLite + SQLAlchemy, 저장/조회 API       | 라우터에 일이 너무 많아집니다           |
| 4주차 | 변경을 안전하게 하려면 책임을 어떻게 나누는가?     | 레이어드 아키텍처 + LangChain 연동             | 동시에 요청이 몰리면 서버에 부담이 갑니다.\  |
| 5주차 | 한 사용자가 여러 URL을 한꺼번에 처리할 수 있는가? | URL 크롤링, async/await, asyncio.gather | 완성입니다                      |


---

## 1주차: HTTP 요청과 응답을 핸즈온으로 확인합니다

**핵심 질문:** 요청이 들어오고 응답이 나가는가?

**구현 포인트:**

- `GET /health` → 서버가 살아 있음을 확인하는 기준 API입니다
- `POST /summarize` → JSON body를 받아서 그대로 돌려 주는 에코입니다

**이 단계에서 확인하셔야 할 것 (기능이 아니라 사실입니다):**

- 보낸 JSON이 서버 함수 입력으로 들어왔는지
- 서버가 JSON을 만들어서 돌려 주었는지
- 상태 코드가 200으로 왔는지

**다음 주로 넘어가는 이유:**  
지금 `/summarize` 는 아무 JSON이나 받습니다. 이건 “우연히 돌아가는 함수”에 가깝습니다. 시스템이 되려면 항상 같은 규격의 입력을 강제해야 합니다.

---

## 2주차: API 계약을 코드로 강제합니다

**핵심 질문:** 어떤 입력을 받고, 어떤 출력이 나가는지 코드로 강제할 수 있는가?

**구현 포인트:**

- `SummaryRequest` Pydantic 모델: `content_text`(필수), `title`, `output_format`
- `SummaryResponse` Pydantic 모델: `summary`, `key_points`, `meta`
- 계약을 만족하지 않는 입력 → 로직 실행 전 422 반환 (FastAPI가 자동 처리합니다)

**확인하셔야 할 사실:**

- `content_text` 없이 요청하면 422가 자동으로 나옵니다
- 응답 형태가 항상 동일합니다

**다음 주로 넘어가는 이유:**  
요약 결과는 다시 꺼내 볼 수 있어야 합니다. 따라서 저장이 필요합니다.

---

## 3주차: 지나가는 값을 기록 시스템으로 바꿉니다

**핵심 질문:** API의 입력과 출력을 저장하고 다시 꺼낼 수 있는가?

**구현 포인트:**

- `summaries` 테이블 생성 (DB 스키마 문서 참고)
- `POST /summarize` = 요약 생성 + DB 저장 + 응답 반환 (한 흐름으로 묶습니다)
- `GET /summaries` = 목록 조회
- `GET /summaries/{id}` = 단건 조회

**DB:** SQLite를 씁니다. Python에 내장되어 있어 별도 설치가 없고, `summary.db` 파일 하나로 전체 DB가 동작합니다.

**원칙:** DB는 AI 내부를 저장하는 것이 아니라, API의 입력과 출력(계약)을 그대로 저장합니다.

**다음 주로 넘어가는 이유:**  
라우터 함수에 입력 검증, 요약 생성, DB 저장, 조회 로직이 한꺼번에 들어갑니다. 수정이 어렵습니다.

---

## 4주차: 책임을 레이어로 나눕니다

**핵심 질문:** 한 함수에 모든 책임이 몰리지 않도록 구조를 어떻게 나누는가?

**구현 포인트:**

```
Controller  → HTTP만 담당 (request 수신, status code 결정, response 반환)
Service     → 업무 흐름 담당 (프롬프트 조립, LLM 호출, JSON 파싱, 검증 후 저장)
Repository  → DB 접근만 담당 (세션, 쿼리, 저장/조회)
```

**LangChain이 Service에 들어가는 이유:**  
LangChain은 LLM 호출 방식의 문제이고, HTTP나 DB 접근과는 관계가 없습니다. 업무 흐름(Service)에 속합니다.

**핵심 원칙:** JSON 파싱 후 Pydantic 검증을 통과한 것만 저장합니다.

**다음 주로 넘어가는 이유:**  
LLM 호출은 수 초가 걸리는 I/O입니다. 동기로 처리하면 그 시간 동안 다른 요청이 기다립니다.

---

## 5주차: 여러 URL을 한꺼번에 처리합니다

**핵심 질문:** 한 사용자가 여러 URL을 한꺼번에 제출했을 때, 동시에 처리할 수 있는가?

**왜 이 질문인가:**
실제 사용자는 텍스트를 복붙하지 않습니다. URL을 공유합니다. 그리고 한 번에 하나씩이 아니라 이번 주 읽을 링크 5개를 한꺼번에 정리하고 싶어합니다. 이 자연스러운 니즈가 비동기의 동기가 됩니다.

**구현 포인트:**

- `POST /summarize` → `Playwright`로 URL 크롤링(JS 렌더링 포함) 후 요약
- `POST /summarize/batch` → 최대 10개 URL을 `asyncio.gather`로 동시 처리
- `aiosqlite`로 DB 접근도 비동기화

**핵심 개념:**
비동기는 무조건 빠른 것이 아닙니다. I/O 대기(네트워크, DB)가 있을 때만 의미가 있습니다. URL 크롤링과 LLM 호출은 둘 다 대표적인 I/O 대기 작업입니다.

```
순차 처리 (동기):
URL1 → fetch → LLM 호출 3초 → 완료
URL2 ──────────────────────── fetch → LLM 호출 3초 → 완료  (3초 기다림)
URL3 ──────────────────────────────────────────────── fetch → LLM 호출 3초  (6초 기다림)
총 소요: ~15초

동시 처리 (asyncio.gather):
URL1 → fetch → LLM 호출 대기 중...
URL2 → fetch → LLM 호출 대기 중...  ← URL1이 기다리는 동안 시작
URL3 → fetch → LLM 호출 대기 중...  ← URL2가 기다리는 동안 시작
총 소요: ~3초
```

**최종 결론:**
사용자가 URL 5개를 보내면, 서버는 5개를 동시에 크롤링·요약하고 결과를 한꺼번에 돌려줍니다.

---

## 주차별 파일 구조 변화

나중에 코드를 나눌 때 참고하실 수 있도록, 주차별로 디렉터리 구조가 어떻게 바뀌는지 정리해 두었습니다.

### 1~2주차

```
app/
└── main.py
```

### 3주차

```
app/
├── main.py
├── models.py      # SQLAlchemy ORM 모델
├── schemas.py     # Pydantic 스키마
└── database.py    # DB 연결 설정
```

### 4주차

```
app/
├── main.py
├── controllers/
│   └── summary_controller.py
├── services/
│   └── summary_service.py
├── repositories/
│   └── summary_repository.py
├── domain/
│   └── summary.py
├── dto/
│   ├── summary_request_dto.py
│   └── summary_response_dto.py
└── database/
    └── connection.py
```

### 5주차

```
app/
├── main.py                 # async 라우터 전환
├── controllers/
│   └── summary_controller.py   # async def, 신규 엔드포인트 추가
├── services/
│   └── summary_service.py      # await llm.ainvoke(), fetch_url(), asyncio.gather
├── repositories/
│   └── summary_repository.py   # async 세션
├── domain/
│   └── summary.py              # url 컬럼 추가
├── dto/
│   ├── summary_request_dto.py  # SummaryURLRequest, BatchURLRequest 추가
│   └── summary_response_dto.py # BatchSummaryResponse 추가
└── database/
    └── connection.py           # aiosqlite 엔진 (SQLite async 드라이버)
```

