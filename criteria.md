# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. My own writing is almost never called AI

Of **10 pieces I wrote myself**, at most **1** is labelled high-confidence AI,
in **each** of the three trials.

**Why this target:** on a writing site a wrong accusation costs the writer far
more than a missed detection costs the site, so this is the number that
matters most. I allow 1 rather than 0 because signal one can't tell plain
human writing from AI writing (0.87 vs 0.89 when I measured it). Promising zero
would mean a target I can't honestly defend. And it has to hold in all three
trials, not on average.

---

## 2. Plain writing is never called AI

Of **5 plainly written human passages** (short sentences and common words, in
the style of a second-language or younger writer), **0** are labelled
high-confidence AI, and at least **4 of 5** are labelled "unsure" or
high-confidence human, in **each** of the three trials.

**Why this target:** this is the writer from my Milestone 1 false-positive
trace, and the one signal one is built to accuse: their passage scored
0.87 on the model signal alone. They have the least room to argue back, so for
them the target is zero, not "rarely". If my combining rule and thresholds
can't hold this, the system shouldn't be giving anyone a confident AI label.

---

## 3. Every label is reachable

From a set of **9 inputs** (3 I'm confident are AI-generated, 3 I'm confident
are human-written and 3 I judge borderline), each of the three labels,
**high-confidence human, unsure and high-confidence AI**, is produced by
**at least 1** input in **each** trial.

**Why this target:** a label no score can reach is a gap in my ranges, and the
most likely one is high-confidence AI going missing once I raise the threshold
to protect criteria 1 and 2. That would mean the detector never says anything
useful about AI text. I picked "at least 1 of each per trial" because a stable
range shouldn't depend on which trial happened to run.

---

## 4. Bad input is refused, never crashes, and leaves a trace

Of **6 malformed requests** (empty `text`, no `text` field, `text` set to
`null`, `text` that's a number, a 50,000-word `text` and a body that's a JSON
list instead of an object), **6 of 6** get a 4xx status with an `error` field
in the body, **0** get a 5xx, and **6 of 6** appear in the audit log as
`rejected`, in each trial.

**Why this target:** a crash on a malformed input is one of the most common
real failures, and a 500 tells the caller nothing about what to fix. It has to
be 6 of 6 because each of these is a decision I've already written into the
endpoint contract from Milestone 1; there's no randomness to allow for. The log
requirement is there because a refused request that leaves no trace is
invisible when I'm diagnosing an attack in unit 8.

---

## 5. Every appeal changes status and gets recorded

For **5 appeals** against real `content_id`s, **5 of 5** return `200` with
`status: "under_review"`, and **5 of 5** appear in `GET /log` as an `appeal`
entry *after* the original decision, which stays unchanged. **1 appeal**
against a made-up `content_id` returns `404` and creates no appeal entry.

**Why this target:** the appeal is the only thing standing between a wrong
accusation and nothing at all. An appeal that is silently lost is worse than
having no appeal button, because the writer thinks they've been heard. I'm
checking the fake-id case too, because a typo that "succeeds" would be that
same silent loss. `run_eval.py` only sends submissions, so I'll test this one
by hand with `curl`: submit, take the `content_id`, appeal, then read the log.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Capstone criteria (unit 9)

Written before running any capstone tests. The five criteria above are from
unit 7 and stay as they were.

## 1. Every request leaves useful timing and input metadata (extension)

In a test of 12 requests covering successful /submit decisions, rejected submissions, one rate-limited submission, and one successful /appeal, 12 of 12 produce an audit entry with a timestamp, a numeric duration_ms of 0 or more, and an identifiable outcome (status and either a guess or a reason/appeal event). Every /submit entry also has text_chars, text_words, and a 12-character text_hash when text is supplied as a string, or input_type when it is missing or invalid.

**Why this target (rather than stricter or looser):** I chose 12 requests because that is enough to exercise the different paths through my local service—accepted submissions, validation failures, rate limiting, and appeals—without simply repeating the same success case dozens of times. I require 12/12 complete records, not 11/12, because even one missing rejection could hide an attempted attack and one missing duration could distort my cost estimate. A larger sample would be useful for load testing, but would not make a missing field acceptable: these fields are generated deterministically on every request.

---

## 2. The public audit log never stores submitted writing (extension)

For 10 distinct valid submissions containing unique test sentences, 0 of 10 audit entries include the complete submitted text or any of those unique sentences verbatim. Instead, 10 of 10 contain the submission's character count, word count, and a 12-character SHA-256-derived hash.

**Why this target (rather than stricter or looser):** My audit log can be committed to a public repository, so even one leaked submission would expose someone's writing; that is why the acceptable leak count is 0, not 1 or 2. I use 10 distinct test passages so a test can check that none reappears verbatim in the log, while avoiding unnecessary real user data. Requiring no input metadata at all would be stricter about storage but would defeat the extension: text_chars, text_words, and the 12-character hash let me diagnose input size and duplicates without keeping the original passage. This criterion covers /submit text; appeal reasoning is a separate privacy limitation.

---

## 3. Timings are complete enough to estimate local compute cost (extension)

After one model-loading (cold) request, send 10 valid warm submissions. 10 of 10 must have numeric duration_ms values in the audit log, and their mean logged duration must be under 200 ms on the documented 8 GB Apple-silicon test laptop under a comparable idle workload. Report the mean in milliseconds and the approximate total compute time for 100 submissions using those readings; report the cold-start duration separately.

**Why this target (rather than stricter or looser):** I previously measured a 67.2 ms warm-request average, so a ceiling of 200 ms allows for normal background activity on my 8 GB laptop without treating a threefold slowdown as normal. A stricter 70 ms limit would likely fail because of ordinary machine variation, while a looser 1,000 ms limit could hide a significant performance regression. I require timing for all 10 requests because a missing slow request would make the average misleading. I measure the cold model-loading request separately so one startup delay does not distort the estimated cost of 100 routine submissions.

---

## 4. Someone can start the service from the documented local run path (extension)

On one fresh clone on a machine meeting the documented Python, disk, and memory requirements, a tester can follow RUNNING.md to install dependencies, make the GPT-2 model available, pass python test.py, start the service with python app.py, and get a successful JSON response from POST /ping and POST /submit, without changing project source code.

**Why this target (rather than stricter or looser):** My chosen deployment is Path B: local, not a public cloud host, so the meaningful success condition is one complete fresh-clone setup with no edits to source code—not a public URL or uptime guarantee. One independently repeatable setup is enough to uncover missing instructions or dependencies; asking for ten machines would test hardware compatibility beyond my project scope. I do not loosen the requirement to “the server starts on my laptop,” because that would miss fresh-install problems. I limit the test to documented hardware because my model needs roughly 9 GB free disk space, and an earlier run with 8.2 GB failed that requirement.

---

## 5. Failed requests return explanations and remain visible (extension; bad path)

Send 5 deliberately failing requests: empty text, missing text, malformed JSON, an /appeal with a nonexistent content_id, and a sixth /submit from the same creator_id within one minute of five accepted submissions. 5 of 5 must return a 4xx status (the final case specifically 429), a JSON error field, and a corresponding status: "rejected" audit entry containing reason, endpoint, and numeric duration_ms. 0 of 5 may return a 5xx error or create a fake successful decision/appeal.

**Why this target (rather than stricter or looser):** The five cases represent different failures my service explicitly handles, including the configured limit of 5 submissions per minute. I require 5/5 clear 4xx responses and rejection logs, rather than allowing 4/5, because one invisible refusal could conceal abusive traffic or leave a writer unable to tell why an appeal failed. A stricter goal such as zero milliseconds of response time is not meaningful on a local laptop; the important observable behavior is the correct error, recorded reason, endpoint, and duration. I also require zero fabricated decisions or appeals because a failed request must never look successful.
