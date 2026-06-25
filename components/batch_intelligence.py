from collections import Counter, defaultdict
import streamlit as st


def render_batch_intelligence(results: list):
    if not results:
        st.warning("No results to display.")
        return

    st.markdown("## 📈 Batch Intelligence Report")
    st.markdown(f"*Aggregate analysis across {len(results)} content items — answers what matters at scale*")
    st.divider()

    _render_campaign_health(results)
    st.divider()
    _render_review_queue(results)
    st.divider()
    _render_top_flagged_claims(results)
    st.divider()
    _render_entity_frequency(results)
    st.divider()
    _render_intent_breakdown(results)
    st.divider()
    _render_campaign_coverage(results)
    st.divider()
    _render_verdict_distribution(results)
    st.divider()
    _render_action_distribution(results)


def _render_campaign_health(results: list):
    st.markdown("### 🎯 Campaign Health Overview")

    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    campaign_scores = []

    for r in results:
        level = r.get("risk_assessment", {}).get("risk_level", "LOW")
        risk_counts[level] = risk_counts.get(level, 0) + 1
        score = r.get("campaign_fit", {}).get("score", 0)
        if isinstance(score, (int, float)):
            campaign_scores.append(score)

    avg_fit = round(sum(campaign_scores) / len(campaign_scores), 1) if campaign_scores else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card" style="border-color:#FF4B6E;">
                <div style="font-size:28px;">🔴</div>
                <div style="font-size:36px;font-weight:700;color:#FF4B6E;">{risk_counts['HIGH']}</div>
                <div style="color:#6B7280;font-size:13px;">HIGH RISK items</div>
                <div style="color:#6B7280;font-size:11px;margin-top:4px;">Immediate attention needed</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card" style="border-color:#FFB800;">
                <div style="font-size:28px;">🟡</div>
                <div style="font-size:36px;font-weight:700;color:#FFB800;">{risk_counts['MEDIUM']}</div>
                <div style="color:#6B7280;font-size:13px;">MEDIUM RISK items</div>
                <div style="color:#6B7280;font-size:11px;margin-top:4px;">Review recommended</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card" style="border-color:#00D4AA;">
                <div style="font-size:28px;">🟢</div>
                <div style="font-size:36px;font-weight:700;color:#00D4AA;">{risk_counts['LOW']}</div>
                <div style="color:#6B7280;font-size:13px;">LOW RISK items</div>
                <div style="color:#6B7280;font-size:11px;margin-top:4px;">Generally safe content</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        fit_color = "#00D4AA" if avg_fit >= 60 else "#FFB800" if avg_fit >= 30 else "#FF4B6E"
        st.markdown(f"""
            <div class="metric-card" style="border-color:{fit_color};">
                <div style="font-size:28px;">🎯</div>
                <div style="font-size:36px;font-weight:700;color:{fit_color};">{avg_fit}%</div>
                <div style="color:#6B7280;font-size:13px;">Avg Campaign Fit</div>
                <div style="color:#6B7280;font-size:11px;margin-top:4px;">Across all content</div>
            </div>
        """, unsafe_allow_html=True)

    total = len(results)
    if total > 0:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Risk Distribution**")
        high_pct = int((risk_counts["HIGH"] / total) * 100)
        med_pct  = int((risk_counts["MEDIUM"] / total) * 100)
        low_pct  = 100 - high_pct - med_pct
        st.markdown(f"""
            <div style="display:flex;height:24px;border-radius:8px;overflow:hidden;margin:8px 0;">
                <div style="width:{high_pct}%;background:#FF4B6E;display:flex;align-items:center;
                            justify-content:center;font-size:11px;font-weight:600;color:white;">
                    {high_pct}%
                </div>
                <div style="width:{med_pct}%;background:#FFB800;display:flex;align-items:center;
                            justify-content:center;font-size:11px;font-weight:600;color:#0F1117;">
                    {med_pct}%
                </div>
                <div style="width:{low_pct}%;background:#00D4AA;display:flex;align-items:center;
                            justify-content:center;font-size:11px;font-weight:600;color:#0F1117;">
                    {low_pct}%
                </div>
            </div>
            <div style="display:flex;gap:16px;font-size:11px;color:#6B7280;">
                <span>🔴 HIGH</span><span>🟡 MEDIUM</span><span>🟢 LOW</span>
            </div>
        """, unsafe_allow_html=True)


def _render_review_queue(results: list):
    st.markdown("### 🚨 Human Review Queue")
    st.caption("Items flagged for mandatory human review based on risk score, false claims, and intent analysis")

    flagged = []
    for r in results:
        risk = r.get("risk_assessment", {})
        if risk.get("needs_human_review", False):
            flagged.append({
                "source": r.get("source_name", "Unknown"),
                "risk_level": risk.get("risk_level", "MEDIUM"),
                "risk_score": risk.get("risk_score", 0),
                "reason": risk.get("review_reason", "Manual review recommended"),
                "risk_factors": risk.get("risk_factors", []),
                "fit_score": r.get("campaign_fit", {}).get("score", 0),
                "false_claims": sum(
                    1 for fc in r.get("fact_checks", [])
                    if fc.get("verdict") in ["FALSE", "MISLEADING"]
                ),
            })

    flagged.sort(key=lambda x: x["risk_score"], reverse=True)

    if not flagged:
        st.markdown("""
            <div class="metric-card" style="text-align:center;border-color:#00D4AA;padding:30px;">
                <div style="font-size:32px;">✅</div>
                <div style="color:#00D4AA;font-size:16px;font-weight:600;margin-top:8px;">
                    No items flagged for review
                </div>
                <div style="color:#6B7280;font-size:13px;margin-top:4px;">
                    All content passed automated risk assessment
                </div>
            </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"**{len(flagged)} of {len(results)} items require human review**")
    for item in flagged:
        with st.expander(
            f"🚨 {item['source']} — Risk Score: {item['risk_score']}/10 ({item['risk_level']})",
            expanded=(item["risk_level"] == "HIGH"),
        ):
            c1, c2, c3 = st.columns(3)
            c1.metric("Risk Score", f"{item['risk_score']}/10")
            c2.metric("False/Misleading", item["false_claims"])
            c3.metric("Campaign Fit", f"{item['fit_score']}/100")
            st.markdown(f"**Review Reason:** {item['reason']}")
            if item["risk_factors"]:
                st.markdown("**Risk Factors:**")
                for factor in item["risk_factors"]:
                    st.markdown(f"• {factor}")


def _render_top_flagged_claims(results: list):
    st.markdown("### ❌ Top Flagged Claims Across Batch")
    st.caption("Verified false or misleading claims found across all content — sorted by severity")

    all_flagged = []
    for r in results:
        source = r.get("source_name", "Unknown")
        for fc in r.get("fact_checks", []):
            if fc.get("verdict") in ["FALSE", "MISLEADING", "PARTIALLY_TRUE"]:
                all_flagged.append({
                    "claim": fc.get("claim", ""),
                    "verdict": fc.get("verdict", ""),
                    "confidence": fc.get("confidence", 0),
                    "reasoning": fc.get("reasoning", ""),
                    "correct_fact": fc.get("correct_fact", ""),
                    "content_source": source,
                })

    verdict_order = {"FALSE": 0, "MISLEADING": 1, "PARTIALLY_TRUE": 2}
    all_flagged.sort(key=lambda x: (verdict_order.get(x["verdict"], 3), -x["confidence"]))

    if not all_flagged:
        st.markdown("""
            <div class="metric-card" style="text-align:center;border-color:#00D4AA;padding:30px;">
                <div style="font-size:32px;">✅</div>
                <div style="color:#00D4AA;font-size:16px;font-weight:600;margin-top:8px;">
                    No false or misleading claims verified
                </div>
                <div style="color:#6B7280;font-size:13px;">
                    Either all claims checked out, or fact-checking was skipped
                </div>
            </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"**{len(all_flagged)} flagged claims found**")
    styles = {
        "FALSE":          ("❌", "#FF4B6E", "#2D0F1A"),
        "MISLEADING":     ("⚠️", "#FFB800", "#2D1F00"),
        "PARTIALLY_TRUE": ("🔶", "#40C4AA", "#1A2020"),
    }
    for claim in all_flagged[:10]:
        icon, text_color, bg_color = styles.get(claim["verdict"], ("❓", "#6B7280", "#1A1D27"))
        correct_html = (
            f'<div style="color:#00D4AA;font-size:12px;">✏️ Correct fact: {claim["correct_fact"]}</div>'
            if claim.get("correct_fact") else ""
        )
        st.markdown(f"""
            <div class="metric-card" style="margin-bottom:12px;border-left:3px solid {text_color};">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                    <span style="background:{bg_color};color:{text_color};padding:3px 10px;
                                border-radius:4px;font-size:12px;font-weight:700;">
                        {icon} {claim['verdict']}
                    </span>
                    <span style="color:#6B7280;font-size:12px;">Confidence: {claim['confidence']}%</span>
                    <span style="color:#6B7280;font-size:12px;margin-left:auto;">
                        Source: {claim['content_source']}
                    </span>
                </div>
                <div style="color:#E8E8F0;font-size:14px;font-weight:500;margin-bottom:6px;">
                    "{claim['claim']}"
                </div>
                <div style="color:#6B7280;font-size:12px;margin-bottom:6px;">
                    {(claim['reasoning'] or '')[:200]}{'...' if len(claim.get('reasoning','')) > 200 else ''}
                </div>
                {correct_html}
            </div>
        """, unsafe_allow_html=True)

    if len(all_flagged) > 10:
        st.caption(f"Showing top 10 of {len(all_flagged)} flagged claims. Download Excel export for full list.")


def _render_entity_frequency(results: list):
    st.markdown("### 👥 Entity Frequency Analysis")
    st.caption("People and organizations mentioned across all content — with their overall stance pattern")

    entity_data: dict = defaultdict(lambda: {
        "total": 0, "supported": 0, "criticized": 0, "neutral": 0,
        "type": "unknown", "sources": [],
    })

    for r in results:
        source = r.get("source_name", "Unknown")
        for entity in r.get("entities", []):
            name = (entity.get("name") or "").strip()
            if len(name) < 2:
                continue
            entity_data[name]["total"] += 1
            stance = entity.get("stance", "neutral")
            entity_data[name][stance] = entity_data[name].get(stance, 0) + 1
            entity_data[name]["type"] = entity.get("type", "unknown")
            if source not in entity_data[name]["sources"]:
                entity_data[name]["sources"].append(source)

    if not entity_data:
        st.info("No entities found in analyzed content.")
        return

    sorted_entities = sorted(entity_data.items(), key=lambda x: x[1]["total"], reverse=True)[:12]
    max_count = sorted_entities[0][1]["total"] if sorted_entities else 1
    type_icons = {"person": "👤", "organization": "🏢", "government": "🏛️", "brand": "🏷️"}

    for name, data in sorted_entities:
        bar_pct = int((data["total"] / max_count) * 100)
        if data["criticized"] > data["supported"]:
            bar_color, stance_label = "#FF4B6E", "mostly criticized"
        elif data["supported"] > data["criticized"]:
            bar_color, stance_label = "#00D4AA", "mostly supported"
        else:
            bar_color, stance_label = "#6B7280", "mixed/neutral"
        icon = type_icons.get(data["type"], "📌")
        st.markdown(f"""
            <div style="margin-bottom:14px;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <span style="color:#E8E8F0;font-size:14px;font-weight:500;">{icon} {name}</span>
                    <span style="color:#6B7280;font-size:12px;">{data['total']} mentions — {stance_label}</span>
                </div>
                <div style="display:flex;height:8px;border-radius:4px;overflow:hidden;background:#1A1D27;">
                    <div style="width:{bar_pct}%;background:{bar_color};border-radius:4px;"></div>
                </div>
                <div style="display:flex;gap:12px;margin-top:4px;font-size:11px;">
                    <span style="color:#00D4AA;">✓ {data['supported']} supported</span>
                    <span style="color:#FF4B6E;">✗ {data['criticized']} criticized</span>
                    <span style="color:#6B7280;">~ {data['neutral']} neutral</span>
                    <span style="color:#6B7280;margin-left:auto;">In {len(data['sources'])} item(s)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)


def _render_intent_breakdown(results: list):
    st.markdown("### 🧠 Intent & Alignment Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Intent Distribution**")
        intent_counts = Counter(r.get("intent", "unknown") for r in results)
        intent_colors = {
            "inform": "#6C63FF", "persuade": "#FFB800", "mislead": "#FF4B6E",
            "criticize": "#FF8C42", "promote": "#00D4AA", "entertain": "#40C4AA",
        }
        for intent, count in intent_counts.most_common():
            pct = int((count / len(results)) * 100)
            color = intent_colors.get(intent, "#6B7280")
            st.markdown(f"""
                <div style="margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px;">
                        <span style="color:#E8E8F0;text-transform:capitalize;">{intent}</span>
                        <span style="color:{color};font-weight:600;">{count} items ({pct}%)</span>
                    </div>
                    <div style="height:6px;background:#1A1D27;border-radius:3px;">
                        <div style="width:{pct}%;height:6px;background:{color};border-radius:3px;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("**Campaign Alignment**")
        aligned = sum(1 for r in results if r.get("campaign_alignment", {}).get("aligned", False))
        not_aligned = len(results) - aligned
        aligned_pct = int((aligned / len(results)) * 100) if results else 0
        fit_color = "#00D4AA" if aligned_pct >= 50 else "#FF4B6E"
        st.markdown(f"""
            <div class="metric-card" style="text-align:center;padding:24px;">
                <div style="font-size:42px;font-weight:700;color:{fit_color};">{aligned_pct}%</div>
                <div style="color:#6B7280;font-size:13px;margin-top:4px;">Content aligned with campaign</div>
                <div style="margin-top:16px;font-size:13px;">
                    <span style="color:#00D4AA;">✓ {aligned} aligned</span>
                    &nbsp;&nbsp;
                    <span style="color:#FF4B6E;">✗ {not_aligned} off-message</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        all_flags = []
        for r in results:
            all_flags.extend(r.get("campaign_alignment", {}).get("red_flags", []))
        if all_flags:
            st.markdown("**Top Red Flags:**")
            for flag, count in Counter(all_flags).most_common(3):
                st.markdown(f"• {flag} *({count} items)*")


def _render_campaign_coverage(results: list):
    st.markdown("### 🎯 Campaign Coverage Metrics")
    st.caption("How well does the entire batch cover your campaign requirements?")

    total = len(results)
    if total == 0:
        return

    msg_scores    = [r.get('campaign_fit', {}).get('component_scores', {}).get('message_alignment', 0) for r in results]
    entity_scores = [r.get('campaign_fit', {}).get('component_scores', {}).get('entity_coverage', 0) for r in results]
    theme_scores  = [r.get('campaign_fit', {}).get('component_scores', {}).get('theme_coverage', 0) for r in results]

    avg_msg    = round(sum(msg_scores) / total, 1)
    avg_entity = round(sum(entity_scores) / total, 1)
    avg_theme  = round(sum(theme_scores) / total, 1)

    cols = st.columns(3)
    for col, (label, score) in zip(cols, [
        ("💬 Message Alignment", avg_msg),
        ("👥 Entity Coverage",   avg_entity),
        ("🎯 Theme Coverage",    avg_theme),
    ]):
        color = "#00D4AA" if score >= 70 else "#FFB800" if score >= 40 else "#FF4B6E"
        with col:
            st.markdown(f"""
                <div class="metric-card" style="text-align:center;border-color:{color};">
                    <div style="font-size:28px;font-weight:700;color:{color};">{score}%</div>
                    <div style="color:#6B7280;font-size:12px;margin-top:4px;">{label}</div>
                </div>
            """, unsafe_allow_html=True)

    all_missing = []
    for r in results:
        all_missing.extend(r.get('campaign_fit', {}).get('missing_talking_points', []))
    if all_missing:
        st.markdown("**⚠️ Most Frequently Missing from Content:**")
        for point, count in Counter(all_missing).most_common(5):
            st.markdown(f"• {point} *(missing in {count} items)*")


def _render_verdict_distribution(results: list):
    st.markdown("### 📊 Claim Verdict Distribution")

    verdict_counts = {"TRUE": 0, "FALSE": 0, "MISLEADING": 0, "PARTIALLY_TRUE": 0, "UNVERIFIABLE": 0}
    for r in results:
        for fc in r.get("fact_checks", []):
            v = fc.get("verdict", "")
            if v in verdict_counts:
                verdict_counts[v] += 1

    total_claims = sum(verdict_counts.values())
    if total_claims == 0:
        st.info("No fact checks performed.")
        return

    colors = {"TRUE": "#00D4AA", "FALSE": "#FF4B6E", "MISLEADING": "#FFB800", "PARTIALLY_TRUE": "#40C4AA", "UNVERIFIABLE": "#6B7280"}
    icons  = {"TRUE": "✅",       "FALSE": "❌",       "MISLEADING": "⚠️",      "PARTIALLY_TRUE": "🔶",      "UNVERIFIABLE": "❓"}

    cols = st.columns(5)
    for col, (verdict, count) in zip(cols, verdict_counts.items()):
        pct = round((count / total_claims) * 100, 1)
        color = colors[verdict]
        with col:
            st.markdown(f"""
                <div class="metric-card" style="text-align:center;border-color:{color};padding:14px;">
                    <div style="font-size:20px;">{icons[verdict]}</div>
                    <div style="color:{color};font-size:22px;font-weight:700;">{count}</div>
                    <div style="color:#6B7280;font-size:10px;">{verdict}</div>
                    <div style="color:{color};font-size:11px;">{pct}%</div>
                </div>
            """, unsafe_allow_html=True)


def _render_action_distribution(results: list):
    st.markdown("### 📋 Batch Action Summary")

    action_counts = {"PUBLISH": 0, "REVIEW": 0, "REJECT": 0}
    action_items  = {"PUBLISH": [], "REVIEW": [], "REJECT": []}

    for r in results:
        action = r.get("recommendation", {}).get("action", "REVIEW")
        if action in action_counts:
            action_counts[action] += 1
            action_items[action].append(r.get("source_name", "Unknown"))

    total = len(results)
    styles = {
        "PUBLISH": ("🟢", "#00D4AA", "#0D2818"),
        "REVIEW":  ("🟡", "#FFB800", "#2D1F00"),
        "REJECT":  ("🔴", "#FF4B6E", "#2D0F1A"),
    }

    cols = st.columns(3)
    for col, (action, (icon, color, bg)) in zip(cols, styles.items()):
        count = action_counts[action]
        pct   = round((count / total) * 100) if total else 0
        items = action_items[action]
        items_html = "<br>".join(
            f"• {i[:35]}..." if len(i) > 35 else f"• {i}"
            for i in items[:3]
        ) + ("<br><i>+ more</i>" if len(items) > 3 else "")
        with col:
            st.markdown(f"""
                <div class="metric-card" style="border-color:{color};background:{bg};
                            padding:20px;text-align:center;">
                    <div style="font-size:28px;">{icon}</div>
                    <div style="font-size:32px;font-weight:800;color:{color};">{count}</div>
                    <div style="color:{color};font-size:13px;font-weight:600;margin-bottom:8px;">
                        {action} ({pct}%)
                    </div>
                    <div style="color:#6B7280;font-size:11px;text-align:left;">
                        {items_html}
                    </div>
                </div>
            """, unsafe_allow_html=True)
