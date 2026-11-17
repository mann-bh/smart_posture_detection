
from exercise_tips import (
    get_exercise_tip,
    get_break_exercise
)

print("HEAD TILT:")
print(get_exercise_tip("HEAD TILTED", "NORMAL"))

print("\nFORWARD LEAN:")
print(get_exercise_tip("NORMAL", "LEANING FORWARD"))

print("\nBREAK EXERCISE:")
print(get_break_exercise())
