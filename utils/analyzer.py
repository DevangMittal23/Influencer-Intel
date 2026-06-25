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

Risk score rules (be consistent):
- Start at 0
- Add 3 if intent is "mislead"
- Add 2 if intent is "criticize" AND target is an official/government body
- Add 1.5 per checkworthy factual claim that appears exaggerated or emotional
- Add 2 if content_warnings is not empty
- Add 2 if campaign fit score is below 20
- Maximum score is 10
- risk_level: 7-10 = HIGH, 4-6 = MEDIUM, 0-3 = LOW
- needs_human_review = true if risk_score >= 6 OR if intent == "mislead" OR if any claim makes a specific statistic that contradicts established science

Campaign component scores must be consistent:
- message_alignment: 0-100, how closely does content match the required_message field
- entity_coverage: 0-100, how many required_people are mentioned positively or neutrally (0 if none mentioned, 100 if all mentioned)
- theme_coverage: 0-100, how thoroughly is the campaign theme covered
- purpose_alignment: 0-100, does the content purpose match campaign purpose
- audience_alignment: 0-100, is tone/complexity right for target audience
- Final score = (message_alignment * 0.35) + (entity_coverage * 0.25) + (theme_coverage * 0.20) + (purpose_alignment * 0.10) + (audience_alignment * 0.10)

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
    "reasoning": "overall explanation",
    "missing_elements": ["what is missing from campaign requirements"],
    "component_scores": {{
      "message_alignment": 80,
      "entity_coverage": 60,
      "theme_coverage": 75,
      "purpose_alignment": 70,
      "audience_alignment": 65
    }},
    "component_explanations": {{
      "message_alignment": "how well content matches required message",
      "entity_coverage": "which required people/groups were mentioned",
      "theme_coverage": "how well content covers the campaign theme",
      "purpose_alignment": "does content purpose match campaign purpose",
      "audience_alignment": "is tone/content right for target audience"
    }},
    "missing_talking_points": ["specific talking points absent from this content"]
  }},
  "factual_claims": [
    {{
      "claim": "exact verifiable claim from content",
      "claim_type": "statistic|quote|historical|scientific|political",
      "checkworthy": true
    }}
  ],
  "risk_assessment": {{
    "risk_score": 7,
    "risk_level": "HIGH",
    "risk_factors": [
      "Contains unverified health statistics",
      "Promotes distrust of government sources",
      "High potential to mislead general audience"
    ],
    "needs_human_review": true,
    "review_reason": "Multiple unverified claims with anti-authority framing"
  }},
  "campaign_alignment": {{
    "aligned": false,
    "alignment_summary": "Content directly contradicts evidence-based health messaging",
    "red_flags": [
      "Promotes unverified statistics",
      "Undermines official health bodies"
    ]
  }},
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


def _compute_risk_score(result: dict, fact_checks: list = None) -> dict:
    score = 0
    factors = []

    intent = result.get('intent', '')
    if intent == 'mislead':
        score += 3
        factors.append("Misleading intent detected by LLM")
    elif intent == 'criticize':
        score += 1
        factors.append("Critical intent detected")

    warnings = result.get('content_warnings', [])
    if warnings and warnings != ['none']:
        score += 2
        factors.append(f"Content warnings present: {len(warnings)} flags")

    fit_score = result.get('campaign_fit', {}).get('score', 100)
    if isinstance(fit_score, (int, float)):
        if fit_score < 20:
            score += 2
            factors.append(f"Very low campaign alignment ({fit_score}/100)")
        elif fit_score < 40:
            score += 1
            factors.append(f"Weak campaign alignment ({fit_score}/100)")

    claims = result.get('factual_claims', [])
    checkworthy_count = sum(1 for c in claims if c.get('checkworthy', False))
    if checkworthy_count >= 3:
        score += 1.5
        factors.append(f"{checkworthy_count} checkworthy claims detected")

    if fact_checks:
        false_count = sum(1 for fc in fact_checks if fc.get('verdict') in ['FALSE', 'MISLEADING'])
        score += false_count * 2
        if false_count > 0:
            factors.append(f"{false_count} false/misleading claims verified")

    score = min(10, round(score, 1))
    level = "HIGH" if score >= 7 else "MEDIUM" if score >= 4 else "LOW"
    needs_review = (
        score >= 6
        or intent == 'mislead'
        or (fact_checks and any(fc.get('verdict') == 'FALSE' for fc in fact_checks))
    )

    existing = result.get('risk_assessment', {})
    llm_score = existing.get('risk_score', 0)

    if score > llm_score:
        result['risk_assessment'] = {
            'risk_score': score,
            'risk_level': level,
            'risk_factors': factors,
            'needs_human_review': needs_review,
            'review_reason': existing.get(
                'review_reason',
                " | ".join(factors[:2]) if factors else "Manual review recommended"
            ),
        }
    else:
        if 'risk_assessment' not in result:
            result['risk_assessment'] = {}
        result['risk_assessment']['needs_human_review'] = needs_review

    return result


def compute_recommendation(result: dict) -> dict:
    risk_score = result.get('risk_assessment', {}).get('risk_score', 0)
    risk_level = result.get('risk_assessment', {}).get('risk_level', 'LOW')
    fit_score = result.get('campaign_fit', {}).get('score', 0)
    intent = result.get('intent', 'inform')
    fact_checks = result.get('fact_checks', [])
    needs_review = result.get('risk_assessment', {}).get('needs_human_review', False)

    false_claims = sum(1 for fc in fact_checks if fc.get('verdict') == 'FALSE')
    misleading_claims = sum(1 for fc in fact_checks if fc.get('verdict') == 'MISLEADING')
    unverifiable_claims = sum(1 for fc in fact_checks if fc.get('verdict') == 'UNVERIFIABLE')

    reasons = []
    action = 'PUBLISH'

    # REJECT conditions
    if false_claims >= 2:
        action = 'REJECT'
        reasons.append(f"{false_claims} verified false claims detected")
    if risk_score >= 8:
        action = 'REJECT'
        reasons.append(f"Unacceptable risk score ({risk_score}/10)")
    if intent == 'mislead' and false_claims >= 1:
        action = 'REJECT'
        reasons.append("Confirmed misleading intent with false claims")
    if fit_score < 15 and risk_score >= 5:
        action = 'REJECT'
        reasons.append("Poor campaign alignment with elevated risk")

    # REVIEW conditions
    if action != 'REJECT':
        if false_claims == 1:
            action = 'REVIEW'
            reasons.append("1 verified false claim — verify before publishing")
        if misleading_claims >= 1:
            action = 'REVIEW'
            reasons.append(f"{misleading_claims} misleading claim(s) need editorial review")
        if risk_level == 'HIGH':
            action = 'REVIEW'
            reasons.append("High risk score requires human approval")
        if fit_score < 40:
            action = 'REVIEW'
            reasons.append(f"Low campaign fit ({fit_score}/100) — check alignment")
        if unverifiable_claims >= 3:
            action = 'REVIEW'
            reasons.append(f"{unverifiable_claims} claims could not be verified")
        if needs_review and action == 'PUBLISH':
            action = 'REVIEW'
            reasons.append("Flagged by automated risk assessment")

    # PUBLISH — positive reasons
    if action == 'PUBLISH':
        if fit_score >= 70:
            reasons.append(f"Strong campaign alignment ({fit_score}/100)")
        if false_claims == 0:
            reasons.append("No false claims detected")
        if risk_score <= 3:
            reasons.append("Low risk content")

    return {
        'action': action,
        'reasons': reasons,
        'primary_reason': reasons[0] if reasons else "Automated assessment",
        'fit_score': fit_score,
        'risk_score': risk_score,
        'false_claims': false_claims,
    }


def analyze_content(text: str, source_name: str, campaign_brief: dict, llm_client: LLMClient) -> dict:
    prompt = _build_prompt(text, campaign_brief)
    raw, provider = llm_client.generate(prompt, SYSTEM_PROMPT, temperature=0.1)

    try:
        result = _parse_json(raw)
    except (json.JSONDecodeError, ValueError):
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
    result = _compute_risk_score(result, fact_checks=[])
    return result
