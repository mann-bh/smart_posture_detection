
import random


# Exercise recommendations for different posture problems

HEAD_TILT_EXERCISES = [
    "Keep your head straight and gently stretch your neck.",
    "Slowly tilt your head left and right.",
    "Gently turn your head from side to side.",
    "Relax your shoulders and maintain a neutral head position."
]

FORWARD_LEAN_EXERCISES = [
    "Move back and sit upright in your chair.",
    "Relax your shoulders and gently stretch your chest.",
    "Keep your screen at a comfortable viewing distance.",
    "Take a short break and gently roll your shoulders."
]

BREAK_EXERCISES = [
    "Stand up and walk for a minute.",
    "Stretch your arms and shoulders gently.",
    "Look away from your screen and relax your eyes.",
    "Take a short walk and stretch your back."
]


def get_exercise_tip(head_status, lean_status):

    if head_status == "HEAD TILTED":
        return random.choice(HEAD_TILT_EXERCISES)

    elif lean_status == "LEANING FORWARD":
        return random.choice(FORWARD_LEAN_EXERCISES)

    else:
        return "Your posture looks good. Keep it up!"


def get_break_exercise():

    return random.choice(BREAK_EXERCISES)
