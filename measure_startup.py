#!/usr/bin/env python3
"""
What it costs to start the service, and where the first-request delay goes.
<- UNIT 9, the improvement

    python measure_startup.py --label before
    python measure_startup.py --label after

Starts a fresh copy of the service on port 5052 three times. For each start
it records how long until /health answers, how much memory the process holds
once it's answering and before anyone submits anything, and how long the first
submission then takes (from its logged duration_ms). Stops the service after
each start. A server already running on 5000 is left alone.

Writes results/startup_<date>_<label>.md.
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

import audit
import config

ROOT = Path(__file__).parent
TEXT = ("The bus was late again this morning, so I walked the long way past the bakery "
        "and bought two cinnamon rolls, one for me and one for my roommate.")


def rss_mb(pid):
    out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True).stdout
    return round(int(out.strip()) / 1024, 1)


def one_start(port, n):
    env = {**os.environ, "PORT": str(port), "AI201_DEBUG": "0"}
    t = time.perf_counter()
    proc = subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}"
    try:
        while True:
            try:
                requests.get(f"{url}/health", timeout=2)
                break
            except requests.RequestException:
                if time.perf_counter() - t > 120:
                    raise RuntimeError("the service didn't answer within 120 s")
                time.sleep(0.1)
        ready_s = round(time.perf_counter() - t, 2)
        idle_mb = rss_mb(proc.pid)
        r = requests.post(f"{url}/submit", json={"text": TEXT, "creator_id": f"startup_{n}"}, timeout=120)
        cid = r.json().get("content_id")
        first_ms = next((e.get("duration_ms") for e in reversed(audit.read_entries())
                         if e.get("content_id") == cid), None)
        return {"start": n, "ready_s": ready_s, "idle_memory_mb": idle_mb,
                "first_submit_ms": first_ms, "first_submit_status": r.status_code}
    finally:
        proc.terminate()
        proc.wait(timeout=20)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--label", default="")
    parser.add_argument("--starts", type=int, default=3)
    parser.add_argument("--port", type=int, default=5052)
    args = parser.parse_args()

    rows = [one_start(args.port, n) for n in range(1, args.starts + 1)]
    for r in rows:
        print(json.dumps(r))

    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    suffix = f"_{args.label}" if args.label else ""
    out = config.RESULTS_DIR / f"startup_{stamp}{suffix}.md"
    out.write_text(
        f"# Start-up cost — {args.label or 'unlabelled'}\n\n"
        f"- Produced by: `measure_startup.py::main`\n- {stamp}\n\n```json\n"
        + "\n".join(json.dumps(r) for r in rows) + "\n```\n",
        encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
