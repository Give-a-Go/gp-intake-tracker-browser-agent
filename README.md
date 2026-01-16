# GP Intake Checker (Browser Use)

Checks GP practice websites to determine whether they are accepting new patients. The agent navigates each practice’s homepage, rejects cookie pop-ups, searches for “new patients / accepting / registration” language, and returns evidence with a status.

## Requirements

- Python 3.11+
- A Browser Use API key: https://cloud.browser-use.com/

## Key Technology

- [Browser Use](https://github.com/browser-use/browser-use) agent framework
- Browser Use Cloud (hosted browser + LLM orchestration)
- Pydantic v2 for structured JSON outputs

## Setup

From this folder:

```bash
uv sync
```

Set your API key:

```bash
export BROWSER_USE_API_KEY="<your_key>"
```

## Run

```bash
python gp_intake_checker.py
```

## Output

```json
[
  {
    "practice": "Ark Medical Centre (New patient enquiry)",
    "url": "https://arkmedical.ie/",
    "status": "Not Accepting",
    "evidence": "We are temporarily not accepting new patients.",
    "contact_email": null,
    "checked_at": "2026-01-16T22:41:18.562894Z"
  }
]
```

## LLM Setup Prompt (copy/paste)

Use this prompt with your favorite LLM to clone and set up the project automatically:

```
Clone and set up this project to run the GP intake checker:

1) git clone https://github.com/Give-a-Go/gp-intake-tracker-browser-agent.git
2) cd gp-intake-tracker-browser-agent/
3) uv sync
4) export BROWSER_USE_API_KEY="<your_key>"
5) python gp_intake_checker.py

If uv is missing, install it first from https://docs.astral.sh/uv/.
```
