"""Declarative plan -> Garmin workout JSON (no network)."""
from garmin_sync import workouts


def test_running_cardio_workout_has_hr_targets_and_sequential_order():
    w = {
        "sport": "running", "name": "Easy Run",
        "steps": [
            {"kind": "warmup", "minutes": 5, "hrLow": 110, "hrHigh": 145},
            {"kind": "interval", "minutes": 40, "hrLow": 138, "hrHigh": 150, "note": "Z2"},
            {"kind": "cooldown", "minutes": 5, "hrLow": 110, "hrHigh": 140},
        ],
    }
    out = workouts.build_workout(w)
    assert out["sportType"]["sportTypeKey"] == "running"
    steps = out["workoutSegments"][0]["workoutSteps"]
    assert [s["stepOrder"] for s in steps] == [1, 2, 3]
    mid = steps[1]
    assert mid["targetType"]["workoutTargetTypeKey"] == "heart.rate.zone"
    assert mid["targetValueOne"] == 138.0
    assert mid["targetValueTwo"] == 150.0
    # minutes -> seconds
    assert mid["endConditionValue"] == 2400.0


def test_strength_block_becomes_repeat_group():
    w = {
        "sport": "strength", "name": "Push",
        "steps": [
            {"block": {"sets": 4, "exercise": "INCLINE_BARBELL_BENCH_PRESS",
                       "category": "BENCH_PRESS", "reps": 8, "restSec": 120,
                       "note": "~50kg RPE8"}},
        ],
    }
    out = workouts.build_workout(w)
    assert out["sportType"]["sportTypeKey"] == "strength_training"
    grp = out["workoutSegments"][0]["workoutSteps"][0]
    assert grp["type"] == "RepeatGroupDTO"
    assert grp["numberOfIterations"] == 4
    ex = grp["workoutSteps"][0]
    assert ex["exerciseName"] == "INCLINE_BARBELL_BENCH_PRESS"
    assert ex["category"] == "BENCH_PRESS"
    assert ex["endConditionValue"] == 8.0
    assert ex["description"] == "~50kg RPE8"
    # rest step present inside the block
    assert grp["workoutSteps"][1]["stepType"]["stepTypeKey"] == "rest"


def test_invalid_exercise_name_drops_to_generic_category():
    w = {"sport": "strength", "name": "x",
         "steps": [{"block": {"sets": 3, "exercise": "MACHINE_CHEST_PRESS",
                              "category": "BENCH_PRESS", "reps": 10}}]}
    out = workouts.build_workout(w)
    ex = out["workoutSegments"][0]["workoutSteps"][0]["workoutSteps"][0]
    assert ex["category"] == "BENCH_PRESS"
    assert "exerciseName" not in ex or ex.get("exerciseName") is None


def test_circuit_builds_multi_station_round():
    w = {"sport": "strength", "name": "hyrox",
         "steps": [{"circuit": {"rounds": 3, "restSec": 75, "stations": [
             {"exercise": "WALL_BALL", "category": "SQUAT", "reps": 15},
             {"exercise": "FARMERS_CARRY", "category": "CARRY", "meters": 40},
         ]}}]}
    out = workouts.build_workout(w)
    grp = out["workoutSegments"][0]["workoutSteps"][0]
    assert grp["numberOfIterations"] == 3
    # 2 stations + 1 rest
    assert len(grp["workoutSteps"]) == 3
    carry = grp["workoutSteps"][1]
    assert carry["endCondition"]["conditionTypeKey"] == "distance"
    assert carry["endConditionValue"] == 40.0


def test_build_plan_returns_dated_workouts():
    plan = {"workouts": [
        {"date": "2099-01-01", "sport": "running", "name": "A",
         "steps": [{"kind": "interval", "minutes": 30, "hrLow": 130, "hrHigh": 150}]},
        {"date": "2099-01-02", "sport": "strength", "name": "B",
         "steps": [{"block": {"sets": 3, "exercise": "LAT_PULLDOWN",
                             "category": "PULL_UP", "reps": 10}}]},
    ]}
    built = workouts.build_plan(plan)
    assert [d for d, _ in built] == ["2099-01-01", "2099-01-02"]
    assert built[0][1]["sportType"]["sportTypeKey"] == "running"
