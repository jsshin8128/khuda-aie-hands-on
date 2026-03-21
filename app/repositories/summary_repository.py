"""4주차: Repository 레이어 — DB 접근 전담.

Repository 패턴의 핵심 규칙:
  - DB 세션(db)을 받아서 ORM 조작만 합니다.
  - "어떤 데이터를 저장할지"는 Service가 결정합니다.
  - 이 파일은 "어떻게 저장하는지"만 알면 됩니다.

덕분에 나중에 SQLite → PostgreSQL 로 바꿔도 이 파일만 수정하면 됩니다.

실습: TODO [1]~[3]을 순서대로 채우세요.
"""

from typing import Optional

from sqlalchemy.orm import Session

from app import models


def save(db: Session, row: models.Summary) -> models.Summary:
    # TODO [1] 새 행을 DB에 저장하고 반환하세요.
    #
    #   db.add(row)      — 세션에 객체 등록 (아직 INSERT 안 됨)
    #   db.commit()      — 실제로 DB에 씁니다
    #   db.refresh(row)  — DB가 채운 값(id, created_at)을 row에 반영합니다
    #   return row
    raise NotImplementedError("TODO [1]")


def list_all(db: Session) -> list[models.Summary]:
    # TODO [2] 전체 행을 최신순(created_at 내림차순)으로 조회하세요.
    #
    #   db.query(models.Summary)
    #     .order_by(models.Summary.created_at.desc())
    #     .all()
    raise NotImplementedError("TODO [2]")


def get_by_id(db: Session, id: int) -> Optional[models.Summary]:
    # TODO [3] id 로 단건 조회하세요. 없으면 None 을 반환합니다.
    #          (None 처리는 Service에서 HTTPException 으로 변환합니다)
    #
    #   db.query(models.Summary).filter(models.Summary.id == id).first()
    raise NotImplementedError("TODO [3]")
