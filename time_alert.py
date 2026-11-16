
import time
from plyer import notification


class DistanceAlertManager:

    def __init__(
        self,
        too_close=40,
        too_far=80,
        persistence_seconds=5,
        cooldown_seconds=30
    ):

        self.too_close = too_close
        self.too_far = too_far

        self.persistence_seconds = persistence_seconds
        self.cooldown_seconds = cooldown_seconds

        self.problem_start_time = None
        self.current_problem = None

        self.last_alert_time = float("-inf")

    def update(self, distance):

        if distance is None:
            self.problem_start_time = None
            self.current_problem = None
            return "WAITING FOR FACE"

        # Determine current distance status
        if distance < self.too_close:
            problem = "TOO CLOSE"

        elif distance > self.too_far:
            problem = "TOO FAR"

        else:
            problem = None

        # Normal distance: reset problem timer
        if problem is None:

            self.problem_start_time = None
            self.current_problem = None

            return "NORMAL"

        current_time = time.monotonic()

        # Start or restart persistence timer
        if problem != self.current_problem:

            self.current_problem = problem
            self.problem_start_time = current_time

        # Check whether problem has persisted long enough
        elapsed = current_time - self.problem_start_time

        if elapsed >= self.persistence_seconds:

            # Check cooldown
            if (
                current_time - self.last_alert_time
                >= self.cooldown_seconds
            ):

                self.send_notification(problem)

                self.last_alert_time = current_time

        return problem

    def send_notification(self, problem):

        if problem == "TOO CLOSE":

            message = (
                "You are sitting too close to your screen. "
                "Move slightly backward."
            )

        else:

            message = (
                "You are sitting far from your screen. "
                "Check your sitting position."
            )

        try:

            notification.notify(
                title="Smart Posture Monitor",
                message=message,
                timeout=5
            )

            print("Alert sent:", problem)

        except Exception as error:

            print("Notification failed:", error)
            print("Distance warning:", problem)
