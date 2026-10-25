"""Command-line entry point: ``powatlas <command>``.

Commands used by the ``collect.yml`` workflow: ``resolve-schedule``, ``plan``,
``collect``, ``report``. GitHub access reads ``GITHUB_TOKEN`` and
``GITHUB_REPOSITORY`` from the environment.
"""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from powatlas import __version__, collect
from powatlas.catalogue import load_catalogue, task_for_cron
from powatlas.github import GitHub
from powatlas.http import HttpClient
from powatlas.units import best_states, parse_unit_id

ISSUE_LABEL = "collecte"


def _now(text: str | None) -> datetime:
    if text is None:
        return datetime.now(timezone.utc)
    t = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("--now must carry a time zone (e.g. 2026-11-01T02:35:00Z)")
    return t.astimezone(timezone.utc)


def _output(**values: str) -> None:
    """Write key=value lines to $GITHUB_OUTPUT (Actions) or stdout."""
    text = "".join(f"{k}={v}\n" for k, v in values.items())
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text, end="")


def make_github() -> GitHub:
    return GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"])


def pc_token(env_file: Path) -> str:
    """Read-only GitHub token of the pilot's PC: POWATLAS_GITHUB_TOKEN, else the .env file."""
    if os.environ.get("POWATLAS_GITHUB_TOKEN"):
        return os.environ["POWATLAS_GITHUB_TOKEN"]
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            key, sep, value = line.strip().partition("=")
            if sep and key.strip() == "POWATLAS_GITHUB_TOKEN" and value.strip():
                return value.strip().strip("\"'")
    raise SystemExit(f"POWATLAS_GITHUB_TOKEN not set and not found in {env_file}")


def make_http(settings: dict, retries: int | None = None, max_backoff: float | None = None) -> HttpClient:
    h = settings["http"]
    return HttpClient(
        retries=h["retries"] if retries is None else retries, backoff=h["backoff"],
        max_backoff=h["max_backoff"] if max_backoff is None else max_backoff,
        min_interval=h["min_interval"], max_interval=h["max_interval"], timeout=h["timeout"],
    )


def _register_adapters() -> None:
    # Imported here so that adapters register themselves in powatlas.adapters.ADAPTERS.
    import powatlas.adapters.all  # noqa: F401


def cmd_resolve_schedule(args) -> int:
    _, tasks, _ = load_catalogue()
    task, attempt = task_for_cron(args.cron, tasks)
    _output(task=task, attempt=attempt)
    return 0


def cmd_plan(args) -> int:
    sources, tasks, _ = load_catalogue()
    now = _now(args.now)
    artifacts = make_github().list_artifacts()
    names = [a["name"] for a in artifacts]
    skip = collect.recently_attempted(artifacts, now, collect.RETRY_HOURS) if args.task == collect.AUTO else set()
    units = collect.plan(args.task, now, names, sources, tasks, skip=skip)
    # The report job starts after the collection (up to 90 min later): it uses this time.
    _output(units=json.dumps(units), now=f"{now:%Y-%m-%dT%H:%M:%SZ}")
    return 0


def cmd_collect(args) -> int:
    _register_adapters()
    sources, _, settings = load_catalogue()
    if args.skip_if_complete:
        # Another run may have completed the unit since this one was planned.
        unit = parse_unit_id(args.unit)
        if best_states(make_github().list_artifact_names()).get(unit) == "complete":
            print(f"{args.unit}: already complete, skipped")
            _output(state="already-complete")
            return 0
    m = collect.collect_unit(args.unit, Path(args.out), make_http(settings), sources, settings, _now(args.now))
    print(f"{args.unit}: {m.state}" + (f" (missing: {', '.join(m.missing[:10])})" if m.missing else ""))
    for note in m.notes:
        print(f"  note: {note}")
    _output(state=m.state)
    return 0


def cmd_report(args) -> int:
    sources, tasks, _ = load_catalogue()
    now = _now(args.now)
    gh = make_github()
    last_commit = gh.last_commit_date("main")
    losses, summary = collect.report(args.task, now, args.attempt, gh.list_artifact_names(), last_commit, sources,
                                     tasks)
    inactive = (now - last_commit).days >= collect.INACTIVITY_WARNING_DAYS
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(summary)
    print(summary)
    if args.task == collect.AUTO:
        inactive = inactive and now.hour == 12  # one failed run a day, not one an hour
    if losses:
        run = "{}/{}/actions/runs/{}".format(
            os.environ.get("GITHUB_SERVER_URL", "https://github.com"), os.environ.get("GITHUB_REPOSITORY", ""),
            os.environ.get("GITHUB_RUN_ID", ""))
        when = "the last trigger of each task" if args.task == collect.AUTO else f"the {args.attempt} trigger"
        body = f"Task `{args.task}`: units lost for good after {when}.\n\n{summary}\nRun: {run}\n"
        gh.open_or_comment_issue(f"Collecte : pertes du {now:%Y-%m-%d}", body, ISSUE_LABEL)
    return 1 if losses or inactive else 0


def cmd_sync(args) -> int:
    from powatlas.sync import STALE_WARNING_HOURS, sync

    _, _, settings = load_catalogue()
    gh = GitHub(settings["repository"], pc_token(Path(args.env)))
    r = sync(Path(args.data), gh, _now(None))
    print(f"new {r.new}, replaced {r.replaced}, kept {r.kept}, rejected {len(r.rejected)}")
    for name in r.rejected:
        print(f"  rejected (retried next time): {name}")
    if r.stale_hours > STALE_WARNING_HOURS:
        print(f"WARNING: newest artifact is {r.stale_hours:.0f} h old: check the collect workflow on GitHub "
              "(Actions tab; re-enable it if GitHub disabled it).")
        return 1
    return 1 if r.rejected else 0


def cmd_status(args) -> int:
    from datetime import date

    from powatlas.status import status

    print(status(Path(args.data), date.fromisoformat(args.start), date.fromisoformat(args.end)), end="")
    return 0


def probe_urls(source_id: str, day: str, steps: list[int]) -> list[str]:
    from datetime import date

    from powatlas.adapters.ecmwf import ecmwf_path

    sources, _, _ = load_catalogue()
    s = sources[source_id]
    d = date.fromisoformat(day)
    run = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    return [s.urls["aws"] + ecmwf_path(s.urls["model"], run, step) for step in steps]


def cmd_backfill_probe(args) -> int:
    from powatlas.backfill import probe

    _, _, settings = load_catalogue()
    http = make_http(settings)
    r = probe(http, probe_urls(args.source, args.day, [int(x) for x in args.steps.split(",")]), args.ranges)
    rate = r.requests / r.seconds if r.seconds else float("inf")
    print(f"requests {r.requests}, seconds {r.seconds:.1f} ({rate:.2f} req/s), retries {r.slowdowns}, "
          f"bytes {r.bytes / 1e6:.1f} MB")
    return 0


def cmd_backfill(args) -> int:
    from datetime import date

    from powatlas.backfill import backfill

    _register_adapters()
    sources, _, settings = load_catalogue()
    b = settings["backfill"]
    from powatlas.backfill import default_range, last_available_day

    source = sources[args.source]
    start, end = default_range(source, settings, _now(None))
    if args.start:
        start = date.fromisoformat(args.start)
    if args.end:
        end = min(date.fromisoformat(args.end), last_available_day(source, _now(None)))
    http = make_http(settings, retries=b["retries"], max_backoff=b["max_backoff"])
    r = backfill(source, start, end, Path(args.data),
                 http, settings, tuple(b["months"]), b["max_step"], args.max_hours,
                 retry_given_up=args.retry_given_up)
    print(f"done {r.done} (partial {r.partial}), skipped {r.skipped}, given up {r.given_up}"
          + (", stopped at --max-hours" if r.stopped else ""))
    return 0


def cmd_progress(args) -> int:
    from powatlas.backfill import default_range, progress, render_progress

    sources, _, settings = load_catalogue()
    months = tuple(settings["backfill"]["months"])
    for sid in settings["backfill"]["start"]:
        start, end = default_range(sources[sid], settings, _now(None))
        print(render_progress(sid, progress(sources[sid], start, end, Path(args.data), months)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="powatlas", description="PowAtlas daily archive.")
    parser.add_argument("--version", action="version", version=f"powatlas {__version__}")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("resolve-schedule", help="task and attempt of a cron expression")
    p.add_argument("--cron", required=True)
    p.set_defaults(func=cmd_resolve_schedule)

    p = sub.add_parser("plan", help="units of a task still to collect (JSON)")
    p.add_argument("--task", required=True)
    p.add_argument("--now")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("collect", help="collect one unit")
    p.add_argument("--unit", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--skip-if-complete", action="store_true", help="check the artifacts first (Actions)")
    p.add_argument("--now")
    p.set_defaults(func=cmd_collect)

    p = sub.add_parser("report", help="summary, issue and exit status of a task run")
    p.add_argument("--task", required=True)
    p.add_argument("--attempt", required=True, choices=["first", "last"])
    p.add_argument("--now")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("sync", help="bring new artifacts into the archive (pilot's PC)")
    p.add_argument("--data", required=True)
    p.add_argument("--env", default=".env", help="file holding POWATLAS_GITHUB_TOKEN (never committed)")
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("backfill-probe", help="measure the request rate on the AWS copy (pilot's PC)")
    p.add_argument("--source", required=True, choices=["ifs-0p25", "aifs-single"])
    p.add_argument("--day", required=True, help="AAAA-MM-JJ")
    p.add_argument("--steps", default="0,24,48,72")
    p.add_argument("--ranges", type=int, default=14, help="ranges read per step file")
    p.set_defaults(func=cmd_backfill_probe)

    p = sub.add_parser("backfill", help="historical 00 UTC runs from AWS into the archive (pilot's PC)")
    p.add_argument("--source", required=True, choices=["ifs-0p25", "aifs-single", "gfs-0p25"])
    p.add_argument("--from", dest="start", help="default: settings.backfill.start of the catalogue")
    p.add_argument("--to", dest="end", help="default: settings.backfill.end, else the last published day")
    p.add_argument("--data", required=True)
    p.add_argument("--max-hours", type=float, default=None, help="stop cleanly after this many hours")
    p.add_argument("--retry-given-up", action="store_true", help="collect given-up units again, counts reset")
    p.set_defaults(func=cmd_backfill)

    p = sub.add_parser("progress", help="progress bar of the historical backfill of each source (pilot's PC)")
    p.add_argument("--data", required=True)
    p.set_defaults(func=cmd_progress)

    p = sub.add_parser("status", help="complete / partial / missing units per source and day")
    p.add_argument("--data", required=True)
    p.add_argument("--from", dest="start", required=True)
    p.add_argument("--to", dest="end", required=True)
    p.set_defaults(func=cmd_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2
    return args.func(args)
