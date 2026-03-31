# async/await 가이드

> 이 가이드는 async/await를 처음 접하는 분들을 위해 작성되었습니다.
> "왜 필요한가?"부터 시작해, 핵심 개념을 하나씩 쌓아 가며 5주차 코드와 연결합니다.

---

## 0. 이 프로젝트에서 비동기가 왜 필요한가

우리가 만든 API 서버는 기술 블로그 URL를 받아서 요약이라는 task를 수행하죠? 그 처리 흐름은 아래와 같습니다.

```
URL 수신 → 크롤링 (크롤링 대상 웹사이트의 서버에 대한 응답 대기) → LLM 호출 (OpenAI 서버에 대한 응답 대기) → DB 저장 → 최종 응답 반환
```

이 흐름에서 **두 구간이 I/O 대기**입니다.

- **크롤링**: 외부 서버에서 HTML을 받아올 때까지 대기. 수백ms ~ 수초
- **LLM 호출**: OpenAI 서버가 응답할 때까지 대기. 수초 ~ 수십초

동기 코드에서는 이 기다리는 동안 서버 전체가 멈춥니다.

```
사용자1 → [크롤링 1s] → [LLM 5s] → 응답       (6초)
사용자2 →                           [크롤링 1s] → [LLM 5s] → 응답   (12초, 6초 기다림)
사용자3 →                                                     [크롤링 1s] → [LLM 5s] → 응답
```

배치 요청은 더 심각합니다. URL 5개를 순차 처리하면 5 × 6초 = **30초**. 그 30초 동안 다른 요청은 모두 줄을 서서 기다립니다.

비동기로 바꾸면 크롤링과 LLM 호출이 진행되는 동안 다른 요청을 처리할 수 있습니다. URL 5개 배치도 가장 오래 걸리는 것 하나 기준인 **~6초**로 줄어듭니다.

이게 가능한 이유가 뒤에 나옵니다.

---

## 1. 프로세스와 스레드

프로그램을 실행하면 OS가 **프로세스**를 만듭니다. 프로세스 안에 **스레드**가 있고, 스레드가 코드를 한 줄씩 실행하는 주체입니다.

---

## 2. 블락킹 I/O 문제

스레드가 이 코드를 만납니다.

```python
response = requests.get("https://example.com")
```

스레드는 OS에게 "이 주소로 HTTP 요청 보내줘" 하고 시스템콜을 합니다. OS는 **소켓**을 만들고, 그 소켓으로 패킷을 보냅니다. 근데 응답이 올 때까지 시간이 걸립니다.

그 동안 스레드는 **그냥 멈춥니다.** CPU는 놀고 있습니다.

### 소켓이란?

소켓은 OS가 관리하는 **통신 창구**입니다. 네트워크 연결 하나마다 소켓 하나가 만들어집니다.

```
클라이언트 ──[소켓]──── 인터넷 ──── 서버
```

스레드는 소켓에 데이터를 쓰거나 읽는 방식으로 통신합니다. `requests.get()`을 호출하면 내부에서 이런 일이 일어납니다.

```
1. OS에게 소켓 만들어달라고 요청
2. 그 소켓으로 HTTP 요청 패킷 전송
3. 소켓에 응답이 올 때까지 스레드가 대기 (블락킹)
4. 응답 도착 → 스레드 재개 → response 반환
```

소켓은 나중에 epoll에서 다시 등장합니다. "소켓을 등록한다"는 건 "이 통신 창구를 감시해달라"는 뜻입니다.

---

## 3. 블락킹 / 논블락킹 / 동기 / 비동기

용어를 짚고 넘어갑니다. 두 가지 축입니다.

**블락킹 vs 논블락킹** — 스레드가 멈추냐 안 멈추냐

- 블락킹: 응답 올 때까지 스레드가 멈춤
- 논블락킹: 일단 바로 리턴. 스레드는 계속 돔

**동기 vs 비동기** — 완료를 내가 확인하냐, 시스템이 알려주냐

- 동기: 내가 주기적으로 "됐어?" 하고 확인
- 비동기: 시스템이 완료되면 "됐어!" 하고 알려줌


|         | 블락킹                         | 논블락킹                 |
| ------- | --------------------------- | -------------------- |
| **동기**  | `requests.get()` ← 지금 우리 코드 | -                    |
| **비동기** | -                           | `asyncio` ← 앞으로 배울 것 |


`requests.get()`은 **블락킹 + 동기**입니다. 응답 올 때까지 스레드가 멈추고, 그 자리에서 바로 결과를 받습니다.

`asyncio`는 **논블락킹 + 비동기**입니다. 스레드는 안 멈추고, 완료되면 이벤트 루프가 알려줍니다. 이게 어떻게 동작하는지가 뒤에 나옵니다.

---

## 4. 스레드 100개 방식의 한계

URL이 100개면 어떻게 할까요? 가장 단순한 방법은 스레드 100개를 만드는 겁니다.

```python
for url in urls:
    thread = Thread(target=fetch, args=(url,))
    thread.start()
```

문제가 있습니다.

- 스레드 하나가 메모리를 수 MB씩 씁니다. 1000개면 수 GB
- OS가 스레드들 사이를 왔다갔다하는 **컨텍스트 스위칭** 비용이 큽니다

스레드를 1개만 쓰면서 100개 요청을 처리할 수 없을까요?

---

## 5. 이벤트 루프의 기반이 되는 epoll

소켓 감시는 항상 OS가 합니다. 차이는 **한 번에 몇 개를 맡기냐**입니다.

블락킹 방식에서는 스레드가 소켓 하나에 `recv(소켓1)`을 호출하면 거기서 멈춥니다. 응답이 올 때까지 소켓2는 쳐다볼 수가 없습니다. 결국 소켓 하나씩 순서대로 처리할 수밖에 없습니다.

```
소켓1 요청 → [기다림] → 응답 → 소켓2 요청 → [기다림] → 응답 → ...
```

OS에는 **epoll**이라는 시스템콜이 있습니다.

> "소켓 여러 개를 등록해놓을 테니, 그 중 하나라도 응답 오면 나 깨워줘"

아무것도 안 오면 스레드를 재웁니다. 응답이 오면 OS가 깨워줍니다. 스레드 1개로 소켓 수백 개를 동시에 감시할 수 있습니다.

덕분에 요청을 한꺼번에 날릴 수 있습니다. 기다리는 시간이 겹치니까 전체 시간이 줄어듭니다.

```
소켓1 요청 보냄 ─┐
소켓2 요청 보냄 ─┤ 동시에 날아감
소켓3 요청 보냄 ─┘
       ↓
epoll이 셋 다 감시 (OS)
       ↓
먼저 오는 순서대로 처리
```

---

## 6. 이벤트 루프

이벤트 루프는 Python(asyncio)으로 구현한 while 루프입니다. 

OS의 epoll을 호출해서 "완료된 소켓 있어?"를 물어보는 방식으로 동작합니다.

```
while True:
    완료된 소켓 있나? → 없으면 잠
    OS가 완료 신호와 함께 깨움
    완료된 작업 재개
    다시 확인
```

그런데 여기서 문제가 생깁니다.

이벤트 루프가 url1 작업을 재개하려면, url1이 **어디까지 실행됐는지** 기억해야 합니다. 

그런데 url1을 처리하는 코드, 즉 `fetch(url)`같은 함수는 중간에 멈출 수 없습니다. 호출하면 끝까지 실행됩니다.

```python
def fetch(url):
    response = requests.get(url)  # 여기서 기다리는 동안 멈출 방법이 없음
    return response.text          # 응답 오기 전까지 이 줄에 도달 불가

# 이벤트 루프 입장에서는...
fetch(url1)  # 얘가 끝날 때까지 다음 줄로 못 넘어감
fetch(url2)  # url1 끝나야 시작
```

중간에 멈추고, 나중에 그 지점부터 다시 시작할 수 있는 무언가가 필요합니다.

---

## 7. 코루틴과 async/await

**코루틴**은 실행 중간에 상태를 저장하고 멈출 수 있는 함수입니다. `await`가 그 지점입니다.

```python
async def fetch(url):
    result = await get(url)  # 여기서 상태 저장하고 멈춤
    return result            # 나중에 여기서 재개
```

`await`를 만나는 순간 이런 일이 일어납니다.

**1단계 — 소켓 생성 및 요청 전송**
OS에 소켓을 만들어달라고 요청하고, 그 소켓으로 HTTP 요청 패킷을 전송합니다.

**2단계 — 소켓을 이벤트 루프에 등록**
"이 소켓에 응답 오면 나 재개해줘"라고 이벤트 루프에 등록합니다. 이벤트 루프는 소켓→코루틴 매핑 테이블에 기록합니다.

```
# url1 await 후
{ 소켓1: fetch(url1) }

# url2 await 후
{ 소켓1: fetch(url1), 소켓2: fetch(url2) }

# url3 await 후
{ 소켓1: fetch(url1), 소켓2: fetch(url2), 소켓3: fetch(url3) }
```

**3단계 — 실행 상태 저장 후 제어권 반납**
현재 지역변수, 실행 위치 등 상태를 저장하고 멈춥니다. 이벤트 루프에 제어권을 돌려줍니다.

**4단계 — 이벤트 루프가 다음 코루틴 실행**
이벤트 루프는 대기 중인 다음 코루틴을 실행합니다. url2도 `await`까지 달리고 1~3단계 반복. url3도 마찬가지.

**5단계 — epoll에 감시 위임 후 대기**
더 이상 실행할 코루틴이 없으면, 이벤트 루프는 등록된 소켓들을 epoll에 넘기고 잡니다.

```
이벤트 루프 → epoll: "소켓1, 소켓2, 소켓3 감시해줘. 뭐라도 오면 깨워줘"
```

**6단계 — 응답 도착 → 재개**
응답이 오면 OS가 이벤트 루프를 깨웁니다. 이벤트 루프는 매핑 테이블을 확인해서 해당 소켓을 기다리던 코루틴을 꺼내고, `await` 다음 줄부터 재개합니다.

```
# OS: "소켓2 응답 왔어"
# 이벤트 루프: 매핑 테이블에서 소켓2 조회 → fetch(url2) 꺼냄 → await 다음 줄부터 재개
{ 소켓1: fetch(url1), 소켓3: fetch(url3) }  # 소켓2는 완료됐으니 제거
```

```python
# 동기 함수 → 블락킹
def get_page(url: str) -> str:
    response = requests.get(url)   # 여기서 스레드 전체가 멈춤
    return response.text

# 비동기 함수 → 논블락킹
async def get_page(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)   # 여기서 상태 저장 후 비켜남
    return response.text
```

> `await`는 `async def` 함수 안에서만 쓸 수 있습니다. `await` 없이 비동기 함수를 호출하면 코루틴 객체만 만들어지고 실행되지 않습니다.

---

## 8. asyncio.gather: 여러 작업을 동시에

`await`만 쓰면 여전히 순차 실행입니다.

```python
# 순차: 5 × 4초 = 20초
async def summarize_all(urls):
    results = []
    for url in urls:
        result = await summarize_url(url)   # 하나 끝나야 다음 시작
        results.append(result)
    return results
```

`asyncio.gather`는 코루틴 N개를 이벤트 루프에 한꺼번에 등록합니다.

```python
# 동시: ~4초 (N개가 동시에 시작됨)
async def summarize_all(urls):
    tasks = [summarize_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

url1 기다리는 동안 url2, url3도 이미 요청이 나가 있습니다. 완료되는 순서대로 재개되고, 결과는 입력 순서대로 반환됩니다.

**구조**: 스레드 1개 + 이벤트 루프 1개 + 코루틴 N개

### 일부 실패해도 나머지는 계속

기본적으로 하나가 실패하면 전체가 실패합니다. `return_exceptions=True`를 쓰면 실패한 것은 예외 객체로, 성공한 것은 결과로 받을 수 있습니다.

```python
results = await asyncio.gather(*tasks, return_exceptions=True)

successes, failures = [], []
for url, result in zip(urls, results):
    if isinstance(result, Exception):
        failures.append({"url": url, "error": str(result)})
    else:
        successes.append(result)
```

이게 `POST /summarize/batch`의 `results`와 `failed` 구조가 나오는 이유입니다.

---

## 9. Playwright: JS 렌더링까지 처리하는 async 크롤러

`requests`나 `httpx`는 정적 HTML만 받아옵니다. React·Vue 같은 SPA(Single Page Application)는 JavaScript가 실행된 후에 본문이 채워지기 때문에, 정적 크롤러로는 내용을 제대로 가져올 수 없습니다.

```python
# httpx로 SPA를 크롤링하면 이렇게 됩니다
async def fetch(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    # JS 실행 전 껍데기만 옴 → 본문 없음
    return response.text
```

`Playwright`는 실제 Chromium 브라우저를 실행해 JS 렌더링까지 완료한 뒤 HTML을 가져옵니다. (그래서 시간이 좀 걸려요)

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


|        | requests | httpx | Playwright |
| ------ | -------- | ----- | ---------- |
| 동기     | O        | O     | X          |
| async  | X        | O     | O          |
| JS 렌더링 | X        | X     | O          |
| SPA 지원 | X        | X     | O          |


---

## 10. 우리 프로젝트에 적용해보자

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

URL 스킴이 `sqlite://`에서 `sqlite+aiosqlite://`로 바뀝니다. `aiosqlite`가 SQLite를 비동기로 다룰 수 있게 해주는 드라이버입니다.

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
content_text, title = await fetch_url(url)
result = await chain.ainvoke({"title": title or "", "content_text": content_text})
```

LangChain의 `ainvoke`는 `invoke`의 async 버전입니다.

### 배치 처리 (핵심)

```python
async def create_batch(request: BatchURLRequest, db: AsyncSession):
    async def process_one(url: str):
        content = await fetch_url(url)
        return await create_from_content(content, url, db)

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


| 개념               | 한 줄 설명                  | 이 프로젝트에서                                     |
| ---------------- | ----------------------- | -------------------------------------------- |
| `async def`      | 코루틴 선언. 중간에 멈출 수 있는 함수  | 라우터, 서비스, 리포지토리 전부 전환                        |
| `await`          | 여기서 비켜남. 이벤트 루프에 제어권 반납 | `await llm.ainvoke()`, `await db.commit()` 등 |
| `asyncio.gather` | 코루틴 N개를 이벤트 루프에 한꺼번에 등록 | 배치 요청에서 URL N개를 동시에 처리                       |
| `Playwright`     | JS 렌더링 async 크롤러        | URL 크롤링 (SPA 포함)                             |
| `aiosqlite`      | SQLite async 드라이버       | DB 접근 비동기화                                   |


핵심은 **"멈추는 주체"를 스레드에서 코루틴으로 바꿨다는 것!** 기억해주세요~