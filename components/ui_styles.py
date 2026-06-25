import streamlit as st


def apply_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp { background-color: #0F1117; color: #E8E8F0; }
.block-container { padding-top: 1.5rem !important; }

[data-testid="stSidebar"] { background: #13151F !important; border-right: 1px solid #2D3045; }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: #E8E8F0 !important; }

.metric-card {
    background: #1A1D27; border: 1px solid #2D3045;
    border-radius: 12px; padding: 20px; text-align: center;
}
.metric-card .metric-value { font-size: 32px; font-weight: 700; color: #6C63FF; }
.metric-card .metric-label { font-size: 13px; color: #6B7280; margin-top: 4px; }

.verdict-TRUE {
    background: #0D2818; border: 1px solid #00D4AA; color: #00D4AA;
    border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px; display: inline-block;
}
.verdict-FALSE {
    background: #2D0F1A; border: 1px solid #FF4B6E; color: #FF4B6E;
    border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px; display: inline-block;
}
.verdict-MISLEADING {
    background: #2D1F00; border: 1px solid #FFB800; color: #FFB800;
    border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px; display: inline-block;
}
.verdict-UNVERIFIABLE {
    background: #1A1D27; border: 1px solid #6B7280; color: #6B7280;
    border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px; display: inline-block;
}
.verdict-PARTIALLY_TRUE {
    background: #1A2020; border: 1px solid #40C4AA; color: #40C4AA;
    border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px; display: inline-block;
}
.verdict-SKIPPED {
    background: #1A1D27; border: 1px solid #6B7280; color: #6B7280;
    border-radius: 6px; padding: 4px 10px; font-size: 12px; display: inline-block;
}

.campaign-score-high { color: #00D4AA; font-size: 28px; font-weight: 700; }
.campaign-score-mid  { color: #FFB800; font-size: 28px; font-weight: 700; }
.campaign-score-low  { color: #FF4B6E; font-size: 28px; font-weight: 700; }

.entity-supported { color: #00D4AA; font-weight: 600; }
.entity-criticized { color: #FF4B6E; font-weight: 600; }
.entity-neutral { color: #6B7280; }

.provider-badge {
    background: #1A1D27; border: 1px solid #6C63FF; color: #6C63FF;
    border-radius: 4px; padding: 2px 8px; font-size: 11px; display: inline-block;
}

.intent-badge {
    background: #1A1D27; border: 1px solid #6C63FF; color: #6C63FF;
    border-radius: 6px; padding: 3px 10px; font-size: 12px; font-weight: 600; display: inline-block;
}
.sentiment-positive { color: #00D4AA; font-weight: 600; }
.sentiment-negative { color: #FF4B6E; font-weight: 600; }
.sentiment-neutral  { color: #6B7280; font-weight: 600; }
.sentiment-mixed    { color: #FFB800; font-weight: 600; }

.stTabs [data-baseweb="tab-list"] {
    gap: 8px; background: #13151F; border-radius: 10px;
    padding: 4px; border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important; padding: 8px 20px !important;
    color: #6B7280 !important; background: transparent !important;
    border: none !important; font-weight: 500;
}
.stTabs [aria-selected="true"] { background: #6C63FF !important; color: #FFFFFF !important; }

.stButton > button {
    background: #6C63FF !important; color: #FFFFFF !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; padding: 10px 24px !important;
}
.stButton > button:hover { background: #5A52E0 !important; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: #1A1D27 !important; border: 1px solid #2D3045 !important;
    color: #E8E8F0 !important; border-radius: 8px !important;
}

[data-testid="stFileUploader"] {
    background: #1A1D27; border: 2px dashed #2D3045; border-radius: 12px; padding: 16px;
}

details {
    background: #1A1D27 !important; border: 1px solid #2D3045 !important;
    border-radius: 10px !important; margin-bottom: 8px;
}
details summary { color: #E8E8F0 !important; font-weight: 600; }

.stProgress > div > div { background: #6C63FF !important; }
.stDataFrame { border: 1px solid #2D3045; border-radius: 8px; }
hr { border-color: #2D3045 !important; }
.stAlert { border-radius: 8px !important; }
#MainMenu, footer, header { visibility: hidden; }

/* Risk Cards */
.risk-card-high {
    background: #2D0F1A; border: 1px solid #FF4B6E;
    border-radius: 12px; padding: 20px; text-align: center;
}
.risk-card-medium {
    background: #2D1F00; border: 1px solid #FFB800;
    border-radius: 12px; padding: 20px; text-align: center;
}
.risk-card-low {
    background: #0D2818; border: 1px solid #00D4AA;
    border-radius: 12px; padding: 20px; text-align: center;
}

/* Review Queue */
.review-flag-card {
    background: #2D0F1A; border: 1px solid #FF4B6E;
    border-left: 4px solid #FF4B6E; border-radius: 8px;
    padding: 14px 16px; margin-bottom: 10px;
    color: #E8E8F0; font-size: 14px;
}

/* Claim rows */
.claim-row {
    background: #1A1D27; border: 1px solid #2D3045;
    border-radius: 8px; padding: 14px 16px;
    margin-bottom: 10px; font-size: 14px; color: #E8E8F0;
}

/* Risk badges */
.risk-badge-high {
    background: #2D0F1A; color: #FF4B6E; border: 1px solid #FF4B6E;
    border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 700;
}
.risk-badge-medium {
    background: #2D1F00; color: #FFB800; border: 1px solid #FFB800;
    border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 700;
}
.risk-badge-low {
    background: #0D2818; color: #00D4AA; border: 1px solid #00D4AA;
    border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: 700;
}

/* Key status */
.key-active { color: #00D4AA; font-size: 12px; font-weight: 600; }
.key-missing { color: #FF4B6E; font-size: 12px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)
