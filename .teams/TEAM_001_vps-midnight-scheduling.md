# TEAM_001 — VPS midnight scheduling

## Goal
Guarantee bot execution at **00:00:00** and **06:00:00** (America/Toronto) with ~seconds accuracy (no GitHub Actions queue delays).

## Recommendation
Run the bot on a small always-on Linux VPS using:
- `chrony` (NTP time sync)
- `systemd` service + timer (`AccuracySec=1s`)

## Notes
- GitHub Actions scheduled workflows are best-effort and can start late (minutes) due to runner availability.
- VPS removes queue latency; timer triggers are local and deterministic.
