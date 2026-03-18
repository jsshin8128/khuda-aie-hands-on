"""3주차: SQLite 연결 (summary.db).

실습: TODO [1]~[3]을 채워 DB 연결 객체를 완성하세요.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./summary.db"

# TODO [1] create_engine으로 engine 생성.
#          힌트: connect_args={"check_same_thread": False} 필요 (SQLite 전용)
engine = None  # TODO [1]

# TODO [2] sessionmaker로 SessionLocal 생성. 힌트: bind=engine
SessionLocal = None  # TODO [2]

# TODO [3] declarative_base()로 Base 생성
Base = None  # TODO [3]
