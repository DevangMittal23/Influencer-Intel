import streamlit as st


def apply_styles():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Background */
.stApp { background-color: #0F1117; color: #E8E8F0; }

/* Remove top padding */
.block-container { padding-top: 1.5rem !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: #13151F !important; border-right: 1px solid #2D3045; }
[data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label { color: #E8E8F0 !important; }

/* Metric cards */
.metric-card {
    background: #1A1D27;
    border: 1px solid #2D3045;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.metric-card .metric-value { font-size: 32px; font-weight: 700; color: #6C63FF; }
.metric-card .metric-label { font-size: 13px; color: #6B7280; margin-top: 4px; }

/* Verdict badges */
.verdict-TRUE {
    background: #0D2818; border: 1px solid #00D4AA; color: #00D4AA;
    border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px;
    display: inline-block;
}
.verdict-FALSE {
    background: #2D0F1A; border: 1px solid #FF4B6E; color: #FF4B6E;
    border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px;
    display: inline-block;
}
.verdict-MISLEADING {
    background: #2D1F00; border: 1px solid #FFB800; color: #FFB800;
    border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px;
    display: inline-block;
}
.verdict-UNVERIFIABLE {
    background: #1A1D27; border: 1px solid #6B7280; color: #6B7280;
    border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px;
    display: inline-block;
}
.verdict-PARTIALLY_TRUE {
    background: #1A2020; border: 1px solid #40C4AA; color: #40C4AA;
    border-radius: 6px; padding: 4px 10px; font-weight: 600; font-size: 12px;
    display: inline-block;
}
.verdict-SKIPPED {
    background: #1A1D27; border: 1px solid #6B7280; color: #6B7280;
    border-radius: 6px; padding: 4px 10px; font-size: 12px;
    display: inline-block;
}

/* Campaign score */
.campaign-score-high { color: #00D4AA; font-size: 28px; font-weight: 700; }
.campaign-score-mid  { color: #FFB800; font-size: 28px; font-weight: 700; }
.campaign-score-low  { color: #FF4B6E; font-size: 28px; font-weight: 700; }

/* Entity stances */
.entity-supported { color: #00D4AA; font-weight: 600; }
.entity-criticized { color: #FF4B6E; font-weight: 600; }
.entity-neutral { color: #6B7280; }

/* Provider badge */
.provider-badge {
    background: #1A1D27; border: 1px solid #6C63FF; color: #6C63FF;
    border-radius: 4px; padding: 2px 8px; font-size: 11px; display: inline-block;
}

/* Intent / sentiment badges */
.intent-badge {
    background: #1A1D27; border: 1px solid #6C63FF; color: #6C63FF;
    border-radius: 6px; padding: 3px 10px; font-size: 12px; font-weight: 600;
    display: inline-block;
}
.sentiment-positive { color: #00D4AA; font-weight: 600; }
.sentiment-negative { color: #FF4B6E; font-weight: 600; }
.sentiment-neutral  { color: #6B7280; font-weight: 600; }
.sentiment-mixed    { color: #FFB800; font-weight: 600; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: #13151F;
    border-radius: 10px;
    padding: 4px;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 20px !important;
    color: #6B7280 !important;
    background: transparent !important;
    border: none !important;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #6C63FF !important;
    color: #FFFFFF !important;
}

/* Buttons */
.stButton > button {
    background: #6C63FF !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
}
.stButton > button:hover { background: #5A52E0 !important; }

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: #1A1D27 !important;
    border: 1px solid #2D3045 !important;
    color: #E8E8F0 !important;
    border-radius: 8px !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #1A1D27;
    border: 2px dashed #2D3045;
    border-radius: 12px;
    padding: 16px;
}

/* Expanders */
details {
    background: #1A1D27 !important;
    border: 1px solid #2D3045 !important;
    border-radius: 10px !important;
    margin-bottom: 8px;
}
details summary { color: #E8E8F0 !important; font-weight: 600; }

/* Progress bar */
.stProgress > div > div { background: #6C63FF !important; }

/* Dataframe */
.stDataFrame { border: 1px solid #2D3045; border-radius: 8px; }

/* Divider */
hr { border-color: #2D3045 !important; }

/* Warning / success messages */
.stAlert { border-radius: 8px !important; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)
