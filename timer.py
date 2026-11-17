
import time
from plyer import notification


class ScreenTimeManager:

    def __init__(self, break_interval_minutes=20):
        self.break_interval = break_interval_minutes * 60
        self.session_start_time = time.time()
        self.break_reminder_sent = False

    def get_screen_time(self):
        elapsed_time = time.time() - self.session_start_time
        return elapsed_time

    def format_time(self, seconds):
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)

        return f"{minutes:02d}:{remaining_seconds:02d}"

    def check_break_time(self):
        elapsed_time = self.get_screen_time()

        if elapsed_time >= self.break_interval:
            if not self.break_reminder_sent:
                self.send_break_notification()
                self.break_reminder_sent = True

            return True

        return False

    def send_break_notification(self):
        notification.notify(
            title="Time for a Break!",
            message="You've been using your screen continuously. Take a short break and stretch!",
            timeout=10
        )

    def reset_timer(self):
        self.session_start_time = time.time()
        self.break_reminder_sent = False
