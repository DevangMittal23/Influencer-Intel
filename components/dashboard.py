import streamlit as st
import pandas as pd


def _count_verdicts(fact_checks: list) -> dict:
    counts = {"TRUE": 0, "FALSE": 0, "MISLEADING": 0, "UNVERIFIABLE": 0}
    for fc in fact_checks:
        v = fc.get("verdict", "")
        if v in counts:
            counts[v] += 1
    return counts


def generate_executive_summary(results: list) -> dict:
    total = len(results)
    publish = sum(1 for r in results if r.get('recommendation', {}).get('action') == 'PUBLISH')
    review  = sum(1 for r in results if r.get('recommendation', {}).get('action') == 'REVIEW')
    reject  = sum(1 for r in results if r.get('recommendation', {}).get('action') == 'REJECT')

    fit_scores = [r.get('campaign_fit', {}).get('score', 0) for r in results]
    avg_fit = round(sum(fit_scores) / total, 1) if total else 0

    high_risk = sum(1 for r in results if r.get('risk_assessment', {}).get('risk_level') == 'HIGH')

    misleading_total = sum(
        sum(1 for fc in r.get('fact_checks', []) if fc.get('verdict') in ['FALSE', 'MISLEADING'])
        for r in results
    )

    highest_risk_item = max(
        results,
        key=lambda r: r.get('risk_assessment', {}).get('risk_score', 0),
        default=None,
    )

    return {
        'total': total,
        'publish': publish,
        'review': review,
        'reject': reject,
        'avg_fit': avg_fit,
        'high_risk_count': high_risk,
        'misleading_total': misleading_total,
        'highest_risk_source': (
            highest_risk_item.get('source_name', 'N/A') if highest_risk_item else 'N/A'
        ),
    }


def render_executive_summary(summary: dict):
    st.markdown("### 📋 Executive Summary")

    if summary['reject'] == 0 and summary['review'] == 0:
        overall_color = "#00D4AA"
        overall_text  = "✅ Batch is safe for publication"
    elif summary['reject'] > 0:
        overall_color = "#FF4B6E"
        overall_text  = f"🔴 {summary['reject']} item(s) should be rejected"
    else:
        overall_color = "#FFB800"
        overall_text  = f"🟡 {summary['review']} item(s) need manual review"

    st.markdown(f"""
        <div style="background:#1A1D27;border:1px solid {overall_color};
                    border-left:4px solid {overall_color};
                    border-radius:10px;padding:18px 20px;margin-bottom:20px;">
            <div style="color:{overall_color};font-size:16px;font-weight:700;margin-bottom:12px;">
                {overall_text}
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:12px;">
                <div style="text-align:center;">
                    <div style="color:#E8E8F0;font-size:24px;font-weight:700;">{summary['total']}</div>
                    <div style="color:#6B7280;font-size:12px;">Items Analyzed</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#00D4AA;font-size:24px;font-weight:700;">{summary['avg_fit']}%</div>
                    <div style="color:#6B7280;font-size:12px;">Avg Campaign Fit</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#FF4B6E;font-size:24px;font-weight:700;">{summary['misleading_total']}</div>
                    <div style="color:#6B7280;font-size:12px;">Misleading Claims</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#FFB800;font-size:24px;font-weight:700;">{summary['high_risk_count']}</div>
                    <div style="color:#6B7280;font-size:12px;">High Risk Items</div>
                </div>
            </div>
            <div style="display:flex;gap:20px;padding-top:12px;border-top:1px solid #2D3045;font-size:13px;">
                <span style="color:#00D4AA;">🟢 Publish: <strong>{summary['publish']}</strong></span>
                <span style="color:#FFB800;">🟡 Review: <strong>{summary['review']}</strong></span>
                <span style="color:#FF4B6E;">🔴 Reject: <strong>{summary['reject']}</strong></span>
                <span style="color:#6B7280;margin-left:auto;">
                    Highest Risk: {summary['highest_risk_source']}
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)


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
        ("📦", "Items Analyzed",    total,       "#6C63FF"),
        ("🎯", "Avg Campaign Fit",  f"{avg_score}%", "#00D4AA"),
        ("🔍", "Claims Checked",    total_claims, "#FFB800"),
        ("⚠️", "False / Misleading", bad_claims,  "#FF4B6E"),
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
        sort_by = st.selectbox("Sort by", ["Campaign Score ↓", "Source Name", "False Claims ↓", "Risk Score ↓"], key="sort_filter")

    rows = []
    for r in results:
        if r.get("analysis_status") != "success":
            continue
        fcs = r.get("fact_checks", [])
        counts = _count_verdicts(fcs)
        row_verdicts = {fc.get("verdict") for fc in fcs}
        if selected_verdicts and not row_verdicts.intersection(set(selected_verdicts)) and fcs:
            continue
        score = r.get("campaign_fit", {}).get("score", 0)
        if isinstance(score, (int, float)) and score < min_score:
            continue
        risk = r.get("risk_assessment", {})
        action = r.get("recommendation", {}).get("action", "—")
        rows.append({
            "_result": r,
            "Source": r.get("source_name", ""),
            "Narrative Preview": (r.get("core_narrative", "") or "")[:80] + "…",
            "Intent": r.get("intent", ""),
            "Fit Score": score,
            "Risk Score": risk.get("risk_score", 0),
            "Risk Level": risk.get("risk_level", "N/A"),
            "Action": action,
            "Review": "🚨 Review" if risk.get("needs_human_review", False) else "✅ Clear",
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
    elif sort_by == "Risk Score ↓":
        rows.sort(key=lambda x: x["Risk Score"], reverse=True)

    if rows:
        display_df = pd.DataFrame([{k: v for k, v in row.items() if k != "_result"} for row in rows])
        st.dataframe(
            display_df,
            column_config={
                "Fit Score": st.column_config.ProgressColumn("Fit Score", min_value=0, max_value=100, format="%d"),
                "Risk Score": st.column_config.ProgressColumn("Risk Score", min_value=0, max_value=10, format="%.1f"),
                "Action": st.column_config.TextColumn("📋 Action", width="small"),
                "Review": st.column_config.TextColumn("👁 Review", width="small"),
                "Narrative Preview": st.column_config.TextColumn("Narrative Preview", width="large"),
            },
            use_container_width=True,
            hide_index=True,
            height=400,
        )

    return [row["_result"] for row in rows]
