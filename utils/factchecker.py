import json
import sys
from utils.llm_client import LLMClient

FACT_SYSTEM = "You are a fact-checker. Return ONLY valid JSON. No markdown, no explanation outside JSON."


def _verdict_prompt(claim: str, search_results: list) -> str:
    return f"""Based ONLY on the provided search results, evaluate the following claim.

CLAIM: {claim}

SEARCH RESULTS:
{json.dumps(search_results, indent=2)}

Return ONLY this JSON:
{{
  "verdict": "TRUE|FALSE|MISLEADING|PARTIALLY_TRUE|UNVERIFIABLE",
  "confidence": 85,
  "reasoning": "one paragraph explanation citing the sources",
  "correct_fact": "corrected version if FALSE or MISLEADING, else null",
  "primary_source_url": "most relevant source URL or null",
  "primary_source_title": "source title or null"
}}

If search results are insufficient to verify, verdict must be UNVERIFIABLE. Never guess. Never fabricate sources."""


def _parse_verdict(raw: str) -> dict:
    import re
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw.strip())
    return json.loads(raw)


def fact_check_claims(
    claims: list,
    source_name: str,
    llm_client: LLMClient,
    tavily_api_key: str,
) -> list:
    results = []

    for claim_obj in claims:
        base = {
            "claim": claim_obj.get("claim", ""),
            "claim_type": claim_obj.get("claim_type", ""),
            "verdict": "SKIPPED",
            "confidence": 0,
            "reasoning": "",
            "correct_fact": None,
            "source_url": None,
            "source_title": None,
            "search_performed": False,
        }

        if not claim_obj.get("checkworthy", False):
            results.append(base)
            continue

        # Step 1: Tavily search
        search_results = []
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=tavily_api_key)
            response = client.search(
                query=claim_obj["claim"],
                search_depth="basic",
                max_results=3,
            )
            search_results = [
                {"title": r.get("title"), "url": r.get("url"), "content": r.get("content"), "score": r.get("score")}
                for r in response.get("results", [])
            ]
            base["search_performed"] = True
        except Exception as e:
            print(f"[FactChecker] Tavily error for claim '{claim_obj['claim'][:60]}': {e}", file=sys.stderr)
            base["verdict"] = "UNVERIFIABLE"
            base["reasoning"] = "Search unavailable"
            results.append(base)
            continue

        # Step 2: LLM verdict
        try:
            raw, _ = llm_client.generate(
                _verdict_prompt(claim_obj["claim"], search_results),
                FACT_SYSTEM,
                temperature=0.1,
            )
            verdict_data = _parse_verdict(raw)
            base.update({
                "verdict": verdict_data.get("verdict", "UNVERIFIABLE"),
                "confidence": verdict_data.get("confidence", 0),
                "reasoning": verdict_data.get("reasoning", ""),
                "correct_fact": verdict_data.get("correct_fact"),
                "source_url": verdict_data.get("primary_source_url"),
                "source_title": verdict_data.get("primary_source_title"),
            })
        except Exception as e:
            print(f"[FactChecker] LLM verdict error: {e}", file=sys.stderr)
            base["verdict"] = "UNVERIFIABLE"
            base["reasoning"] = f"LLM verdict failed: {e}"

        results.append(base)

    return results
