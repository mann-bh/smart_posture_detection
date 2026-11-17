
import time
from timer import ScreenTimeManager

timer = ScreenTimeManager(break_interval_minutes=0.1)

print("Screen-time timer started!")

while True:
    elapsed = timer.get_screen_time()

    print("Screen Time:", timer.format_time(elapsed))

    if timer.check_break_time():
        print("BREAK TIME!")
        break

    time.sleep(1)
