import asyncio
import json
import os
from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, RootModel

from browser_use import Agent, Browser, ChatBrowserUse


Status = Literal["Accepting", "Not Accepting", "Unclear"]


class PracticeCheck(BaseModel):
    practice: str
    url: str
    status: Status
    evidence: str
    contact_email: Optional[str] = None
    checked_at: Optional[str] = None


class PracticeChecks(RootModel[list[PracticeCheck]]):
    pass


def _parse_checks(payload: str) -> list[PracticeCheck]:
    return PracticeChecks.model_validate_json(payload).root


def _utc_now_iso() -> str:
    dt = datetime.now(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def _build_task(practice: str, url: str) -> str:
    return (
        "You are an automated browser agent. Determine whether the GP practice is currently accepting new patients.\n\n"
        f"Practice: {practice}\n"
        f"URL: {url}\n\n"
        "Steps:\n"
        "1. Open the given homepage URL.\n"
        "2. If a cookie pop-up appears, reject/decline all cookies (do not accept).\n"
        "3. Navigate through the site to find content about ‘new patients’, ‘accepting’, ‘not accepting’, ‘registration’, or similar.\n"
        "4. Scroll as needed to locate the relevant statement.\n"
        "5. Extract the exact text that indicates the status.\n"
        "6. Decide one of three statuses: Accepting, Not Accepting, or Unclear.\n"
        "7. If status is Accepting, find a contact email address for the practice; otherwise leave it null.\n\n"
        "Output requirements:\n"
        "- Return ONLY valid JSON (no markdown, no code fences, no extra text).\n"
        "- The JSON MUST be a single-element array with exactly one object for this practice.\n"
        "- evidence MUST be an exact snippet copied from the page that supports the status.\n"
        "- If you cannot find an explicit statement, set status to Unclear and set evidence to the closest relevant text you found (or empty string if none).\n"
        "- contact_email MUST be a single email address string when status is Accepting; otherwise null.\n\n"
        "Schema for the single object:\n"
        "{\n"
        f'  "practice": {json.dumps(practice)},\n'
        f'  "url": {json.dumps(url)},\n'
        '  "status": "Accepting" | "Not Accepting" | "Unclear",\n'
        '  "evidence": "...",\n'
        '  "contact_email": null,\n'
        '  "checked_at": null\n'
        "}"
    )


async def check_practices() -> list[PracticeCheck]:
    practices = [
        {
            "practice": "Ark Medical Centre (New patient enquiry)",
            "url": "https://arkmedical.ie/",
        },
        {
            "practice": "Mercer’s Medical Centre",
            "url": "https://www.mercersmedicalcentre.com/",
        },
        {
            "practice": "Sirona Medical (Practice policies)",
            "url": "https://www.sironamedical.ie/",
        },
        {
            "practice": "GPdoc Medical Centre",
            "url": "https://www.gpdoc.ie/",
        },
    ]

    use_cloud_browser = os.getenv("BROWSER_USE_USE_CLOUD", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    llm = ChatBrowserUse()

    results: list[PracticeCheck] = []

    for item in practices:
        browser = Browser(use_cloud=use_cloud_browser)
        task = _build_task(item["practice"], item["url"])
        agent = Agent(
            task=task, llm=llm, browser=browser, output_model_schema=PracticeChecks
        )
        history = await agent.run(max_steps=40)

        payload = history.final_result() or "[]"
        parsed = _parse_checks(payload)
        if not parsed:
            parsed = [
                PracticeCheck(
                    practice=item["practice"],
                    url=item["url"],
                    status="Unclear",
                    evidence="",
                )
            ]

        check = parsed[0]
        check.practice = item["practice"]
        check.url = item["url"]
        if check.status != "Accepting":
            check.contact_email = None
        elif check.contact_email:
            check.contact_email = check.contact_email.strip() or None
        check.checked_at = _utc_now_iso()
        results.append(check)

    return results


async def main() -> None:
    results = await check_practices()
    print(json.dumps([r.model_dump() for r in results], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
