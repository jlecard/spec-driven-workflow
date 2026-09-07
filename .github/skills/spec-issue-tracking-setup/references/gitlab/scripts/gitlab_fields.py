#!/usr/bin/env python3
"""Reads and writes GitLab issue fields (milestone, iteration, labels,
weight, due date) via `glab api`, for whichever project this repo's
issues are tracked in -- see spec-issue-tracking-setup's gitlab
reference (ISSUE_TRACKING.md) for why this exists and how it's meant to
be adapted into a project-specific tracking skill.

Milestones and iterations are resolved fresh on every run (never
hardcoded) -- a milestone/iteration relevant "now" changes as the
project's schedule moves forward, same reasoning as the GitHub
reference's project_fields.py.

Usage:
    python gitlab_fields.py fields [--project group/subgroup/project]
    python gitlab_fields.py set --issue IID [--issue IID ...] \
        --field "milestone=Sprint 14" --field "iteration=current" \
        --field "labels=+bug,+priority::1,-wontfix" --field "weight=3" \
        --field "due_date=+3bd" \
        [--project group/subgroup/project] [--date YYYY-MM-DD] [--dry-run]

Field value syntax for `set`:
    milestone   -> an exact milestone title, or "current" (the open
                    milestone with the nearest due date on/after today)
    iteration   -> an exact iteration title, or "current" (the iteration
                    whose [start_date, due_date] window contains today)
                    -- requires GitLab Premium/Ultimate with iterations
                    configured on the project's group; fails clearly if
                    none are found
    labels      -> comma-separated tokens, each prefixed "+" (add) or
                    "-" (remove), e.g. "+bug,+priority::1,-wontfix"
    weight      -> a plain number
    due_date    -> "today" (or --date), "+Nbd" (N business days from
                    today), "+Nd" (N calendar days), or YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from urllib.parse import quote


def run_glab_api(path: str, method: str = "GET", fields: dict | None = None) -> object:
    """Runs one `glab api` call and returns the parsed JSON body (or
    None for an empty response). `glab` is assumed already authenticated
    against this project's GitLab host -- self-managed instances work
    the same as gitlab.com as long as `glab auth status` is green."""
    cmd = ["glab", "api", path]
    if method != "GET":
        cmd += ["-X", method]
    for key, value in (fields or {}).items():
        cmd += ["-f", f"{key}={value}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout) if result.stdout.strip() else None


def project_path_from_remote() -> str:
    """Parses the `group/subgroup/project` path out of `git remote get-url
    origin` -- works for both the https and git@ remote forms, and for
    any host (self-managed GitLab instances are common, so the host
    itself is never assumed to be gitlab.com)."""
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True
    )
    url = result.stdout.strip()
    match = re.search(r"(?:https?://[^/]+/|git@[^:]+:)(.+?)(?:\.git)?$", url)
    if not match:
        raise SystemExit(f"Couldn't parse a project path from remote url: {url!r}")
    return match.group(1)


def encoded_project_id(project_path: str) -> str:
    """GitLab's REST API takes a project's `id` as either a numeric id
    or its URL-encoded full path (namespace/subgroups/project) -- the
    latter avoids one extra lookup call per invocation."""
    return quote(project_path, safe="")


def group_path_from_project(project_path: str) -> str:
    """The project's own top-level namespace path, used for the
    iterations lookup (iterations are configured on a group's cadence,
    not the project itself) -- best-effort: a project several subgroups
    deep may have its cadence on an ancestor group rather than this
    exact parent, so treat a 404 here as "no iterations found" rather
    than a hard error."""
    return project_path.rsplit("/", 1)[0]


def add_business_days(start: date, count: int) -> date:
    result = start
    added = 0
    while added < count:
        result += timedelta(days=1)
        if result.weekday() < 5:
            added += 1
    return result


def resolve_date(raw: str, today: date) -> str:
    if raw.lower() == "today":
        return today.isoformat()
    offset_match = re.fullmatch(r"\+(\d+)(d|bd)", raw, re.IGNORECASE)
    if offset_match:
        count, unit = int(offset_match.group(1)), offset_match.group(2).lower()
        target = add_business_days(today, count) if unit == "bd" else today + timedelta(days=count)
        return target.isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        raise SystemExit(
            f"{raw!r} isn't 'today', '+Nbd' (N business days), '+Nd' (N calendar days), "
            "or a YYYY-MM-DD date."
        )
    return raw


def resolve_milestone(raw: str, milestones: list[dict], today: date) -> int:
    if raw.lower() == "current":
        dated = sorted((m for m in milestones if m.get("due_date")), key=lambda m: m["due_date"])
        for m in dated:
            if date.fromisoformat(m["due_date"]) >= today:
                return m["id"]
        raise SystemExit("No open milestone has a due date on/after today -- pick one explicitly.")
    for m in milestones:
        if m["title"].lower() == raw.lower():
            return m["id"]
    titles = ", ".join(m["title"] for m in milestones)
    raise SystemExit(f"No open milestone named {raw!r} -- open milestones: {titles or '(none)'}")


def resolve_iteration(raw: str, iterations: list[dict], today: date) -> int:
    if not iterations:
        raise SystemExit(
            "No iterations found for this project's group -- Iterations require GitLab "
            "Premium/Ultimate with a cadence configured; fall back to milestones if this "
            "project doesn't have that."
        )
    if raw.lower() == "current":
        for it in iterations:
            start, end = date.fromisoformat(it["start_date"]), date.fromisoformat(it["due_date"])
            if start <= today <= end:
                return it["id"]
        raise SystemExit(f"No iteration covers {today.isoformat()}.")
    for it in iterations:
        if (it.get("title") or "").lower() == raw.lower():
            return it["id"]
    titles = ", ".join(it.get("title", "") for it in iterations)
    raise SystemExit(f"No iteration titled {raw!r} -- open iterations: {titles or '(none)'}")


def resolve_labels(raw: str) -> dict[str, str]:
    add, remove = [], []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        if token.startswith("+"):
            add.append(token[1:])
        elif token.startswith("-"):
            remove.append(token[1:])
        else:
            add.append(token)
    body: dict[str, str] = {}
    if add:
        body["add_labels"] = ",".join(add)
    if remove:
        body["remove_labels"] = ",".join(remove)
    return body


def cmd_fields(args: argparse.Namespace) -> None:
    project_path = args.project or project_path_from_remote()
    project_id = encoded_project_id(project_path)

    milestones = run_glab_api(f"projects/{project_id}/milestones?state=active") or []
    print("Open milestones:")
    for m in milestones:
        print(f"  {m['title']!r} (due {m.get('due_date', 'no due date')})")

    group_path = group_path_from_project(project_path)
    group_id = encoded_project_id(group_path)
    try:
        iterations = run_glab_api(f"groups/{group_id}/iterations?state=opened") or []
    except SystemExit:
        iterations = []
    print("\nOpen iterations (group cadence, Premium/Ultimate only):")
    if not iterations:
        print("  (none found -- not configured, or this tier doesn't have Iterations)")
    for it in iterations:
        print(f"  {it.get('title', '(untitled)')!r} ({it['start_date']} -> {it['due_date']})")


def cmd_set(args: argparse.Namespace) -> None:
    today = date.fromisoformat(args.date) if args.date else date.today()
    project_path = args.project or project_path_from_remote()
    project_id = encoded_project_id(project_path)

    milestones = None
    iterations = None
    body: dict[str, str] = {}

    for raw in args.field:
        if "=" not in raw:
            raise SystemExit(f"--field {raw!r} isn't in 'name=value' form.")
        name, _, value = raw.partition("=")
        name = name.strip().lower()

        if name == "milestone":
            if milestones is None:
                milestones = run_glab_api(f"projects/{project_id}/milestones?state=active") or []
            body["milestone_id"] = str(resolve_milestone(value, milestones, today))
        elif name == "iteration":
            if iterations is None:
                group_id = encoded_project_id(group_path_from_project(project_path))
                iterations = run_glab_api(f"groups/{group_id}/iterations?state=opened") or []
            body["iteration_id"] = str(resolve_iteration(value, iterations, today))
        elif name == "labels":
            body.update(resolve_labels(value))
        elif name == "weight":
            body["weight"] = str(float(value)) if "." in value else value
        elif name == "due_date":
            body["due_date"] = resolve_date(value, today)
        else:
            raise SystemExit(f"Unknown field {name!r} -- expected one of: milestone, iteration, labels, weight, due_date")

    if args.dry_run:
        print(f"Would PUT to issue(s) {args.issue} on {project_path}: {body}")
        return

    for iid in args.issue:
        run_glab_api(f"projects/{project_id}/issues/{iid}", method="PUT", fields=body)
    print(f"Set {len(body)} field(s) on {len(args.issue)} issue(s): {', '.join(str(n) for n in args.issue)}")


def main() -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--project", help="group/subgroup/project path (defaults to `git remote get-url origin`)")

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[common]
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fields_parser = subparsers.add_parser(
        "fields", help="Print open milestones and iterations", parents=[common]
    )
    fields_parser.set_defaults(func=cmd_fields)

    set_parser = subparsers.add_parser(
        "set", help="Set one or more fields on one or more issues", parents=[common]
    )
    set_parser.add_argument("--issue", type=int, action="append", required=True, dest="issue")
    set_parser.add_argument(
        "--field", action="append", required=True,
        help='"name=value" -- repeatable; name is one of milestone/iteration/labels/weight/due_date'
    )
    set_parser.add_argument("--date", help="Override 'today' for value resolution (YYYY-MM-DD) -- for testing")
    set_parser.add_argument("--dry-run", action="store_true")
    set_parser.set_defaults(func=cmd_set)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
