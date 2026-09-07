#!/usr/bin/env python3
"""Reads and writes GitHub Projects v2 field values via `gh api graphql`,
for whichever project this repo's issues are tracked on -- see
spec-issue-tracking-setup's github reference (ISSUE_TRACKING.md) for why
this exists and how it's meant to be adapted into a project-specific
tracking skill.

Every field's id, option ids, and iteration-bucket ids are resolved
fresh on every run via the `fields` query below -- never hardcoded and
never cached to disk. They're project-specific (a recreated project, a
renamed field, or a rolled-forward iteration schedule all change them)
and cheap to look up, so there's nothing to gain from assuming a past
run's ids are still valid and real risk in being wrong silently (an
Iteration's own id changes every two weeks as new buckets are added).

Usage:
    python project_fields.py fields [--owner LOGIN] [--project-number N]
    python project_fields.py set --issue N [--issue N ...] \
        --field "Status=In progress" --field "Start date=today" \
        [--owner LOGIN] [--project-number N] [--repo owner/name] \
        [--date YYYY-MM-DD] [--dry-run]

Field value syntax for `set` (see resolve_value() for the exact rules):
    SINGLE_SELECT field  -> the option's name, e.g. "In progress"
    ITERATION field       -> "current" (the bucket containing today, or
                              --date if given), or an exact bucket title
                              e.g. "Iteration 3"
    DATE field             -> "today" (or --date), "end-of-current:<Iteration
                              field name>" (e.g. "end-of-current:Iteration"),
                              or a literal YYYY-MM-DD string
    TEXT / NUMBER field    -> the literal value, passed through as-is
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, timedelta

FIELDS_QUERY = """
query {{
  user(login: {owner}) {{
    projectV2(number: {number}) {{
      id
      fields(first: 30) {{
        nodes {{
          ... on ProjectV2FieldCommon {{ name id dataType }}
          ... on ProjectV2SingleSelectField {{ name id dataType options {{ id name }} }}
          ... on ProjectV2IterationField {{
            name id dataType
            configuration {{
              iterations {{ id title startDate duration }}
              completedIterations {{ id title startDate duration }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""


def gql_str(value: str) -> str:
    """Quotes+escapes a Python string for inline embedding in a GraphQL
    query/mutation -- values here (dates, titles, issue bodies) aren't
    trusted to be free of quotes/backslashes, so this isn't optional."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def run_graphql(query: str) -> dict:
    """Runs one GraphQL document through `gh` (already authenticated in
    this environment) and returns the parsed `data` object. `gh` itself
    reports a non-zero exit and useful stderr on a GraphQL error, so
    this just surfaces that rather than trying to re-interpret it."""
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)["data"]


def repo_owner_and_name() -> tuple[str, str]:
    """Parses owner/repo out of `git remote get-url origin` -- works for
    both the https and git@ remote forms, and for a fork/renamed remote
    without hardcoding a repo name."""
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True
    )
    url = result.stdout.strip()
    match = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?$", url)
    if not match:
        raise SystemExit(f"Couldn't parse owner/repo from remote url: {url!r}")
    return match.group(1), match.group(2)


def fetch_project(owner: str, number: int) -> tuple[str, dict[str, dict]]:
    """Returns (project id, {field name -> field dict}). A field dict
    always has name/id/dataType; SINGLE_SELECT adds `options` (list of
    {id, name}), ITERATION adds `configuration` (iterations +
    completedIterations, each {id, title, startDate, duration})."""
    query = FIELDS_QUERY.format(owner=gql_str(owner), number=number)
    data = run_graphql(query)
    project = data["user"]["projectV2"]
    if project is None:
        raise SystemExit(f"No project number {number} found for user {owner!r}.")
    fields = {f["name"]: f for f in project["fields"]["nodes"]}
    return project["id"], fields


def iteration_containing(field: dict, on_date: date) -> dict | None:
    """The iteration/quarter bucket that `on_date` falls in -- an
    ITERATION field's own `configuration.iterations` list already
    carries each bucket's startDate + duration (in days), so "current"
    is just "which bucket's [start, start+duration) window contains
    today," computed fresh each call rather than trusting a
    previously-resolved id (see module docstring)."""
    for iteration in field["configuration"]["iterations"]:
        start = date.fromisoformat(iteration["startDate"])
        end = start + timedelta(days=iteration["duration"])
        if start <= on_date < end:
            return iteration
    return None


def add_business_days(start: date, count: int) -> date:
    """`start` plus `count` weekdays (Mon-Fri), skipping weekends --
    Target date estimates are naturally expressed in working days
    ("about 3 days of work"), not calendar days, so a "+3bd" estimate
    given on a Thursday should land the following Tuesday, not Sunday."""
    result = start
    added = 0
    while added < count:
        result += timedelta(days=1)
        if result.weekday() < 5:
            added += 1
    return result


def resolve_value(field: dict, raw: str, fields: dict[str, dict], today: date) -> str:
    """Turns a --field "Name=Value" pair's raw string into the inline
    GraphQL fragment for updateProjectV2ItemFieldValue's `value` input
    (e.g. `{date: "2026-09-05"}`) -- see the module docstring's "Field
    value syntax" section for what each dataType accepts. Raises with a
    clear message rather than silently sending a value the field can't
    actually hold (e.g. a typo'd option name)."""
    data_type = field["dataType"]

    if data_type == "SINGLE_SELECT":
        for option in field["options"]:
            if option["name"].lower() == raw.lower():
                return f'{{singleSelectOptionId: {gql_str(option["id"])}}}'
        names = ", ".join(o["name"] for o in field["options"])
        raise SystemExit(f"{field['name']!r} has no option named {raw!r} -- options are: {names}")

    if data_type == "ITERATION":
        if raw.lower() == "current":
            iteration = iteration_containing(field, today)
            if iteration is None:
                raise SystemExit(
                    f"{field['name']!r} has no iteration bucket covering {today.isoformat()} "
                    "-- the schedule may need extending in the project's own settings."
                )
            return f'{{iterationId: {gql_str(iteration["id"])}}}'
        for iteration in field["configuration"]["iterations"]:
            if iteration["title"].lower() == raw.lower():
                return f'{{iterationId: {gql_str(iteration["id"])}}}'
        titles = ", ".join(i["title"] for i in field["configuration"]["iterations"])
        raise SystemExit(f"{field['name']!r} has no bucket titled {raw!r} -- buckets are: {titles}")

    if data_type == "DATE":
        if raw.lower() == "today":
            return f"{{date: {gql_str(today.isoformat())}}}"
        end_of_match = re.fullmatch(r"end-of-current:(.+)", raw, re.IGNORECASE)
        if end_of_match:
            source_name = end_of_match.group(1)
            source_field = fields.get(source_name)
            if source_field is None or source_field["dataType"] != "ITERATION":
                raise SystemExit(
                    f"{raw!r} refers to {source_name!r}, which isn't an Iteration-type field on this project."
                )
            iteration = iteration_containing(source_field, today)
            if iteration is None:
                raise SystemExit(f"{source_name!r} has no bucket covering {today.isoformat()}.")
            start = date.fromisoformat(iteration["startDate"])
            end = start + timedelta(days=iteration["duration"])
            return f"{{date: {gql_str(end.isoformat())}}}"
        offset_match = re.fullmatch(r"\+(\d+)(d|bd)", raw, re.IGNORECASE)
        if offset_match:
            count, unit = int(offset_match.group(1)), offset_match.group(2).lower()
            target = add_business_days(today, count) if unit == "bd" else today + timedelta(days=count)
            return f"{{date: {gql_str(target.isoformat())}}}"
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            raise SystemExit(
                f"{field['name']!r} is a date field -- {raw!r} isn't 'today', "
                "'+Nbd' (N business days from today), '+Nd' (N calendar days), "
                "'end-of-current:<Iteration field name>', or a YYYY-MM-DD date."
            )
        return f"{{date: {gql_str(raw)}}}"

    if data_type == "NUMBER":
        return f"{{number: {float(raw)}}}"

    # TEXT and anything else GitHub adds later: pass the literal string
    # through -- there's no fixed vocabulary to validate against.
    return f"{{text: {gql_str(raw)}}}"


def cmd_fields(args: argparse.Namespace) -> None:
    _, fields = fetch_project(args.owner, args.project_number)
    summary = {}
    for name, field in fields.items():
        entry = {"id": field["id"], "dataType": field["dataType"]}
        if "options" in field:
            entry["options"] = [o["name"] for o in field["options"]]
        if "configuration" in field:
            entry["iterations"] = [
                f"{i['title']} ({i['startDate']} +{i['duration']}d)"
                for i in field["configuration"]["iterations"]
            ]
        summary[name] = entry
    print(json.dumps(summary, indent=2))


def cmd_set(args: argparse.Namespace) -> None:
    today = date.fromisoformat(args.date) if args.date else date.today()
    repo_owner, repo_name = (args.repo.split("/", 1) if args.repo else repo_owner_and_name())
    project_id, fields = fetch_project(args.owner or repo_owner, args.project_number)

    assignments: list[tuple[str, str]] = []
    for raw in args.field:
        if "=" not in raw:
            raise SystemExit(f"--field {raw!r} isn't in 'Name=Value' form.")
        name, _, value = raw.partition("=")
        if name not in fields:
            raise SystemExit(f"No field named {name!r} on this project -- run `fields` to list them.")
        assignments.append((name, value))

    # Resolve every value up front (and fail before any mutation runs if
    # one is bad) rather than partially applying a batch.
    resolved = [(name, resolve_value(fields[name], value, fields, today)) for name, value in assignments]

    issue_query = "query {\n" + "".join(
        f'  i{idx}: repository(owner: {gql_str(repo_owner)}, name: {gql_str(repo_name)}) '
        f"{{ issue(number: {number}) {{ id number }} }}\n"
        for idx, number in enumerate(args.issue)
    ) + "}"
    issue_data = run_graphql(issue_query)
    node_ids = [issue_data[f"i{idx}"]["issue"]["id"] for idx in range(len(args.issue))]

    if args.dry_run:
        print(f"Would add {len(args.issue)} issue(s) to project {project_id} and set:")
        for name, fragment in resolved:
            print(f"  {name} = {fragment}")
        return

    add_mutation = "mutation {\n" + "".join(
        f"  a{idx}: addProjectV2ItemById(input: {{projectId: {gql_str(project_id)}, "
        f"contentId: {gql_str(node_id)}}}) {{ item {{ id }} }}\n"
        for idx, node_id in enumerate(node_ids)
    ) + "}"
    add_data = run_graphql(add_mutation)
    item_ids = [add_data[f"a{idx}"]["item"]["id"] for idx in range(len(node_ids))]

    set_lines = []
    counter = 0
    for item_id in item_ids:
        for name, fragment in resolved:
            set_lines.append(
                f"  u{counter}: updateProjectV2ItemFieldValue(input: {{projectId: {gql_str(project_id)}, "
                f"itemId: {gql_str(item_id)}, fieldId: {gql_str(fields[name]['id'])}, "
                f"value: {fragment}}}) {{ projectV2Item {{ id }} }}\n"
            )
            counter += 1
    run_graphql("mutation {\n" + "".join(set_lines) + "}")
    print(f"Set {len(resolved)} field(s) on {len(args.issue)} issue(s): {', '.join(str(n) for n in args.issue)}")


def main() -> None:
    # --owner/--project-number are defined on a shared parent parser (not
    # just the top-level one) so they can be written either before or
    # after the subcommand -- argparse doesn't let a subparser see its
    # parent's own options once the subcommand token has been consumed,
    # which otherwise makes `set --issue 51 --owner x` a confusing error
    # for anyone who writes global flags in the more natural, trailing
    # position.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--owner", help="Project owner login (defaults to the repo's own owner)")
    common.add_argument("--project-number", type=int, default=1)

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter, parents=[common]
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fields_parser = subparsers.add_parser(
        "fields", help="Print every field's id/options/iterations as JSON", parents=[common]
    )
    fields_parser.set_defaults(func=cmd_fields)

    set_parser = subparsers.add_parser(
        "set", help="Set one or more field values on one or more issues", parents=[common]
    )
    set_parser.add_argument("--issue", type=int, action="append", required=True, dest="issue")
    set_parser.add_argument("--field", action="append", required=True, help='"Field Name=Value" -- repeatable')
    set_parser.add_argument("--repo", help="owner/name (defaults to `git remote get-url origin`)")
    set_parser.add_argument("--date", help="Override 'today' for value resolution (YYYY-MM-DD) -- for testing")
    set_parser.add_argument("--dry-run", action="store_true")
    set_parser.set_defaults(func=cmd_set)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
