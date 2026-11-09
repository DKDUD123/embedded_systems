import sqlite3
import csv
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# 1. 데이터베이스 연결
conn = sqlite3.connect("sensors.db")

# 2. 오늘 날짜 설정
KST = ZoneInfo("Asia/Seoul")
today = datetime.now(KST).date()
day = str(today)

start_ts = f"{day}T00:00:00+09:00"
end_ts = f"{today + timedelta(days=1)}T00:00:00+09:00"

# 3. 오늘의 정상 데이터 조회
rows = conn.execute("""
SELECT timestamp, temperature, humidity
FROM readings
WHERE status = 'OK'
AND timestamp >= ?
AND timestamp < ?
ORDER BY timestamp ASC
""", (start_ts, end_ts)).fetchall()

# 4. 오늘의 통계 조회
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

# 5. 오늘의 오류 개수 조회
errors = conn.execute("""
SELECT COUNT(*)
FROM readings
WHERE status = 'ERROR'
AND timestamp >= ?
AND timestamp < ?
""", (start_ts, end_ts)).fetchone()[0]

# 6. HTML 리포트 내용 만들기
if count > 0:
    avg_t_text = f"{avg_t:.1f}"
    min_t_text = f"{min_t:.1f}"
    max_t_text = f"{max_t:.1f}"
    avg_h_text = f"{avg_h:.1f}"
else:
    avg_t_text = "데이터 없음"
    min_t_text = "데이터 없음"
    max_t_text = "데이터 없음"
    avg_h_text = "데이터 없음"

html = f"""
<!doctype html>
<html lang="ko">
<meta charset="utf-8">
<title>{day} 센서 리포트</title>

<h1>{day} 센서 리포트</h1>

<ul>
    <li>평균 온도: {avg_t_text} °C</li>
    <li>최저 온도: {min_t_text} °C</li>
    <li>최고 온도: {max_t_text} °C</li>
    <li>평균 습도: {avg_h_text} %</li>
    <li>정상 {count}건 · 오류 {errors}건</li>
</ul>

</html>
"""

# 7. reports 폴더 만들기
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

# 8. HTML 파일 저장
report_path = REPORT_DIR / f"report_{day}.html"
report_path.write_text(html, encoding="utf-8")

print("HTML 리포트 생성:", report_path.resolve())

# 9. CSV 파일 내보내기
with open("daily_export.csv", "w",
          newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow([
        "timestamp",
        "temperature",
        "humidity"
    ])

    writer.writerows(rows)

print("CSV 내보내기 완료!")

# 10. 행 개수 비교
db_count = len(rows)

with open("daily_export.csv", "r",
          newline="", encoding="utf-8") as file:

    reader = csv.reader(file)
    next(reader)  # 헤더 건너뛰기
    csv_count = sum(1 for row in reader)

print("SQLite 조회 행 수:", db_count)
print("CSV 내보내기 행 수:", csv_count)

if db_count == csv_count:
    print("검증 성공! 두 데이터의 행 수가 같습니다.")
else:
    print("검증 실패! 행 수가 다릅니다.")

# 11. 데이터베이스 연결 종료
conn.close()