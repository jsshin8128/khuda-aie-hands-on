#!/usr/bin/env python3
"""
인덱스 유무에 따른 조회 속도 비교.
프로젝트 루트에서: python3 scripts/benchmark_index.py
"""
import sqlite3
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_FILE = PROJECT_ROOT / "summary.db"
TARGET_ROWS = 100_000  # 인덱스 차이가 보이도록 행 수 확대
RUNS = 5  # 여러 번 측정 후 평균
QUERY = "SELECT id, url, title FROM summaries ORDER BY created_at DESC"
MINIMAL_JSON = '{"main_points":[],"core_summary":"","structure_summary":"","practical_insights":[],"meta":{"prompt_version":"v1.0","generated_at":"2024-01-01T00:00:00Z"}}'


def main() -> None:
    if not DB_FILE.exists():
        print("summary.db가 없습니다. 3주차 서버를 한 번 실행한 뒤 다시 시도하세요.")
        return

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='summaries'")
    if not cur.fetchone():
        conn.close()
        print("summaries 테이블이 없습니다. 3주차 서버를 한 번 실행한 뒤 다시 시도하세요.")
        return

    cur.execute("DELETE FROM summaries")
    print(f"더미 {TARGET_ROWS}건 삽입 중...")
    for i in range(TARGET_ROWS):
        cur.execute(
            "INSERT INTO summaries (url, title, content_text, output_json, prompt_version, created_at) VALUES (?, ?, ?, ?, ?, datetime('now', ?))",
            (f"https://example.com/post-{i}", None, "x", MINIMAL_JSON, "v2.0", f"-{i} seconds"),
        )
    conn.commit()
    print(f"총 {TARGET_ROWS}건 준비됨.\n")

    cur.execute("DROP INDEX IF EXISTS idx_summaries_created_at")
    conn.commit()

    def run_query() -> float:
        t0 = time.perf_counter()
        cur.execute(QUERY)
        list(cur.fetchall())
        return time.perf_counter() - t0

    t_no_index = sum(run_query() for _ in range(RUNS)) / RUNS
    cur.execute("CREATE INDEX idx_summaries_created_at ON summaries(created_at DESC)")
    conn.commit()
    t_with_index = sum(run_query() for _ in range(RUNS)) / RUNS
    conn.close()

    print(f"인덱스 없이: {t_no_index:.4f}초 ({t_no_index*1000:.2f}ms)")
    print(f"인덱스 있음: {t_with_index:.4f}초 ({t_with_index*1000:.2f}ms)")
    if t_no_index > t_with_index:
        ratio = t_no_index / t_with_index
        print(f"인덱스 사용 시 약 {ratio:.1f}배 빠릅니다.")
    else:
        print("인덱스가 있으면 정렬 조회가 더 빠릅니다.")


if __name__ == "__main__":
    main()
