#!/usr/bin/env python3
"""Bootstrap a real (non-demo) clinic on a fresh install, from a profile file.

Drives the same first-run contract as the browser wizard — ``POST
/api/v1/auth/setup`` — so everything the wizard promises happens here too:
the country preset (currency, timezone, language, VAT preset), the
``clinic.created`` seeding (VAT types, stock catalog, invoice series, a
cabinet, weekly hours) and the admin account. Nothing is duplicated from
the backend; this is a thin, repeatable client for it.

The endpoint is self-closing (409 once any user exists), so re-running the
script is safe and reports the instance as already initialised.

Profile files are plain ``KEY=value`` lines (``scripts/clinics/*.env``).
The admin password is never stored in a profile: pass it with
``CLINIC_ADMIN_PASSWORD`` or type it at the prompt (12+ characters, a
letter and a digit, mirrored server-side).

Run (stack up: ``docker compose up -d``)::

    python3 scripts/bootstrap_clinic.py scripts/clinics/oryon.env
    CLINIC_ADMIN_PASSWORD='…' python3 scripts/bootstrap_clinic.py scripts/clinics/oryon.env
    python3 scripts/bootstrap_clinic.py scripts/clinics/oryon.env --api http://192.168.1.20:8000

Standard library only — runs on the host, no backend checkout required.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Profile key → setup payload field. Keys absent from the profile and the
# environment are simply not sent, so the server-side preset applies.
_FIELDS: dict[str, str] = {
    "CLINIC_NAME": "clinic_name",
    "CLINIC_TAX_ID": "clinic_tax_id",
    "CLINIC_COUNTRY": "country",
    "CLINIC_LANGUAGE": "language",
    "CLINIC_TIMEZONE": "timezone",
    "CLINIC_CURRENCY": "currency",
    "CLINIC_STREET": "clinic_street",
    "CLINIC_CITY": "clinic_city",
    "CLINIC_POSTAL_CODE": "clinic_postal_code",
    "CLINIC_ADMIN_FIRST_NAME": "admin_first_name",
    "CLINIC_ADMIN_LAST_NAME": "admin_last_name",
    "CLINIC_ADMIN_EMAIL": "admin_email",
}
_REQUIRED = ("clinic_name", "clinic_tax_id", "admin_first_name", "admin_last_name", "admin_email")


def read_profile(path: Path) -> dict[str, str]:
    """Parse ``KEY=value`` lines; ``#`` comments and blank lines are skipped.

    Values may be wrapped in single or double quotes (needed for names with
    spaces or Hebrew punctuation such as ``ד"ר``).
    """
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        values[key.strip()] = value
    return values


def build_payload(profile: dict[str, str], password: str) -> dict[str, object]:
    """Environment overrides the profile; empty values are dropped."""
    payload: dict[str, object] = {}
    for key, field in _FIELDS.items():
        value = os.environ.get(key) or profile.get(key) or ""
        if value:
            payload[field] = value
    missing = [f for f in _REQUIRED if f not in payload]
    if missing:
        raise SystemExit(f"profile is missing: {', '.join(missing)}")
    payload["admin_password"] = password
    professional = os.environ.get("CLINIC_ADMIN_IS_PROFESSIONAL") or profile.get(
        "CLINIC_ADMIN_IS_PROFESSIONAL", "true"
    )
    payload["admin_is_professional"] = professional.strip().lower() in {"1", "true", "yes"}
    return payload


def post_setup(api: str, payload: dict[str, object]) -> tuple[int, dict]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{api.rstrip('/')}/api/v1/auth/setup",
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 - fixed scheme/host from CLI
            return resp.status, json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read() or b"{}")
        except json.JSONDecodeError:
            detail = {}
        return exc.code, detail
    except urllib.error.URLError as exc:
        raise SystemExit(f"cannot reach {api}: {exc.reason} — is the stack up?") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "profile", type=Path, help="KEY=value profile, e.g. scripts/clinics/oryon.env"
    )
    parser.add_argument(
        "--api",
        default=os.environ.get("API_BASE_URL", "http://localhost:8000"),
        help="backend origin (default: $API_BASE_URL or http://localhost:8000)",
    )
    args = parser.parse_args(argv)

    if not args.profile.is_file():
        raise SystemExit(f"profile not found: {args.profile}")
    profile = read_profile(args.profile)

    password = os.environ.get("CLINIC_ADMIN_PASSWORD") or ""
    while len(password) < 12:
        if not sys.stdin.isatty():
            raise SystemExit("set CLINIC_ADMIN_PASSWORD (12+ chars, letter + digit)")
        password = getpass.getpass("Admin password (12+ chars, letter + digit): ")

    payload = build_payload(profile, password)
    shown = {k: v for k, v in payload.items() if k != "admin_password"}
    print(f"POST {args.api}/api/v1/auth/setup")
    print(json.dumps(shown, ensure_ascii=False, indent=2))

    status, data = post_setup(args.api, payload)
    if status == 201:
        print(f"\nClinic created. Sign in at the app with {payload['admin_email']}.")
        return 0
    if status == 409:
        print("\nThis instance is already initialised — nothing to do.")
        return 0
    detail = data.get("detail", data)
    print(f"\nSetup failed ({status}): {json.dumps(detail, ensure_ascii=False)}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
