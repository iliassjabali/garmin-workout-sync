"""Command-line interface.

    garmin-sync auth                         # log in, cache token
    garmin-sync push PLAN.json [--dry-run]   # build + schedule a plan
    garmin-sync wellness [--days N]          # recovery snapshot (RHR, Body Battery)
    garmin-sync zones [--profile profile.json]
"""
import argparse
import json
import sys

from . import workouts, zones


def _load_profile(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def cmd_auth(args) -> int:
    from .auth import authenticate
    g = authenticate(env_path=args.env)
    name = g.get_full_name() if hasattr(g, "get_full_name") else "?"
    print(f"Authenticated as: {name}")
    return 0


def cmd_push(args) -> int:
    with open(args.plan) as f:
        plan = json.load(f)
    built = workouts.build_plan(plan)

    if args.dry_run:
        for d, wo in built:
            print(f"\n=== {d}  {wo['workoutName']}  ({wo['sportType']['sportTypeKey']}) ===")
            print(json.dumps(wo, indent=2))
        print(f"\n[dry-run] {len(built)} workout(s) built, nothing pushed.")
        return 0

    from .auth import load_client
    from .client import GarminClient
    gc = GarminClient(load_client())
    print(f"Logged in as {gc.name}\n")

    # idempotent replace per distinct prefix present in the plan
    prefixes = {w.get("replaceByPrefix") for w in plan["workouts"] if w.get("replaceByPrefix")}
    for p in prefixes:
        for nm in gc.replace_by_prefix(p):
            print(f"  (removed old '{nm}')")

    for (d, wo), src in zip(built, plan["workouts"]):
        wid = gc.push(wo, schedule_date=src.get("date"))
        print(f"✅ {d}  {wo['workoutName']}  (id {wid})")
    print("\nDone. Sync your watch from the Garmin Connect app.")
    return 0


def cmd_wellness(args) -> int:
    from .auth import load_client
    from .client import GarminClient
    gc = GarminClient(load_client())
    snap = gc.recovery_snapshot(days=args.days)
    print(f"{'date':12} {'restingHr':>9} {'bodyBattery':>12}")
    for row in snap:
        bb = row["bodyBattery"]
        bb_s = f"+{bb['charged']}/-{bb['drained']}" if bb else "-"
        print(f"{row['date']:12} {str(row['restingHr'] or '-'):>9} {bb_s:>12}")
    return 0


def cmd_zones(args) -> int:
    z = zones.compute_zones(_load_profile(args.profile))
    print(json.dumps(z, indent=2))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="garmin-sync")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("auth", help="log in and cache a token")
    a.add_argument("--env", default=".env")
    a.set_defaults(func=cmd_auth)

    pu = sub.add_parser("push", help="build + schedule a plan JSON")
    pu.add_argument("plan")
    pu.add_argument("--dry-run", action="store_true")
    pu.set_defaults(func=cmd_push)

    we = sub.add_parser("wellness", help="recovery snapshot")
    we.add_argument("--days", type=int, default=7)
    we.set_defaults(func=cmd_wellness)

    zo = sub.add_parser("zones", help="print HR zones from profile")
    zo.add_argument("--profile", default="profile.json")
    zo.set_defaults(func=cmd_zones)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
