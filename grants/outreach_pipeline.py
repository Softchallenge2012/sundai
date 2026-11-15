from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

PROSPECTS_PATH = Path(__file__).with_name("prospects.json")


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _isoformat_utc(dt: datetime | None = None) -> str:
    return (dt or _now_utc()).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_prospects(path: str | Path = PROSPECTS_PATH) -> dict:
    with Path(path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_prospects(data: dict, path: str | Path = PROSPECTS_PATH) -> None:
    with Path(path).open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
        fh.write("\n")


def add_prospect(
    name: str,
    organization: str,
    website: str,
    officer: str,
    stage: str = "new",
    mission_fit: str | None = None,
    focus_areas: list[str] | None = None,
    priority: str = "medium",
    source: str = "manual",
    path: str | Path = PROSPECTS_PATH,
) -> dict:
    data = load_prospects(path)
    prospect = {
        "id": f"prospect-{len(data.get('prospects', [])) + 1:03d}",
        "name": name,
        "organization": organization,
        "website": website,
        "program_officer": officer,
        "stage": stage,
        "last_contacted_at": None,
        "next_follow_up_at": None,
        "status": "pending",
        "notes": [],
        "mission_fit": mission_fit or "Unspecified program fit",
        "focus_areas": focus_areas or [],
        "priority": priority,
        "source": source,
        "created_at": _isoformat_utc(),
    }
    data.setdefault("prospects", []).append(prospect)
    save_prospects(data, path)
    return prospect


def update_status(
    prospect_id: str,
    stage: str | None = None,
    status: str | None = None,
    note: str | None = None,
    follow_up_days: int = 14,
    path: str | Path = PROSPECTS_PATH,
) -> dict:
    data = load_prospects(path)
    for prospect in data.get("prospects", []):
        if prospect["id"] == prospect_id:
            if stage:
                prospect["stage"] = stage
            if status:
                prospect["status"] = status
            if note:
                prospect["notes"].append({
                    "text": note,
                    "timestamp": _isoformat_utc(),
                })
            prospect["last_contacted_at"] = _isoformat_utc()
            prospect["next_follow_up_at"] = _isoformat_utc(_now_utc() + timedelta(days=follow_up_days))
            save_prospects(data, path)
            return prospect
    raise ValueError(f"Prospect {prospect_id} not found")


def generate_outreach_email(
    path: str | Path = PROSPECTS_PATH,
    prospect_id: str | None = None,
    prospect: dict | None = None,
    template: str = "intro",
) -> str:
    data = load_prospects(path)
    selected = prospect or next((p for p in data.get("prospects", []) if p.get("id") == prospect_id), None)
    if selected is None:
        raise ValueError("Prospect not found")

    name = selected.get("name", "Program Officer")
    org = selected.get("organization", "your organization")
    mission_fit = selected.get("mission_fit", "community-driven programs and equitable access")
    focus_areas = selected.get("focus_areas") or ["local resilience", "equitable opportunity"]
    focus_text = ", ".join(focus_areas[:3])

    if template == "follow_up":
        return (
            f"Subject: Following up on our shared priorities\n\n"
            f"Hi {name},\n\n"
            f"I wanted to follow up on my note introducing Neighborhood Grant Partners. We are building a community-centered funding strategy around {mission_fit}, and we believe that {org}'s work on {focus_text} is closely aligned.\n\n"
            f"If there is a fit, I would welcome the opportunity to share a brief overview of our work and learn about the priorities your team is tracking this cycle.\n\n"
            f"Thank you for your time and consideration.\n\n"
            f"Best,\n"
            f"[Your Name]"
        )

    return (
        f"Subject: Intro and alignment on community funding priorities\n\n"
        f"Hi {name},\n\n"
        f"I am writing from Neighborhood Grant Partners to introduce our work supporting community resilience and equitable access. We are particularly focused on {mission_fit}, and the priorities at {org} around {focus_text} stood out to us as highly relevant.\n\n"
        f"As a mission-aligned organization, we would value the chance to learn more about your funding priorities and whether there may be a natural fit for a brief conversation or a concept note aligned with your current cycle.\n\n"
        f"Thank you for your time, and I would be grateful for any guidance you can share on the most relevant next step.\n\n"
        f"Warmly,\n"
        f"[Your Name]"
    )


def list_due_followups(path: str | Path = PROSPECTS_PATH, days_ahead: int = 14) -> list[dict[str, Any]]:
    data = load_prospects(path)
    due: list[dict[str, Any]] = []
    cutoff = _now_utc() + timedelta(days=days_ahead)

    for prospect in data.get("prospects", []):
        next_follow_up = prospect.get("next_follow_up_at")
        if not next_follow_up:
            due.append(prospect)
            continue

        try:
            dt = datetime.fromisoformat(next_follow_up.replace("Z", "+00:00"))
        except ValueError:
            continue

        if dt <= cutoff:
            due.append(prospect)

    return sorted(due, key=lambda item: item.get("next_follow_up_at") or "0000-00-00T00:00:00Z")


def pipeline_summary(path: str | Path = PROSPECTS_PATH) -> dict:
    data = load_prospects(path)
    prospects = data.get("prospects", [])
    status = {"total": len(prospects)}
    for key in ["new", "contacted", "follow_up", "reply_received", "rejected"]:
        status[key] = sum(1 for p in prospects if p.get("stage") == key)
    return status


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage nonprofit outreach prospect records.")
    parser.add_argument("--add", nargs=4, metavar=("NAME", "ORGANIZATION", "WEBSITE", "OFFICER"), help="Add a new prospect")
    parser.add_argument("--mission-fit", help="Mission-fit description for the prospect")
    parser.add_argument("--focus-area", action="append", default=[], help="Add a focus area for the prospect")
    parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium", help="Priority level")
    parser.add_argument("--status-id", help="Update a prospect by ID")
    parser.add_argument("--stage", help="Stage to set for the updated prospect")
    parser.add_argument("--status", help="Status to set for the updated prospect")
    parser.add_argument("--note", help="Append a note to the prospect record")
    parser.add_argument("--summary", action="store_true", help="Print a summary of the pipeline")
    parser.add_argument("--due", action="store_true", help="List prospects due for follow-up")
    parser.add_argument("--email-id", help="Generate the outreach email draft for a prospect ID")
    parser.add_argument("--template", choices=["intro", "follow_up"], default="intro", help="Email template to generate")

    args = parser.parse_args()

    if args.add:
        prospect = add_prospect(
            *args.add,
            mission_fit=args.mission_fit,
            focus_areas=args.focus_area,
            priority=args.priority,
        )
        print(json.dumps(prospect, indent=2))
        return

    if args.status_id:
        updated = update_status(args.status_id, stage=args.stage, status=args.status, note=args.note)
        print(json.dumps(updated, indent=2))
        return

    if args.email_id:
        print(generate_outreach_email(prospect_id=args.email_id, template=args.template))
        return

    if args.due:
        print(json.dumps(list_due_followups(days_ahead=14), indent=2))
        return

    if args.summary:
        print(json.dumps(pipeline_summary(), indent=2))
        return

    print(json.dumps(load_prospects(), indent=2))


if __name__ == "__main__":
    main()
