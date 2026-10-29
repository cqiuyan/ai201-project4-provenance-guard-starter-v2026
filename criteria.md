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
