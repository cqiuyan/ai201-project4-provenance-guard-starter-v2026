# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

Provenance Guard takes a piece of writing and tells the writer whether it
reads as human-written, AI-generated, or something it can't call. If they
disagree with the result, they can appeal. A submission goes through seven
steps:

1. **The route checks the input:** `POST /submit` in `app.py`. It pulls out
   `text` and `creator_id` and refuses anything malformed before any scoring
   happens: a missing field, fewer than 20 words, more than 10,000 characters.
   A refusal returns a 4xx with an `error` and a `message`, and is logged as
   `rejected`.
2. **The submission gets an id:** a `content_id` (a UUID). From here on the
   submission has a name, which the log and `/appeal` both use.
3. **Signal one reads the words:** `detector.model_signal`. A local gpt2
   model measures how predictable the text is and turns that into
   `model_score`, 0–1, where higher means more AI-like.
4. **Signal two measures the shape:** `stylometry.style_signal`. It looks at
   how much sentence lengths vary and how much expressive punctuation there
   is, without reading a word, and produces `style_score`, 0–1, where higher
   means more AI-like.
5. **The combining rule makes one score:**
   `scoring.combine_signals`. It averages the two signals with equal weight.
   If they disagree by more than 0.4, the score is held in the unsure band.
6. **The label turns the score into words:** `scoring.score_to_label`.
   Below 0.35 is human, 0.35–0.75 is unsure, and above 0.75 is AI. Each
   comes with a full sentence written for the writer, not a number.
7. **The decision is logged, then returned:** `audit.log_decision`
   writes the scores, guess, label and `status: "decided"` to
   `logs/audit.jsonl`. The response goes back with the `content_id`, guess,
   combined score, label and both signal scores. The label is what the
   writer reads.

If the writer thinks it's wrong, `POST /appeal` with their `content_id` and
reasoning records an appeal next to the original decision and moves it to
`under_review`, so a person can look at it.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** how predictable the text is to a language model. A
local gpt2 model (`detector.py`) computes perplexity, its average surprise
at each next word over the first 400 tokens. That number is squashed onto
0–1 so that low surprise gives a high score. A perplexity of 45 scores 0.5.

**Why that might differ between human and AI writing:** a language model
writes by picking likely next words, so its output tends to be text another
model finds easy to predict. People make odder choices: a specific word
where a typical one would do, an abrupt turn, a detail nobody would guess.

**What it can't see:** who wrote the text. Predictability is a property of
the words, not the author, so anyone who writes in plain, common words and
short sentences scores as machine-like. My plain human paragraph about
running scored 0.81, next to AI boilerplate at 0.86. It fails the other way
too: AI text that uses rare or ornate words scores as human, because rare
words are exactly what gpt2 fails to predict. And it only reads the first
~300 words.

### Signal two — the style signal

**What it measures:** the shape of the text, without reading it
(`stylometry.py`):

- **Sentence-length spread:** stdev ÷ mean of words per sentence.
- **Expressive punctuation:** marks per 100 words (`; : ! ? ( ) — " …`).

The two are averaged. Type-token ratio is computed too but carries no
weight, for the reason given in the combining rule below.

**Why that might differ between human and AI writing:** "most likely next
word", averaged over a whole text, produces even, mid-length sentences and
tidy punctuation. Human writing is lumpier: a three-word sentence next to a
forty-word one, a dash, a bracketed aside.

**What it can't see:** what the text says. Anything that changes the shape
without changing the substance moves it, and all of these are cheap to do
on purpose:

- chopping sentences up or gluing them together
- dropping in a few dashes or semicolons
- pasting in a quotation

It also shares signal one's blind spot. A plain writer's even sentences and
lack of semicolons read as AI here too, so it agrees with signal one on
exactly the person who most needs it not to: my plain paragraph scored 0.88.
On short texts it's noisy. Two sentences are too few for "spread" to mean
much, which is the split case below.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** average the two signals with equal weight. Then, if the
signals disagree by more than 0.4, keep the result inside the "unsure" band,
whatever the average says. Two methods that disagree that much is
uncertainty, and the system should say so rather than pick a side.

I weight the signals equally because neither one deserves more trust. Signal
one accuses plain writers; signal two can be fooled by anyone who adds a few
dashes or changes their sentence lengths. A confident label in either
direction needs both signals pointing the same way.

**The numbers:**

- Weights: `WEIGHT_MODEL_SIGNAL = 0.5`, `WEIGHT_STYLE_SIGNAL = 0.5` (in `config.py`)
- Disagreement gap: `DISAGREEMENT_GAP = 0.4` (in `config.py`). Above it, the
  score is clamped to the range `HUMAN_THRESHOLD`–`AI_THRESHOLD`.
- Inside signal two (`stylometry.py::style_signal`), the average of two
  measures, each scaled to 0–1 where higher means more AI-like:
  - sentence-length spread (stdev ÷ mean): 0.20 or less scores 1.0, 0.70 or
    more scores 0.0, linear in between. One sentence scores 0.5 (no evidence).
  - expressive punctuation per 100 words (`; : ! ? ( ) — " …`): none scores
    0.75, 3 or more scores 0.0, linear in between. Having none is only weak
    evidence, because plenty of people never use a semicolon.
  - type-token ratio is computed and shown but has **zero weight**. On my test
    texts it pointed the wrong way: the AI text had the *more* varied
    vocabulary (0.92–0.95 against 0.83 for human).

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

"Dad's truck died on the bridge again, right in the middle lane, hazards
blinking like an apology. …": two long, vivid sentences.

- Signal one: **0.22** (human). The words are specific and hard to predict.
- Signal two: **0.75** (AI). Two sentences of similar length and no
  expressive punctuation look even and tidy.
- The gap is 0.54, which is over 0.4, so the rule keeps the score in the
  unsure band (0.49). It doesn't call this human just because one signal says
  so, and it can't call it AI. Signal two is the one that's wrong here: two
  sentences are too few for "spread" to mean much.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | below 0.35 | This reads like it was written by a person. Neither of our checks found the patterns we usually see in AI-generated writing. |
| unsure | 0.35 – 0.75 (both ends included) | We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID. |
| high-confidence AI | above 0.75 | This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it. |

The thresholds are in `config.py`: `HUMAN_THRESHOLD = 0.35`,
`AI_THRESHOLD = 0.75`. I raised the AI threshold from 0.65. My clearly-AI
test text scored 0.71, so it now lands in "unsure". That's one missed
detection, accepted so that human writing scoring 0.65–0.75 isn't accused.
It doesn't save the plain writer: my plain human paragraph scores 0.84, next
to real AI boilerplate at 0.85, and no threshold separates two scores that
close. That case is why the AI label says "this is not proof" and points to
the appeal.

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

The person reading "unsure" most often wrote every word themselves: formal
writing, short pieces and plain writing all land here. So it does three
things:

- It says plainly that *we* can't tell. The uncertainty belongs to the
  system, not to the writer.
- It says outright "this is not a finding that you used AI", so nobody has
  to read between the lines.
- It offers the appeal as something they *can* do, not something they have
  to do to clear their name.

It also never mentions a number. "0.58" would mean nothing to the writer and
would sound more precise than it is.


---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

The text is my plain human test paragraph. It gets the high-confidence AI
label: the false positive I traced in Milestone 1, and the case the appeal is
for.

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "I started running last spring because my doctor said I should. The first week was hard and I could only go about a mile. Now I run three times a week, usually in the morning before work. It helps me sleep better and I feel less stressed.", "creator_id": "qiuyan"}'
```

```json
{
  "confidence": 0.8408,
  "content_id": "44dde83d-c0d1-4cd5-a116-c76102052288",
  "creator_id": "qiuyan",
  "guess": "ai",
  "label": "This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it.",
  "model_score": 0.8066,
  "status": "decided",
  "style_score": 0.875
}
```

**The other two labels**, from the same run:

| Input | `model_score` | `style_score` | `confidence` | `guess` |
|---|---|---|---|---|
| Casual human (flooded dishwasher) | 0.389 | 0.0503 | 0.2197 | `human` |
| Formal human (Federalist No. 10 opening) | 0.449 | 0.7037 | 0.5764 | `unsure` |
| AI boilerplate ("In today's fast-paced digital landscape…") | 0.8558 | 0.8515 | 0.8537 | `ai` |

**A refused submission** (empty text)

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "", "creator_id": "qiuyan"}'
```

```json
{
  "error": "text_too_short",
  "message": "Text needs at least 20 words to be scored."
}
```

HTTP 400.

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "44dde83d-c0d1-4cd5-a116-c76102052288", "reasoning": "I wrote this myself about my own running routine. I write in short, plain sentences on purpose."}'
```

```json
{
  "content_id": "44dde83d-c0d1-4cd5-a116-c76102052288",
  "message": "Your appeal is recorded and a person will review this submission. The original result is not final.",
  "original_guess": "ai",
  "status": "under_review"
}
```

An appeal against an ID that doesn't exist is refused, not silently accepted:

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "not-a-real-id", "reasoning": "test"}'
```

```json
{
  "error": "unknown_content_id",
  "message": "No submission has that ID. Check it was copied exactly from your result."
}
```

HTTP 404.

**What the log shows afterwards**

The original decision is unchanged, and the appeal sits after it with
`status: "under_review"`.

```bash
$ curl "http://127.0.0.1:5000/log?limit=2"
```

```json
{
  "count": 2,
  "entries": [
    {
      "combined_score": 0.8408,
      "content_id": "44dde83d-c0d1-4cd5-a116-c76102052288",
      "creator_id": "qiuyan",
      "guess": "ai",
      "label": "This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it.",
      "model_score": 0.8066,
      "status": "decided",
      "style_score": 0.875,
      "timestamp": "2026-10-29T01:33:39+00:00"
    },
    {
      "content_id": "44dde83d-c0d1-4cd5-a116-c76102052288",
      "creator_id": "qiuyan",
      "event": "appeal",
      "reasoning": "I wrote this myself about my own running routine. I write in short, plain sentences on purpose.",
      "status": "under_review",
      "timestamp": "2026-10-29T01:34:00+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1: **

- *What I asked for:* I pasted my critera and asked for opinion for the five criterion. 
- *What came back:* four out of five are good with one recommendation to remove a redundant condition. 
- *What I changed:* I didn't change anything. 
 

**Moment 2: **

- *What I asked for:* I pasted the three label and ask what it thinks. 
- *What came back:* overall postivie with one concern "Even "unsure" might make me feel like I'm being accused of using AI. I would want to know whether it is simply an uncertain result or whether my writing is actually being flagged for review."
- *What I changed:* I didn't change anything.







<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 5 per minute, 50 per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

A real writer submits a few times an hour. At most they resubmit three or
four times in quick succession after small edits, to see if the result
changes. Five a minute never gets in their way, and no honest writer comes
near 50 in a day.

A script mapping my thresholds needs hundreds of nearly identical
submissions to find where "unsure" turns into "AI". At 50 a day it would
take 20 days to send a thousand variations from one caller, instead of 5
days at the starter's 200. Each submission also runs a language model for a
second or two, so 5 a minute caps how much of my laptop one caller can use.

I didn't go lower. 2 or 3 a minute would start blocking a writer checking a
few edits, and that's the person the limit is supposed to leave alone.

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

Per `creator_id`, falling back to the IP address when there isn't one
(`app.py::rate_limit_key`). That keeps one household or classroom sharing an
address from being counted as a single caller. The weakness is the other
direction: `creator_id` is whatever the caller sends, so a script that
invents a new one for every request never hits the limit at all. Counting
per address would catch that script but would lump a whole school's
network into one caller. Neither choice is safe; this one protects the
writers and leaves the door open to a script that rotates ids.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
15 submissions as 'flood_tester' against http://127.0.0.1:5000
The first one is slow while the model loads.

  [ 1/15] 200
  [ 2/15] 200
  [ 3/15] 200
  [ 4/15] 200
  [ 5/15] 200
  [ 6/15] 429
  [ 7/15] 429
  [ 8/15] 429
  [ 9/15] 429
  [10/15] 429
  [11/15] 429
  [12/15] 429
  [13/15] 429
  [14/15] 429
  [15/15] 429

============================================================
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
============================================================

10 of 15 were rate limited. Paste the run above into your README
under **Rate Limiting**, and check GET /log recorded the rejections.
```

Every one of the 10 rejections is in the audit log, e.g.:

```json
{"timestamp": "2026-11-10T23:02:36+00:00", "creator_id": "flood_tester", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json
{"timestamp": "2026-11-10T23:14:37+00:00", "content_id": "baa7e815-845b-4a60-81f4-bdd218d672c5", "creator_id": "attacker_FP03", "guess": "ai", "model_score": 0.8051, "style_score": 0.7468, "combined_score": 0.776, "label": "This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T23:14:37+00:00", "content_id": "316a565a-e567-4d05-9176-68b56764a7db", "creator_id": "attacker_FP02", "guess": "ai", "model_score": 0.7387, "style_score": 0.8347, "combined_score": 0.7867, "label": "This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T23:14:37+00:00", "content_id": "83b0edf8-e053-4895-ae97-88400dc87314", "creator_id": "attacker_FP04", "guess": "ai", "model_score": 0.8329, "style_score": 0.7083, "combined_score": 0.7706, "label": "This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T23:14:37+00:00", "content_id": "ced5ff4d-1a5e-4173-8738-570fa77ee2d0", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.7981, "combined_score": 0.7993, "label": "This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it.", "status": "decided"}
{"timestamp": "2026-11-10T23:14:37+00:00", "creator_id": "attacker_FP08", "event": "rejected", "status": "rejected", "reason": "text_too_short"}
{"timestamp": "2026-11-10T23:14:36+00:00", "content_id": "965d9eea-d0a3-4725-b881-896293c0cc83", "creator_id": "attacker_EV05", "guess": "human", "model_score": 0.3212, "style_score": 0.2473, "combined_score": 0.2843, "label": "This reads like it was written by a person. Neither of our checks found the patterns we usually see in AI-generated writing.", "status": "decided"}
{"timestamp": "2026-11-10T23:14:37+00:00", "content_id": "1160c40e-3894-40dc-84aa-08423733b078", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.1454, "combined_score": 0.1749, "label": "This reads like it was written by a person. Neither of our checks found the patterns we usually see in AI-generated writing.", "status": "decided"}
{"timestamp": "2026-11-10T23:14:36+00:00", "content_id": "7a76738d-f0bd-441a-8fdf-511759884588", "creator_id": "attacker_EV01", "guess": "unsure", "model_score": 0.1635, "style_score": 0.875, "combined_score": 0.5192, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided"}
{"timestamp": "2026-11-10T23:14:36+00:00", "content_id": "a26e6d56-ed95-4107-a044-e718962e0305", "creator_id": "attacker_EV02", "guess": "unsure", "model_score": 0.5943, "style_score": 0.0, "combined_score": 0.35, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided"}
{"timestamp": "2026-11-10T23:14:38+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute"}
```

The last entry is RQ10 (a form-encoded body), identified by its position in the run: its `creator_id` is `unknown`, so the log alone can't tie it to the attack.

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
