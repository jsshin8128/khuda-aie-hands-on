# DB 스키마

> 이 문서는 3주차부터 적용됩니다. 1~2주차에는 DB를 사용하지 않습니다.

> **DB(데이터베이스)란?** 데이터를 구조적으로 저장하고 다시 꺼낼 수 있도록 해 주는 저장소입니다. 서버가 꺼져도 데이터가 사라지지 않도록 하는 역할을 합니다.

**영속성(persistence)** 이란, 프로그램이나 서버를 종료해도 데이터가 남아 있다가 나중에 다시 꺼낼 수 있는 성질을 말합니다. 메모리에만 두면 프로세스가 끝나는 순간 사라지지만, DB에 저장해 두면 `summary.db` 파일에 그대로 남아 있어서 서버를 다시 켜도 이전에 저장한 요약을 조회할 수 있습니다. 3주차에서 DB를 쓰는 이유가 바로 이 영속성을 얻기 위해서입니다.

---

## 설계 원칙

DB는 AI 내부 상태를 저장하는 것이 아닙니다. **API의 입력과 출력, 즉 계약을 그대로 저장합니다.**

이유는 다음과 같습니다. DB에 저장된 레코드를 꺼냈을 때, 그 시점의 요청과 응답이 완전히 재현되어야 합니다. "이 글로 요약을 요청했고, 이런 결과가 나왔다"가 하나의 레코드에 담겨야 합니다.

---

## DB 선택: SQLite

SQLite는 Python에 기본 내장되어 있습니다. 별도 설치 없이 파일 하나(`summary.db`)로 DB 전체가 동작합니다. 서버를 처음 실행하면 프로젝트 폴더에 `summary.db` 파일이 자동으로 생성됩니다.

> 나중에 MySQL 같은 다른 DB로 교체하더라도, SQLAlchemy를 쓰면 연결 주소 한 줄만 바꾸면 됩니다.

---

## 테이블: `summaries`

### 1. 테이블 설명

> **테이블이란?** DB 안에서 데이터를 담는 구조입니다. 엑셀 시트처럼 행(row)과 열(column)로 이루어져 있습니다. 하나의 요약 결과 = 하나의 행입니다.

요약 API의 요청(입력)과 응답(출력)을 한 레코드로 저장합니다. "이 글로 요약을 요청했고, 이런 결과가 나왔다"가 한 행에 담깁니다.

### 2. 테이블 이름

`summaries`

### 3. 컬럼 명세

> **컬럼(Column)이란?** 테이블의 열입니다. Name, Type, Constraint, Description, Example 순서로 정리합니다.


| Name           | Type    | Constraint                          | Description                                                            | Example                                                                                                             |
| -------------- | ------- | ----------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| id             | INTEGER | PRIMARY KEY AUTOINCREMENT           | 레코드 고유 번호. 저장 시 자동 증가. `GET /summaries/{id}` 의 id.                     | 1                                                                                                                   |
| title          | TEXT    | NONE                                | 요청의 title. 선택 필드라 비울 수 있음.                                             | FastAPI 완벽 가이드                                                                                                      |
| content_text   | TEXT    | NOT NULL                            | 요약 요청 본문. 필수.                                                          | FastAPI는 Python의 타입 힌트를 활용해 빠르고 안전한 API를 작성할 수 있는 프레임워크입니다.                                                         |
| output_json    | TEXT    | NOT NULL                            | 요약 결과(SummaryResponse) 전체를 JSON 문자열로 저장. Python에서 json.dumps/loads 사용. | {"summary":"...","key_points":["..."],"meta":{"prompt_version":"v1.0","generated_at":"2024-01-15T10:30:00Z"}} |
| prompt_version | TEXT    | NOT NULL                            | 요약에 사용한 프롬프트 버전. 나중에 구분용.                                              | v1.0                                                                                                                |
| created_at     | TEXT    | NOT NULL, DEFAULT (datetime('now')) | 저장 시각. 목록 최신순 정렬 기준.                                                   | 2024-01-15 10:30:00                                                                                                 |


### 4. 인덱스 명세

> **인덱스란?** 특정 컬럼 기준으로 조회를 빠르게 하기 위한 색인입니다. 데이터가 많아질 때만 추가해도 됩니다.


| Name                     | Table     | Column          | Type  | Description                |
| ------------------------ | --------- | --------------- | ----- | -------------------------- |
| idx_summaries_created_at | summaries | created_at DESC | BTREE | 목록 최신순 정렬 조회 시 사용. (선택 사항) |


### 5. Example Row

한 행이 어떤 값들을 갖는지 예시입니다.


| id  | title          | content_text               | output_json                          | prompt_version | created_at          |
| --- | -------------- | -------------------------- | ------------------------------------ | -------------- | ------------------- |
| 1   | FastAPI 완벽 가이드 | FastAPI는 Python의 타입 힌트를... | {"summary":"...","key_points":["..."],"meta":{...}} | v1.0           | 2024-01-15 10:30:00 |


---

**제약 조건이란?** 컬럼에 "비우면 안 된다", "자동으로 채워라" 같은 규칙을 거는 것입니다. 위 표에 나온 것만 정리합니다.


| 제약                | 의미                                               |
| ----------------- | ------------------------------------------------ |
| **NOT NULL**      | 반드시 값을 넣어야 함. 비우면 저장 거부.                         |
| **NONE**          | 제약 없음. 비워 두면 NULL로 저장됨.                          |
| **PRIMARY KEY**   | 행을 유일하게 구분하는 컬럼. 중복·비우기 불가.                      |
| **AUTOINCREMENT** | 값을 안 넣어도 1, 2, 3… 자동 증가. PRIMARY KEY와 함께 고유 번호용. |
| **DEFAULT**       | 값을 안 넣으면 지정한 기본값 사용. `created_at`은 저장 시각 자동 입력.  |


---

### DDL (테이블 생성 명령문)

실제 테이블은 아래 SQL로 생성합니다. (앱 기동 시 SQLAlchemy가 자동 실행합니다.)

```sql
CREATE TABLE summaries (
    id             INTEGER  PRIMARY KEY AUTOINCREMENT,
    title          TEXT,
    content_text   TEXT     NOT NULL,
    output_json    TEXT     NOT NULL,
    prompt_version TEXT     NOT NULL,
    created_at     TEXT     NOT NULL DEFAULT (datetime('now'))
);
```

> SQLite에는 JSON 전용 타입이 없어서 `output_json`은 TEXT로 저장하고, Python에서 `json.dumps()` / `json.loads()` 로 다룹니다.

---

## 저장 흐름

`POST /summarize` 요청이 들어왔을 때 DB 저장까지의 흐름입니다.

```
요청 수신
    ↓
SummaryRequest 스키마 검증 → 실패 시 422 반환 (여기서 끝)
    ↓
LLM 호출 → 결과 텍스트 반환
    ↓
결과를 SummaryResponse 스키마로 파싱·검증 → 실패 시 저장 안 함
    ↓
검증 통과한 경우에만 summaries 테이블에 저장
    ↓
저장된 레코드의 id 포함해서 응답 반환
```

DB에는 항상 유효한 계약만 들어가도록 보장합니다.

---

## 조회 쿼리

> **SQL이란?** DB에 데이터를 넣고 꺼낼 때 쓰는 언어입니다. `SELECT` 는 조회, `FROM` 은 어떤 테이블에서, `WHERE` 는 어떤 조건으로 꺼낼지를 의미합니다.

### 목록 조회 (`GET /summaries`)

```sql
SELECT id, title, created_at
FROM summaries
ORDER BY created_at DESC;  -- 최신순 정렬
```

### 단건 조회 (`GET /summaries/{id}`)

```sql
SELECT id, title, content_text, output_json, prompt_version, created_at
FROM summaries
WHERE id = :id;  -- :id 자리에 실제 숫자가 들어갑니다
```

---

## 인덱스 생성 (선택)

위 **인덱스 명세**의 `idx_summaries_created_at`를 쓰려면 아래를 실행합니다. 데이터가 적을 때는 없어도 되고, 목록 조회가 느려질 때 추가하면 됩니다.

```sql
CREATE INDEX idx_summaries_created_at ON summaries (created_at DESC);
```

---

## 인덱스 체감 실습

인덱스가 있으면 **같은 쿼리**라도 더 빨리 실행될 수 있습니다. 데이터가 적을 때는 차이가 거의 없고, 행이 많아질수록 체감됩니다.

1. **데이터가 충분히 있어야** 차이가 난다. 아래 스크립트가 부족하면 더미 행을 자동으로 넣어 준다.
2. **인덱스 없이** `SELECT ... ORDER BY created_at DESC` 를 실행해 걸린 시간을 본다.
3. **인덱스를 만든 뒤** 같은 쿼리를 다시 실행해 걸린 시간을 본다.

한 번에 실행하려면 프로젝트 루트에서:

```bash
python3 scripts/benchmark_index.py
```

---

## DB 초기화

데이터만 지우고 **테이블 구조는 그대로 두고** 싶을 때 사용합니다. (테이블을 없애고 처음부터 만들려면 `summary.db` 파일을 삭제한 뒤 서버를 다시 실행하면 됩니다.)

**데이터만 비우기**

```bash
sqlite3 summary.db "DELETE FROM summaries;"
```

- `summaries` 테이블의 모든 행만 삭제됩니다. 테이블과 컬럼은 그대로 있습니다.
- 다음에 `POST /summarize`로 저장하면 id는 **기존 최대값 다음 번호**부터 이어서 붙습니다.

**데이터 비우고 id도 1부터 다시 시작하게 하려면**

먼저 데이터만 비운 뒤, **한 번에 한 문장씩** 실행하세요.

```bash
sqlite3 summary.db "DELETE FROM summaries;"
sqlite3 summary.db "DELETE FROM sqlite_sequence WHERE name='summaries';"
```

- SQLite는 자동 증가 id 값을 `sqlite_sequence` 테이블에 저장합니다. 두 번째 명령으로 그 값을 지우면 다음 INSERT 시 id가 1부터 다시 시작합니다.
- **두 번째 명령에서 `no such table: sqlite_sequence` 가 나와도 괜찮습니다.** 아직 한 번도 `summaries`에 INSERT한 적이 없으면 이 테이블이 없고, 그 경우엔 다음에 저장할 때 id가 1부터 붙으므로 두 번째 명령은 실행하지 않았어도 됩니다.

> 프로젝트 루트에서 실행하세요. `summary.db`가 없는 경우에는 서버를 한 번 실행해 테이블이 생성된 뒤에 위 명령을 사용하면 됩니다.

---

## 4주차: SQLAlchemy ORM 모델

> **ORM(Object-Relational Mapping)이란?** SQL을 직접 쓰는 대신, Python 클래스로 DB를 다룰 수 있게 해 주는 도구입니다. `SELECT * FROM summaries` 대신 `session.query(Summary).all()` 처럼 쓸 수 있습니다.

4주차에서 레이어를 나눌 때 아래 모델을 사용합니다. 위의 DDL 테이블과 컬럼이 1:1로 대응합니다.

```python
from sqlalchemy import Column, Integer, Text, func
from database import Base

class Summary(Base):
    __tablename__ = "summaries"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    title          = Column(Text, nullable=True)
    content_text   = Column(Text, nullable=False)
    output_json    = Column(Text, nullable=False)   # json.dumps()로 저장
    prompt_version = Column(Text, nullable=False)
    created_at     = Column(Text, server_default=func.now(), nullable=False)
```

DB 연결 설정은 아래와 같습니다.

```python
# database.py (3주차에서 추가)
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./summary.db"   # 프로젝트 루트에 summary.db 파일 생성

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

> `check_same_thread=False` 는 SQLite 전용 설정입니다. SQLite는 기본적으로 같은 스레드에서만 연결을 쓰도록 제한하는데, FastAPI는 요청마다 다른 스레드를 쓸 수 있어서 이 제한을 풀어 주어야 합니다.

