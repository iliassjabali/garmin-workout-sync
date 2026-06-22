"""Verified Garmin strength-exercise catalog.

Discovered empirically against the Garmin workout-service API:

- `category` is validated server-side: an unknown category returns HTTP 400.
- `exerciseName` is NOT rejected when unknown - Garmin silently nulls it to an
  EMPTY STRING and keeps the category as a generic on-watch label. So a name is
  "resolved" only if it is in this catalog; otherwise fall back to the generic
  category label and put the real movement in the step description.

Only enums confirmed to round-trip are listed. Where a movement has no valid
name (e.g. machine chest press, pec deck, cable lateral raise) use the category
alone and describe the machine in the note.
"""
from dataclasses import dataclass


class InvalidCategory(ValueError):
    """Raised when a category is not accepted by Garmin."""


# category -> set of exerciseName values verified to resolve under that category
CATALOG: dict[str, set[str]] = {
    # --- Chest / push ---
    "BENCH_PRESS": {"INCLINE_BARBELL_BENCH_PRESS", "BARBELL_BENCH_PRESS"},
    "FLYE": set(),            # pec deck / cable crossover -> generic FLYE + note
    "PUSH_UP": {"PUSH_UP"},
    # --- Shoulders ---
    "SHOULDER_PRESS": {"BARBELL_SHOULDER_PRESS", "SMITH_MACHINE_OVERHEAD_PRESS", "PUSH_PRESS"},
    "LATERAL_RAISE": {"FRONT_RAISE", "DUMBBELL_LATERAL_RAISE"},  # no cable lateral enum -> generic
    # --- Back / pull ---
    "PULL_UP": {"LAT_PULLDOWN", "WIDE_GRIP_LAT_PULLDOWN", "CHIN_UP", "ASSISTED_PULL_UP", "PULL_UP"},
    "ROW": {"SEATED_CABLE_ROW", "BARBELL_ROW", "T_BAR_ROW", "INVERTED_ROW", "DUMBBELL_ROW", "FACE_PULL"},
    # --- Arms ---
    "CURL": {"CABLE_BICEPS_CURL", "BARBELL_BICEPS_CURL", "DUMBBELL_BICEPS_CURL",
             "INCLINE_DUMBBELL_BICEPS_CURL", "ALTERNATING_DUMBBELL_BICEPS_CURL"},
    "TRICEPS_EXTENSION": {"CABLE_OVERHEAD_TRICEPS_EXTENSION", "TRICEPS_PRESSDOWN",
                          "CABLE_KICKBACK", "CABLE_LYING_TRICEPS_EXTENSION",
                          "OVERHEAD_DUMBBELL_TRICEPS_EXTENSION", "BENCH_DIP", "WEIGHTED_BENCH_DIP"},
    # --- Legs ---
    "SQUAT": {"BARBELL_BACK_SQUAT", "LEG_PRESS", "HACK_SQUAT", "SMITH_MACHINE_SQUAT",
              "LEG_EXTENSION", "GOBLET_SQUAT", "WALL_BALL", "THRUSTER"},
    "DEADLIFT": {"ROMANIAN_DEADLIFT"},
    "LEG_CURL": {"LEG_CURL"},
    "CALF_RAISE": {"STANDING_CALF_RAISE", "SEATED_CALF_RAISE"},
    "HIP_RAISE": {"HIP_THRUST", "BARBELL_HIP_THRUST"},
    "LUNGE": {"WALKING_LUNGE", "DUMBBELL_LUNGE"},
    "OLYMPIC_LIFT": {"CLEAN", "CLEAN_AND_JERK"},
    # --- Conditioning / Hyrox ---
    "TOTAL_BODY": {"BURPEE"},
    "PLYO": {"BOX_JUMP", "TUCK_JUMP", "JUMP_ROPE"},
    "CARDIO": {"BATTLE_ROPE", "JUMPING_JACK"},
    "CARRY": {"FARMERS_CARRY", "SUITCASE_CARRY"},
    # --- Core ---
    "PLANK": {"PLANK", "SIDE_PLANK", "MOUNTAIN_CLIMBER"},
    "CORE": {"RUSSIAN_TWIST", "HANGING_KNEE_RAISE"},
    "CRUNCH": {"CRUNCH"},
    "SIT_UP": {"SIT_UP"},
}


@dataclass(frozen=True)
class Resolved:
    category: str
    exercise_name: str | None  # None when not in catalog -> generic label
    is_generic: bool


def resolve(category: str, name: str | None) -> Resolved:
    """Resolve a (category, name) pair against the verified catalog.

    Raises InvalidCategory if the category is not Garmin-accepted. A name that is
    None, empty, or not in the catalog resolves to the generic category label.
    """
    if category not in CATALOG:
        raise InvalidCategory(
            f"{category!r} is not a Garmin-accepted exercise category. "
            f"Known: {', '.join(sorted(CATALOG))}"
        )
    if name and name in CATALOG[category]:
        return Resolved(category=category, exercise_name=name, is_generic=False)
    return Resolved(category=category, exercise_name=None, is_generic=True)
