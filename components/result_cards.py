import streamlit as st


def _score_class(score) -> str:
    try:
        s = int(score)
    except (TypeError, ValueError):
        return "campaign-score-low"
    if s >= 80:
        return "campaign-score-high"
    if s >= 50:
        return "campaign-score-mid"
    return "campaign-score-low"


def _sentiment_class(s: str) -> str:
    return f"sentiment-{s.lower()}" if s else "sentiment-neutral"


def render_result_card(r: dict):
    source = r.get("source_name", "Unknown")
    status = r.get("analysis_status", "success")

    with st.expander(f"📄 {source}", expanded=False):
        if status != "success":
            st.error(f"Analysis failed: {r.get('error', 'Unknown error')}")
            return

        # Row 1: Narrative + intent + sentiment
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.markdown("**Core Narrative**")
            st.markdown(r.get("core_narrative", "—"))
        with col2:
            st.markdown("**Intent**")
            intent = r.get("intent", "—")
            st.markdown(f'<span class="intent-badge">{intent}</span>', unsafe_allow_html=True)
        with col3:
            st.markdown("**Sentiment**")
            sentiment = r.get("sentiment_overall", "—")
            st.markdown(f'<span class="{_sentiment_class(sentiment)}">{sentiment}</span>', unsafe_allow_html=True)

        st.divider()

        # Row 2: Campaign fit
        cf = r.get("campaign_fit", {})
        score = cf.get("score", 0)
        col_s, col_r = st.columns([1, 3])
        with col_s:
            st.markdown("**Campaign Fit**")
            st.markdown(f'<span class="{_score_class(score)}">{score}/100</span>', unsafe_allow_html=True)
            if cf.get("label"):
                st.caption(cf["label"])
        with col_r:
            st.markdown("**Reasoning**")
            st.markdown(cf.get("reasoning", "—"))
            missing = cf.get("missing_elements", [])
            if missing:
                st.markdown("**Missing:** " + ", ".join(missing))

        st.divider()

        # Row 3: Risk Assessment
        st.markdown("**⚠️ Risk Assessment**")
        risk = r.get("risk_assessment", {})
        risk_level = risk.get("risk_level", "LOW")
        risk_score = risk.get("risk_score", 0)
        needs_review = risk.get("needs_human_review", False)

        level_colors = {"HIGH": "#FF4B6E", "MEDIUM": "#FFB800", "LOW": "#00D4AA"}
        color = level_colors.get(risk_level, "#6B7280")

        risk_col1, risk_col2, risk_col3 = st.columns([1, 2, 1])
        with risk_col1:
            st.markdown(f"""
                <div style="background:{color}22;border:1px solid {color};border-radius:8px;
                            padding:12px;text-align:center;">
                    <div style="color:{color};font-size:24px;font-weight:700;">{risk_score}/10</div>
                    <div style="color:{color};font-size:12px;font-weight:600;">{risk_level} RISK</div>
                </div>
            """, unsafe_allow_html=True)
        with risk_col2:
            factors = risk.get("risk_factors", [])
            if factors:
                st.markdown("**Risk Factors:**")
                for f in factors:
                    st.markdown(f"• {f}")
            else:
                st.markdown("*No specific risk factors identified*")
        with risk_col3:
            if needs_review:
                st.markdown("""
                    <div style="background:#2D0F1A;border:1px solid #FF4B6E;border-radius:8px;
                                padding:12px;text-align:center;">
                        <div style="font-size:20px;">🚨</div>
                        <div style="color:#FF4B6E;font-size:12px;font-weight:600;margin-top:4px;">
                            HUMAN REVIEW<br>REQUIRED
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="background:#0D2818;border:1px solid #00D4AA;border-radius:8px;
                                padding:12px;text-align:center;">
                        <div style="font-size:20px;">✅</div>
                        <div style="color:#00D4AA;font-size:12px;font-weight:600;margin-top:4px;">
                            CLEARED<br>AUTO-CHECK
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Campaign Alignment
        alignment = r.get("campaign_alignment", {})
        if alignment:
            aligned = alignment.get("aligned", False)
            align_color = "#00D4AA" if aligned else "#FF4B6E"
            align_icon = "✅" if aligned else "❌"
            align_label = "Aligned" if aligned else "Off-Message"
            st.markdown(f"""
                <div class="metric-card" style="margin-top:8px;border-color:{align_color};text-align:left;">
                    <span style="color:{align_color};font-weight:600;">
                        {align_icon} Campaign Alignment: {align_label}
                    </span><br>
                    <span style="color:#6B7280;font-size:13px;">
                        {alignment.get('alignment_summary', '')}
                    </span>
                </div>
            """, unsafe_allow_html=True)
            red_flags = alignment.get("red_flags", [])
            if red_flags:
                st.markdown("**Red Flags:** " + " • ".join(f"`{f}`" for f in red_flags))

        st.divider()

        # Row 4: Entities
        entities = r.get("entities", [])
        if entities:
            st.markdown("**Entities Mentioned**")
            cols = st.columns([2, 2, 2, 4])
            cols[0].markdown("**Name**")
            cols[1].markdown("**Type**")
            cols[2].markdown("**Stance**")
            cols[3].markdown("**Context**")
            for e in entities:
                stance = e.get("stance", "neutral")
                c1, c2, c3, c4 = st.columns([2, 2, 2, 4])
                c1.markdown(e.get("name", ""))
                c2.markdown(e.get("type", ""))
                c3.markdown(f'<span class="entity-{stance}">{stance}</span>', unsafe_allow_html=True)
                c4.markdown(e.get("context", ""))
            st.divider()

        # Row 5: Fact checks — enhanced HTML cards
        fact_checks = r.get("fact_checks", [])
        if fact_checks:
            st.markdown("**Fact Checks**")
            verdict_map = {
                "TRUE":           ("✅", "#00D4AA", "#0D2818"),
                "FALSE":          ("❌", "#FF4B6E", "#2D0F1A"),
                "MISLEADING":     ("⚠️", "#FFB800", "#2D1F00"),
                "PARTIALLY_TRUE": ("🔶", "#40C4AA", "#1A2020"),
                "UNVERIFIABLE":   ("❓", "#6B7280", "#1A1D27"),
            }
            for fc in fact_checks:
                verdict = fc.get("verdict", "UNVERIFIABLE")
                if verdict == "SKIPPED":
                    continue
                confidence = fc.get("confidence", 0)
                icon, text_color, bg_color = verdict_map.get(verdict, ("❓", "#6B7280", "#1A1D27"))
                correct_html = (
                    f'<div style="color:#00D4AA;font-size:12px;margin-top:6px;">✏️ Correct: {fc.get("correct_fact","")}</div>'
                    if fc.get("correct_fact") else ""
                )
                source_html = (
                    f'<a href="{fc.get("source_url","")}" target="_blank" '
                    f'style="color:#6C63FF;font-size:12px;">🔗 {fc.get("source_title","View Source")}</a>'
                    if fc.get("source_url") else ""
                )
                reasoning_text = (fc.get("reasoning") or "")[:200]
                claim_text = fc.get("claim", "")
                st.markdown(f"""
                    <div style="background:{bg_color};border:1px solid {text_color};
                                border-radius:8px;padding:12px;margin-bottom:10px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
                            <span style="color:{text_color};font-weight:700;">{icon} {verdict}</span>
                            <span style="color:#6B7280;font-size:12px;">{confidence}% confidence</span>
                        </div>
                        <div style="background:#0F1117;height:4px;border-radius:2px;">
                            <div style="width:{confidence}%;height:4px;background:{text_color};border-radius:2px;"></div>
                        </div>
                        <div style="color:#E8E8F0;font-size:13px;margin-top:8px;">"{claim_text}"</div>
                        <div style="color:#6B7280;font-size:12px;margin-top:6px;">{reasoning_text}</div>
                        {correct_html}
                        {source_html}
                    </div>
                """, unsafe_allow_html=True)

        # Row 6: Warnings
        warnings = [w for w in r.get("content_warnings", []) if w and w.lower() != "none"]
        if warnings:
            st.markdown("**⚠️ Content Warnings**")
            for w in warnings:
                st.warning(w)

        provider = r.get("provider_used", "")
        if provider:
            st.markdown(f'<span class="provider-badge">Analyzed by: {provider}</span>', unsafe_allow_html=True)
