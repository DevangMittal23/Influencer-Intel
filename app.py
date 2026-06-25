import time
import streamlit as st

st.set_page_config(
    page_title="Influencer Intel",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.ui_styles import apply_styles
from components.result_cards import render_result_card
from components.dashboard import render_metrics, render_dashboard_table
from utils.llm_client import LLMClient
from utils.extractor import extract_text
from utils.analyzer import analyze_content
from utils.factchecker import fact_check_claims
from utils.exporter import export_to_csv, export_to_excel

apply_styles()

# ── Demo data ────────────────────────────────────────────────────────────────
DEMO_TEXTS = [
    {
        "text": (
            "Studies show that people who take Vitamin D supplements have "
            "67% lower risk of COVID-19. Dr. Anjali from AIIMS confirms that "
            "natural immunity is 13 times stronger than vaccine immunity. "
            "The government is hiding this data from citizens."
        ),
        "name": "demo_health_claim.txt",
    },
    {
        "text": (
            "Yaar suno, ye jo naye chips aaye hain na market mein, "
            "inke andar plastic particles milte hain scientifically proven. "
            "WHO ne bhi isko ban karne ki baat ki hai last month. "
            "Aap sab in companies ka boycott karo!"
        ),
        "name": "demo_hinglish_claim.txt",
    },
]
DEMO_BRIEF = {
    "theme": "Public Health Awareness",
    "required_message": "Promote evidence-based health practices",
    "required_people": ["Ministry of Health", "WHO", "AIIMS"],
    "purpose": "Public Health",
    "target_audience": "General public",
}

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in [
    ("results", []),
    ("run_timestamp", None),
    ("active_tab", 0),
    ("demo_loaded", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Read Streamlit secrets (optional) ────────────────────────────────────────
def _secret(key: str, fallback: str = "") -> str:
    try:
        return st.secrets["api_keys"].get(key, fallback)
    except Exception:
        return fallback

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Influencer Intel")
    st.markdown("---")

    st.markdown("### 🎯 Campaign Brief")
    campaign_theme = st.text_input(
        "Campaign Theme",
        value=st.session_state.get("sb_theme", ""),
        placeholder="e.g. Natural immunity, Climate action",
    )
    required_message = st.text_area(
        "Required Message",
        value=st.session_state.get("sb_message", ""),
        placeholder="What should the content say?",
        height=80,
    )
    key_people = st.text_input(
        "Key People/Groups to Track",
        value=st.session_state.get("sb_people", ""),
        placeholder="Comma separated: Dr. Anjali, Ministry of Health",
    )
    campaign_purpose = st.selectbox(
        "Campaign Purpose",
        ["Public Health", "Political", "Brand Promotion", "Social Awareness", "Entertainment", "Other"],
    )
    target_audience = st.text_input(
        "Target Audience",
        value=st.session_state.get("sb_audience", ""),
        placeholder="e.g. General public, Youth 18-25",
    )

    st.markdown("---")
    st.markdown("### 🔑 API Configuration")
    gemini_key = st.text_input(
        "Gemini API Key", type="password",
        value=_secret("GEMINI_API_KEY"),
    )
    groq_key = st.text_input(
        "Groq API Key", type="password",
        value=_secret("GROQ_API_KEY"),
    )
    tavily_key = st.text_input(
        "Tavily API Key", type="password",
        value=_secret("TAVILY_API_KEY"),
    )
    st.caption("🔒 Keys are used only for this session")

    st.markdown("---")
    st.markdown("### ⚙️ Processing Settings")
    max_claims = st.slider("Max Claims to Fact-Check per Item", 1, 10, 5)
    skip_factcheck = st.checkbox("Skip Fact-Checking (faster)", value=False)
    # concurrency note: Streamlit is sequential
    st.selectbox("Batch Concurrency", [1, 2, 3], index=1)

# ── Build campaign brief dict ─────────────────────────────────────────────────
def build_brief() -> dict:
    people = [p.strip() for p in key_people.split(",") if p.strip()]
    return {
        "theme": campaign_theme,
        "required_message": required_message,
        "required_people": people,
        "purpose": campaign_purpose,
        "target_audience": target_audience,
    }

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📥 Input Content", "📊 Results Dashboard", "📤 Export"])

# ─────────────────────────── TAB 1: INPUT ────────────────────────────────────
with tab1:
    st.markdown("### Upload or Paste Content")

    if st.button("🧪 Load Demo Content", key="demo_btn"):
        st.session_state["demo_loaded"] = True
        st.session_state["sb_theme"] = DEMO_BRIEF["theme"]
        st.session_state["sb_message"] = DEMO_BRIEF["required_message"]
        st.session_state["sb_people"] = ", ".join(DEMO_BRIEF["required_people"])
        st.session_state["sb_audience"] = DEMO_BRIEF["target_audience"]
        st.success("✅ Demo content loaded! The sidebar has been pre-filled with the demo campaign brief. Click **Run Analysis** to proceed.")

    col_left, col_right = st.columns(2)
    with col_left:
        uploaded_files = st.file_uploader(
            "Upload Content Files",
            accept_multiple_files=True,
            type=["pdf", "docx", "txt"],
        )
        if uploaded_files:
            st.caption(f"📁 {len(uploaded_files)} file(s) ready")

    with col_right:
        url_input = st.text_area(
            "Paste URLs (one per line)",
            height=120,
            placeholder="https://example.com/article1\nhttps://example.com/article2",
        )
        raw_text_input = st.text_area(
            "Or paste raw text content",
            height=100,
            placeholder="Paste a single content piece here for quick analysis…",
        )

    # Count items
    url_list = [u.strip() for u in url_input.splitlines() if u.strip()]
    n_files = len(uploaded_files) if uploaded_files else 0
    n_urls = len(url_list)
    n_raw = 1 if raw_text_input.strip() else 0
    n_demo = len(DEMO_TEXTS) if st.session_state["demo_loaded"] else 0
    total_items = n_files + n_urls + n_raw + n_demo

    if total_items:
        st.info(f"Ready to analyze: {n_files} file(s) + {n_urls} URL(s) + {n_raw} raw text + {n_demo} demo = **{total_items} total items**")

    st.markdown("")
    run_clicked = st.button("🚀 Run Analysis", use_container_width=True, key="run_btn")

    if run_clicked:
        # Validation
        errors = []
        if not gemini_key and not groq_key:
            errors.append("Please enter at least one LLM API key (Gemini or Groq) in the sidebar.")
        if not campaign_theme.strip():
            errors.append("Please enter a Campaign Theme in the sidebar.")
        if total_items == 0:
            errors.append("Please upload files, enter URLs, paste text, or load demo content.")
        if errors:
            for err in errors:
                st.error(err)
            st.stop()

        brief = build_brief()
        llm = LLMClient(gemini_api_key=gemini_key, groq_api_key=groq_key)

        # Gather all sources
        sources = []
        if uploaded_files:
            for f in uploaded_files:
                ext = f.name.rsplit(".", 1)[-1].lower()
                sources.append({"bytes": f.read(), "type": ext, "name": f.name})
        for url in url_list:
            sources.append({"bytes": url, "type": "url", "name": url})
        if raw_text_input.strip():
            sources.append({"bytes": raw_text_input.strip(), "type": "raw_text", "name": "pasted_text"})
        if st.session_state["demo_loaded"]:
            for d in DEMO_TEXTS:
                sources.append({"bytes": d["text"], "type": "raw_text", "name": d["name"]})

        progress_bar = st.progress(0, text="Starting…")
        status_box = st.status("Processing…", expanded=True)
        all_results = []
        start_time = time.time()
        total = len(sources)

        # Phase 1: Extraction
        status_box.write("**Phase 1 — Extracting text…**")
        extracted_items = []
        for i, src in enumerate(sources):
            extracted = extract_text(src["bytes"], src["type"], src["name"])
            if extracted["extraction_success"]:
                status_box.write(f"✅ `{src['name']}` extracted ({extracted['char_count']:,} chars)")
            else:
                status_box.write(f"⚠️ `{src['name']}` extraction failed: {extracted['error']}")
            extracted_items.append(extracted)
            progress_bar.progress((i + 1) / (total * 3), text=f"Extracting [{i+1}/{total}]…")

        # Phase 2: Analysis
        status_box.write("**Phase 2 — Analyzing content…**")
        analyzed_items = []
        for i, item in enumerate(extracted_items):
            if not item["extraction_success"]:
                analyzed_items.append({
                    "source_name": item["source_name"],
                    "analysis_status": "extraction_failed",
                    "error": item["error"],
                    "fact_checks": [],
                })
                continue
            try:
                result = analyze_content(item["text"], item["source_name"], brief, llm)
                status_box.write(f"✅ `{item['source_name']}` analyzed ({result.get('provider_used', '?')})")
            except Exception as e:
                result = {
                    "source_name": item["source_name"],
                    "analysis_status": "analysis_failed",
                    "error": str(e),
                    "fact_checks": [],
                }
                status_box.write(f"❌ `{item['source_name']}` analysis failed: {e}")
            result["fact_checks"] = []
            analyzed_items.append(result)
            progress_bar.progress(
                (total + i + 1) / (total * 3),
                text=f"Analyzing [{i+1}/{total}]…",
            )

        # Phase 3: Fact-checking
        if not skip_factcheck and tavily_key:
            status_box.write("**Phase 3 — Fact-checking claims…**")
            for i, result in enumerate(analyzed_items):
                if result.get("analysis_status") != "success":
                    continue
                raw_claims = result.get("factual_claims", [])[:max_claims]
                if not raw_claims:
                    continue
                try:
                    fcs = fact_check_claims(raw_claims, result["source_name"], llm, tavily_key)
                    result["fact_checks"] = fcs
                    checked = sum(1 for f in fcs if f.get("search_performed"))
                    status_box.write(f"✅ {checked} claim(s) checked for `{result['source_name']}`")
                except Exception as e:
                    status_box.write(f"⚠️ Fact-check failed for `{result['source_name']}`: {e}")
                progress_bar.progress(
                    (total * 2 + i + 1) / (total * 3),
                    text=f"Fact-checking [{i+1}/{total}]…",
                )
        elif not skip_factcheck and not tavily_key:
            status_box.write("⚠️ Tavily key not provided — fact-checking skipped.")

        progress_bar.progress(1.0, text="Complete!")
        elapsed = round(time.time() - start_time, 1)
        status_box.update(label=f"✅ Done in {elapsed}s", state="complete", expanded=False)
        st.success(f"🎉 Analysis complete! {total} item(s) processed in {elapsed}s.")
        st.balloons()

        st.session_state["results"] = analyzed_items
        st.session_state["run_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

# ─────────────────────────── TAB 2: RESULTS ──────────────────────────────────
with tab2:
    results = st.session_state.get("results", [])
    if not results:
        st.info("No results yet. Go to **📥 Input Content** and run analysis.")
    else:
        ts = st.session_state.get("run_timestamp", "")
        if ts:
            st.caption(f"Last run: {ts}")

        render_metrics(results)
        st.markdown("")

        filtered = render_dashboard_table(results)
        st.markdown("---")
        st.markdown("### Detailed Results")
        for r in filtered:
            render_result_card(r)

# ─────────────────────────── TAB 3: EXPORT ───────────────────────────────────
with tab3:
    results = st.session_state.get("results", [])
    if not results:
        st.info("No results to export yet. Run analysis first.")
    else:
        st.markdown("### Export Results")
        good = [r for r in results if r.get("analysis_status") == "success"]
        total_claims_export = sum(len(r.get("fact_checks", [])) for r in good)
        st.markdown(
            f"- **{len(good)}** successfully analyzed items\n"
            f"- **{total_claims_export}** fact-checked claims\n"
            f"- **{sum(len(r.get('entities',[])) for r in good)}** entities extracted"
        )

        col_xl, col_csv = st.columns(2)

        with col_xl:
            st.markdown("**Excel Report** — 3 sheets: Summary, Fact Checks, Entities. Color-coded verdicts and fit scores.")
            try:
                excel_bytes = export_to_excel(results)
                st.download_button(
                    "⬇️ Download Excel Report",
                    data=excel_bytes,
                    file_name=f"influencer_intel_{time.strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Excel export failed: {e}")

        with col_csv:
            st.markdown("**CSV Summary** — Flat file with all claims as rows. Ideal for further data processing.")
            try:
                csv_bytes = export_to_csv(results)
                st.download_button(
                    "⬇️ Download CSV Summary",
                    data=csv_bytes,
                    file_name=f"influencer_intel_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"CSV export failed: {e}")
