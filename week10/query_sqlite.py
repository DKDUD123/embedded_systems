import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 1. 데이터베이스 연결
conn = sqlite3.connect("sensors.db")

# 2. 오늘 날짜 설정 (한국 시간)
KST = ZoneInfo("Asia/Seoul")
today = datetime.now(KST).date()

start_ts = f"{today}T00:00:00+09:00"
end_ts = f"{today + timedelta(days=1)}T00:00:00+09:00"

# 3. 가장 최근 기록 조회
latest = conn.execute("""
SELECT timestamp, temperature, humidity, status
FROM readings
ORDER BY timestamp DESC
LIMIT 1
""").fetchone()

print("===== 최신 기록 =====")
if latest is not None:
    print(latest)
else:
    print("저장된 데이터가 없습니다.")

# 4. 오늘 날짜의 정상 기록 조회
rows = conn.execute("""
SELECT timestamp, temperature, humidity
FROM readings
WHERE status = 'OK'
AND timestamp >= ?
AND timestamp < ?
ORDER BY timestamp ASC
""", (start_ts, end_ts)).fetchall()

print("\n===== 오늘의 정상 기록 =====")
for row in rows:
    print(row)

print("오늘 정상 기록 개수:", len(rows))

# 5. 오늘의 통계 계산
stats = conn.execute("""
SELECT
    AVG(temperature),
    MIN(temperature),
    MAX(temperature),
    AVG(humidity),
    COUNT(*)
FROM readings
WHERE status = 'OK'
AND timestamp >= ?
AND timestamp < ?
""", (start_ts, end_ts)).fetchone()

avg_t, min_t, max_t, avg_h, count = stats

print("\n===== 오늘의 통계 =====")
print("평균 온도:", avg_t)
print("최저 온도:", min_t)
print("최고 온도:", max_t)
print("평균 습도:", avg_h)
print("정상 기록 개수:", count)

# 6. 오늘의 오류 기록 개수
errors = conn.execute("""
SELECT COUNT(*)
FROM readings
WHERE status = 'ERROR'
AND timestamp >= ?
AND timestamp < ?
""", (start_ts, end_ts)).fetchone()[0]

print("오류 기록 개수:", errors)

# 7. 데이터베이스 연결 종료
conn.close()