import streamlit as st


def _verdict_badge(verdict: str) -> str:
    return f'<span class="verdict-{verdict}">{verdict}</span>'


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
            sc = _sentiment_class(sentiment)
            st.markdown(f'<span class="{sc}">{sentiment}</span>', unsafe_allow_html=True)

        st.divider()

        # Row 2: Campaign fit
        cf = r.get("campaign_fit", {})
        score = cf.get("score", 0)
        score_cls = _score_class(score)
        col_s, col_r = st.columns([1, 3])
        with col_s:
            st.markdown("**Campaign Fit**")
            st.markdown(f'<span class="{score_cls}">{score}/100</span>', unsafe_allow_html=True)
            label = cf.get("label", "")
            if label:
                st.caption(label)
        with col_r:
            st.markdown("**Reasoning**")
            st.markdown(cf.get("reasoning", "—"))
            missing = cf.get("missing_elements", [])
            if missing:
                st.markdown("**Missing:** " + ", ".join(missing))

        st.divider()

        # Row 3: Entities
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
                stance_cls = f"entity-{stance}"
                c1, c2, c3, c4 = st.columns([2, 2, 2, 4])
                c1.markdown(e.get("name", ""))
                c2.markdown(e.get("type", ""))
                c3.markdown(f'<span class="{stance_cls}">{stance}</span>', unsafe_allow_html=True)
                c4.markdown(e.get("context", ""))
            st.divider()

        # Row 4: Fact checks
        fact_checks = r.get("fact_checks", [])
        if fact_checks:
            st.markdown("**Fact Checks**")
            for fc in fact_checks:
                verdict = fc.get("verdict", "SKIPPED")
                if verdict == "SKIPPED":
                    continue
                with st.container():
                    fcol1, fcol2 = st.columns([5, 1])
                    with fcol1:
                        st.markdown(f"🔍 *{fc.get('claim', '')}*")
                    with fcol2:
                        st.markdown(_verdict_badge(verdict), unsafe_allow_html=True)

                    confidence = fc.get("confidence", 0)
                    if isinstance(confidence, (int, float)) and confidence > 0:
                        st.progress(int(confidence) / 100, text=f"Confidence: {confidence}%")

                    reasoning = fc.get("reasoning", "")
                    if reasoning:
                        st.caption(reasoning)

                    correct = fc.get("correct_fact")
                    if correct:
                        st.markdown(f"✏️ **Correction:** {correct}")

                    url = fc.get("source_url")
                    title = fc.get("source_title") or url
                    if url:
                        st.markdown(f"🔗 [Source: {title}]({url})")
                    st.markdown("---")

        # Row 5: Warnings
        warnings = [w for w in r.get("content_warnings", []) if w and w.lower() != "none"]
        if warnings:
            st.markdown("**⚠️ Content Warnings**")
            for w in warnings:
                st.warning(w)

        # Provider badge
        provider = r.get("provider_used", "")
        if provider:
            st.markdown(f'<span class="provider-badge">Analyzed by: {provider}</span>', unsafe_allow_html=True)
