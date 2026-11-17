
import csv
import os
from datetime import datetime

CSV_FILE = "log.csv"


def initialize_log():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Timestamp",
                "Distance_CM",
                "Head_Tilt",
                "Head_Status",
                "Lean_Status",
                "Screen_Time_Seconds",
                "Break_Reminder"
            ])


def log_data(
    distance,
    head_tilt,
    head_status,
    lean_status,
    screen_time,
    break_reminder
):
    initialize_log()

    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            round(distance, 2) if distance is not None else "",
            round(head_tilt, 2) if head_tilt is not None else "",
            head_status,
            lean_status,
            round(screen_time, 2),
            break_reminder
        ])
