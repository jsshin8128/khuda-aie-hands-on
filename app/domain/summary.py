"""5주차: summaries 테이블 ORM — url 컬럼 추가.

4주차 models.py 에서 달라지는 점:
  - url 컬럼이 추가됩니다. 사용자가 보낸 URL을 저장합니다.

실습: TODO [1]을 채워 url 컬럼을 추가하세요.
"""

from sqlalchemy import Column, Integer, Text, text

from app.database.connection import Base


class Summary(Base):
    __tablename__ = "summaries"

    id           = Column(Integer, primary_key=True, autoincrement=True)

    # TODO [1] url 컬럼을 추가하세요.
    #
    #   사용자가 보낸 URL을 저장합니다. 크롤링에 실패했을 때를 대비해 nullable=True 로 둡니다.
    #
    #   힌트:
    #     url = Column(Text, nullable=True)

    title        = Column(Text, nullable=True)
    content_text = Column(Text, nullable=False)
    output_json  = Column(Text, nullable=False)
    prompt_version = Column(Text, nullable=False)
    created_at   = Column(
        Text,
        nullable=False,
        server_default=text("(datetime('now'))"),
    )
