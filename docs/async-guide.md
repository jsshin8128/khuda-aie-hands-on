# async/await 가이드

> 이 가이드는 async/await를 처음 접하는 분들을 위해 작성되었습니다.
> "왜 필요한가?"부터 시작해, 핵심 개념을 하나씩 쌓아 가며 5주차 코드와 함께 연결해서 설명드려보겠습니다.

---

## 1. 왜 비동기가 필요한가

우리가 만든 서버를 떠올려 봅시다. 사용자가 URL을 보내면, 서버는 이런 일을 합니다.

```
URL 수신 → 페이지 크롤링 (네트워크 대기) → LLM 호출 (네트워크 대기) → DB 저장 → 응답 반환
```

이 흐름에서 **"네트워크 대기"** 구간이 두 곳 있습니다. 크롤링은 외부 서버에서 페이지를 받아올 때까지, LLM 호출은 OpenAI 서버가 응답할 때까지 기다립니다.

동기 코드에서는 이 기다리는 동안 서버 전체가 멈춥니다.

```
사용자1 요청 → [크롤링 1초] → [LLM 3초] → 응답
사용자2 요청 ──────────────────────────────[크롤링 1초] → [LLM 3초] → 응답
                                           ↑ 사용자1이 끝날 때까지 기다림
```

사용자1이 4초 걸리는 동안, 사용자2는 줄을 서서 기다립니다. 사용자가 많아질수록 대기는 길어집니다.

---

## 2. 이벤트 루프: 기다리는 동안 다른 일을 한다

비동기의 핵심 아이디어는 단순합니다. **기다리는 동안 다른 일을 한다.**

Python의 `asyncio`는 **이벤트 루프**라는 구조로 이를 구현합니다. 이벤트 루프는 싱글 스레드에서 동작하지만, 여러 작업을 번갈아 가며 처리합니다.

```
이벤트 루프:

사용자1 요청 시작 → 크롤링 요청 보냄 → [대기 중...] ─┐
                                                    │ 대기하는 동안
사용자2 요청 시작 → 크롤링 요청 보냄 → [대기 중...] ─┤ 이벤트 루프가
                                                    │ 다른 작업 처리
사용자3 요청 시작 → 크롤링 요청 보냄 → [대기 중...] ─┘

크롤링 응답 도착 → 사용자1 다음 단계 (LLM 호출) ...
```

핵심: CPU가 쉬는 시간(I/O 대기)을 낭비하지 않고 다른 작업에 씁니다.

> **언제 비동기가 의미 없나?** CPU를 계속 쓰는 연산(이미지 압축, 행렬 계산 등)은 "기다리는 시간"이 없어서 비동기로 해도 빨라지지 않습니다. 비동기는 **I/O 대기가 있을 때**만 효과가 있습니다.

---

## 3. async/await 문법

### `async def` - 비동기 함수 선언

```python
# 동기 함수
def get_page(url: str) -> str:
    response = requests.get(url)   # 여기서 블로킹 (전체가 멈춤)
    return response.text

# 비동기 함수
async def get_page(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)   # 여기서 대기하는 동안 다른 작업 가능
    return response.text
```

`async def`로 선언된 함수는 **코루틴**이 됩니다. 코루틴은 바로 실행되지 않고, `await`를 만나면 제어권을 이벤트 루프에 돌려줍니다.

### `await` - "여기서 기다리는 동안 다른 거 해도 돼"

```python
async def summarize_url(url: str):
    # await: "페이지 받아오는 동안 다른 요청 처리해도 돼"
    content = await fetch_page(url)

    # await: "LLM 응답 오는 동안 다른 요청 처리해도 돼"
    result = await llm.ainvoke({"content": content})

    return result
```

`await`는 `async def` 함수 안에서만 쓸 수 있습니다. `await` 없이 비동기 함수를 호출하면 코루틴 객체만 만들어지고 실행되지 않습니다.

---

## 4. asyncio.gather: 여러 작업을 동시에

`await`만으로는 순차 실행입니다.

```python
# 순차: 5 × 4초 = 20초
async def summarize_all(urls):
    results = []
    for url in urls:
        result = await summarize_url(url)   # 하나 끝나야 다음 시작
        results.append(result)
    return results
```

여러 작업을 동시에 시작하려면 `asyncio.gather`를 씁니다.

```python
import asyncio

# 동시: ~4초 (5개가 동시에 시작됨)
async def summarize_all(urls):
    tasks = [summarize_url(url) for url in urls]   # 코루틴 목록 생성
    results = await asyncio.gather(*tasks)          # 동시에 실행
    return results
```

`asyncio.gather`는 모든 작업이 완료될 때까지 기다린 뒤, 결과를 입력 순서대로 반환합니다.

### 일부 실패해도 나머지는 계속

기본적으로 `asyncio.gather`는 하나가 실패하면 전체가 실패합니다. `return_exceptions=True`를 쓰면 실패한 것은 예외 객체로, 성공한 것은 결과로 받을 수 있습니다.

```python
results = await asyncio.gather(*tasks, return_exceptions=True)

successes = []
failures = []
for url, result in zip(urls, results):
    if isinstance(result, Exception):
        failures.append({"url": url, "error": str(result)})
    else:
        successes.append(result)
```

이게 `POST /summarize/batch`의 `results`와 `failed` 구조가 나오는 이유입니다.

---

## 5. Playwright: JS 렌더링까지 처리하는 async 크롤러

`requests`나 `httpx`는 정적 HTML만 받아옵니다. React·Vue 같은 SPA(Single Page Application)는 JavaScript가 실행된 후에 본문이 채워지기 때문에, 정적 크롤러로는 네비게이션 메뉴만 가져오는 경우가 많습니다.

```python
# httpx로 SPA를 크롤링하면 이렇게 됩니다
async def fetch(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    # JS 실행 전 껍데기만 옴 → 본문 없음
    return response.text
```

`Playwright`는 실제 Chromium 브라우저를 실행해 JS 렌더링까지 완료한 뒤 HTML을 가져옵니다.

```python
from playwright.async_api import async_playwright

async def fetch(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")  # JS 렌더링 완료까지 대기
        html = await page.content()
        await browser.close()
    return html
```

`wait_until="networkidle"` 은 네트워크 요청이 잠잠해질 때까지 기다린다는 의미입니다. 이 시점이면 SPA의 본문 로딩도 완료됩니다.

| | requests | httpx | Playwright |
|---|---|---|---|
| 동기 | O | O | X |
| async | X | O | O |
| JS 렌더링 | X | X | O |
| SPA 지원 | X | X | O |

---

## 6. 이 프로젝트에서의 적용

5주차에서 달라지는 부분을 레이어별로 정리합니다.

### Database (database.py)

```python
# 4주차: 동기 엔진
from sqlalchemy import create_engine
engine = create_engine("sqlite:///./summary.db", ...)
SessionLocal = sessionmaker(bind=engine)

# 5주차: 비동기 엔진
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
engine = create_async_engine("sqlite+aiosqlite:///./summary.db")
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession)
```

URL 스킴이 `sqlite://`에서 `sqlite+aiosqlite://`로 바뀝니다. `aiosqlite`가 SQLite를 비동기로 다룰 수 있게 해 주는 드라이버입니다.

### Repository (summary_repository.py)

```python
# 4주차
def save(db: Session, row: Summary) -> Summary:
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

# 5주차
async def save(db: AsyncSession, row: Summary) -> Summary:
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row
```

### Service (summary_service.py)

```python
# 4주차
result = chain.invoke({"title": ..., "content_text": ...})

# 5주차: ainvoke + Playwright 크롤링
content_text, title = await fetch_url(url)   # Playwright로 JS 렌더링 후 본문 추출
result = await chain.ainvoke({"title": title or "", "content_text": content_text})
```

LangChain의 `ainvoke`는 `invoke`의 async 버전입니다. `fetch_url`은 Playwright를 사용하기 때문에 SPA 사이트도 본문을 정확히 가져올 수 있습니다.

### 배치 처리 (핵심 패턴)

```python
async def create_batch(request: BatchURLRequest, db: AsyncSession):
    async def process_one(url: str):
        content = await fetch_url(url)          # 크롤링
        return await create_from_content(content, url, db)  # 요약 + 저장

    tasks = [process_one(url) for url in request.urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successes, failures = [], []
    for url, result in zip(request.urls, results):
        if isinstance(result, Exception):
            failures.append({"url": url, "error": str(result)})
        else:
            successes.append(result)

    return BatchSummaryResponse(results=successes, failed=failures)
```

---

## 정리

| 개념 | 한 줄 설명 | 이 프로젝트에서 |
|---|---|---|
| `async def` | 비동기 함수 선언 | 라우터, 서비스, 리포지토리 모두 `async def`로 전환 |
| `await` | 여기서 기다리는 동안 다른 작업 허용 | `await llm.ainvoke()`, `await db.commit()` 등 |
| `asyncio.gather` | 여러 코루틴을 동시에 실행 | 배치 요청에서 URL 5개를 동시에 처리 |
| `Playwright` | JS 렌더링 async 크롤러 | URL 크롤링 (SPA 포함) |
| `aiosqlite` | SQLite async 드라이버 | DB 접근 비동기화 |

비동기는 코드를 복잡하게 만들기도 합니다. 하지만 LLM 호출처럼 I/O 대기가 긴 작업이 여러 개 동시에 일어날 때, 그 효과는 명확합니다. URL 5개를 순차 처리하면 20초, 동시 처리하면 4초입니다.
