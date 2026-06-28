"""Build Garmin workout JSON from a declarative plan.

A plan is data, not code - an agent (or you) compose it as JSON and this module
turns it into the workout-service payload. See examples/week-base.json.

Cardio step:   {"kind": "warmup|interval|cooldown|recovery",
                "minutes": N, "hrLow": N, "hrHigh": N, "note": "..."}
Strength set:  {"block": {"sets": N, "exercise": "ENUM", "category": "CAT",
                "reps": N | "seconds": N | "meters": N, "restSec": N, "note": "..."}}
Circuit:       {"circuit": {"rounds": N, "restSec": N, "stations": [<station>, ...]}}
               where each station is the inner part of a block (no "sets").

Notes on Garmin limits (discovered empirically):
- Target WEIGHT cannot be set via the API - it is silently dropped. Put load in
  the step note instead; you log the actual weight on the device.
- A single workout is one sport. Mixed-modality days = multiple workouts.
"""
from . import exercises

SPORTS = {
    "running": {"sportTypeId": 1, "sportTypeKey": "running"},
    "cycling": {"sportTypeId": 2, "sportTypeKey": "cycling"},
    "strength": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
}

_STEP_TYPE = {"warmup": 1, "cooldown": 2, "interval": 3, "recovery": 4, "rest": 5, "repeat": 6}
_COND = {"time": 2, "distance": 3, "reps": 10, "iterations": 7}


class _Order:
    """Monotonic stepOrder shared across nested steps."""

    def __init__(self):
        self.n = 0

    def next(self) -> int:
        self.n += 1
        return self.n


def _hr_target(low, high) -> dict:
    return {
        "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone"},
        "targetValueOne": float(low),
        "targetValueTwo": float(high),
        "zoneNumber": None,
    }


def _cardio_step(o: _Order, step: dict) -> dict:
    kind = step["kind"]
    s = {
        "type": "ExecutableStepDTO",
        "stepOrder": o.next(),
        "stepType": {"stepTypeId": _STEP_TYPE[kind], "stepTypeKey": kind},
        "description": step.get("note", ""),
    }
    # End condition: distance (km/meters) takes precedence over time (minutes).
    if "km" in step or "meters" in step:
        meters = float(step["meters"]) if "meters" in step else float(step["km"]) * 1000.0
        s["endCondition"] = {"conditionTypeId": _COND["distance"], "conditionTypeKey": "distance"}
        s["endConditionValue"] = meters
    else:
        s["endCondition"] = {"conditionTypeId": _COND["time"], "conditionTypeKey": "time"}
        s["endConditionValue"] = float(step["minutes"]) * 60.0
    if "hrLow" in step and "hrHigh" in step:
        s.update(_hr_target(step["hrLow"], step["hrHigh"]))
    return s


def _exercise_step(o: _Order, spec: dict) -> dict:
    """One strength/station executable step (reps | seconds | meters)."""
    resolved = exercises.resolve(spec["category"], spec.get("exercise"))
    s = {
        "type": "ExecutableStepDTO",
        "stepOrder": o.next(),
        "stepType": {"stepTypeId": _STEP_TYPE["interval"], "stepTypeKey": "interval"},
        "category": resolved.category,
        "description": spec.get("note", ""),
    }
    if resolved.exercise_name:
        s["exerciseName"] = resolved.exercise_name
    if "meters" in spec:
        s["endCondition"] = {"conditionTypeId": _COND["distance"], "conditionTypeKey": "distance"}
        s["endConditionValue"] = float(spec["meters"])
    elif "seconds" in spec:
        s["endCondition"] = {"conditionTypeId": _COND["time"], "conditionTypeKey": "time"}
        s["endConditionValue"] = float(spec["seconds"])
    else:
        s["endCondition"] = {"conditionTypeId": _COND["reps"], "conditionTypeKey": "reps"}
        s["endConditionValue"] = float(spec["reps"])
    return s


def _rest_step(o: _Order, secs: int) -> dict:
    return {
        "type": "ExecutableStepDTO",
        "stepOrder": o.next(),
        "stepType": {"stepTypeId": _STEP_TYPE["rest"], "stepTypeKey": "rest"},
        "endCondition": {"conditionTypeId": _COND["time"], "conditionTypeKey": "time"},
        "endConditionValue": float(secs),
    }


def _repeat_group(o: _Order, iterations: int, children: list) -> dict:
    grp_order = o.next()
    built = []
    for child in children:
        built.append(child(o))
    return {
        "type": "RepeatGroupDTO",
        "stepOrder": grp_order,
        "stepType": {"stepTypeId": _STEP_TYPE["repeat"], "stepTypeKey": "repeat"},
        "numberOfIterations": iterations,
        "smartRepeat": False,
        "endCondition": {"conditionTypeId": _COND["iterations"], "conditionTypeKey": "iterations"},
        "endConditionValue": float(iterations),
        "workoutSteps": built,
    }


def _block(o: _Order, block: dict) -> dict:
    children = [lambda o: _exercise_step(o, block)]
    if block.get("restSec"):
        children.append(lambda o: _rest_step(o, block["restSec"]))
    return _repeat_group(o, block["sets"], children)


def _circuit(o: _Order, circ: dict) -> dict:
    children = [(lambda st: (lambda o: _exercise_step(o, st)))(st) for st in circ["stations"]]
    if circ.get("restSec"):
        children.append(lambda o: _rest_step(o, circ["restSec"]))
    return _repeat_group(o, circ["rounds"], children)


def build_workout(w: dict) -> dict:
    """Turn one declarative workout into a Garmin workout payload."""
    sport = SPORTS[w["sport"]]
    o = _Order()
    steps = []
    for step in w["steps"]:
        if "block" in step:
            steps.append(_block(o, step["block"]))
        elif "circuit" in step:
            steps.append(_circuit(o, step["circuit"]))
        else:
            steps.append(_cardio_step(o, step))
    return {
        "sportType": sport,
        "workoutName": w["name"],
        "description": w.get("description", ""),
        "workoutSegments": [{"segmentOrder": 1, "sportType": sport, "workoutSteps": steps}],
    }


def build_plan(plan: dict) -> list[tuple[str, dict]]:
    """Build all workouts in a plan -> list of (date, workout_json)."""
    return [(w["date"], build_workout(w)) for w in plan["workouts"]]
