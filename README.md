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
   Below 0.35 is human, 0.35–0.82 is unsure, and above 0.82 is AI. Each
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
| unsure | 0.35 – 0.82 (both ends included) | We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID. |
| high-confidence AI | above 0.82 | This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it. |

The thresholds are in `config.py`: `HUMAN_THRESHOLD = 0.35`,
`AI_THRESHOLD = 0.82`. The AI threshold was 0.75 through unit 7 and moved to
0.82 in unit 8 (see The Improvement). The rest of this paragraph is the unit
7 reasoning for 0.75.

In unit 7 I raised the AI threshold from 0.65 to 0.75. My clearly-AI
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

From `results/attack_run_2026-11-10_1714.md`, with `AI_THRESHOLD = 0.75`.
**50 HELD, 6 BROKE.** Score is the combined score; `—` means the request
was refused before scoring.

| ID | Family | Status | Guess | Score | Verdict |
|---|---|---|---|---|---|
| EV01 | evasion | 200 | unsure | 0.519 | HELD |
| EV02 | evasion | 200 | unsure | 0.350 | HELD |
| EV03 | evasion | 200 | unsure | 0.461 | HELD |
| EV04 | evasion | 200 | unsure | 0.743 | HELD |
| EV05 | evasion | 200 | human | 0.284 | BROKE |
| EV06 | evasion | 200 | unsure | 0.474 | HELD |
| EV07 | evasion | 200 | unsure | 0.418 | HELD |
| EV08 | evasion | 400 | — | — | HELD |
| EV09 | evasion | 200 | unsure | 0.656 | HELD |
| EV10 | evasion | 200 | ai | 0.830 | HELD |
| FP01 | false_positive | 200 | unsure | 0.618 | HELD |
| FP02 | false_positive | 200 | ai | 0.787 | BROKE |
| FP03 | false_positive | 200 | ai | 0.776 | BROKE |
| FP04 | false_positive | 200 | ai | 0.771 | BROKE |
| FP05 | false_positive | 200 | ai | 0.799 | BROKE |
| FP06 | false_positive | 200 | unsure | 0.719 | HELD |
| FP07 | false_positive | 200 | unsure | 0.628 | HELD |
| FP08 | false_positive | 400 | — | — | HELD |
| PI01 | prompt_injection | 200 | unsure | 0.437 | HELD |
| PI02 | prompt_injection | 200 | human | 0.175 | BROKE |
| PI03 | prompt_injection | 200 | unsure | 0.476 | HELD |
| PI04 | prompt_injection | 200 | unsure | 0.402 | HELD |
| PI05 | prompt_injection | 200 | unsure | 0.434 | HELD |
| PI06 | prompt_injection | 200 | unsure | 0.594 | HELD |
| MF01 | malformed | 400 | — | — | HELD |
| MF02 | malformed | 400 | — | — | HELD |
| MF03 | malformed | 400 | — | — | HELD |
| MF04 | malformed | 400 | — | — | HELD |
| MF05 | malformed | 400 | — | — | HELD |
| MF06 | malformed | 400 | — | — | HELD |
| MF07 | malformed | 400 | — | — | HELD |
| MF08 | malformed | 413 | — | — | HELD |
| RQ01 | malformed | 400 | — | — | HELD |
| RQ02 | malformed | 400 | — | — | HELD |
| RQ03 | malformed | 400 | — | — | HELD |
| RQ04 | malformed | 400 | — | — | HELD |
| RQ05 | malformed | 400 | — | — | HELD |
| RQ06 | malformed | 400 | — | — | HELD |
| RQ07 | malformed | 400 | — | — | HELD |
| RQ08 | malformed | 400 | — | — | HELD |
| RQ09 | malformed | 400 | — | — | HELD |
| RQ10 | malformed | 429 | — | — | HELD |
| RQ11 | malformed | 429 | — | — | HELD |
| RQ12 | malformed | 400 | — | — | HELD |
| FL01_01 | flood_same_creator | 400 | — | — | HELD |
| FL01_02 | flood_same_creator | 400 | — | — | HELD |
| FL01_03 | flood_same_creator | 400 | — | — | HELD |
| FL01_04 | flood_same_creator | 400 | — | — | HELD |
| FL01_05 | flood_same_creator | 400 | — | — | HELD |
| FL01_06 | flood_same_creator | 429 | — | — | HELD |
| FL01_07 | flood_same_creator | 429 | — | — | HELD |
| FL01_08 | flood_same_creator | 429 | — | — | HELD |
| FL01_09 | flood_same_creator | 429 | — | — | HELD |
| FL01_10 | flood_same_creator | 429 | — | — | HELD |
| FL01_11 | flood_same_creator | 429 | — | — | HELD |
| FL01_12 | flood_same_creator | 429 | — | — | HELD |


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

**FP03**, a non-native English speaker describing their first month in a new
country, was labelled high-confidence AI at 0.776. It's the exact writer I
traced in Milestone 1: careful, plain sentences and safe word choices, which
is what both of my signals read as machine-made. The label told them their
writing "has a lot in common with AI-generated writing". They're the person
with the least room to argue back, and the most likely to stop writing like
themselves to avoid it. After the fix, FP03 lands in "unsure", but its score
didn't move; only the line did.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing | At most 1 of 10 labelled AI | 1 of 10 | 1 of 10 | 1 of 10 | **MET**, at the limit |
| 2. Plain writing | 0 of 5 labelled AI, at least 4 of 5 unsure or human | 3 of 5 AI | 3 of 5 AI | 3 of 5 AI | **MISSED** |
| 3. Label coverage | Each label at least once per trial | 3 AI, 5 unsure, 1 human | 3 AI, 5 unsure, 1 human | 3 AI, 5 unsure, 1 human | **MET** |
| 4. Bad input | 6 of 6 get a 4xx with `error`, 0 get a 5xx, 6 of 6 logged | 6 of 6 4xx, 0 5xx, 6 of 6 logged | 5 of 5 4xx, 0 5xx, 5 of 5 logged | 5 of 5 4xx, 0 5xx, 5 of 5 logged | **MET** |
| 5. Appeals | 5 of 5 return `under_review` and are logged; a fake ID gets 404 with no entry | 5 of 5, fake ID 404 | 5 of 5, fake ID 404 | 5 of 5, fake ID 404 | **MET** |

Criteria 1–4 ran through `run_eval.py --label before`
(`results/run_2026-11-10_1818_before.md`). Two parts were tested by hand
with `curl`, because `run_eval.py` only sends submissions as JSON objects:

- **Criterion 4, the sixth case:** a body that's a JSON list. I sent it once,
  so Run 1 covers 6 of 6, and Runs 2 and 3 cover the 5 sent automatically.
  It returned `400 invalid_json` and was logged as `rejected`.
- **Criterion 5:** three rounds of 5 appeals plus a fake ID. That left 15
  appeal entries in the log, none for the fake ID, and every original
  decision still `decided`.

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

From `results/run_2026-11-10_1818_before.md`, produced by `run_eval.py::main`
against `app.py::submit`. Criterion 2, trial 1, before the fix: entries 2–4
(FP03, FP04, FP05) are labelled `ai`.

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6175,
    "model_score": 0.6175,
    "style_score": 0.6175,
    "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
    "sent": "We got to the campsite about four. The pitch was fine, a bit sloped, b"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.776,
    "model_score": 0.8051,
    "style_score": 0.7468,
    "label": "This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it.",
    "sent": "I want to describe my experience of the first month in this country. T"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7706,
    "model_score": 0.8329,
    "style_score": 0.7083,
    "label": "This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it.",
    "sent": "There are three main causes of the conflict. The first cause is econom"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7993,
    "model_score": 0.8005,
    "style_score": 0.7981,
    "label": "This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it.",
    "sent": "To configure the service, edit the settings file in the installation d"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6283,
    "model_score": 0.8816,
    "style_score": 0.375,
    "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
    "sent": "It rained on Monday. It rained on Tuesday. It rained on Wednesday and "
  }
]
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

The misses: criterion 2, plus six broken attacks (FP02, FP03, FP04, FP05,
EV05, PI02). The other 50 attacks held. Every malformed request got a 4xx
with no crash, and the flood was cut off at the 6th request. They come down
to two patterns.

**Pattern 1: plain, conventional human writing reads as AI to *both*
signals.** This is one problem behind five failures. Criterion 2's miss
(FP03, FP04, FP05 labelled AI in every trial) and the four broken
false-positive attacks (FP02–FP05) are the same failure; three of those
passages appear in both.

- **Signal one** scored them 0.74–0.83. A non-native writer choosing safe
  words, a rubric essay and technical instructions all use common words in
  ordinary order, which is exactly what gpt2 predicts well.
- **Signal two** agreed, at 0.71–0.83. Their sentences are even in length and
  use almost no expressive punctuation, which my style measure treats as
  AI-shaped. On FP02, the formal report, signal two was the bigger accuser
  (0.83 against 0.74).
- **The combining rule couldn't help.** It only holds a score in "unsure"
  when the signals *disagree* by more than 0.4. Here they disagreed by only
  0.06–0.12, so the equal-weight average passed 0.75 untouched.

**Stage:** signal one and signal two, with the combining rule unable to catch
it. **Mechanism:** the two signals share a blind spot. "Plain and
conventional" looks like "machine-made" to both. My disagreement rule assumed
that when one signal is wrong, the other would disagree. On plain writing
they're wrong *together*.

**Pattern 2: anything that adds unusual tokens or punctuation reads as human
to both signals.** Two evasions:

- **EV05** (AI text after a heavy human edit) scored model 0.32 and style
  0.25, so it was labelled human. Casual phrasing ("Obviously.", "the
  away-day kind") is hard for gpt2 to predict. A dash and one-word fragments
  raise sentence-length spread and expressive punctuation.
- **PI02** (a fake "SYSTEM:" instruction above AI text) scored model 0.20 and
  style 0.15, so it was also labelled human. Nothing in my service reads
  instructions, so it wasn't obeyed. But tokens like `SYSTEM:`, `guess=human`
  and `confidence=0.02` are things gpt2 never expects, which drives
  perplexity up. The colons and the short instruction lines raise both style
  measures. The injection failed as an instruction and succeeded as noise.

**Stage:** signal one and signal two. **Mechanism:** neither signal reads
meaning. Both measure surface unpredictability, and casual or junk tokens
produce it as easily as a human writer does. Again both signals moved the
same way, so the disagreement rule never fired.

**Across both patterns:** every failure is a case where the two signals
*agree* and are both wrong. My combining rule only protects against them
disagreeing. That's the weakness to fix.

**Judgment calls I marked HELD:**

- **AI evasions landing in "unsure"** (EV01–04, 06, 07, 09). The system
  didn't call them human, and "unsure" is what raising the AI threshold to
  0.75 was meant to produce.
- **FP08.** A real eight-word submission was refused as too short. The writer
  wasn't accused, but they weren't scored either. That's the cost of my
  20-word minimum.
- **RQ10 and RQ11.** They were refused, but with `429` instead of `400`. Both
  bodies had no readable `creator_id`, so they counted against the shared
  IP-address bucket, which five earlier malformed requests had already
  filled. The log records them as `creator_id: "unknown"`, so they can't be
  traced back to the attack that sent them.

**No criterion revised.** All five could be measured. Criterion 2 was
measurable and simply missed, so it stays as written.



---

## The Improvement

**What I changed:** one setting. `AI_THRESHOLD` in `config.py` went from
0.75 to 0.82, which widens the "unsure" band from 0.35–0.75 to 0.35–0.82.
Nothing else changed: same signals, same weights, same combining rule, same
label text.

**Which diagnosis pointed at it:** Pattern 1. Plain, conventional human
writing reads as AI to *both* signals, so the disagreement rule never fires
and the average lands just above the old threshold. FP02–FP05 scored
0.77–0.80. Reweighting couldn't fix that, because both signals were wrong in
the same direction. What the diagnosis left me was the threshold. Before
choosing, I scored every test text locally:

| Combined score | Text | What it is |
|---|---|---|
| 0.854 | AI boilerplate (criterion 3) | AI |
| 0.853 | AI time-management essay (criterion 3) | AI |
| 0.830 | EV10 | AI |
| 0.799 | FP05, technical documentation | human |
| 0.787 | FP02, formal report | human |
| 0.776 | FP03, non-native writer | human |
| 0.772 | my documentary paragraph (criterion 1) | human |
| 0.771 | FP04, student essay | human |

Every AI text scored 0.83 or more, and every human text 0.80 or less. I
picked 0.82 rather than 0.80 because FP05 sits at 0.7993, only 0.0007 under
0.80.

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

From `results/attack_run_2026-11-10_2225_after.md`, with `AI_THRESHOLD = 0.82`.
**54 HELD, 2 BROKE.**

| ID | Family | Status | Guess | Score | Verdict |
|---|---|---|---|---|---|
| EV01 | evasion | 200 | unsure | 0.519 | HELD |
| EV02 | evasion | 200 | unsure | 0.350 | HELD |
| EV03 | evasion | 200 | unsure | 0.461 | HELD |
| EV04 | evasion | 200 | unsure | 0.743 | HELD |
| EV05 | evasion | 200 | human | 0.284 | BROKE |
| EV06 | evasion | 200 | unsure | 0.474 | HELD |
| EV07 | evasion | 200 | unsure | 0.418 | HELD |
| EV08 | evasion | 400 | — | — | HELD |
| EV09 | evasion | 200 | unsure | 0.656 | HELD |
| EV10 | evasion | 200 | ai | 0.830 | HELD |
| FP01 | false_positive | 200 | unsure | 0.618 | HELD |
| FP02 | false_positive | 200 | unsure | 0.787 | HELD |
| FP03 | false_positive | 200 | unsure | 0.776 | HELD |
| FP04 | false_positive | 200 | unsure | 0.771 | HELD |
| FP05 | false_positive | 200 | unsure | 0.799 | HELD |
| FP06 | false_positive | 200 | unsure | 0.719 | HELD |
| FP07 | false_positive | 200 | unsure | 0.628 | HELD |
| FP08 | false_positive | 400 | — | — | HELD |
| PI01 | prompt_injection | 200 | unsure | 0.437 | HELD |
| PI02 | prompt_injection | 200 | human | 0.175 | BROKE |
| PI03 | prompt_injection | 200 | unsure | 0.476 | HELD |
| PI04 | prompt_injection | 200 | unsure | 0.402 | HELD |
| PI05 | prompt_injection | 200 | unsure | 0.434 | HELD |
| PI06 | prompt_injection | 200 | unsure | 0.594 | HELD |
| MF01 | malformed | 400 | — | — | HELD |
| MF02 | malformed | 400 | — | — | HELD |
| MF03 | malformed | 400 | — | — | HELD |
| MF04 | malformed | 400 | — | — | HELD |
| MF05 | malformed | 400 | — | — | HELD |
| MF06 | malformed | 400 | — | — | HELD |
| MF07 | malformed | 400 | — | — | HELD |
| MF08 | malformed | 413 | — | — | HELD |
| RQ01 | malformed | 400 | — | — | HELD |
| RQ02 | malformed | 400 | — | — | HELD |
| RQ03 | malformed | 400 | — | — | HELD |
| RQ04 | malformed | 400 | — | — | HELD |
| RQ05 | malformed | 400 | — | — | HELD |
| RQ06 | malformed | 400 | — | — | HELD |
| RQ07 | malformed | 400 | — | — | HELD |
| RQ08 | malformed | 400 | — | — | HELD |
| RQ09 | malformed | 400 | — | — | HELD |
| RQ10 | malformed | 429 | — | — | HELD |
| RQ11 | malformed | 429 | — | — | HELD |
| RQ12 | malformed | 400 | — | — | HELD |
| FL01_01 | flood_same_creator | 400 | — | — | HELD |
| FL01_02 | flood_same_creator | 400 | — | — | HELD |
| FL01_03 | flood_same_creator | 400 | — | — | HELD |
| FL01_04 | flood_same_creator | 400 | — | — | HELD |
| FL01_05 | flood_same_creator | 400 | — | — | HELD |
| FL01_06 | flood_same_creator | 429 | — | — | HELD |
| FL01_07 | flood_same_creator | 429 | — | — | HELD |
| FL01_08 | flood_same_creator | 429 | — | — | HELD |
| FL01_09 | flood_same_creator | 429 | — | — | HELD |
| FL01_10 | flood_same_creator | 429 | — | — | HELD |
| FL01_11 | flood_same_creator | 429 | — | — | HELD |
| FL01_12 | flood_same_creator | 429 | — | — | HELD |

**Side by side: the only rows that changed**

| Attack | Score | Before (0.75) | After (0.82) |
|---|---|---|---|
| FP02, formal report | 0.787 | `ai`, BROKE | `unsure`, HELD |
| FP03, non-native writer | 0.776 | `ai`, BROKE | `unsure`, HELD |
| FP04, student essay | 0.771 | `ai`, BROKE | `unsure`, HELD |
| FP05, technical documentation | 0.799 | `ai`, BROKE | `unsure`, HELD |

Every score is identical between the two runs. Only the label boundary
moved.

**Run log — after** (`results/run_2026-11-10_2225_after.md`, criterion 5 by hand)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. my own writing | At most 1 of 10 labelled AI | 0 of 10 | 0 of 10 | 0 of 10 | **MET** |
| 2. plain writing | 0 of 5 labelled AI, at least 4 of 5 unsure or human | 0 of 5 AI, 5 unsure | 0 of 5 AI, 5 unsure | 0 of 5 AI, 5 unsure | **MET** |
| 3. label coverage | Each label at least once per trial | 2 AI, 6 unsure, 1 human | 2 AI, 6 unsure, 1 human | 2 AI, 6 unsure, 1 human | **MET** |
| 4. bad input | 6 of 6 get a 4xx with `error`, 0 get a 5xx, 6 of 6 logged | 6 of 6 4xx, 0 5xx, 6 of 6 logged | 5 of 5 4xx, 0 5xx, 5 of 5 logged | 5 of 5 4xx, 0 5xx, 5 of 5 logged | **MET** |
| 5. appeals (by hand) | 5 of 5 return `under_review` and are logged; a fake ID gets 404 with no entry | 5 of 5, fake ID 404 | 5 of 5, fake ID 404 | 5 of 5, fake ID 404 | **MET** |

**Before and after, side by side**

| Criterion | Before (0.75) | After (0.82) |
|---|---|---|
| 1. My own writing | 1 of 10 AI, **MET** at the limit | 0 of 10 AI, **MET** |
| 2. Plain writing | 3 of 5 AI, **MISSED** | 0 of 5 AI, **MET** |
| 3. Label coverage | 3 AI, 5 unsure, 1 human, **MET** | 2 AI, 6 unsure, 1 human, **MET** |
| 4. Bad input | **MET** | **MET** |
| 5. Appeals | **MET** | **MET** |
| Attacks | 50 HELD, 6 BROKE | 54 HELD, 2 BROKE |


**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

**It helped with what it targeted, and nothing else.** All four broken
false-positive attacks now hold, criterion 2 went from MISSED to MET, and my
own writing went from 1 of 10 labelled AI to 0. I know it was the threshold
and nothing else because every score in both runs is identical; only the
labels on FP02–FP05 changed.

**What it didn't fix:** EV05 and PI02 are still BROKE. They're AI text
scored as *human* (0.28 and 0.17), at the other end of the scale. That's
Pattern 2, and a higher AI threshold can't touch it.

**What it cost:**

- **Fewer AI texts get the AI label.** Any AI text scoring 0.75–0.82 is now
  "unsure". My test set happens to have no AI text in that range, so the
  cost doesn't show up in these tables. That doesn't mean it isn't there.
- **Criterion 3 got thinner.** The AI label is now reached by 2 of my 9
  inputs instead of 3. It still meets the target, but the margin is smaller.
- **The AI label now means "reads like generic boilerplate".** Only text
  scoring above 0.82 gets it.

**The honest caveat:** I chose 0.82 by looking at these same test texts, so
it separates *this* set perfectly partly because it was tuned to it. Human
writing that scores 0.82–0.85 would still be accused, and AI text that
scores 0.76 now walks through as "unsure".



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

**EV05** (AI text after a heavy human edit, scored 0.28, labelled human) and
**PI02** (a fake "SYSTEM:" instruction above AI text, scored 0.17, labelled
human).

- **What I'd do:** the cheapest fix is lowering `HUMAN_THRESHOLD` from 0.35 to
  about 0.15, which would move both into "unsure". The real fix is a signal
  that doesn't just measure surface unpredictability, for example a classifier
  trained on human versus AI text. Both of my signals reward odd tokens and
  punctuation, whoever wrote them.
- **Why I stopped:** the milestone allowed one change, and lowering the human
  threshold creates a new problem. In my tests, **no genuinely human text
  ever reached the human label**. The only inputs that did were EV05 and
  PI02, which are both AI. At 0.15, the human label would be unreachable and
  criterion 3 would fail. That's a finding in itself: my "high-confidence
  human" label currently goes to AI text that's been dressed up, not to
  people.

**RQ10 and RQ11** (marked HELD, but not cleanly). They were refused with
`429` instead of `400`, because requests with no readable `creator_id` share
one IP-address bucket. They're logged as `creator_id: "unknown"`, so they
can't be traced.

- **What I'd do:** log the request's IP address and content type on every
  rejection.
- **Why I stopped:** they were refused and nothing crashed, so I put the one
  change toward the accusations.

**The threshold is tuned to my test set.** I chose 0.82 by looking at these
same texts.

- **What I'd do:** test it on a fresh set of human and AI writing I haven't
  scored yet.
- **Why I stopped:** I didn't have a second set, and gathering one is the
  next step.

**No criterion is still missed** after the fix. Criterion 1 went from meeting
its target at the limit to 0 of 10.

**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

I'd keep the wide "unsure" band and the 0.82 threshold, choosing fewer wrong
accusations even though more AI-written text gets through as "unsure". The
site and its readers pay for that in AI posts that go unflagged, while plain,
student and non-native writers, the people my system was most likely to
accuse, are the ones it protects.


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

---

## Capstone

**The Shape**

I'm extending **Provenance Guard** (units 7 and 8) with **shape A: deploy and
instrument**. It runs locally (**Path B**), because the gpt2 model it loads
is about 525 MB on disk and needs more memory than a 512 MB free host offers.
What's new:

- **Two new kinds of field on every audit log entry.** Decisions,
  rejections (including rate-limit 429s) and appeals all get *how long the
  request took* and *what came in*: the text's length and a short hash, never
  the text itself, because the log is committed to a public repo.
- **A measured cost per run,** in seconds of compute, taken from those log
  durations rather than from a guess.
- **A run path someone else can follow:** RUNNING.md with one start command
  and the environment it needs, tested from a fresh clone.

**Out of scope**

- **Hosting it.** The model doesn't fit a free host's memory, and the course
  treats Path B as equal.
- **Changing how the system scores.** No changes to the signals, weights,
  combining rule, thresholds or label text. This unit measures the system;
  it doesn't change what it decides.
- **Fixing the attacks that still get through** (EV05, PI02) and the
  untraceable RQ10/RQ11 rejections. Those are unit 8's open problems, and
  fixing them would be shape B or C, not A.

**Instrumentation**

Every request to `/submit` and `/appeal` writes one JSON line to
`logs/audit.jsonl` (`audit.py::_append`, called from `app.py`). Since this
unit, each entry has:

- **When:** `timestamp`, and `duration_ms` from the moment the request
  arrived to the moment it was logged (`app.py::start_timer` and
  `elapsed_ms`).
- **What came in:** `text_chars`, `text_words` and a 12-character
  `text_hash`, never the text itself, because this log is committed to a
  public repo. When the text was missing or wasn't a string, `input_type`
  instead, and `body_bytes` when the body wasn't a JSON object.
- **What came out:** for a decision, `guess`, `model_score`, `style_score`,
  `combined_score` and `label`. For a refusal, `reason` and `endpoint`.
  Refused appeals are now logged too, as `rejected` with the
  `requested_content_id`.

Twelve entries from a real session on 2026-11-12, against the running
service (`python app.py`, freshly started). Twelve test writers (`writer_01`
to `writer_12`) each submitted one piece, using texts I wrote for the test.
Then I triggered failures on purpose: an empty text, a missing `text` field,
unparseable JSON, an appeal against a made-up ID, and `writer_01` submitting
again until the rate limit hit. Last came one real appeal. The first entry
is the cold start, while the model loaded.

```json
{"timestamp": "2026-11-12T01:46:32+00:00", "content_id": "4de35aab-3cd8-44c8-8493-6bd1fdccc421", "creator_id": "writer_01", "guess": "unsure", "model_score": 0.6801, "style_score": 0.6664, "combined_score": 0.6733, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided", "duration_ms": 5458.4, "text_chars": 223, "text_words": 45, "text_hash": "160f577defcf"}
{"timestamp": "2026-11-12T01:46:32+00:00", "content_id": "4c053aa3-aeef-4af7-b66f-2e73a6df6e27", "creator_id": "writer_02", "guess": "unsure", "model_score": 0.7443, "style_score": 0.7607, "combined_score": 0.7525, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided", "duration_ms": 78.9, "text_chars": 279, "text_words": 35, "text_hash": "40573a1c1234"}
{"timestamp": "2026-11-12T01:46:32+00:00", "content_id": "42f6f8b7-b817-4053-84d4-a3df73d1cd83", "creator_id": "writer_03", "guess": "unsure", "model_score": 0.3527, "style_score": 0.375, "combined_score": 0.3639, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided", "duration_ms": 69.1, "text_chars": 221, "text_words": 43, "text_hash": "01f3478706b2"}
{"timestamp": "2026-11-12T01:46:32+00:00", "content_id": "3224f258-b8d1-4727-9c91-ed03a63ebaf9", "creator_id": "writer_06", "guess": "ai", "model_score": 0.8878, "style_score": 0.875, "combined_score": 0.8814, "label": "This has a lot in common with AI-generated writing: very predictable wording and evenly shaped sentences. Clear, plain writing by real people can look like this too, so this is not proof. If you wrote it yourself, you can appeal using your submission ID and a person will review it.", "status": "decided", "duration_ms": 57.5, "text_chars": 275, "text_words": 35, "text_hash": "85294c044e86"}
{"timestamp": "2026-11-12T01:46:33+00:00", "content_id": "38c55532-6a4b-4b3b-b43d-3a7a755baefb", "creator_id": "writer_10", "guess": "unsure", "model_score": 0.7038, "style_score": 0.7995, "combined_score": 0.7516, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided", "duration_ms": 59.1, "text_chars": 267, "text_words": 34, "text_hash": "9e814767c201"}
{"timestamp": "2026-11-12T01:46:33+00:00", "content_id": "b657df93-d012-4c54-849d-14681a77c45c", "creator_id": "writer_12", "guess": "unsure", "model_score": 0.5743, "style_score": 0.6026, "combined_score": 0.5885, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided", "duration_ms": 64.4, "text_chars": 261, "text_words": 33, "text_hash": "a78df160d61d"}
{"timestamp": "2026-11-12T01:46:33+00:00", "creator_id": "writer_13", "event": "rejected", "status": "rejected", "reason": "text_too_short", "endpoint": "/submit", "duration_ms": 0.2, "text_chars": 0, "text_words": 0, "text_hash": "e3b0c44298fc"}
{"timestamp": "2026-11-12T01:46:33+00:00", "creator_id": "writer_14", "event": "rejected", "status": "rejected", "reason": "missing_field", "endpoint": "/submit", "duration_ms": 0.1, "input_type": "missing"}
{"timestamp": "2026-11-12T01:46:33+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "invalid_json", "endpoint": "/submit", "duration_ms": 0.2, "input_type": "not_a_json_object", "body_bytes": 22}
{"timestamp": "2026-11-12T01:46:33+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "unknown_content_id", "endpoint": "/appeal", "duration_ms": 1.9, "requested_content_id": "not-a-real-id", "reasoning_chars": 11}
{"timestamp": "2026-11-12T01:46:33+00:00", "creator_id": "writer_01", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute", "endpoint": "/submit", "duration_ms": 0.2, "text_chars": 223, "text_words": 45, "text_hash": "160f577defcf"}
{"timestamp": "2026-11-12T01:46:33+00:00", "content_id": "4de35aab-3cd8-44c8-8493-6bd1fdccc421", "creator_id": "writer_01", "event": "appeal", "status": "under_review", "reasoning": "I wrote this about my own morning.", "duration_ms": 1.0}
```

Failures are in the record: the `text_too_short`, `missing_field`,
`invalid_json`, `unknown_content_id` and `rate_limited` entries above are
each a refused request, logged with how long it took and what came in.
Entries in the log from before this unit (units 7 and 8) don't have
`duration_ms` or the input fields, because those didn't exist yet.

**What It Costs**

The cost of one run is **seconds of compute on my laptop**. There's no API
and no token bill: the model runs locally.

| | Time per request |
|---|---|
| **A warm submission**, mean of 10 | **67.2 ms** (median 65.2, range 57.5–85.3) |
| The cold first submission after start-up | 5,458 ms, once per server start |
| A refused request | 0.1–1.9 ms |

**How I measured it:** I started the service fresh and sent the session
above. The 10 warm submissions are `writer_02` to `writer_11`, and the number
is the mean of their logged `duration_ms`. The service times each request
itself, from arrival to log line, so the number comes from the log, not from
a stopwatch or a pricing page. It's wall-clock time on an 8 GB Apple-silicon
MacBook Air with nothing else heavy running, so a busier machine would be
slower. All 15 warm decisions in the session averaged 68.4 ms, close to the
10-run figure.

**For a hundred people a day:** at one submission each, 100 × 67.2 ms =
6.72 seconds of compute a day, plus one 5.5-second cold start per day if the
server restarts daily: about 12 seconds of compute a day in total. The real
cost is that the machine has to stay on with 525 MB of model in memory, not
the compute itself.

**Run Log — before**

From `results/capstone_2026-11-11_2006_before.md`, produced by
`run_capstone.py::main`. Each trial starts a fresh copy of the service on
port 5052 (a real cold start, fresh rate-limit counters), runs criteria 3, 2,
1 and 5 against it, stops it, then makes a fresh clone from GitHub for
criterion 4 and deletes it afterwards. Every check reads back exactly the log
entries its own requests created.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves timing and input metadata | 12 of 12 complete entries | 12/12 | 12/12 | 12/12 | MET |
| 2. The log never stores submitted writing | 0 of 10 leaked, 10 of 10 with metadata | 0/10 leaked, 10/10 | 0/10 leaked, 10/10 | 0/10 leaked, 10/10 | MET |
| 3. Timings give a local compute cost | 10 of 10 timed, warm mean under 200 ms | 10/10, 60.4 ms | 10/10, 70.3 ms | 10/10, 64.9 ms | MET |
| 4. A fresh clone starts from RUNNING.md | 1 complete setup per trial | succeeded | succeeded | succeeded | MET |
| 5. Failed requests explain themselves and stay visible | 5 of 5, 0 5xx, 0 fabricated | 5/5, 0, 0 | 5/5, 0, 0 | 5/5, 0, 0 | MET |

**Why the counts are identical across trials:** these were three real
re-runs. The cold starts were 5,550, 5,395, 5,532 ms, the
warm means 60.4, 70.3, 64.9 ms, and each trial's fresh clone
installed its own dependencies (29.9–32.7 s each). The counts don't move
because everything they check is deterministic: the same request always gets
the same log fields and the same refusal, and gpt2 scores the same text the
same way every time. Only the timings vary, and they did.

**Real output, trial 1**

Criterion 1 (`run_capstone.py::criterion_1`): the 12 log entries its
requests wrote, as they appear in `logs/audit.jsonl`. Five accepted
submissions from one writer, the sixth rate-limited, five refused
submissions, then an appeal.

```json
{"timestamp": "2026-11-12T02:02:37+00:00", "content_id": "364b07e0-6d64-4f8e-8e50-f11c94aa267a", "creator_id": "c1_t1_writer", "guess": "unsure", "model_score": 0.0647, "style_score": 0.875, "combined_score": 0.4698, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided", "duration_ms": 58.5, "text_chars": 208, "text_words": 36, "text_hash": "327a5983d212"}
{"timestamp": "2026-11-12T02:02:37+00:00", "content_id": "4136f4af-bf1f-4979-98a9-8b5b544cb38b", "creator_id": "c1_t1_writer", "guess": "unsure", "model_score": 0.047, "style_score": 0.875, "combined_score": 0.461, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided", "duration_ms": 76.9, "text_chars": 205, "text_words": 35, "text_hash": "f856d428a448"}
{"timestamp": "2026-11-12T02:02:37+00:00", "content_id": "4ccad555-048f-4370-b225-f572c19872cf", "creator_id": "c1_t1_writer", "guess": "unsure", "model_score": 0.0177, "style_score": 0.875, "combined_score": 0.4464, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided", "duration_ms": 64.8, "text_chars": 204, "text_words": 35, "text_hash": "00327f86c247"}
{"timestamp": "2026-11-12T02:02:37+00:00", "content_id": "04e9a8ef-4573-45e9-8642-1fe2a72d637c", "creator_id": "c1_t1_writer", "guess": "unsure", "model_score": 0.0667, "style_score": 0.875, "combined_score": 0.4708, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided", "duration_ms": 66.3, "text_chars": 204, "text_words": 37, "text_hash": "67225179839f"}
{"timestamp": "2026-11-12T02:02:37+00:00", "content_id": "bc0a02af-05c4-4e45-b722-ca72059c1c36", "creator_id": "c1_t1_writer", "guess": "unsure", "model_score": 0.0174, "style_score": 0.875, "combined_score": 0.4462, "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.", "status": "decided", "duration_ms": 58.0, "text_chars": 204, "text_words": 35, "text_hash": "cfd187c42b2e"}
{"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "c1_t1_writer", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute", "endpoint": "/submit", "duration_ms": 0.4, "text_chars": 201, "text_words": 34, "text_hash": "53f13cb951a6"}
{"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "c1_t1_empty", "event": "rejected", "status": "rejected", "reason": "text_too_short", "endpoint": "/submit", "duration_ms": 0.1, "text_chars": 0, "text_words": 0, "text_hash": "e3b0c44298fc"}
{"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "c1_t1_missing", "event": "rejected", "status": "rejected", "reason": "missing_field", "endpoint": "/submit", "duration_ms": 0.1, "input_type": "missing"}
{"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "c1_t1_null", "event": "rejected", "status": "rejected", "reason": "missing_field", "endpoint": "/submit", "duration_ms": 0.1, "input_type": "NoneType"}
{"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "c1_t1_number", "event": "rejected", "status": "rejected", "reason": "missing_field", "endpoint": "/submit", "duration_ms": 0.2, "input_type": "int"}
{"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "invalid_json", "endpoint": "/submit", "duration_ms": 0.1, "input_type": "not_a_json_object", "body_bytes": 22}
{"timestamp": "2026-11-12T02:02:37+00:00", "content_id": "364b07e0-6d64-4f8e-8e50-f11c94aa267a", "creator_id": "c1_t1_writer", "event": "appeal", "status": "under_review", "reasoning": "I wrote this.", "duration_ms": 1.2}
```

Criterion 2 (`run_capstone.py::criterion_2`): for each of the 10
submissions, its unique marker sentence, whether it (or any sentence of the
text) was found anywhere in that trial's log entries, and what the log kept
instead.

```json
{"marker": "Capstone marker sentence 2-1-1 mentions a plum lantern numbered 2101 beside the quiet harbour wall.", "leaked": false, "text_chars": 208, "text_words": 36, "text_hash": "db7a7e3b2ff0"}
{"marker": "Capstone marker sentence 2-1-2 mentions a plum lantern numbered 2102 beside the quiet harbour wall.", "leaked": false, "text_chars": 205, "text_words": 35, "text_hash": "11fd85bbc69a"}
{"marker": "Capstone marker sentence 2-1-3 mentions a plum lantern numbered 2103 beside the quiet harbour wall.", "leaked": false, "text_chars": 204, "text_words": 35, "text_hash": "0ef84fc44393"}
{"marker": "Capstone marker sentence 2-1-4 mentions a plum lantern numbered 2104 beside the quiet harbour wall.", "leaked": false, "text_chars": 204, "text_words": 37, "text_hash": "3568c8a5a20a"}
{"marker": "Capstone marker sentence 2-1-5 mentions a plum lantern numbered 2105 beside the quiet harbour wall.", "leaked": false, "text_chars": 204, "text_words": 35, "text_hash": "ce0224d89bbe"}
{"marker": "Capstone marker sentence 2-1-6 mentions a plum lantern numbered 2106 beside the quiet harbour wall.", "leaked": false, "text_chars": 201, "text_words": 34, "text_hash": "36646d59e7ae"}
{"marker": "Capstone marker sentence 2-1-7 mentions a plum lantern numbered 2107 beside the quiet harbour wall.", "leaked": false, "text_chars": 203, "text_words": 30, "text_hash": "362b9e17a7c7"}
{"marker": "Capstone marker sentence 2-1-8 mentions a plum lantern numbered 2108 beside the quiet harbour wall.", "leaked": false, "text_chars": 205, "text_words": 28, "text_hash": "d6fdee4e9ed0"}
{"marker": "Capstone marker sentence 2-1-9 mentions a plum lantern numbered 2109 beside the quiet harbour wall.", "leaked": false, "text_chars": 204, "text_words": 31, "text_hash": "2e577b4d8dc4"}
{"marker": "Capstone marker sentence 2-1-10 mentions a plum lantern numbered 2110 beside the quiet harbour wall.", "leaked": false, "text_chars": 202, "text_words": 30, "text_hash": "247c06d50d8b"}
```

Criterion 3 (`run_capstone.py::criterion_3`): `duration_ms` read back from
the log for the cold request and the 10 warm ones.

```json
{
  "cold_ms": 5550.1,
  "warm_ms": [
    71.8,
    59.2,
    55.6,
    71.0,
    71.9,
    56.1,
    54.6,
    55.1,
    53.8,
    54.9
  ],
  "warm_mean_ms": 60.4,
  "per_100_submissions_s": 6.04
}
```

Criterion 4 (`run_capstone.py::criterion_4`): each step of the fresh-clone
setup, with how long it took and its last lines of output.

```json
{
  "result": "setup succeeded",
  "free_disk_gb_before": 12.3,
  "source_changed": null,
  "steps": [
    {
      "step": "git clone",
      "ok": true,
      "seconds": 0.6,
      "tail": []
    },
    {
      "step": "python3 -m venv .venv (/opt/anaconda3/bin/python3)",
      "ok": true,
      "seconds": 2.1,
      "tail": []
    },
    {
      "step": "pip install -r requirements.txt",
      "ok": true,
      "seconds": 32.7,
      "tail": [
        "[notice] A new release of pip is available: 24.0 -> 26.3",
        "[notice] To update, run: /var/folders/yj/xy5g5b9d4q14gpqbq1vprd900000gn/T/capstone_clone_t1_0mabklje/repo/.venv/bin/python -m pip install --upgrade pip"
      ]
    },
    {
      "step": "python detector.py",
      "ok": true,
      "seconds": 17.0,
      "tail": [
        "model_signal   0.8864   (higher = more likely AI)",
        "`loss_type=None` was set in the config but it is unrecognized. Using the default loss: `ForCausalLMLoss`."
      ]
    },
    {
      "step": "python test.py",
      "ok": true,
      "seconds": 3.4,
      "tail": [
        "",
        "You're set. See you in class."
      ]
    },
    {
      "step": "python app.py, then POST /ping and POST /submit",
      "ok": true,
      "ping": true,
      "submit": true,
      "submit_guess": "unsure"
    }
  ]
}
```

Criterion 5 (`run_capstone.py::criterion_5`): each deliberate failure, the
response it got, and the log entry it left.

```json
{"case": "empty text", "status": 400, "error": "text_too_short", "log_entry": {"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "c5_t1_empty", "event": "rejected", "status": "rejected", "reason": "text_too_short", "endpoint": "/submit", "duration_ms": 0.2, "text_chars": 0, "text_words": 0, "text_hash": "e3b0c44298fc"}}
{"case": "missing text", "status": 400, "error": "missing_field", "log_entry": {"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "c5_t1_missing", "event": "rejected", "status": "rejected", "reason": "missing_field", "endpoint": "/submit", "duration_ms": 0.1, "input_type": "missing"}}
{"case": "malformed JSON", "status": 400, "error": "invalid_json", "log_entry": {"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "invalid_json", "endpoint": "/submit", "duration_ms": 0.1, "input_type": "not_a_json_object", "body_bytes": 22}}
{"case": "appeal, nonexistent id", "status": 404, "error": "unknown_content_id", "log_entry": {"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "unknown", "event": "rejected", "status": "rejected", "reason": "unknown_content_id", "endpoint": "/appeal", "duration_ms": 1.1, "requested_content_id": "c5-t1-no-such-id", "reasoning_chars": 5}}
{"case": "6th submit in a minute", "status": 429, "error": "rate_limited", "log_entry": {"timestamp": "2026-11-12T02:02:37+00:00", "creator_id": "c5_t1_writer", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "5 per 1 minute", "endpoint": "/submit", "duration_ms": 0.2, "text_chars": 201, "text_words": 34, "text_hash": "9d07cc3a9ea3"}}
```
