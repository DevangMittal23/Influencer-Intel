import streamlit as st
import pandas as pd


def _count_verdicts(fact_checks: list) -> dict:
    counts = {"TRUE": 0, "FALSE": 0, "MISLEADING": 0, "UNVERIFIABLE": 0}
    for fc in fact_checks:
        v = fc.get("verdict", "")
        if v in counts:
            counts[v] += 1
    return counts


def render_metrics(results: list):
    total = len(results)
    scores = [
        r.get("campaign_fit", {}).get("score", 0)
        for r in results
        if r.get("analysis_status") == "success"
    ]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    total_claims = sum(len(r.get("fact_checks", [])) for r in results)
    bad_claims = sum(
        _count_verdicts(r.get("fact_checks", []))["FALSE"] +
        _count_verdicts(r.get("fact_checks", []))["MISLEADING"]
        for r in results
    )

    cols = st.columns(4)
    metrics = [
        ("📦", "Items Analyzed", total, "#6C63FF"),
        ("🎯", "Avg Campaign Fit", f"{avg_score}%", "#00D4AA"),
        ("🔍", "Claims Checked", total_claims, "#FFB800"),
        ("⚠️", "False / Misleading", bad_claims, "#FF4B6E"),
    ]
    for col, (icon, label, value, color) in zip(cols, metrics):
        with col:
            st.markdown(
                f'<div class="metric-card">'
                f'<div style="font-size:24px">{icon}</div>'
                f'<div class="metric-value" style="color:{color}">{value}</div>'
                f'<div class="metric-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_dashboard_table(results: list) -> list:
    """Render filters + table. Returns filtered results list."""
    if not results:
        return results

    st.markdown("#### Filters")
    all_verdicts = ["TRUE", "FALSE", "MISLEADING", "PARTIALLY_TRUE", "UNVERIFIABLE"]
    fcol1, fcol2, fcol3 = st.columns([2, 2, 2])
    with fcol1:
        selected_verdicts = st.multiselect("Filter by Verdict", all_verdicts, default=all_verdicts, key="verdict_filter")
    with fcol2:
        min_score = st.slider("Min Campaign Fit Score", 0, 100, 0, key="score_filter")
    with fcol3:
        sort_by = st.selectbox("Sort by", ["Campaign Score ↓", "Source Name", "False Claims ↓"], key="sort_filter")

    # Build rows for display
    rows = []
    for r in results:
        if r.get("analysis_status") != "success":
            continue
        fcs = r.get("fact_checks", [])
        counts = _count_verdicts(fcs)
        # Check verdict filter: include row if any of its verdicts match selected
        row_verdicts = {fc.get("verdict") for fc in fcs}
        if selected_verdicts and not row_verdicts.intersection(set(selected_verdicts)) and fcs:
            continue
        score = r.get("campaign_fit", {}).get("score", 0)
        if isinstance(score, (int, float)) and score < min_score:
            continue
        rows.append({
            "_result": r,
            "Source": r.get("source_name", ""),
            "Narrative Preview": (r.get("core_narrative", "") or "")[:80] + "…",
            "Intent": r.get("intent", ""),
            "Fit Score": score,
            "✅ True": counts["TRUE"],
            "❌ False": counts["FALSE"],
            "⚠️ Mislead": counts["MISLEADING"],
            "❓ Unverif.": counts["UNVERIFIABLE"],
        })

    if sort_by == "Campaign Score ↓":
        rows.sort(key=lambda x: x["Fit Score"], reverse=True)
    elif sort_by == "Source Name":
        rows.sort(key=lambda x: x["Source"].lower())
    elif sort_by == "False Claims ↓":
        rows.sort(key=lambda x: x["❌ False"], reverse=True)

    if rows:
        display_df = pd.DataFrame([{k: v for k, v in row.items() if k != "_result"} for row in rows])
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    return [row["_result"] for row in rows]
