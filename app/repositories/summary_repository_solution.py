"""4주차 정답: Repository 레이어 — DB 접근 전담."""

from typing import Optional

from sqlalchemy.orm import Session

from app import models


def save(db: Session, row: models.Summary) -> models.Summary:
    db.add(row)      # 세션에 등록
    db.commit()      # INSERT 실행
    db.refresh(row)  # DB가 채운 id, created_at 을 row 에 반영
    return row


def list_all(db: Session) -> list[models.Summary]:
    return (
        db.query(models.Summary)
        .order_by(models.Summary.created_at.desc())  # 최신순
        .all()
    )


def get_by_id(db: Session, id: int) -> Optional[models.Summary]:
    return db.query(models.Summary).filter(models.Summary.id == id).first()
