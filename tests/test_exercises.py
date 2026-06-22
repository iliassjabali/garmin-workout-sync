"""Exercise-catalog validation.

Garmin validates strength exercises two ways:
- `category` is validated server-side (HTTP 400 if unknown).
- `exerciseName` is silently nulled to an EMPTY STRING if unknown (category kept
  as a generic label). So resolution must treat "" as "not resolved".
"""
import pytest

from garmin_sync import exercises


def test_known_category_and_name_resolves():
    r = exercises.resolve("BENCH_PRESS", "INCLINE_BARBELL_BENCH_PRESS")
    assert r.category == "BENCH_PRESS"
    assert r.exercise_name == "INCLINE_BARBELL_BENCH_PRESS"
    assert r.is_generic is False


def test_unknown_name_falls_back_to_generic_category():
    # MACHINE_CHEST_PRESS is not a valid Garmin enum -> generic BENCH_PRESS label
    r = exercises.resolve("BENCH_PRESS", "MACHINE_CHEST_PRESS")
    assert r.category == "BENCH_PRESS"
    assert r.exercise_name is None
    assert r.is_generic is True


def test_none_name_is_generic_not_error():
    r = exercises.resolve("FLYE", None)
    assert r.category == "FLYE"
    assert r.exercise_name is None
    assert r.is_generic is True


def test_unknown_category_raises():
    with pytest.raises(exercises.InvalidCategory):
        exercises.resolve("NOT_A_CATEGORY", "WHATEVER")


def test_catalog_contains_verified_machine_and_hyrox_names():
    # A representative sample of names we verified this session.
    assert "LAT_PULLDOWN" in exercises.CATALOG["PULL_UP"]
    assert "SEATED_CABLE_ROW" in exercises.CATALOG["ROW"]
    assert "CABLE_OVERHEAD_TRICEPS_EXTENSION" in exercises.CATALOG["TRICEPS_EXTENSION"]
    assert "WALL_BALL" in exercises.CATALOG["SQUAT"]
    assert "FARMERS_CARRY" in exercises.CATALOG["CARRY"]
    assert "FACE_PULL" in exercises.CATALOG["ROW"]  # face pull lives under ROW, not SHOULDER_PRESS


def test_face_pull_under_shoulder_press_is_generic():
    # SHOULDER_PRESS/FACE_PULL nulls; only ROW/FACE_PULL resolves.
    r = exercises.resolve("SHOULDER_PRESS", "FACE_PULL")
    assert r.is_generic is True
