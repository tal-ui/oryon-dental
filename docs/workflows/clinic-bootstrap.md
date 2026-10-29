# Bootstrapping a real clinic from a profile (Israel example)

> Runbook. Audience: whoever installs DentalPin for one specific practice
> — here Dr. Liad Oryon's dental clinic in Israel — and wants the first
> run to be scripted and repeatable instead of typed into the wizard.

## What you get

One command creates exactly what the browser wizard (`/setup`) would:

| Piece | Where it comes from |
|---|---|
| Clinic row: name, dealer number, country `IL`, ILS, `Asia/Jerusalem`, communications language `he` | `backend/app/core/auth/country_presets.py` (`IL` preset) |
| Admin account, flagged as a professional (solo practice) | the profile file |
| VAT types: **18 % (default)** + exempt (עוסק פטור) | catalog `il` preset, seeded on `clinic.created` |
| Stock treatment catalog at price 0 (Spanish reference prices are meaningless in ILS — price it in Settings → Catalog) | catalog module |
| Invoice series `FAC` / `RECT` | billing module |
| One room, `חדר 1` | agenda module |
| Weekly hours Sun–Thu 09:00–18:00, Fri 09:00–13:00, Shabbat closed | schedules module (`DEFAULT_WEEKLY_TEMPLATES["IL"]`) |
| Agenda week starting on Sunday | derived from the clinic country (`useWeekStart`) |

Everything above is editable afterwards in Settings; the script only
removes the typing.

## Steps

1. **Stack up** — `docker compose up -d` (dev) or the production compose.
   Set the white-label name in `.env` first if you want it on the login
   page from the first boot:

   ```bash
   APP_NAME="Oryon Dental"
   APP_LOGO=/logo-oryon.svg   # teal tooth-and-ring mark shipped in frontend/public/
   EMAIL_FROM_NAME="Oryon Dental"
   ```

2. **Edit the profile** — `scripts/clinics/oryon.env`. Put the real
   9-digit dealer number in `CLINIC_TAX_ID` (the placeholder is
   `000000000`; invoices must carry the real one), the address, and the
   admin email. The password is deliberately *not* in the file.

3. **Run it** — from the repo root, on the host:

   ```bash
   python3 scripts/bootstrap_clinic.py scripts/clinics/oryon.env
   # or non-interactively
   CLINIC_ADMIN_PASSWORD='…12+ chars, letters and digits…' \
     python3 scripts/bootstrap_clinic.py scripts/clinics/oryon.env
   # remote backend
   python3 scripts/bootstrap_clinic.py scripts/clinics/oryon.env --api https://clinic.example.com
   ```

   Standard library only; it prints the payload it sends (minus the
   password) and the outcome. `201` = created, `409` = this instance was
   already initialised (safe to re-run; nothing changes).

4. **Sign in** at the app with the admin email. Pick **עברית** in the
   language switcher if the browser didn't already; the UI flips to RTL.

5. **Finish in the app** — the dashboard's *Getting started* card tracks
   what is left: clinic address (shows on quotes/invoices), catalog prices,
   SMTP or WhatsApp for patient messages, the first patient.

## Israel-specific notes

- **VAT.** Catalog prices are entered **net**; quotes and invoices add the
  18 %. If the practice is an עוסק פטור, set the exempt type as default
  under Settings → Billing & tax → VAT types.
- **Invoices.** Patient (B2C) invoices need no allocation number. B2B
  invoices above the Israel Tax Authority threshold do — that is not
  implemented; see `docs/technical/country-readiness.md`.
- **Week.** The agenda and the clinic-hours grid start on Sunday because
  the clinic's country is `IL`; a Hebrew UI on a non-Israeli clinic keeps
  Monday.
- **Communications.** Patient emails go out in Hebrew (RTL templates under
  `backend/templates/email/he/`); the WhatsApp/SMS channels need a
  provider (Settings → Communications).

## Other clinics

Copy `scripts/clinics/oryon.env`, change the values, run the script with
the new file. A country without a preset falls back to the generic one
(EUR / UTC / English) — set `CLINIC_CURRENCY`, `CLINIC_TIMEZONE` and
`CLINIC_LANGUAGE` explicitly in that case.
