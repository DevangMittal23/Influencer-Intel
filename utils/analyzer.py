import json
import re
from utils.llm_client import LLMClient

SYSTEM_PROMPT = """You are an expert content intelligence analyst. You analyze influencer 
content with precision and return ONLY valid JSON. No markdown. 
No explanations outside the JSON. Be objective and factual.
Content may be in Hindi, English, or mixed Hinglish — analyze as-is."""

STRICT_RETRY_SUFFIX = "\n\nReturn ONLY the raw JSON object. No markdown fences, no explanation, just the JSON."


def _build_prompt(text: str, campaign_brief: dict) -> str:
    people = ", ".join(campaign_brief.get("required_people", []))
    return f"""Analyze the following influencer content against the campaign brief.

CAMPAIGN BRIEF:
Theme: {campaign_brief.get('theme', '')}
Required Message: {campaign_brief.get('required_message', '')}
Required People/Groups: {people}
Purpose: {campaign_brief.get('purpose', '')}
Target Audience: {campaign_brief.get('target_audience', '')}

CONTENT TO ANALYZE:
{text}

Return ONLY this JSON structure, nothing else:
{{
  "core_narrative": "2-3 sentence summary of main message",
  "intent": "inform|persuade|mislead|entertain|promote|criticize",
  "intent_explanation": "one sentence explaining the intent",
  "sentiment_overall": "positive|negative|neutral|mixed",
  "entities": [
    {{
      "name": "person or group name",
      "type": "person|organization|government|brand",
      "stance": "supported|criticized|neutral",
      "context": "one sentence on how they are mentioned"
    }}
  ],
  "campaign_fit": {{
    "score": 72,
    "label": "Good Fit|Strong Fit|Weak Fit|No Fit|Off-Message",
    "reasoning": "explanation of score",
    "missing_elements": ["what is missing from campaign requirements"]
  }},
  "factual_claims": [
    {{
      "claim": "exact verifiable claim from content",
      "claim_type": "statistic|quote|historical|scientific|political",
      "checkworthy": true
    }}
  ],
  "content_warnings": ["list any concerning content patterns or none"],
  "language_detected": "en|hi|mixed",
  "word_count": 250
}}"""


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r'^```[a-z]*\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw.strip())
    return json.loads(raw)


def analyze_content(text: str, source_name: str, campaign_brief: dict, llm_client: LLMClient) -> dict:
    prompt = _build_prompt(text, campaign_brief)
    raw, provider = llm_client.generate(prompt, SYSTEM_PROMPT, temperature=0.1)

    try:
        result = _parse_json(raw)
    except (json.JSONDecodeError, ValueError):
        # Retry once with stricter prompt
        raw2, provider = llm_client.generate(prompt + STRICT_RETRY_SUFFIX, SYSTEM_PROMPT, temperature=0.1)
        try:
            result = _parse_json(raw2)
        except (json.JSONDecodeError, ValueError) as e:
            return {
                "source_name": source_name,
                "analysis_status": "parse_error",
                "error": str(e),
                "provider_used": provider,
            }

    result["source_name"] = source_name
    result["analysis_status"] = "success"
    result["provider_used"] = provider
    return result
