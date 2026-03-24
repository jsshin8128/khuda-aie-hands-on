# LangChain 가이드

> 이 가이드는 LangChain을 처음 접하는 분들을 위해 작성되었습니다.  
> "왜 필요한가?"부터 시작해, 핵심 개념을 하나씩 쌓아 가며 4주차 코드와 함께 연결해서 설명드려보겠습니다.

---

## 1. 왜 LangChain이 필요한가

우리가 지금까지 만든 서비스를 떠올려 봅시다. FastAPI로 요청을 받고, Pydantic으로 입력을 검증하고, SQLAlchemy로 결과를 저장합니다. 각 단계마다 필요한 도구를 사용했고, 덕분에 안정적인 코드를 작성할 수 있었습니다.

만약, LLM을 직접 호출해 본 적이 있다면, 여러분은 이런 코드를 써야 한다는 걸 알 것입니다.

```python
from openai import OpenAI # AI 모델을 불러와서,

client = OpenAI() # 모델 객체를 선언하고,
response = client.chat.completions.create( # 요청 파라미터를 전달해서 create 메서드로 모델 호출, 받은 응답을 response에 할당
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "블로그 글을 읽고 JSON으로 요약하세요..."},
        {"role": "user", "content": f"제목: {title}\n\n내용:\n{content_text}"},
    ],
    temperature=0,
)
result_text = response.choices[0].message.content # response의 content 필드를 result_text에 할당
```

이 코드 자체는 잘 동작합니다. 하지만 여기서 질문을 하나 던져 봅시다.

**나중에 OpenAI를 Claude나 Gemini로 바꿔야 한다면 어떻게 될까요?**

`client.chat.completions.create()` 대신 다른 SDK의 문법을 써야 합니다. `messages` 구조도 조금씩 다릅니다. 결과를 꺼내는 방법도 바뀝니다. 즉, 모델을 바꾸는 결정 하나가 코드 전반을 건드리게 됩니다.

LangChain은 바로 이 문제를 해결하기 위해 등장했습니다.

---

## 2. 첫 번째 특징: 추상화

LangChain의 첫 번째 아이디어는 **추상화**입니다. LLM 호출의 복잡한 세부 사항을 감싸고, 개발자에게는 단순한 인터페이스만 노출합니다.

LangChain에서 GPT-4o-mini를 부르는 코드는 이렇습니다.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
response = llm.invoke("안녕하세요")
print(response.content)  # "안녕하세요! 무엇을 도와드릴까요?"
```

그리고 이 코드를 Claude로 바꾸려면 딱 한 줄만 바꾸면 됩니다.

```python
from langchain_anthropic import ChatAnthropic  # 이 줄만 바뀝니다

llm = ChatAnthropic(model="claude-3-5-sonnet-latest", temperature=0)
response = llm.invoke("안녕하세요")  # 나머지는 그대로
print(response.content)
```

`llm.invoke()`의 인터페이스가 동일하기 때문에, 이 `llm` 객체를 사용하는 아래 코드들은 **전혀 수정할 필요가 없습니다**. 이게 추상화의 힘입니다.

추상화는 단순히 코드를 줄여 주는 게 아닙니다. "어떤 모델을 쓸 것인가"라는 결정을 코드의 나머지 부분과 분리합니다. 덕분에 개발자는 세부 구현 대신 서비스 로직에 집중할 수 있습니다.

---

## 3. 두 번째 특징: 표준화

추상화가 "LLM 호출 방식"을 통일했다면, **표준화**는 더 나아가 LangChain이 다루는 모든 데이터를 통일된 형식으로 만드는 것입니다.

### `ChatModel`과 메시지

LangChain에서 모든 LLM은 `ChatModel`이라는 공통 인터페이스를 따릅니다. 그리고 이 모델에 전달하는 입력은 **메시지 객체**로 표준화됩니다.

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
messages = [
    SystemMessage(content="당신은 친절한 어시스턴트입니다."),
    HumanMessage(content="파이썬의 장점을 알려주세요."),
]
response = llm.invoke(messages)
print(response.content)
```

`SystemMessage`, `HumanMessage`, `AIMessage`라는 표준화된 객체 덕분에, OpenAI의 `{"role": "system", "content": "..."}` 같은 딕셔너리 구조를 직접 다루지 않아도 됩니다.

### 도큐먼트

텍스트 데이터도 표준화됩니다. LangChain은 파일, 웹 페이지, DB 등 다양한 소스에서 가져온 텍스트를 `Document` 객체로 통일합니다.

```python
from langchain_core.documents import Document

doc = Document(
    page_content="FastAPI는 Python 기반의 웹 프레임워크입니다.",
    metadata={"source": "tutorial.txt", "page": 1}
)
```

소스가 어디든 코드는 동일한 `Document` 객체를 다룹니다. 데이터 소스를 바꿔도 이후 처리 로직은 그대로입니다.

---

## 4. 세 번째 특징: 체이닝

추상화와 표준화가 "레고 블록을 만드는 것"이라면, **체이닝**은 "그 블록들을 연결하는 방법"입니다.

LangChain의 컴포넌트들은 모두 동일한 규칙을 따릅니다. **입력을 받아 출력을 반환한다.** 그리고 이 규칙 덕분에 `|` 연산자로 컴포넌트들을 파이프처럼 이어 붙일 수 있습니다.

```python
chain = prompt | llm | parser

result = chain.invoke({"title": "FastAPI 소개", "content_text": "..."})
```

이 한 줄이 실제로 하는 일은 이렇습니다.

```
1. prompt.invoke({"title": ..., "content_text": ...})
       → 메시지 배열 생성
2. llm.invoke(메시지 배열)
       → AI 응답 (AIMessage 객체)
3. parser.invoke(AIMessage 객체)
       → 파싱된 최종 결과
```

각 단계의 출력이 다음 단계의 입력이 됩니다. 코드가 흐름을 그대로 표현하기 때문에, 읽는 것만으로 "무슨 일이 일어나는지" 파악됩니다.

이 체이닝 방식을 LCEL(LangChain Expression Language)이라고 부릅니다.

---

## 5. 핵심 컴포넌트: 프롬프트 템플릿

체인을 이해했다면, 이제 컴포넌트를 하나씩 살펴봅시다. 첫 번째는 **프롬프트 템플릿**입니다.

프롬프트는 LLM에게 전달하는 지시문입니다. 그런데 실제 서비스에서는 프롬프트의 일부가 요청마다 달라집니다. 예를 들어 "이 블로그 글을 요약해 줘"라는 지시는 고정이지만, 블로그 글의 내용은 요청마다 다릅니다.

`ChatPromptTemplate`은 이 고정된 부분과 변동되는 부분을 분리합니다.

```python
from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """블로그 글을 읽고 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 순수 JSON만 반환하세요.

{{
  "summary": "2~3문장 핵심 요약",
  "key_points": ["포인트 1", "포인트 2", "포인트 3"]
}}""",
    ),
    ("user", "제목: {title}\n\n내용:\n{content_text}"),
])
```

`{title}`과 `{content_text}`는 나중에 채워질 자리입니다. `{{ }}`는 JSON 형식의 중괄호를 프롬프트 문자열 안에서 그대로 표현하기 위한 이스케이프입니다.

이 템플릿을 호출할 때는 이렇게 합니다.

```python
messages = prompt.invoke({
    "title": "FastAPI 소개",
    "content_text": "FastAPI는 Python 기반의 고성능 웹 프레임워크입니다..."
})
# → SystemMessage + HumanMessage 배열이 만들어집니다
```

프롬프트를 코드에서 분리하면 두 가지 이점이 생깁니다. 첫째, 프롬프트를 수정해도 로직 코드를 건드리지 않아도 됩니다. 둘째, 같은 프롬프트를 다른 체인에서 재사용할 수 있습니다.

---

## 6. 핵심 컴포넌트: LLM

프롬프트 템플릿이 "무엇을 물어볼지"를 정한다면, **LLM**은 실제로 물어보는 역할입니다.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

`temperature=0`은 LLM의 출력을 최대한 일관되게 만드는 설정입니다. 요약 서비스처럼 정해진 형식(JSON)으로 응답을 받아야 할 때, 값이 높을수록 창의적이지만 형식을 벗어날 가능성이 커집니다.

LLM은 체인에서 이렇게 동작합니다.

```python
chain = prompt | llm
result = chain.invoke({"title": "...", "content_text": "..."})
# result는 AIMessage 객체
print(result.content)  # '{"summary": "...", "key_points": [...]}'
```

`result.content`는 문자열입니다. LLM이 JSON 형식으로 응답했더라도, 아직 Python 딕셔너리가 아닙니다. 이걸 사용 가능한 데이터로 바꾸려면 파싱이 필요합니다.

---

## 7. 핵심 컴포넌트: 출력 파서

**출력 파서**는 LLM의 문자열 응답을 Python에서 바로 쓸 수 있는 형태로 변환합니다.

가장 간단한 방법은 `StrOutputParser`입니다. `AIMessage` 객체에서 `.content` 문자열만 꺼냅니다.

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | llm | StrOutputParser()
result = chain.invoke({"title": "...", "content_text": "..."})
# result는 이제 str: '{"summary": "...", "key_points": [...]}'
```

우리 프로젝트에서는 `StrOutputParser` 없이 직접 `result.content`에 접근하고 `json.loads()`로 파싱합니다. 결과는 같지만, 이해를 돕기 위해 중간 과정을 코드에서 직접 보이게 써둔 것이라고 이해하시면 됩니다.

```python
# summary_service.py에서
chain = _PROMPT | _LLM
result = chain.invoke({"title": body.title or "", "content_text": body.content_text})
data = json.loads(result.content)  # 여기서 직접 파싱
```

---

## 8. 전체 흐름: 4주차 코드와 연결

이제 개별 컴포넌트를 배웠으니, 4주차 `summary_service.py`의 전체 흐름을 한 번에 읽을 수 있습니다.

```python
# 1. 프롬프트 템플릿: 고정 지시문 + {title}, {content_text} 자리
_PROMPT = ChatPromptTemplate.from_messages([...])

# 2. LLM: temperature=0으로 JSON 형식 응답을 최대한 고정
_LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def create_summary(body: schemas.SummaryRequest, db: Session):
    # 3. 체이닝: 프롬프트 → LLM 순서로 연결
    chain = _PROMPT | _LLM

    # 4. 실행: {title}과 {content_text}를 채워서 OpenAI API 호출
    result = chain.invoke({"title": body.title or "", "content_text": body.content_text})

    # 5. 파싱: AIMessage.content 문자열 → Python dict
    data = json.loads(result.content)

    # 6. Pydantic 검증: 필드가 빠지거나 타입이 다르면 여기서 에러
    response = schemas.SummaryResponse(
        summary=data["summary"],
        key_points=data["key_points"],
        meta=schemas.SummaryMeta(prompt_version="v1.0", generated_at=now),
    )

    # 7. DB 저장: 검증을 통과한 결과만 저장
    row = models.Summary(...)
    summary_repository.save(db, row)

    return schemas.SummaryResponseWithId(id=row.id, **response.model_dump())
```

LangChain이 담당하는 부분은 3번과 4번, 즉 "프롬프트를 조립하고 LLM을 호출하는 것"입니다. HTTP 처리(Router)나 DB 접근(Repository)과는 완전히 분리되어 있습니다. 이게 4주차에서 LangChain이 Service 레이어에 들어간 이유입니다.

---

## 9. LangChain을 잘 쓰는 방법

LangChain을 처음 보면 기능이 너무 많아서 어디서부터 시작해야 할지 막막합니다. 몇 가지 기준을 드립니다.

**컴포넌트의 입력과 출력을 먼저 파악하세요.**
`ChatPromptTemplate.invoke()` → 메시지 배열, `ChatOpenAI.invoke()` → `AIMessage`, `json.loads()` → dict. 이 흐름을 머릿속에 갖고 있으면 체인이 어디서 왜 끊기는지 바로 보입니다.

**모든 기능을 한 번에 이해하려 하지 마세요.**  
LangChain에는 메모리, 에이전트, RAG, 스트리밍 등 수많은 기능이 있습니다. 지금 당장 필요한 건 Prompt → LLM → Output 이 세 가지입니다. 나머지는 이 흐름이 익숙해진 후 필요해지면 다른 것들도 공부해보세요~

**추상화된 체인을 이해 가능한 단위로 분해해서 쓰세요.**  
`chain = prompt | llm | parser` 한 줄은 간결하지만, 에러가 났을 때 어느 단계에서 문제가 생겼는지 추적하기 어렵습니다. 개발 중에는 단계별로 실행하고 중간 결과를 확인하는 습관을 들여봐요! (보통 이걸 디버깅이라고 하죠)

---

## 정리


| 특징      | 하는 일               | 우리 코드에서                                        |
| ------- | ------------------ | ---------------------------------------------- |
| **추상화** | LLM 호출의 복잡함을 감춤    | `ChatOpenAI`를 다른 모델로 바꿔도 `chain.invoke()`는 그대로 |
| **표준화** | 다양한 LLM을 같은 인터페이스로 | `_PROMPT \| _LLM` — 모델이 달라도 `\|`로 연결 가능 |
| **체이닝** | 컴포넌트를 파이프로 연결      | `chain = _PROMPT \| _LLM` → `chain.invoke(...)` |


LangChain은 LLM 호출이라는 반복적이고 복잡한 과정을 단순하게 만들어 줍니다. 그리고 그 단순함은 서비스의 나머지 부분이 LLM에 영향받지 않도록 보호합니다. 4주차에서 배운 레이어드 아키텍처와 LangChain은 바로 이 지점에서 맞닿아 있습니다.