"""Thin wrapper over garminconnect for pushing workouts and reading wellness.

Wraps the high-level methods that survive across garminconnect versions:
upload_workout / schedule_workout / delete_workout / get_workouts, plus the
wellness reads used for recovery decisions (resting HR, Body Battery, activities).
"""
from datetime import date, timedelta


class GarminClient:
    def __init__(self, garmin):
        self._g = garmin

    @property
    def name(self) -> str:
        try:
            return self._g.get_full_name()
        except Exception:
            return "(unknown)"

    # --- workouts ---
    def replace_by_prefix(self, prefix: str, sport_key: str | None = None) -> list[str]:
        """Delete existing workouts whose name starts with prefix (optionally one sport).

        Makes re-running a plan idempotent instead of creating duplicates.
        """
        removed = []
        for w in self._g.get_workouts(0, 100):
            name = w["workoutName"]
            if not name.startswith(prefix):
                continue
            if sport_key and w.get("sportType", {}).get("sportTypeKey") != sport_key:
                continue
            self._g.delete_workout(w["workoutId"])
            removed.append(name)
        return removed

    def push(self, workout_json: dict, schedule_date: str | None = None) -> int:
        """Upload a workout and optionally schedule it. Returns workoutId."""
        wid = self._g.upload_workout(workout_json)["workoutId"]
        if schedule_date:
            self._g.schedule_workout(wid, schedule_date)
        return wid

    # --- wellness (recovery) ---
    def resting_hr(self, day: str) -> int | None:
        try:
            r = self._g.get_rhr_day(day)
            return r["allMetrics"]["metricsMap"]["WELLNESS_RESTING_HEART_RATE"][0]["value"]
        except Exception:
            return None

    def body_battery(self, day: str) -> dict | None:
        try:
            bb = self._g.get_body_battery(day, day)[0]
            return {"charged": bb.get("charged"), "drained": bb.get("drained")}
        except Exception:
            return None

    def activities(self, day: str) -> list[dict]:
        try:
            out = []
            for a in self._g.get_activities_by_date(day, day):
                out.append({
                    "type": a.get("activityType", {}).get("typeKey"),
                    "name": a.get("activityName"),
                    "minutes": round((a.get("duration") or 0) / 60),
                    "km": round((a.get("distance") or 0) / 1000, 2),
                    "avgHr": a.get("averageHR"),
                    "maxHr": a.get("maxHR"),
                    "aerobicTE": a.get("aerobicTrainingEffect"),
                })
            return out
        except Exception:
            return []

    def recovery_snapshot(self, days: int = 7) -> list[dict]:
        """RHR + Body Battery for the last `days` days (most recent last)."""
        today = date.today()
        out = []
        for i in range(days - 1, -1, -1):
            d = (today - timedelta(days=i)).isoformat()
            out.append({"date": d, "restingHr": self.resting_hr(d),
                        "bodyBattery": self.body_battery(d)})
        return out
