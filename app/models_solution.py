"""3주차 정답: summaries 테이블 ORM (docs/db-schema.md와 1:1)."""

from sqlalchemy import Column, Integer, Text, text

from app.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text, nullable=True)
    content_text = Column(Text, nullable=False)
    output_json = Column(Text, nullable=False)
    prompt_version = Column(Text, nullable=False)
    created_at = Column(
        Text,
        nullable=False,
        server_default=text("(datetime('now'))"),
    )
