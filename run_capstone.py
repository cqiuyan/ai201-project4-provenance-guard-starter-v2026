#!/usr/bin/env python3
"""
Run the five capstone criteria in criteria.md, three trials each.  <- UNIT 9

    python run_capstone.py --label before
    python run_capstone.py --label after

You don't start the service yourself. Each trial starts its own fresh copy on
a spare port (5052), so criterion 3 gets a real cold start and criterion 5 gets
fresh rate-limit counters, then stops it. A server you already have running on
5000 is left alone. Criterion 4 makes its own fresh clone from GitHub on every
trial, follows RUNNING.md in it, then deletes it.

Every request it sends is logged by the service as usual, in logs/audit.jsonl,
and each check reads back exactly the entries its own requests created.

The texts it submits are test passages written for this script, each with a
marker sentence that's unique to its criterion, trial and position. That's
what lets criterion 2 search the log for them.

It writes results/capstone_<date>_<label>.md with every trial's real output.
"""

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

import audit
import config

ROOT = Path(__file__).parent
REPO_URL = "https://github.com/cqiuyan/ai201-project4-provenance-guard-starter-v2026.git"

PASSAGES = [
    "The bus was late again this morning, so I walked the long way past the bakery and bought two cinnamon rolls.",
    "My grandfather kept bees for forty years and never wore gloves, because he said the bees knew who he was.",
    "We lost the final by one goal, and nobody talked on the bus home until our keeper started singing badly.",
    "I tried to bake sourdough during exams, and the loaf came out as flat as a frisbee but we ate it anyway.",
    "The library heater on the third floor breaks at ten, so by eleven everyone up there is typing in gloves.",
    "My first apartment had a window that would not close, so a rolled towel was the whole heating system.",
    "Regular exercise strengthens the heart, improves mood, and helps people sleep better through the night.",
    "Organizations that communicate clearly tend to avoid costly misunderstandings and deliver better results.",
    "Reading every day expands vocabulary, improves concentration, and gives people a way to unwind at night.",
    "Good time management means setting priorities, breaking big tasks into steps, and taking real breaks.",
]


def passage(criterion, trial, i):
    """A valid submission (well over 20 words) with a sentence nobody else sent."""
    marker = (f"Capstone marker sentence {criterion}-{trial}-{i} mentions a plum lantern "
              f"numbered {criterion}{trial}{i:02d} beside the quiet harbour wall.")
    return f"{PASSAGES[(i - 1) % len(PASSAGES)]} {marker}", marker


# ── The service, one fresh copy per trial ─────────────────────────────────────

def start_service(port):
    env = {**os.environ, "PORT": str(port), "AI201_DEBUG": "0"}
    proc = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}"
    for _ in range(60):
        try:
            requests.get(f"{url}/health", timeout=2)
            return proc, url
        except requests.RequestException:
            time.sleep(0.5)
    proc.terminate()
    raise RuntimeError(f"the service didn't start on port {port}")


def stop_service(proc):
    proc.terminate()
    proc.wait(timeout=20)


def send(url, path, body=None, raw=None):
    """POST and return (status, parsed JSON body or None)."""
    if raw is not None:
        r = requests.post(url + path, data=raw, timeout=120,
                          headers={"Content-Type": "application/json"})
    else:
        r = requests.post(url + path, json=body, timeout=120)
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, None


def new_entries(since):
    """Audit entries written after the log had `since` entries."""
    return audit.read_entries()[since:]


def is_ms(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


# ── Criterion 1: every request leaves timing and input metadata ──────────────

def criterion_1(url, trial):
    start = len(audit.read_entries())
    flood = f"c1_t{trial}_writer"
    ids = []
    sent = []
    for i in range(1, 6):
        text, _ = passage(1, trial, i)
        status, body = send(url, "/submit", {"text": text, "creator_id": flood})
        ids.append((body or {}).get("content_id"))
        sent.append(("submit, accepted", status))
    text, _ = passage(1, trial, 6)
    sent.append(("submit, 6th from same writer", send(url, "/submit", {"text": text, "creator_id": flood})[0]))
    sent.append(("submit, empty text", send(url, "/submit", {"text": "", "creator_id": f"c1_t{trial}_empty"})[0]))
    sent.append(("submit, no text", send(url, "/submit", {"creator_id": f"c1_t{trial}_missing"})[0]))
    sent.append(("submit, text null", send(url, "/submit", {"text": None, "creator_id": f"c1_t{trial}_null"})[0]))
    sent.append(("submit, text a number", send(url, "/submit", {"text": 42, "creator_id": f"c1_t{trial}_number"})[0]))
    sent.append(("submit, bad JSON", send(url, "/submit", raw='{"text": "unterminated')[0]))
    sent.append(("appeal, real id", send(url, "/appeal", {"content_id": ids[0], "reasoning": "I wrote this."})[0]))

    entries = new_entries(start)
    checks = []
    for entry in entries:
        problems = []
        if not entry.get("timestamp"):
            problems.append("no timestamp")
        if not is_ms(entry.get("duration_ms")):
            problems.append("duration_ms missing or not a number >= 0")
        has_outcome = entry.get("status") and (
            entry.get("guess") or entry.get("reason") or entry.get("event") == "appeal")
        if not has_outcome:
            problems.append("no identifiable outcome")
        is_submit = entry.get("status") == "decided" or entry.get("endpoint") == "/submit"
        if is_submit:
            text_fields = (isinstance(entry.get("text_chars"), int)
                           and isinstance(entry.get("text_words"), int)
                           and isinstance(entry.get("text_hash"), str)
                           and len(entry["text_hash"]) == 12)
            if not text_fields and not entry.get("input_type"):
                problems.append("no text_chars/text_words/12-char text_hash and no input_type")
        checks.append({"entry": entry, "problems": problems})

    complete = sum(not c["problems"] for c in checks)
    return {
        "result": f"{complete}/12",
        "passed": len(entries) == 12 and complete == 12,
        "requests": [{"sent": s, "status": code} for s, code in sent],
        "entries_written": len(entries),
        "checks": checks,
    }


# ── Criterion 2: the log never stores submitted writing ──────────────────────

def criterion_2(url, trial):
    start = len(audit.read_entries())
    sent = []
    for i in range(1, 11):
        text, marker = passage(2, trial, i)
        status, body = send(url, "/submit", {"text": text, "creator_id": f"c2_t{trial}_w{i:02d}"})
        sent.append({"text": text, "marker": marker, "status": status,
                     "content_id": (body or {}).get("content_id")})

    entries = new_entries(start)
    raw_log = "\n".join(json.dumps(e, ensure_ascii=False) for e in entries)
    by_id = {e.get("content_id"): e for e in entries if e.get("status") == "decided"}
    rows = []
    for s in sent:
        sentences = [x.strip() for x in s["text"].split(". ") if x.strip()]
        leaked = s["text"] in raw_log or any(x.rstrip(".") in raw_log for x in sentences)
        e = by_id.get(s["content_id"], {})
        has_meta = (isinstance(e.get("text_chars"), int) and isinstance(e.get("text_words"), int)
                    and isinstance(e.get("text_hash"), str) and len(e["text_hash"]) == 12)
        rows.append({"marker": s["marker"], "status": s["status"], "leaked": leaked,
                     "text_chars": e.get("text_chars"), "text_words": e.get("text_words"),
                     "text_hash": e.get("text_hash")})

    leaks = sum(r["leaked"] for r in rows)
    with_meta = sum(r["text_chars"] is not None and r["text_hash"] is not None
                    and len(r["text_hash"]) == 12 for r in rows)
    return {
        "result": f"{leaks}/10 leaked, {with_meta}/10 with metadata",
        "passed": leaks == 0 and with_meta == 10,
        "rows": rows,
    }


# ── Criterion 3: timings, and the cost they give ─────────────────────────────

def criterion_3(url, trial):
    start = len(audit.read_entries())
    text, _ = passage(3, trial, 0)
    status, body = send(url, "/submit", {"text": text, "creator_id": f"c3_t{trial}_cold"})
    cold_id = (body or {}).get("content_id")
    warm_ids = []
    for i in range(1, 11):
        text, _ = passage(3, trial, i)
        status, body = send(url, "/submit", {"text": text, "creator_id": f"c3_t{trial}_w{i:02d}"})
        warm_ids.append((body or {}).get("content_id"))

    by_id = {e.get("content_id"): e for e in new_entries(start) if e.get("status") == "decided"}
    cold = by_id.get(cold_id, {}).get("duration_ms")
    warm = [by_id.get(cid, {}).get("duration_ms") for cid in warm_ids]
    timed = [d for d in warm if is_ms(d)]
    mean = round(sum(timed) / len(timed), 1) if timed else None
    return {
        "result": f"{len(timed)}/10 timed, mean {mean} ms",
        "passed": len(timed) == 10 and mean is not None and mean < 200,
        "cold_ms": cold,
        "warm_ms": warm,
        "warm_mean_ms": mean,
        "per_100_submissions_s": round(mean * 100 / 1000, 2) if mean is not None else None,
    }


# ── Criterion 5: failed requests explain themselves and stay visible ──────────

def criterion_5(url, trial):
    writer = f"c5_t{trial}_writer"
    for i in range(1, 6):
        text, _ = passage(5, trial, i)
        send(url, "/submit", {"text": text, "creator_id": writer})

    start = len(audit.read_entries())
    sixth, _ = passage(5, trial, 6)
    cases = [
        ("empty text", "/submit", {"text": "", "creator_id": f"c5_t{trial}_empty"}, None, None),
        ("missing text", "/submit", {"creator_id": f"c5_t{trial}_missing"}, None, None),
        ("malformed JSON", "/submit", None, '{"text": "unterminated', None),
        ("appeal, nonexistent id", "/appeal", {"content_id": f"c5-t{trial}-no-such-id", "reasoning": "Mine."}, None, None),
        ("6th submit in a minute", "/submit", {"text": sixth, "creator_id": writer}, None, 429),
    ]
    responses = []
    for name, path, body, raw, _ in cases:
        responses.append(send(url, path, body, raw))

    entries = new_entries(start)
    rows = []
    for (name, path, _, _, must_be), (status, body), entry in zip(cases, responses, entries + [{}] * 5):
        ok_status = 400 <= status < 500 and (must_be is None or status == must_be)
        ok_body = isinstance(body, dict) and bool(body.get("error"))
        ok_entry = (entry.get("status") == "rejected" and bool(entry.get("reason"))
                    and entry.get("endpoint") == path and is_ms(entry.get("duration_ms")))
        rows.append({"case": name, "status": status, "error": (body or {}).get("error"),
                     "log_entry": entry, "passed": ok_status and ok_body and ok_entry})

    fabricated = [e for e in entries if e.get("status") == "decided" or e.get("event") == "appeal"]
    server_errors = sum(status >= 500 for status, _ in responses)
    good = sum(r["passed"] for r in rows)
    return {
        "result": f"{good}/5, {server_errors} 5xx, {len(fabricated)} fabricated",
        "passed": good == 5 and server_errors == 0 and not fabricated and len(entries) == 5,
        "rows": rows,
    }


# ── Criterion 4: a fresh clone runs from RUNNING.md alone ────────────────────

def criterion_4(trial, python, port):
    work = Path(tempfile.mkdtemp(prefix=f"capstone_clone_t{trial}_"))
    repo = work / "repo"
    steps = []
    free_gb = round(shutil.disk_usage(work).free / 1e9, 1)

    def run(name, cmd, **kw):
        t = time.perf_counter()
        p = subprocess.run(cmd, capture_output=True, text=True, **kw)
        steps.append({"step": name, "ok": p.returncode == 0,
                      "seconds": round(time.perf_counter() - t, 1),
                      "tail": (p.stdout + p.stderr).strip().splitlines()[-2:]})
        return p.returncode == 0

    venv_python = repo / ".venv" / "bin" / "python"
    ok = (run("git clone", ["git", "clone", "-q", REPO_URL, str(repo)])
          and run(f"python3 -m venv .venv ({python})", [python, "-m", "venv", ".venv"], cwd=repo)
          and run("pip install -r requirements.txt",
                  [str(venv_python), "-m", "pip", "install", "-q", "-r", "requirements.txt"], cwd=repo)
          and run("python detector.py", [str(venv_python), "detector.py"], cwd=repo)
          and run("python test.py", [str(venv_python), "test.py"], cwd=repo))

    ping_ok = submit_ok = False
    if ok:
        env = {**os.environ, "PORT": str(port), "AI201_DEBUG": "0", "VIRTUAL_ENV": str(repo / ".venv")}
        proc = subprocess.Popen([str(venv_python), "app.py"], cwd=repo, env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        url = f"http://127.0.0.1:{port}"
        try:
            for _ in range(60):
                try:
                    requests.get(f"{url}/health", timeout=2)
                    break
                except requests.RequestException:
                    time.sleep(0.5)
            status, body = send(url, "/ping", {"message": "hello"})
            ping_ok = status == 200 and isinstance(body, dict) and body.get("ok") is True
            text, _ = passage(4, trial, 1)
            status, body = send(url, "/submit", {"text": text, "creator_id": f"c4_t{trial}"})
            submit_ok = status == 200 and isinstance(body, dict) and bool(body.get("content_id"))
            steps.append({"step": "python app.py, then POST /ping and POST /submit",
                          "ok": ping_ok and submit_ok, "ping": ping_ok, "submit": submit_ok,
                          "submit_guess": (body or {}).get("guess")})
        finally:
            proc.terminate()
            proc.wait(timeout=20)

    changed = subprocess.run(["git", "status", "--porcelain", "--", ".", ":!logs"],
                             cwd=repo, capture_output=True, text=True).stdout.strip() if repo.exists() else ""
    shutil.rmtree(work, ignore_errors=True)
    passed = ok and ping_ok and submit_ok and not changed
    return {
        "result": "setup succeeded" if passed else "setup failed",
        "passed": passed,
        "free_disk_gb_before": free_gb,
        "source_changed": changed or None,
        "steps": steps,
    }


# ── Running and reporting ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", default="")
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--port", type=int, default=5052)
    parser.add_argument("--clone-port", type=int, default=5053)
    parser.add_argument("--python", default="python3",
                        help="the python3 a fresh terminal would use, for criterion 4")
    args = parser.parse_args()

    trials = []
    for t in range(1, args.trials + 1):
        print(f"\n--- trial {t}")
        proc, url = start_service(args.port)
        try:
            result = {"3": criterion_3(url, t)}   # first, so its cold request is the first one
            result["2"] = criterion_2(url, t)
            result["1"] = criterion_1(url, t)
            result["5"] = criterion_5(url, t)
        finally:
            stop_service(proc)
        result["4"] = criterion_4(t, args.python, args.clone_port)
        for n in "12345":
            print(f"  criterion {n}: {result[n]['result']:<40} {'pass' if result[n]['passed'] else 'MISS'}")
        trials.append(result)

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    suffix = f"_{args.label}" if args.label else ""
    out = config.RESULTS_DIR / f"capstone_{stamp}{suffix}.md"
    lines = [
        f"# Capstone run log — {args.label or 'unlabelled'}",
        "",
        "- Produced by: `run_capstone.py::main` (criteria in `run_capstone.py::criterion_1` … `criterion_5`)",
        f"- {args.trials} trials · {stamp}",
        "",
        "| Criterion | " + " | ".join(f"Run {t}" for t in range(1, args.trials + 1)) + " |",
        "|---|" + "---|" * args.trials,
    ]
    for n in "12345":
        lines.append(f"| {n} | " + " | ".join(
            f"{r[n]['result']} ({'pass' if r[n]['passed'] else 'MISS'})" for r in trials) + " |")
    for t, result in enumerate(trials, 1):
        lines += ["", f"## Trial {t}"]
        for n in "12345":
            lines += ["", f"### Criterion {n} — `run_capstone.py::criterion_{n}`", "",
                      "```json", json.dumps(result[n], indent=2, ensure_ascii=False), "```"]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
