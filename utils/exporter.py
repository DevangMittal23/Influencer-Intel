import io
import pandas as pd
from openpyxl.styles import PatternFill, Font
from openpyxl.utils import get_column_letter

VERDICT_FILLS = {
    "TRUE":           PatternFill("solid", fgColor="0D2818"),
    "FALSE":          PatternFill("solid", fgColor="2D0F1A"),
    "MISLEADING":     PatternFill("solid", fgColor="2D1F00"),
    "PARTIALLY_TRUE": PatternFill("solid", fgColor="1A2020"),
    "UNVERIFIABLE":   PatternFill("solid", fgColor="1A1D27"),
    "SKIPPED":        PatternFill("solid", fgColor="1A1D27"),
}
VERDICT_FONTS = {
    "TRUE":           Font(color="00D4AA", bold=True),
    "FALSE":          Font(color="FF4B6E", bold=True),
    "MISLEADING":     Font(color="FFB800", bold=True),
    "PARTIALLY_TRUE": Font(color="40C4AA", bold=True),
    "UNVERIFIABLE":   Font(color="6B7280", bold=True),
    "SKIPPED":        Font(color="6B7280"),
}


def _count_verdicts(fact_checks: list) -> dict:
    counts = {"TRUE": 0, "FALSE": 0, "MISLEADING": 0, "UNVERIFIABLE": 0, "PARTIALLY_TRUE": 0}
    for fc in fact_checks:
        v = fc.get("verdict", "")
        if v in counts:
            counts[v] += 1
    return counts


def export_to_csv(results: list) -> bytes:
    rows = []
    for r in results:
        fact_checks = r.get("fact_checks", [])
        counts = _count_verdicts(fact_checks)
        entities_str = "; ".join(
            f"{e.get('name')} ({e.get('stance')})" for e in r.get("entities", [])
        )
        cf = r.get("campaign_fit", {})
        for fc in fact_checks:
            rows.append({
                "Source": r.get("source_name", ""),
                "Core Narrative": r.get("core_narrative", ""),
                "Intent": r.get("intent", ""),
                "Sentiment": r.get("sentiment_overall", ""),
                "Fit Score": cf.get("score", ""),
                "Fit Label": cf.get("label", ""),
                "Entities": entities_str,
                "True Claims": counts["TRUE"],
                "False Claims": counts["FALSE"],
                "Misleading": counts["MISLEADING"],
                "Unverifiable": counts["UNVERIFIABLE"],
                "Provider": r.get("provider_used", ""),
                "Claim": fc.get("claim", ""),
                "Claim Type": fc.get("claim_type", ""),
                "Verdict": fc.get("verdict", ""),
                "Confidence": fc.get("confidence", ""),
                "Reasoning": fc.get("reasoning", ""),
                "Correct Fact": fc.get("correct_fact", ""),
                "Source URL": fc.get("source_url", ""),
            })
        if not fact_checks:
            rows.append({
                "Source": r.get("source_name", ""),
                "Core Narrative": r.get("core_narrative", ""),
                "Intent": r.get("intent", ""),
                "Sentiment": r.get("sentiment_overall", ""),
                "Fit Score": cf.get("score", ""),
                "Fit Label": cf.get("label", ""),
                "Entities": entities_str,
                "True Claims": 0, "False Claims": 0,
                "Misleading": 0, "Unverifiable": 0,
                "Provider": r.get("provider_used", ""),
                "Claim": "", "Claim Type": "", "Verdict": "",
                "Confidence": "", "Reasoning": "", "Correct Fact": "", "Source URL": "",
            })

    buf = io.BytesIO()
    pd.DataFrame(rows).to_csv(buf, index=False)
    return buf.getvalue()


def export_to_excel(results: list) -> bytes:
    summary_rows, fc_rows, entity_rows = [], [], []

    for r in results:
        fact_checks = r.get("fact_checks", [])
        counts = _count_verdicts(fact_checks)
        cf = r.get("campaign_fit", {})
        warnings = "; ".join(w for w in r.get("content_warnings", []) if w and w != "none")

        summary_rows.append({
            "Source": r.get("source_name", ""),
            "Core Narrative": r.get("core_narrative", ""),
            "Intent": r.get("intent", ""),
            "Campaign Fit Score": cf.get("score", ""),
            "Campaign Fit Label": cf.get("label", ""),
            "Overall Sentiment": r.get("sentiment_overall", ""),
            "Content Warnings": warnings,
            "Total Claims": len(fact_checks),
            "True Claims": counts["TRUE"],
            "False Claims": counts["FALSE"],
            "Misleading": counts["MISLEADING"],
            "Unverifiable": counts["UNVERIFIABLE"],
            "Provider Used": r.get("provider_used", ""),
        })

        for fc in fact_checks:
            fc_rows.append({
                "Source": r.get("source_name", ""),
                "Claim": fc.get("claim", ""),
                "Type": fc.get("claim_type", ""),
                "Verdict": fc.get("verdict", ""),
                "Confidence": fc.get("confidence", ""),
                "Reasoning": fc.get("reasoning", ""),
                "Correct Fact": fc.get("correct_fact", "") or "",
                "Source URL": fc.get("source_url", "") or "",
            })

        for e in r.get("entities", []):
            entity_rows.append({
                "Source": r.get("source_name", ""),
                "Entity Name": e.get("name", ""),
                "Type": e.get("type", ""),
                "Stance": e.get("stance", ""),
                "Context": e.get("context", ""),
            })

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_sum = pd.DataFrame(summary_rows)
        df_fc = pd.DataFrame(fc_rows) if fc_rows else pd.DataFrame(columns=["Source","Claim","Type","Verdict","Confidence","Reasoning","Correct Fact","Source URL"])
        df_ent = pd.DataFrame(entity_rows) if entity_rows else pd.DataFrame(columns=["Source","Entity Name","Type","Stance","Context"])

        df_sum.to_excel(writer, sheet_name="Summary", index=False)
        df_fc.to_excel(writer, sheet_name="Fact Checks", index=False)
        df_ent.to_excel(writer, sheet_name="Entities", index=False)

        wb = writer.book

        # Color: Campaign Fit Score in Summary
        ws_sum = wb["Summary"]
        score_col = None
        for cell in ws_sum[1]:
            if cell.value == "Campaign Fit Score":
                score_col = cell.column
                break
        if score_col:
            for row in ws_sum.iter_rows(min_row=2, min_col=score_col, max_col=score_col):
                for cell in row:
                    if isinstance(cell.value, (int, float)):
                        if cell.value >= 80:
                            cell.font = Font(color="00D4AA", bold=True)
                        elif cell.value >= 50:
                            cell.font = Font(color="FFB800", bold=True)
                        else:
                            cell.font = Font(color="FF4B6E", bold=True)

        # Color: Verdict column in Fact Checks
        ws_fc = wb["Fact Checks"]
        verdict_col = None
        for cell in ws_fc[1]:
            if cell.value == "Verdict":
                verdict_col = cell.column
                break
        if verdict_col:
            for row in ws_fc.iter_rows(min_row=2, min_col=verdict_col, max_col=verdict_col):
                for cell in row:
                    v = str(cell.value or "")
                    if v in VERDICT_FILLS:
                        cell.fill = VERDICT_FILLS[v]
                        cell.font = VERDICT_FONTS.get(v, Font())

        # Auto-width for all sheets
        for ws in wb.worksheets:
            for col in ws.columns:
                max_len = max((len(str(c.value or "")) for c in col), default=10)
                ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 4, 60)

    return buf.getvalue()
