# AI 엔지니어링 트랙 실습 세션 안내

AI 엔지니어링 트랙 실습에 오신 것을 환영합니다!

실습은 **중간고사를 기준으로 두 시즌으로 나뉩니다.**

**1~5주차 (중간고사 이전)** 는 백엔드의 기본기를 다지고, LLM을 연동하는 방법에 대해 공부합니다.  
**6~10주차 (중간고사 이후)** 는 프롬프트 엔지니어링, RAG, 파인튜닝 등 LLM을 더 잘 다루기 우한 다양한 전략들을 다룹니다.

하나의 주제로 매 주차별로 코드를 추가, 수정하면서 실습이 진행됩니다.
따라서, 이전 주차의 내용을 놓치면 다음 주차의 내용에 대한 이해가 어렵습니다.
**이 점 반드시 유의하여 실습에 적극적으로 참여 해주시길 바랍니다.**

실습에서는 파이썬과 FastAPI, 그리고 LangChain을 사용하여 기술 블로그 요약 API 서버를 구현해보려고 합니다.  
여러분은 10주 동안 "요청을 받고 응답을 돌려준다"에서 시작해서 "프롬프트를 정교하게 설계하고, 외부 지식을 검색해 주입하며, 도메인 데이터로 모델을 특화하는 AI 시스템"까지 단계별로 구현해 보는 과정을 경험합니다.

---

## 서버 기본 세팅 명령어

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 서버 실행
uvicorn app.main:app --reload
```

서버가 뜨면 브라우저에서 [http://localhost:8000/docs](http://localhost:8000/docs) 접속 → Swagger UI 확인.

---

## 현재 구현 상태

### 1~5주차: 서버와 LLM 연동 기초 ✅ 완료

| 주차  | 핵심                             | 상태   |
| --- | ------------------------------ | ---- |
| 1주차 | HTTP 요청/응답 구조 확인 (에코 서버)       | ✅ 완료 |
| 2주차 | Pydantic 스키마로 입력/출력 계약 고정      | ✅ 완료 |
| 3주차 | DB 저장/조회 (SQLite + SQLAlchemy) | ✅ 완료 |
| 4주차 | 레이어드 아키텍처 + LangChain 연동       | ✅ 완료 |
| 5주차 | async 처리로 동시 요청 대응             | ✅ 완료 |

### 6~10주차: LLM 심화 기법 (중간고사 이후)

| 주차   | 핵심                                    | 상태 |
| ---- | --------------------------------------- | ---- |
| 6주차  | 프롬프트 엔지니어링 (역할 지정, Few-shot)          | 예정 |
| 7주차  | RAG (임베딩, 벡터 DB)                        | 예정 |
| 8주차  | 파인튜닝 (데이터셋 구성, LoRA)                   | 예정 |
| 9주차  | 모델 경량화 (양자화, 지식 증류)                    | 예정 |
| 10주차 | 심화 프로젝트 주제 기획                                | 예정 |


---

## 문서


| 문서                            | 설명               |
| ----------------------------- | ---------------- |
| [개발 환경 세팅 가이드](docs/setup.md)       | 환경 구성 및 실행 방법                  |
| [개발 로드맵](docs/roadmap.md)               | 10주차 학습·구현 계획 (1~5주차 완료, 6~10주차 예정) |
| [API 명세](docs/api-spec.md)             | 엔드포인트 및 요청/응답 스펙               |
| [DB 스키마](docs/db-schema.md)            | 데이터베이스 테이블 정의                  |
| [LangChain 가이드](docs/langchain-guide.md) | 추상화·표준화·체이닝 개념 가이드         |
| [async/await 가이드](docs/async-guide.md)   | 비동기 처리 개념 가이드                 |


---

## 프로젝트 구조

```
AIE/
├── app/
│   ├── main.py              # 진입점
│   ├── controllers/
│   │   └── summary_controller.py  # HTTP 요청 수신 (4주차~)
│   ├── services/
│   │   └── summary_service.py     # 비즈니스 로직 + LLM 호출 (4주차~)
│   ├── repositories/
│   │   └── summary_repository.py  # DB 접근 (4주차~)
│   ├── domain/
│   │   └── summary.py       # SQLAlchemy ORM
│   ├── dto/
│   │   ├── summary_request_dto.py   # Pydantic 요청 스키마
│   │   └── summary_response_dto.py  # Pydantic 응답 스키마
│   └── database/
│       └── connection.py    # SQLite 연결
├── docs/
│   ├── setup.md
│   ├── roadmap.md
│   ├── api-spec.md
│   ├── db-schema.md
│   ├── langchain-guide.md
│   └── async-guide.md
├── scripts/
│   ├── week1.sh
│   ├── week2.sh
│   ├── week3.sh
│   ├── week4.sh
│   ├── week5.sh
│   └── benchmark_index.py   # 인덱스 실습 (docs/db-schema.md 참고)
├── .env.example             # 환경변수 템플릿 (OPENAI_API_KEY)
├── requirements.txt
└── README.md
```

