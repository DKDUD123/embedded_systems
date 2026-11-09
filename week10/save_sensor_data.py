# 1. 필요한 라이브러리 불러오기
import csv
import sqlite3
import time

from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import board
import adafruit_dht


# 2. 한국 시간 설정
KST = ZoneInfo("Asia/Seoul")


# 3. 파일 저장 위치 설정
CSV_PATH = Path("environment.csv")
DB_PATH = Path("sensors.db")


# 4. 장치 이름 설정
DEVICE_ID = "pi01"


# 5. DHT22 센서 설정
sensor = adafruit_dht.DHT22(
    board.D17,
    use_pulseio=False
)


# 6. 현재 시간을 반환하는 함수
def now_text():
    return datetime.now(KST).isoformat(
        timespec="seconds"
    )
# 7. CSV 파일 생성 및 헤더 작성
def init_csv():

    # CSV 파일이 새 파일인지 확인
    new_file = not CSV_PATH.exists()

    # CSV 파일 열기
    with CSV_PATH.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        # 새 파일일 때만 제목 작성
        if new_file:
            writer.writerow([
                "timestamp",
                "temperature",
                "humidity",
                "status",
                "device_id",
                "error_message"
            ])


# 8. CSV 파일 생성 함수 실행
init_csv()

print("CSV 파일 준비 완료!")
# 9. 센서 데이터 검증 함수
def validate(t, h):

    # 측정값이 없는 경우
    if t is None or h is None:
        raise ValueError("missing value")

    # 온도 범위 확인
    if not (-40.0 <= t <= 80.0):
        raise ValueError("temperature range")

    # 습도 범위 확인
    if not (0.0 <= h <= 100.0):
        raise ValueError("humidity range")

    return round(t, 1), round(h, 1)


# 10. 센서 데이터 읽기 함수
def read_sensor():

    # 현재 시간 기록
    timestamp = now_text()

    try:
        # 센서에서 온도와 습도 읽기
        t = sensor.temperature
        h = sensor.humidity

        # 측정값 검증
        t, h = validate(t, h)

        status = "OK"
        error = None

    except (RuntimeError, ValueError) as exc:

        # 측정 실패 시 빈 값으로 저장할 준비
        t, h = None, None

        status = "ERROR"
        error = str(exc)

    # 하나의 데이터 묶음 만들기
    record = {
        "timestamp": timestamp,
        "temperature": t,
        "humidity": h,
        "status": status,
        "device_id": DEVICE_ID,
        "error_message": error
    }

    return record



# 11. CSV에 센서 데이터 저장하기
def append_csv(record):

    with CSV_PATH.open(
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            record["timestamp"],
            record["temperature"],
            record["humidity"],
            record["status"],
            record["device_id"],
            record["error_message"]
        ])


# 12. 센서 데이터 30개 저장하기
for i in range(30):

    record = read_sensor()

    append_csv(record)

    print(f"{i + 1}/30 번째 저장:", record)

    # 마지막 기록이 아니라면 5초 대기
    if i < 29:
        time.sleep(5)

print("CSV 데이터 30개 저장 완료!")
