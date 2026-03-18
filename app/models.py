"""3주차: summaries 테이블 ORM (docs/db-schema.md와 1:1).

실습: TODO [1]~[2]를 채워 Summary 모델을 완성하세요.
"""

from sqlalchemy import Column, Integer, Text, text

from app.database import Base


class Summary(Base):
    # TODO [1] 테이블 이름을 "summaries"로 지정. 힌트: __tablename__ = ...
    pass

    # TODO [2] 아래 컬럼을 Column으로 정의하세요.
    #   - id       : Integer, primary_key=True, autoincrement=True
    #   - title    : Text, nullable=True
    #   - content_text  : Text, nullable=False
    #   - output_json   : Text, nullable=False
    #   - prompt_version: Text, nullable=False
    #   - created_at    : Text, nullable=False,
    #                     server_default=text("(datetime('now'))")
