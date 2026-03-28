"""5주차 정답: summaries 테이블 ORM — url 컬럼 추가."""

from sqlalchemy import Column, Integer, Text, text

from app.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    url            = Column(Text, nullable=True)   # 5주차: 사용자가 보낸 URL
    title          = Column(Text, nullable=True)
    content_text   = Column(Text, nullable=False)
    output_json    = Column(Text, nullable=False)
    prompt_version = Column(Text, nullable=False)
    created_at     = Column(
        Text,
        nullable=False,
        server_default=text("(datetime('now'))"),
    )
