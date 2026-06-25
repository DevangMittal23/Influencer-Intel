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


def render_recommendation_badge(recommendation: dict):
    action = recommendation.get('action', 'REVIEW')
    styles = {
        'PUBLISH': ('🟢 PUBLISH',      '#00D4AA', '#0D2818', '#00D4AA'),
        'REVIEW':  ('🟡 NEEDS REVIEW', '#FFB800', '#2D1F00', '#FFB800'),
        'REJECT':  ('🔴 REJECT',       '#FF4B6E', '#2D0F1A', '#FF4B6E'),
    }
    label, text_color, bg_color, border_color = styles.get(action, styles['REVIEW'])
    primary_reason = recommendation.get('primary_reason', '')
    reasons = recommendation.get('reasons', [])
    reasons_html = "".join(
        f'<div style="color:#6B7280;font-size:12px;padding:2px 0;">• {r}</div>'
        for r in reasons
    )
    st.markdown(f"""
        <div style="background:{bg_color};border:1px solid {border_color};
                    border-radius:10px;padding:16px 20px;margin-bottom:16px;">
            <div style="display:flex;align-items:center;justify-content:space-between;">
                <span style="color:{text_color};font-size:18px;font-weight:800;letter-spacing:1px;">
                    {label}
                </span>
                <span style="color:#6B7280;font-size:12px;">Analyst Decision</span>
            </div>
            <div style="color:#E8E8F0;font-size:13px;margin-top:8px;">{primary_reason}</div>
            <div style="margin-top:8px;padding-top:8px;border-top:1px solid #2D3045;">
                {reasons_html}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_campaign_components(campaign_fit: dict):
    components = campaign_fit.get('component_scores', {})
    explanations = campaign_fit.get('component_explanations', {})
    if not components:
        return
    labels = {
        'message_alignment': '💬 Message',
        'entity_coverage':   '👥 Entities',
        'theme_coverage':    '🎯 Theme',
        'purpose_alignment': '🏷️ Purpose',
        'audience_alignment':'👤 Audience',
    }
    st.markdown("**Component Breakdown:**")
    for key, display_label in labels.items():
        score = components.get(key, 0)
        explanation = explanations.get(key, '')
        bar_color = "#00D4AA" if score >= 70 else "#FFB800" if score >= 40 else "#FF4B6E"
        st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px;">
                    <span style="color:#E8E8F0;">{display_label}</span>
                    <span style="color:{bar_color};font-weight:600;">{score}/100</span>
                </div>
                <div style="background:#0F1117;height:6px;border-radius:3px;margin-bottom:3px;">
                    <div style="width:{score}%;height:6px;background:{bar_color};border-radius:3px;"></div>
                </div>
                <div style="color:#6B7280;font-size:11px;">{explanation}</div>
            </div>
        """, unsafe_allow_html=True)
    missing = campaign_fit.get('missing_talking_points', [])
    if missing:
        st.markdown("**Missing Talking Points:** " + " • ".join(f"`{m}`" for m in missing))


def render_fact_check_card(fc: dict, index: int):
    verdict = fc.get('verdict', 'UNVERIFIABLE')
    confidence = fc.get('confidence', 0)
    claim = fc.get('claim', '')
    reasoning = fc.get('reasoning', '')
    correct_fact = fc.get('correct_fact', '')
    source_url = fc.get('source_url', '')
    source_title = fc.get('source_title', 'View Source') or 'View Source'

    verdict_config = {
        'TRUE':           {'icon': '✅', 'label': 'VERIFIED TRUE',   'color': '#00D4AA', 'bg': '#0D2818'},
        'FALSE':          {'icon': '❌', 'label': 'VERIFIED FALSE',  'color': '#FF4B6E', 'bg': '#2D0F1A'},
        'MISLEADING':     {'icon': '⚠️', 'label': 'MISLEADING',      'color': '#FFB800', 'bg': '#2D1F00'},
        'PARTIALLY_TRUE': {'icon': '🔶', 'label': 'PARTIALLY TRUE',  'color': '#40C4AA', 'bg': '#1A2020'},
        'UNVERIFIABLE':   {'icon': '❓', 'label': 'UNVERIFIABLE',    'color': '#6B7280', 'bg': '#1A1D27'},
    }
    cfg = verdict_config.get(verdict, verdict_config['UNVERIFIABLE'])
    short_reasoning = (reasoning[:180] + "...") if len(reasoning) > 180 else reasoning

    correct_fact_html = ""
    if correct_fact and verdict in ['FALSE', 'MISLEADING']:
        correct_fact_html = f"""
            <div style="background:#0D2818;border:1px solid #00D4AA22;border-radius:6px;
                        padding:8px 10px;margin-top:8px;">
                <span style="color:#00D4AA;font-size:11px;font-weight:600;">✏️ CORRECT FACT</span>
                <div style="color:#E8E8F0;font-size:12px;margin-top:3px;">{correct_fact}</div>
            </div>"""

    source_html = ""
    if source_url:
        source_html = f"""
            <a href="{source_url}" target="_blank"
               style="color:#6C63FF;font-size:11px;text-decoration:none;
                      display:inline-block;margin-top:8px;">
                🔗 {str(source_title)[:60]}
            </a>"""

    st.markdown(f"""
        <div style="background:{cfg['bg']};border:1px solid {cfg['color']}33;
                    border-left:3px solid {cfg['color']};
                    border-radius:8px;padding:14px 16px;margin-bottom:10px;">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
                <span style="background:{cfg['bg']};color:{cfg['color']};
                             border:1px solid {cfg['color']};border-radius:4px;
                             padding:3px 10px;font-size:11px;font-weight:800;letter-spacing:0.5px;">
                    {cfg['icon']} {cfg['label']}
                </span>
                <span style="color:#6B7280;font-size:11px;">Confidence: {confidence}%</span>
            </div>
            <div style="background:#0F111722;height:3px;border-radius:2px;margin-bottom:10px;">
                <div style="width:{confidence}%;height:3px;background:{cfg['color']};border-radius:2px;"></div>
            </div>
            <div style="color:#E8E8F0;font-size:13px;font-style:italic;
                        margin-bottom:8px;line-height:1.5;">
                "{claim}"
            </div>
            <details>
                <summary style="color:#6B7280;font-size:12px;cursor:pointer;user-select:none;">
                    📄 Evidence Summary
                </summary>
                <div style="color:#9CA3AF;font-size:12px;margin-top:6px;line-height:1.6;padding-left:10px;">
                    {short_reasoning}
                </div>
            </details>
            {correct_fact_html}
            {source_html}
        </div>
    """, unsafe_allow_html=True)


def render_result_card(r: dict):
    source = r.get("source_name", "Unknown")
    status = r.get("analysis_status", "success")

    with st.expander(f"📄 {source}", expanded=False):
        if status != "success":
            st.error(f"Analysis failed: {r.get('error', 'Unknown error')}")
            return

        # Recommendation badge — very top
        rec = r.get('recommendation', {})
        if rec:
            render_recommendation_badge(rec)

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

        # Row 2: Campaign fit + component scores
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

        render_campaign_components(cf)
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

        # Row 5: Fact checks
        fact_checks = r.get("fact_checks", [])
        checked = [fc for fc in fact_checks if fc.get("verdict") != "SKIPPED"]
        st.markdown("**🔍 Fact Checks**")
        if checked:
            for i, fc in enumerate(checked):
                render_fact_check_card(fc, i)
        else:
            st.info("No fact checks performed for this item.")

        # Row 6: Warnings
        warnings = [w for w in r.get("content_warnings", []) if w and w.lower() != "none"]
        if warnings:
            st.markdown("**⚠️ Content Warnings**")
            for w in warnings:
                st.warning(w)

        provider = r.get("provider_used", "")
        if provider:
            st.markdown(f'<span class="provider-badge">Analyzed by: {provider}</span>', unsafe_allow_html=True)
