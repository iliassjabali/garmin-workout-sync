"""Heart-rate zone math from a profile (Karvonen %HRR + MAF cap).

Fixture profile: age 30, resting 55, max 190  ->  HRR = 135.
"""
from garmin_sync import zones

PROFILE = {"age": 30, "restingHr": 55, "maxHr": 190}


def test_estimate_max_hr_from_age():
    assert zones.estimate_max_hr(30) == 190  # 220 - age


def test_maf_cap():
    assert zones.maf_cap(30) == 150  # 180 - age


def test_karvonen_z2_boundaries():
    # Z2 = 60-70% HRR -> 55 + 0.6*135 = 136 ; 55 + 0.7*135 = 149.5 -> 150
    low, high = zones.karvonen(resting=55, max_hr=190, pct_low=0.60, pct_high=0.70)
    assert low == 136
    assert high == 150


def test_compute_zones_uses_explicit_max_hr():
    z = zones.compute_zones(PROFILE)
    assert z["maxHr"] == 190
    assert z["restingHr"] == 55
    assert z["zones"]["z2"] == (136, 150)
    assert z["mafCap"] == 150


def test_compute_zones_estimates_max_when_absent():
    z = zones.compute_zones({"age": 30, "restingHr": 55})
    assert z["maxHr"] == 190  # estimated 220-30


def test_easy_cap_is_top_of_z2():
    z = zones.compute_zones(PROFILE)
    assert z["easyCap"] == z["zones"]["z2"][1]
