#!/usr/bin/env bash
# ---------------------------------------------------------------
# 5주차 · POST /summarize   (URL 입력, async 처리)
#         POST /summarize/batch  (배치 처리)
#         GET  /summaries  |  GET /summaries/{id}
# 사용법: ./scripts/week5.sh
# ---------------------------------------------------------------

BASE_URL="http://localhost:8000"

# ── 출력 헬퍼 ──────────────────────────────────────────────────
BOLD="\033[1m"; RESET="\033[0m"
GREEN="\033[32m"; CYAN="\033[36m"; DIM="\033[2m"; YELLOW="\033[33m"

header() { echo -e "\n${BOLD}${GREEN}▶ $1${RESET}"; }
label()  { echo -e "  ${CYAN}$1${RESET}"; }
note()   { echo -e "  ${YELLOW}$1${RESET}"; }
divider(){ echo -e "  ${DIM}$(printf '─%.0s' {1..52})${RESET}"; }
# ───────────────────────────────────────────────────────────────

echo -e "\n${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║        5주차 API 테스트               ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"

# [1] POST /summarize — URL 입력, 단건 요약
header "[1] POST /summarize  (URL 입력)"
label  "→ 서버가 URL을 크롤링해 요약합니다. recommended_for / difficulty / read_time 포함"
divider
curl -s -X POST "$BASE_URL/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://fastapi.tiangolo.com/tutorial/",
    "output_format": "json"
  }' | jq .

# [2] POST /summarize/batch — 여러 URL 동시 처리
header "[2] POST /summarize/batch  (배치 처리)"
label  "→ 여러 URL을 asyncio.gather 로 동시에 처리합니다"
label  "→ 일부 실패해도 results / failed 로 나뉘어 반환됩니다"
divider
curl -s -X POST "$BASE_URL/summarize/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://fastapi.tiangolo.com/tutorial/",
      "https://docs.python.org/3/library/asyncio.html"
    ],
    "output_format": "json"
  }' | jq .

# [3] GET /summaries — 전체 목록
header "[3] GET /summaries  (전체 목록)"
label  "→ id / url / title 반환 (created_at 제외)"
divider
curl -s "$BASE_URL/summaries" | jq .

# [4] GET /summaries/1 — 단건 조회
header "[4] GET /summaries/1  (단건 조회)"
divider
curl -s "$BASE_URL/summaries/1" | jq .

# [5] POST /summarize — 422 유발
header "[5] POST /summarize  (잘못된 요청)"
note   "  예상 응답: 422 Unprocessable Entity (url 필드 누락)"
divider
curl -s -X POST "$BASE_URL/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "output_format": "json"
  }' | jq .

echo -e "\n${DIM}────────────────────────────────────────────────────${RESET}"
echo -e "${BOLD}  완료${RESET}\n"
