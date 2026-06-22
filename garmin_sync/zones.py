"""Heart-rate zone math from a personal profile.

Uses the Karvonen method (% of heart-rate reserve, HRR = max - resting), which is
more individualized than %max, plus the MAF aerobic cap (180 - age) as a sanity
check for the easy ceiling. All values come from profile.json - nothing personal
is hardcoded here.
"""
import math

# 5-zone model as %HRR (low, high)
_ZONE_BANDS = {
    "z1": (0.50, 0.60),
    "z2": (0.60, 0.70),
    "z3": (0.70, 0.80),
    "z4": (0.80, 0.90),
    "z5": (0.90, 1.00),
}


def _round(x: float) -> int:
    """Standard half-up rounding (avoids Python banker's rounding surprises)."""
    return math.floor(x + 0.5)


def estimate_max_hr(age: int) -> int:
    """Estimate max HR from age (220 - age). Prefer a measured value if known."""
    return 220 - age


def maf_cap(age: int) -> int:
    """MAF aerobic ceiling (180 - age)."""
    return 180 - age


def karvonen(resting: int, max_hr: int, pct_low: float, pct_high: float) -> tuple[int, int]:
    """HR boundaries for a %HRR band."""
    hrr = max_hr - resting
    return _round(resting + pct_low * hrr), _round(resting + pct_high * hrr)


def compute_zones(profile: dict) -> dict:
    """Compute zones from a profile dict {age, restingHr, maxHr?}.

    Returns {maxHr, restingHr, mafCap, easyCap, zones:{z1..z5:(low,high)}}.
    easyCap is the top of Z2 - the ceiling for genuinely easy aerobic work.
    """
    age = profile["age"]
    resting = profile["restingHr"]
    max_hr = profile.get("maxHr") or estimate_max_hr(age)
    zones = {
        name: karvonen(resting, max_hr, lo, hi)
        for name, (lo, hi) in _ZONE_BANDS.items()
    }
    return {
        "maxHr": max_hr,
        "restingHr": resting,
        "mafCap": maf_cap(age),
        "easyCap": zones["z2"][1],
        "zones": zones,
    }
