"""Authenticate to Garmin Connect and cache a token.

Credentials are read from a .env file (gitignored) so nothing is typed into a
chat session or shell history. After a successful login a token is cached and the
password is no longer needed.
"""
import getpass
import os
import sys

from garminconnect import Garmin

DEFAULT_TOKENSTORE = os.path.expanduser("~/.garminconnect")


def load_env(path: str = ".env") -> None:
    """Minimal KEY=VALUE .env loader (no external dependency)."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _cred(key: str, prompt: str, secret: bool = False) -> str | None:
    val = os.environ.get(key)
    if val:
        return val
    if sys.stdin.isatty():
        return getpass.getpass(prompt) if secret else input(prompt).strip()
    return None


def authenticate(tokenstore: str = DEFAULT_TOKENSTORE, env_path: str = ".env") -> Garmin:
    """Log in (using .env creds, MFA if needed) and cache a token. Returns client."""
    load_env(env_path)
    email = _cred("GARMIN_EMAIL", "Garmin email: ")
    password = _cred("GARMIN_PASSWORD", "Garmin password: ", secret=True)
    if not email or not password:
        raise SystemExit(
            "Missing credentials. Set GARMIN_EMAIL and GARMIN_PASSWORD in .env "
            "(copy .env.example), then rerun `garmin-sync auth`."
        )

    garmin = Garmin(email=email, password=password, return_on_mfa=True)
    result1, result2 = garmin.login()
    if result1 == "needs_mfa":
        mfa = os.environ.get("GARMIN_MFA")
        if not mfa and sys.stdin.isatty():
            mfa = input("MFA code: ").strip()
        if not mfa:
            raise SystemExit(
                "Account needs MFA. Add a fresh GARMIN_MFA=code to .env and rerun."
            )
        garmin.resume_login(result2, mfa)

    garmin.garth.dump(tokenstore) if hasattr(garmin, "garth") else garmin.client.dump(tokenstore)
    return garmin


def load_client(tokenstore: str = DEFAULT_TOKENSTORE) -> Garmin:
    """Load a Garmin client from the cached token (no password)."""
    garmin = Garmin()
    garmin.login(tokenstore)
    return garmin
