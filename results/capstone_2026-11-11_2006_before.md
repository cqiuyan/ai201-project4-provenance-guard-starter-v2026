# Capstone run log — before

- Produced by: `run_capstone.py::main` (criteria in `run_capstone.py::criterion_1` … `criterion_5`)
- 3 trials · 2026-11-11_2006

| Criterion | Run 1 | Run 2 | Run 3 |
|---|---|---|---|
| 1 | 12/12 (pass) | 12/12 (pass) | 12/12 (pass) |
| 2 | 0/10 leaked, 10/10 with metadata (pass) | 0/10 leaked, 10/10 with metadata (pass) | 0/10 leaked, 10/10 with metadata (pass) |
| 3 | 10/10 timed, mean 60.4 ms (pass) | 10/10 timed, mean 70.3 ms (pass) | 10/10 timed, mean 64.9 ms (pass) |
| 4 | setup succeeded (pass) | setup succeeded (pass) | setup succeeded (pass) |
| 5 | 5/5, 0 5xx, 0 fabricated (pass) | 5/5, 0 5xx, 0 fabricated (pass) | 5/5, 0 5xx, 0 fabricated (pass) |

## Trial 1

### Criterion 1 — `run_capstone.py::criterion_1`

```json
{
  "result": "12/12",
  "passed": true,
  "requests": [
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, 6th from same writer",
      "status": 429
    },
    {
      "sent": "submit, empty text",
      "status": 400
    },
    {
      "sent": "submit, no text",
      "status": 400
    },
    {
      "sent": "submit, text null",
      "status": 400
    },
    {
      "sent": "submit, text a number",
      "status": 400
    },
    {
      "sent": "submit, bad JSON",
      "status": 400
    },
    {
      "sent": "appeal, real id",
      "status": 200
    }
  ],
  "entries_written": 12,
  "checks": [
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "content_id": "364b07e0-6d64-4f8e-8e50-f11c94aa267a",
        "creator_id": "c1_t1_writer",
        "guess": "unsure",
        "model_score": 0.0647,
        "style_score": 0.875,
        "combined_score": 0.4698,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 58.5,
        "text_chars": 208,
        "text_words": 36,
        "text_hash": "327a5983d212"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "content_id": "4136f4af-bf1f-4979-98a9-8b5b544cb38b",
        "creator_id": "c1_t1_writer",
        "guess": "unsure",
        "model_score": 0.047,
        "style_score": 0.875,
        "combined_score": 0.461,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 76.9,
        "text_chars": 205,
        "text_words": 35,
        "text_hash": "f856d428a448"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "content_id": "4ccad555-048f-4370-b225-f572c19872cf",
        "creator_id": "c1_t1_writer",
        "guess": "unsure",
        "model_score": 0.0177,
        "style_score": 0.875,
        "combined_score": 0.4464,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 64.8,
        "text_chars": 204,
        "text_words": 35,
        "text_hash": "00327f86c247"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "content_id": "04e9a8ef-4573-45e9-8642-1fe2a72d637c",
        "creator_id": "c1_t1_writer",
        "guess": "unsure",
        "model_score": 0.0667,
        "style_score": 0.875,
        "combined_score": 0.4708,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 66.3,
        "text_chars": 204,
        "text_words": 37,
        "text_hash": "67225179839f"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "content_id": "bc0a02af-05c4-4e45-b722-ca72059c1c36",
        "creator_id": "c1_t1_writer",
        "guess": "unsure",
        "model_score": 0.0174,
        "style_score": 0.875,
        "combined_score": 0.4462,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 58.0,
        "text_chars": 204,
        "text_words": 35,
        "text_hash": "cfd187c42b2e"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "c1_t1_writer",
        "event": "rejected",
        "status": "rejected",
        "reason": "rate_limited",
        "limit": "5 per 1 minute",
        "endpoint": "/submit",
        "duration_ms": 0.4,
        "text_chars": 201,
        "text_words": 34,
        "text_hash": "53f13cb951a6"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "c1_t1_empty",
        "event": "rejected",
        "status": "rejected",
        "reason": "text_too_short",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "text_chars": 0,
        "text_words": 0,
        "text_hash": "e3b0c44298fc"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "c1_t1_missing",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "missing"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "c1_t1_null",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "NoneType"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "c1_t1_number",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.2,
        "input_type": "int"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "unknown",
        "event": "rejected",
        "status": "rejected",
        "reason": "invalid_json",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "not_a_json_object",
        "body_bytes": 22
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "content_id": "364b07e0-6d64-4f8e-8e50-f11c94aa267a",
        "creator_id": "c1_t1_writer",
        "event": "appeal",
        "status": "under_review",
        "reasoning": "I wrote this.",
        "duration_ms": 1.2
      },
      "problems": []
    }
  ]
}
```

### Criterion 2 — `run_capstone.py::criterion_2`

```json
{
  "result": "0/10 leaked, 10/10 with metadata",
  "passed": true,
  "rows": [
    {
      "marker": "Capstone marker sentence 2-1-1 mentions a plum lantern numbered 2101 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 208,
      "text_words": 36,
      "text_hash": "db7a7e3b2ff0"
    },
    {
      "marker": "Capstone marker sentence 2-1-2 mentions a plum lantern numbered 2102 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 205,
      "text_words": 35,
      "text_hash": "11fd85bbc69a"
    },
    {
      "marker": "Capstone marker sentence 2-1-3 mentions a plum lantern numbered 2103 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 35,
      "text_hash": "0ef84fc44393"
    },
    {
      "marker": "Capstone marker sentence 2-1-4 mentions a plum lantern numbered 2104 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 37,
      "text_hash": "3568c8a5a20a"
    },
    {
      "marker": "Capstone marker sentence 2-1-5 mentions a plum lantern numbered 2105 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 35,
      "text_hash": "ce0224d89bbe"
    },
    {
      "marker": "Capstone marker sentence 2-1-6 mentions a plum lantern numbered 2106 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 201,
      "text_words": 34,
      "text_hash": "36646d59e7ae"
    },
    {
      "marker": "Capstone marker sentence 2-1-7 mentions a plum lantern numbered 2107 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 203,
      "text_words": 30,
      "text_hash": "362b9e17a7c7"
    },
    {
      "marker": "Capstone marker sentence 2-1-8 mentions a plum lantern numbered 2108 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 205,
      "text_words": 28,
      "text_hash": "d6fdee4e9ed0"
    },
    {
      "marker": "Capstone marker sentence 2-1-9 mentions a plum lantern numbered 2109 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 31,
      "text_hash": "2e577b4d8dc4"
    },
    {
      "marker": "Capstone marker sentence 2-1-10 mentions a plum lantern numbered 2110 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 202,
      "text_words": 30,
      "text_hash": "247c06d50d8b"
    }
  ]
}
```

### Criterion 3 — `run_capstone.py::criterion_3`

```json
{
  "result": "10/10 timed, mean 60.4 ms",
  "passed": true,
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

### Criterion 4 — `run_capstone.py::criterion_4`

```json
{
  "result": "setup succeeded",
  "passed": true,
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

### Criterion 5 — `run_capstone.py::criterion_5`

```json
{
  "result": "5/5, 0 5xx, 0 fabricated",
  "passed": true,
  "rows": [
    {
      "case": "empty text",
      "status": 400,
      "error": "text_too_short",
      "log_entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "c5_t1_empty",
        "event": "rejected",
        "status": "rejected",
        "reason": "text_too_short",
        "endpoint": "/submit",
        "duration_ms": 0.2,
        "text_chars": 0,
        "text_words": 0,
        "text_hash": "e3b0c44298fc"
      },
      "passed": true
    },
    {
      "case": "missing text",
      "status": 400,
      "error": "missing_field",
      "log_entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "c5_t1_missing",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "missing"
      },
      "passed": true
    },
    {
      "case": "malformed JSON",
      "status": 400,
      "error": "invalid_json",
      "log_entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "unknown",
        "event": "rejected",
        "status": "rejected",
        "reason": "invalid_json",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "not_a_json_object",
        "body_bytes": 22
      },
      "passed": true
    },
    {
      "case": "appeal, nonexistent id",
      "status": 404,
      "error": "unknown_content_id",
      "log_entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "unknown",
        "event": "rejected",
        "status": "rejected",
        "reason": "unknown_content_id",
        "endpoint": "/appeal",
        "duration_ms": 1.1,
        "requested_content_id": "c5-t1-no-such-id",
        "reasoning_chars": 5
      },
      "passed": true
    },
    {
      "case": "6th submit in a minute",
      "status": 429,
      "error": "rate_limited",
      "log_entry": {
        "timestamp": "2026-11-12T02:02:37+00:00",
        "creator_id": "c5_t1_writer",
        "event": "rejected",
        "status": "rejected",
        "reason": "rate_limited",
        "limit": "5 per 1 minute",
        "endpoint": "/submit",
        "duration_ms": 0.2,
        "text_chars": 201,
        "text_words": 34,
        "text_hash": "9d07cc3a9ea3"
      },
      "passed": true
    }
  ]
}
```

## Trial 2

### Criterion 1 — `run_capstone.py::criterion_1`

```json
{
  "result": "12/12",
  "passed": true,
  "requests": [
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, 6th from same writer",
      "status": 429
    },
    {
      "sent": "submit, empty text",
      "status": 400
    },
    {
      "sent": "submit, no text",
      "status": 400
    },
    {
      "sent": "submit, text null",
      "status": 400
    },
    {
      "sent": "submit, text a number",
      "status": 400
    },
    {
      "sent": "submit, bad JSON",
      "status": 400
    },
    {
      "sent": "appeal, real id",
      "status": 200
    }
  ],
  "entries_written": 12,
  "checks": [
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "content_id": "ecb8b28f-43a0-4a87-b8d8-25f646001217",
        "creator_id": "c1_t2_writer",
        "guess": "unsure",
        "model_score": 0.0619,
        "style_score": 0.875,
        "combined_score": 0.4684,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 70.6,
        "text_chars": 208,
        "text_words": 36,
        "text_hash": "57200e5cae09"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "content_id": "4fdb0ad8-cfab-40fb-ba17-786f4044f0f7",
        "creator_id": "c1_t2_writer",
        "guess": "unsure",
        "model_score": 0.0465,
        "style_score": 0.875,
        "combined_score": 0.4607,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 66.4,
        "text_chars": 205,
        "text_words": 35,
        "text_hash": "68971a2cc2a4"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "content_id": "9b64a45e-5c6f-4325-ab6c-5c35b2b5990a",
        "creator_id": "c1_t2_writer",
        "guess": "unsure",
        "model_score": 0.0213,
        "style_score": 0.875,
        "combined_score": 0.4481,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 75.4,
        "text_chars": 204,
        "text_words": 35,
        "text_hash": "afae8c519983"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "content_id": "89f99c7d-294b-416a-ab46-45505e6298b6",
        "creator_id": "c1_t2_writer",
        "guess": "unsure",
        "model_score": 0.0701,
        "style_score": 0.875,
        "combined_score": 0.4726,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 75.3,
        "text_chars": 204,
        "text_words": 37,
        "text_hash": "4cf28646318b"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "content_id": "6560603d-3738-4382-bcb4-7e14b5e5a1ff",
        "creator_id": "c1_t2_writer",
        "guess": "unsure",
        "model_score": 0.0177,
        "style_score": 0.875,
        "combined_score": 0.4464,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 61.4,
        "text_chars": 204,
        "text_words": 35,
        "text_hash": "df87729c0bf0"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "creator_id": "c1_t2_writer",
        "event": "rejected",
        "status": "rejected",
        "reason": "rate_limited",
        "limit": "5 per 1 minute",
        "endpoint": "/submit",
        "duration_ms": 0.3,
        "text_chars": 201,
        "text_words": 34,
        "text_hash": "8407179e42b3"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "creator_id": "c1_t2_empty",
        "event": "rejected",
        "status": "rejected",
        "reason": "text_too_short",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "text_chars": 0,
        "text_words": 0,
        "text_hash": "e3b0c44298fc"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "creator_id": "c1_t2_missing",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.2,
        "input_type": "missing"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "creator_id": "c1_t2_null",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "NoneType"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "creator_id": "c1_t2_number",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "int"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "creator_id": "unknown",
        "event": "rejected",
        "status": "rejected",
        "reason": "invalid_json",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "not_a_json_object",
        "body_bytes": 22
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:03:49+00:00",
        "content_id": "ecb8b28f-43a0-4a87-b8d8-25f646001217",
        "creator_id": "c1_t2_writer",
        "event": "appeal",
        "status": "under_review",
        "reasoning": "I wrote this.",
        "duration_ms": 1.3
      },
      "problems": []
    }
  ]
}
```

### Criterion 2 — `run_capstone.py::criterion_2`

```json
{
  "result": "0/10 leaked, 10/10 with metadata",
  "passed": true,
  "rows": [
    {
      "marker": "Capstone marker sentence 2-2-1 mentions a plum lantern numbered 2201 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 208,
      "text_words": 36,
      "text_hash": "8095c5fe0126"
    },
    {
      "marker": "Capstone marker sentence 2-2-2 mentions a plum lantern numbered 2202 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 205,
      "text_words": 35,
      "text_hash": "90dfe268f23a"
    },
    {
      "marker": "Capstone marker sentence 2-2-3 mentions a plum lantern numbered 2203 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 35,
      "text_hash": "111a2165daa6"
    },
    {
      "marker": "Capstone marker sentence 2-2-4 mentions a plum lantern numbered 2204 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 37,
      "text_hash": "c57bf075a2de"
    },
    {
      "marker": "Capstone marker sentence 2-2-5 mentions a plum lantern numbered 2205 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 35,
      "text_hash": "7b455d5adb29"
    },
    {
      "marker": "Capstone marker sentence 2-2-6 mentions a plum lantern numbered 2206 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 201,
      "text_words": 34,
      "text_hash": "12225b2a7442"
    },
    {
      "marker": "Capstone marker sentence 2-2-7 mentions a plum lantern numbered 2207 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 203,
      "text_words": 30,
      "text_hash": "ac3c9b3ae5cc"
    },
    {
      "marker": "Capstone marker sentence 2-2-8 mentions a plum lantern numbered 2208 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 205,
      "text_words": 28,
      "text_hash": "5fd02f086cdf"
    },
    {
      "marker": "Capstone marker sentence 2-2-9 mentions a plum lantern numbered 2209 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 31,
      "text_hash": "33637bce0a20"
    },
    {
      "marker": "Capstone marker sentence 2-2-10 mentions a plum lantern numbered 2210 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 202,
      "text_words": 30,
      "text_hash": "646a12984389"
    }
  ]
}
```

### Criterion 3 — `run_capstone.py::criterion_3`

```json
{
  "result": "10/10 timed, mean 70.3 ms",
  "passed": true,
  "cold_ms": 5395.2,
  "warm_ms": [
    135.2,
    70.7,
    64.1,
    75.9,
    64.3,
    60.8,
    57.6,
    58.1,
    56.4,
    59.6
  ],
  "warm_mean_ms": 70.3,
  "per_100_submissions_s": 7.03
}
```

### Criterion 4 — `run_capstone.py::criterion_4`

```json
{
  "result": "setup succeeded",
  "passed": true,
  "free_disk_gb_before": 11.2,
  "source_changed": null,
  "steps": [
    {
      "step": "git clone",
      "ok": true,
      "seconds": 0.8,
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
      "seconds": 31.5,
      "tail": [
        "[notice] A new release of pip is available: 24.0 -> 26.3",
        "[notice] To update, run: /var/folders/yj/xy5g5b9d4q14gpqbq1vprd900000gn/T/capstone_clone_t2_vwy6hwz6/repo/.venv/bin/python -m pip install --upgrade pip"
      ]
    },
    {
      "step": "python detector.py",
      "ok": true,
      "seconds": 18.3,
      "tail": [
        "model_signal   0.8864   (higher = more likely AI)",
        "`loss_type=None` was set in the config but it is unrecognized. Using the default loss: `ForCausalLMLoss`."
      ]
    },
    {
      "step": "python test.py",
      "ok": true,
      "seconds": 3.1,
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

### Criterion 5 — `run_capstone.py::criterion_5`

```json
{
  "result": "5/5, 0 5xx, 0 fabricated",
  "passed": true,
  "rows": [
    {
      "case": "empty text",
      "status": 400,
      "error": "text_too_short",
      "log_entry": {
        "timestamp": "2026-11-12T02:03:50+00:00",
        "creator_id": "c5_t2_empty",
        "event": "rejected",
        "status": "rejected",
        "reason": "text_too_short",
        "endpoint": "/submit",
        "duration_ms": 0.2,
        "text_chars": 0,
        "text_words": 0,
        "text_hash": "e3b0c44298fc"
      },
      "passed": true
    },
    {
      "case": "missing text",
      "status": 400,
      "error": "missing_field",
      "log_entry": {
        "timestamp": "2026-11-12T02:03:50+00:00",
        "creator_id": "c5_t2_missing",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.2,
        "input_type": "missing"
      },
      "passed": true
    },
    {
      "case": "malformed JSON",
      "status": 400,
      "error": "invalid_json",
      "log_entry": {
        "timestamp": "2026-11-12T02:03:50+00:00",
        "creator_id": "unknown",
        "event": "rejected",
        "status": "rejected",
        "reason": "invalid_json",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "not_a_json_object",
        "body_bytes": 22
      },
      "passed": true
    },
    {
      "case": "appeal, nonexistent id",
      "status": 404,
      "error": "unknown_content_id",
      "log_entry": {
        "timestamp": "2026-11-12T02:03:50+00:00",
        "creator_id": "unknown",
        "event": "rejected",
        "status": "rejected",
        "reason": "unknown_content_id",
        "endpoint": "/appeal",
        "duration_ms": 1.4,
        "requested_content_id": "c5-t2-no-such-id",
        "reasoning_chars": 5
      },
      "passed": true
    },
    {
      "case": "6th submit in a minute",
      "status": 429,
      "error": "rate_limited",
      "log_entry": {
        "timestamp": "2026-11-12T02:03:50+00:00",
        "creator_id": "c5_t2_writer",
        "event": "rejected",
        "status": "rejected",
        "reason": "rate_limited",
        "limit": "5 per 1 minute",
        "endpoint": "/submit",
        "duration_ms": 0.2,
        "text_chars": 201,
        "text_words": 34,
        "text_hash": "9978f20d3b4b"
      },
      "passed": true
    }
  ]
}
```

## Trial 3

### Criterion 1 — `run_capstone.py::criterion_1`

```json
{
  "result": "12/12",
  "passed": true,
  "requests": [
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, accepted",
      "status": 200
    },
    {
      "sent": "submit, 6th from same writer",
      "status": 429
    },
    {
      "sent": "submit, empty text",
      "status": 400
    },
    {
      "sent": "submit, no text",
      "status": 400
    },
    {
      "sent": "submit, text null",
      "status": 400
    },
    {
      "sent": "submit, text a number",
      "status": 400
    },
    {
      "sent": "submit, bad JSON",
      "status": 400
    },
    {
      "sent": "appeal, real id",
      "status": 200
    }
  ],
  "entries_written": 12,
  "checks": [
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "content_id": "8c74327b-014a-48bd-b169-85d81cb15cee",
        "creator_id": "c1_t3_writer",
        "guess": "unsure",
        "model_score": 0.0595,
        "style_score": 0.875,
        "combined_score": 0.4672,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 61.5,
        "text_chars": 208,
        "text_words": 36,
        "text_hash": "6f326f63ab44"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "content_id": "71d3b9d3-ff2c-4f6e-b3a3-61833807b50f",
        "creator_id": "c1_t3_writer",
        "guess": "unsure",
        "model_score": 0.045,
        "style_score": 0.875,
        "combined_score": 0.46,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 56.9,
        "text_chars": 205,
        "text_words": 35,
        "text_hash": "17b751bd50ab"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "content_id": "3cfbba59-a7ef-4d0c-85bc-21e5b4cebeab",
        "creator_id": "c1_t3_writer",
        "guess": "unsure",
        "model_score": 0.0188,
        "style_score": 0.875,
        "combined_score": 0.4469,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 54.4,
        "text_chars": 204,
        "text_words": 35,
        "text_hash": "c01c97f7bffb"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "content_id": "cfaacebe-5f8a-484f-90c9-28f11c410ede",
        "creator_id": "c1_t3_writer",
        "guess": "unsure",
        "model_score": 0.0674,
        "style_score": 0.875,
        "combined_score": 0.4712,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 181.4,
        "text_chars": 204,
        "text_words": 37,
        "text_hash": "9f69b07ce4f7"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "content_id": "f2462197-0894-4c59-9479-68db555657da",
        "creator_id": "c1_t3_writer",
        "guess": "unsure",
        "model_score": 0.0176,
        "style_score": 0.875,
        "combined_score": 0.4463,
        "label": "We can't tell whether this was written by a person or with AI help. Our checks gave mixed or middle-of-the-road results, which is common for writing by real people. This is not a finding that you used AI. If you'd like a person to look at it, you can appeal using your submission ID.",
        "status": "decided",
        "duration_ms": 55.9,
        "text_chars": 204,
        "text_words": 35,
        "text_hash": "b12c361bd678"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "creator_id": "c1_t3_writer",
        "event": "rejected",
        "status": "rejected",
        "reason": "rate_limited",
        "limit": "5 per 1 minute",
        "endpoint": "/submit",
        "duration_ms": 0.3,
        "text_chars": 201,
        "text_words": 34,
        "text_hash": "65415075b215"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "creator_id": "c1_t3_empty",
        "event": "rejected",
        "status": "rejected",
        "reason": "text_too_short",
        "endpoint": "/submit",
        "duration_ms": 0.2,
        "text_chars": 0,
        "text_words": 0,
        "text_hash": "e3b0c44298fc"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "creator_id": "c1_t3_missing",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "missing"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "creator_id": "c1_t3_null",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "NoneType"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "creator_id": "c1_t3_number",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "int"
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "creator_id": "unknown",
        "event": "rejected",
        "status": "rejected",
        "reason": "invalid_json",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "not_a_json_object",
        "body_bytes": 22
      },
      "problems": []
    },
    {
      "entry": {
        "timestamp": "2026-11-12T02:05:02+00:00",
        "content_id": "8c74327b-014a-48bd-b169-85d81cb15cee",
        "creator_id": "c1_t3_writer",
        "event": "appeal",
        "status": "under_review",
        "reasoning": "I wrote this.",
        "duration_ms": 1.5
      },
      "problems": []
    }
  ]
}
```

### Criterion 2 — `run_capstone.py::criterion_2`

```json
{
  "result": "0/10 leaked, 10/10 with metadata",
  "passed": true,
  "rows": [
    {
      "marker": "Capstone marker sentence 2-3-1 mentions a plum lantern numbered 2301 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 208,
      "text_words": 36,
      "text_hash": "61113c298dfe"
    },
    {
      "marker": "Capstone marker sentence 2-3-2 mentions a plum lantern numbered 2302 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 205,
      "text_words": 35,
      "text_hash": "7ae7f7132a39"
    },
    {
      "marker": "Capstone marker sentence 2-3-3 mentions a plum lantern numbered 2303 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 35,
      "text_hash": "8b35d2e021ce"
    },
    {
      "marker": "Capstone marker sentence 2-3-4 mentions a plum lantern numbered 2304 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 37,
      "text_hash": "75cdd0773e63"
    },
    {
      "marker": "Capstone marker sentence 2-3-5 mentions a plum lantern numbered 2305 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 35,
      "text_hash": "90921ab59339"
    },
    {
      "marker": "Capstone marker sentence 2-3-6 mentions a plum lantern numbered 2306 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 201,
      "text_words": 34,
      "text_hash": "5893061e82c0"
    },
    {
      "marker": "Capstone marker sentence 2-3-7 mentions a plum lantern numbered 2307 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 203,
      "text_words": 30,
      "text_hash": "5e34cffa224a"
    },
    {
      "marker": "Capstone marker sentence 2-3-8 mentions a plum lantern numbered 2308 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 205,
      "text_words": 28,
      "text_hash": "6bdc1c015d85"
    },
    {
      "marker": "Capstone marker sentence 2-3-9 mentions a plum lantern numbered 2309 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 204,
      "text_words": 31,
      "text_hash": "fd82ac0f67f4"
    },
    {
      "marker": "Capstone marker sentence 2-3-10 mentions a plum lantern numbered 2310 beside the quiet harbour wall.",
      "status": 200,
      "leaked": false,
      "text_chars": 202,
      "text_words": 30,
      "text_hash": "5f3f1d46f31d"
    }
  ]
}
```

### Criterion 3 — `run_capstone.py::criterion_3`

```json
{
  "result": "10/10 timed, mean 64.9 ms",
  "passed": true,
  "cold_ms": 5532.5,
  "warm_ms": [
    79.0,
    62.3,
    58.7,
    73.7,
    63.1,
    57.5,
    60.1,
    68.6,
    70.5,
    55.8
  ],
  "warm_mean_ms": 64.9,
  "per_100_submissions_s": 6.49
}
```

### Criterion 4 — `run_capstone.py::criterion_4`

```json
{
  "result": "setup succeeded",
  "passed": true,
  "free_disk_gb_before": 11.2,
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
      "seconds": 29.9,
      "tail": [
        "[notice] A new release of pip is available: 24.0 -> 26.3",
        "[notice] To update, run: /var/folders/yj/xy5g5b9d4q14gpqbq1vprd900000gn/T/capstone_clone_t3_v1p0v0a1/repo/.venv/bin/python -m pip install --upgrade pip"
      ]
    },
    {
      "step": "python detector.py",
      "ok": true,
      "seconds": 20.5,
      "tail": [
        "model_signal   0.8864   (higher = more likely AI)",
        "`loss_type=None` was set in the config but it is unrecognized. Using the default loss: `ForCausalLMLoss`."
      ]
    },
    {
      "step": "python test.py",
      "ok": true,
      "seconds": 2.9,
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

### Criterion 5 — `run_capstone.py::criterion_5`

```json
{
  "result": "5/5, 0 5xx, 0 fabricated",
  "passed": true,
  "rows": [
    {
      "case": "empty text",
      "status": 400,
      "error": "text_too_short",
      "log_entry": {
        "timestamp": "2026-11-12T02:05:03+00:00",
        "creator_id": "c5_t3_empty",
        "event": "rejected",
        "status": "rejected",
        "reason": "text_too_short",
        "endpoint": "/submit",
        "duration_ms": 0.2,
        "text_chars": 0,
        "text_words": 0,
        "text_hash": "e3b0c44298fc"
      },
      "passed": true
    },
    {
      "case": "missing text",
      "status": 400,
      "error": "missing_field",
      "log_entry": {
        "timestamp": "2026-11-12T02:05:03+00:00",
        "creator_id": "c5_t3_missing",
        "event": "rejected",
        "status": "rejected",
        "reason": "missing_field",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "missing"
      },
      "passed": true
    },
    {
      "case": "malformed JSON",
      "status": 400,
      "error": "invalid_json",
      "log_entry": {
        "timestamp": "2026-11-12T02:05:03+00:00",
        "creator_id": "unknown",
        "event": "rejected",
        "status": "rejected",
        "reason": "invalid_json",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "input_type": "not_a_json_object",
        "body_bytes": 22
      },
      "passed": true
    },
    {
      "case": "appeal, nonexistent id",
      "status": 404,
      "error": "unknown_content_id",
      "log_entry": {
        "timestamp": "2026-11-12T02:05:03+00:00",
        "creator_id": "unknown",
        "event": "rejected",
        "status": "rejected",
        "reason": "unknown_content_id",
        "endpoint": "/appeal",
        "duration_ms": 1.3,
        "requested_content_id": "c5-t3-no-such-id",
        "reasoning_chars": 5
      },
      "passed": true
    },
    {
      "case": "6th submit in a minute",
      "status": 429,
      "error": "rate_limited",
      "log_entry": {
        "timestamp": "2026-11-12T02:05:03+00:00",
        "creator_id": "c5_t3_writer",
        "event": "rejected",
        "status": "rejected",
        "reason": "rate_limited",
        "limit": "5 per 1 minute",
        "endpoint": "/submit",
        "duration_ms": 0.1,
        "text_chars": 201,
        "text_words": 34,
        "text_hash": "bda0c026879a"
      },
      "passed": true
    }
  ]
}
```
