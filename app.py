import io
import json
import os
import hashlib
import re
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai

# ---------------------------------------------------------------------------
# 1. PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EcoTrack Enterprise",
    layout="wide",
    initial_sidebar_state="collapsed", 
)

# ---------------------------------------------------------------------------
# 1B. GEMINI API CONFIGURATION
# ---------------------------------------------------------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    MODEL = genai.GenerativeModel("gemini-3.5-flash")
except Exception as e:
    MODEL = None

# ---------------------------------------------------------------------------
# 1C. LOCAL AUTHENTICATION DATABASE
# ---------------------------------------------------------------------------
USER_DB_FILE = "users.json"

def init_user_db():
    if not os.path.exists(USER_DB_FILE) or os.path.getsize(USER_DB_FILE) == 0:
        with open(USER_DB_FILE, "w") as f:
            json.dump({}, f)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_credentials(username, password) -> bool:
    with open(USER_DB_FILE, "r") as f:
        users = json.load(f)
    if username in users:
        return users[username]['password'] == hash_password(password)
    return False

def register_user(username, password, role) -> bool:
    with open(USER_DB_FILE, "r") as f:
        users = json.load(f)
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "role": role
    }
    with open(USER_DB_FILE, "w") as f:
        json.dump(users, f)
    return True

def render_auth_page():
    st.markdown("""
        <style>
            .block-container { padding-top: 2rem !important; padding-bottom: 0rem !important; max-width: 1400px; }
            header {visibility: hidden;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([4, 6], gap="large")

    with col1:
        st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:30px;">
                <div style="width:48px; height:48px; border-radius:10px; background-color:#0f766e; display:flex; align-items:center; justify-content:center; color:white; font-size:18px; font-weight:bold; box-shadow: 0 4px 6px -1px rgba(15, 118, 110, 0.2);">ECO</div>
                <div>
                    <div style="font-weight:800; color:#0f172a; font-size:22px; letter-spacing:-0.5px; line-height:1.2;">EcoTrack Enterprise</div>
                    <div style="font-size:13px; color:#64748b; font-weight:500;">Scope 1 & 2 Emissions Analytics Platform</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Log In", "Sign Up"])
        roles = ["Sustainability Officer (Corporate ESG)", "Environmental Engineer (Plant Telemetry)"]

        with tab1:
            with st.form("login_form"):
                st.markdown("<div style='font-size:13px; font-weight:600; color:#334155; margin-bottom:4px;'>SELECT OPERATIONAL ROLE</div>", unsafe_allow_html=True)
                login_role = st.selectbox("Role", roles, label_visibility="collapsed")
                
                st.markdown("<div style='font-size:13px; font-weight:600; color:#334155; margin-top:12px; margin-bottom:4px;'>ENTERPRISE USERNAME</div>", unsafe_allow_html=True)
                login_username = st.text_input("Username", placeholder="e.g. s.analyst", label_visibility="collapsed")
                
                st.markdown("<div style='font-size:13px; font-weight:600; color:#334155; margin-top:12px; margin-bottom:4px;'>PASSWORD</div>", unsafe_allow_html=True)
                login_password = st.text_input("Password", type="password", placeholder="••••••••••••", label_visibility="collapsed")
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("Log In to Analytics Workspace", type="primary", use_container_width=True)

                if submit_login:
                    if verify_credentials(login_username, login_password):
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = login_username
                        st.session_state["role"] = login_role
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        with tab2:
            with st.form("signup_form"):
                st.markdown("<div style='font-size:13px; font-weight:600; color:#334155; margin-bottom:4px;'>ASSIGNED ROLE</div>", unsafe_allow_html=True)
                new_role = st.selectbox("Role", roles, label_visibility="collapsed")
                
                st.markdown("<div style='font-size:13px; font-weight:600; color:#334155; margin-top:12px; margin-bottom:4px;'>CHOOSE USERNAME</div>", unsafe_allow_html=True)
                new_username = st.text_input("Username", placeholder="e.g. j.doe", label_visibility="collapsed")
                
                st.markdown("<div style='font-size:13px; font-weight:600; color:#334155; margin-top:12px; margin-bottom:4px;'>CREATE PASSWORD</div>", unsafe_allow_html=True)
                new_password = st.text_input("Password", type="password", placeholder="At least 8 characters", label_visibility="collapsed")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password", label_visibility="collapsed")
                
                st.caption("By registering, you agree to ESG telemetry data compliance protocol ISO 14064.")
                submit_signup = st.form_submit_button("Register Facility Account", type="primary", use_container_width=True)

                if submit_signup:
                    if not new_username or not new_password:
                        st.error("Please fill in all fields.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        success = register_user(new_username, new_password, new_role)
                        if success:
                            st.success("Account created. Please switch to the Log In tab.")
                        else:
                            st.error("Username already exists.")

    with col2:
        right_panel_html = """
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <div class="h-full p-10 flex flex-col text-white relative overflow-hidden justify-center gap-6 rounded-2xl" style="font-family: 'Inter', sans-serif; background: linear-gradient(135deg, rgb(0, 106, 99) 0%, rgb(0, 92, 85) 40%, rgb(100, 186, 176) 100%); min-height: 80vh; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);">
          <div class="absolute -top-24 -right-24 w-96 h-96 bg-white/10 rounded-full blur-3xl pointer-events-none"></div>
          <div class="absolute bottom-0 right-1/4 w-80 h-80 bg-teal-900/20 rounded-full blur-3xl pointer-events-none"></div>

          <div class="relative z-10">
            <div class="flex items-center justify-between mb-4">
              <span class="px-3 py-1 rounded-full text-xs font-semibold bg-white/15 text-white border border-white/25 flex items-center gap-2 shadow-sm backdrop-blur-md">
                <span class="w-2 h-2 rounded-full bg-emerald-300 animate-ping"></span>
                ENTERPRISE DECARBONIZATION PLATFORM
              </span>
              <div class="flex items-center gap-2 text-xs font-mono text-teal-100 font-medium bg-black/10 px-2.5 py-1 rounded-full backdrop-blur-sm border border-white/10">
                <span class="material-symbols-outlined text-[16px] text-emerald-300">verified</span>
                <span>GHG Protocol & ISO 14064 Verified</span>
              </div>
            </div>
            <div class="max-w-2xl">
              <h1 class="text-3xl font-extrabold tracking-tight text-white leading-tight drop-shadow-sm">EcoTrack Enterprise</h1>
              <p class="text-base font-semibold text-teal-100 mt-1 drop-shadow-sm">Transforming raw petrochemical data into verifiable ESG intelligence.</p>
              <p class="text-xs text-teal-50/90 mt-2 leading-relaxed font-normal">A centralized platform built for sustainability directors and operational engineers to ingest telemetry, validate Scope 1 & 2 emissions, and automate audit-grade ESG analytics.</p>
            </div>
          </div>

          <div class="relative z-10">
            <div class="flex items-center justify-between mb-2.5">
              <span class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <span class="material-symbols-outlined text-[16px] text-teal-200">schema</span>4 Core System Modules
              </span>
              <span class="text-[11px] font-mono font-semibold text-teal-200">End-to-End Operational Pipeline</span>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-white/95 backdrop-blur-md rounded-xl p-3.5 border border-white/40 shadow-md text-slate-900">
                <div class="flex items-center justify-between mb-2">
                  <span class="w-6 h-6 rounded-md bg-teal-50 border border-teal-500/30 flex items-center justify-center text-teal-800 text-xs font-bold font-mono">01</span>
                  <span class="material-symbols-outlined text-[18px] text-teal-700">lock</span>
                </div>
                <h2 class="text-xs font-bold mb-1">Secure Authentication</h2>
                <p class="text-[11px] text-slate-600 leading-relaxed">Role-based local JSON data store ensuring secure access.</p>
              </div>
              <div class="bg-white/95 backdrop-blur-md rounded-xl p-3.5 border border-white/40 shadow-md text-slate-900">
                <div class="flex items-center justify-between mb-2">
                  <span class="w-6 h-6 rounded-md bg-blue-50 border border-blue-400/30 flex items-center justify-center text-blue-800 text-xs font-bold font-mono">02</span>
                  <span class="material-symbols-outlined text-[18px] text-blue-700">edit_note</span>
                </div>
                <h2 class="text-xs font-bold mb-1">Dual-Mode Data Entry</h2>
                <p class="text-[11px] text-slate-600 leading-relaxed">Choose between traditional manual forms or Smart AI Natural Language input.</p>
              </div>
              <div class="bg-white/95 backdrop-blur-md rounded-xl p-3.5 border border-white/40 shadow-md text-slate-900">
                <div class="flex items-center justify-between mb-2">
                  <span class="w-6 h-6 rounded-md bg-emerald-50 border border-emerald-500/30 flex items-center justify-center text-teal-800 text-xs font-bold font-mono">03</span>
                  <span class="material-symbols-outlined text-[18px] text-teal-700">table_view</span>
                </div>
                <h2 class="text-xs font-bold mb-1">Bulk Excel Integration</h2>
                <p class="text-[11px] text-slate-600 leading-relaxed">Download templates and drag-and-drop complete datasets directly into the database.</p>
              </div>
              <div class="bg-white/95 backdrop-blur-md rounded-xl p-3.5 border border-white/40 shadow-md text-slate-900">
                <div class="flex items-center justify-between mb-2">
                  <span class="w-6 h-6 rounded-md bg-teal-50 border border-teal-500/30 flex items-center justify-center text-teal-800 text-xs font-bold font-mono">04</span>
                  <span class="material-symbols-outlined text-[18px] text-teal-700">auto_awesome</span>
                </div>
                <h2 class="text-xs font-bold mb-1">AI-Powered Analytics</h2>
                <p class="text-[11px] text-slate-600 leading-relaxed">Real-time KPI dashboard, dynamic Plotly charts, and automated Gemini reporting.</p>
              </div>
            </div>
          </div>

          <div class="relative z-10 rounded-xl p-4 border border-white/30 bg-white/90 backdrop-blur-md shadow-md text-slate-900 mt-2">
            <div class="flex items-start gap-3.5">
              <div class="w-9 h-9 rounded-lg bg-teal-700 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-sm shadow-teal-700/20">
                <span class="material-symbols-outlined text-[22px]">dns</span>
              </div>
              <div class="flex-1">
                <div class="flex items-center justify-between mb-1">
                  <h2 class="text-xs font-bold uppercase tracking-wider flex items-center gap-2">Scalable Local Architecture</h2>
                  <span class="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-teal-800 border border-emerald-200 uppercase font-mono">High Efficiency</span>
                </div>
                <p class="text-[11px] text-slate-600 leading-relaxed">Designed for efficiency, this system uses a file-based architecture (Excel/JSON) eliminating cloud overhead while delivering enterprise-grade AI analytics and real-time state synchronization.</p>
              </div>
            </div>
          </div>
        </div>
        """
        st.components.v1.html(right_panel_html, height=850, scrolling=False)


# ---------------------------------------------------------------------------
# 2. DESIGN TOKENS
# ---------------------------------------------------------------------------
PRIMARY = "#005c55"          
PRIMARY_CONTAINER = "#0f766e"
SCOPE1_COLOR = "#0051d5"     
SCOPE2_COLOR = "#0d9488"     
SURFACE = "#faf8ff"
SURFACE_LOWEST = "#ffffff"
SURFACE_CONTAINER = "#eaedff"
SURFACE_CONTAINER_LOW = "#f2f3ff"
ON_SURFACE = "#131b2e"
ON_SURFACE_VARIANT = "#3e4947"
OUTLINE = "#6e7977"
OUTLINE_VARIANT = "#bdc9c6"
ERROR = "#ba1a1a"
POSITIVE = "#16a34a"

PLOT_FONT = dict(family="Inter, system-ui, sans-serif", size=12, color=ON_SURFACE_VARIANT)

# ---------------------------------------------------------------------------
# 3. DATA CONTRACT & EXCEL LOGIC
# ---------------------------------------------------------------------------
DATA_FILE = "data 2022-2023.xlsx"
SHEET_NAME = "main"

COL_YEAR = "Reference Year"
COL_SOURCE = "Source ID"
COL_SCOPE = "Scope"
COL_ANNUAL = "Total Emission (Annual)"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
EMISSION_UNIT = "tCO2e"
OPTIONAL_DETAIL_COLS = ["Source Description", "Activity Data", "Activity Data Description", "Units", "Unit", "Emission Factor", "Emission Factor Unit", "Calculated Emission"]

@st.cache_data(show_spinner="Loading emissions dataset...")
def load_data() -> pd.DataFrame:
    df = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def validate_columns(df: pd.DataFrame) -> list:
    required = [COL_YEAR, COL_SOURCE, COL_SCOPE, COL_ANNUAL]
    return [c for c in required if c not in df.columns]

def available_months(df: pd.DataFrame) -> list:
    return [m for m in MONTHS if m in df.columns]

def detail_columns(df: pd.DataFrame) -> list:
    cols = [COL_SOURCE, COL_YEAR, COL_SCOPE]
    cols += [c for c in OPTIONAL_DETAIL_COLS if c in df.columns]
    if COL_ANNUAL in df.columns:
        cols.append(COL_ANNUAL)
    seen, out = set(), []
    for c in cols:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out

def append_to_excel_full(new_record: dict) -> bool:
    """Appends a new full 12-month row to the Excel file dynamically."""
    try:
        df_disk = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME)
        
        new_row = {col: None for col in df_disk.columns}
        
        for k, v in new_record.items():
            if k in df_disk.columns:
                new_row[k] = v
                
        avail_months = available_months(df_disk)
        total = sum(float(new_row.get(m) or 0) for m in avail_months)
        
        if COL_ANNUAL in df_disk.columns:
            new_row[COL_ANNUAL] = total
            
        if "Total" in df_disk.columns:
            new_row["Total"] = None
            
        df_combined = pd.concat([df_disk, pd.DataFrame([new_row])], ignore_index=True)
        df_combined.to_excel(DATA_FILE, sheet_name=SHEET_NAME, index=False)
        
        st.cache_data.clear() 
        return True
    except Exception as e:
        st.error(f"Error saving to database: {str(e)}")
        return False

# ---------------------------------------------------------------------------
# 5. GLOBAL CSS
# ---------------------------------------------------------------------------
def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        html, body, [class*="css"], .stApp {{ font-family: 'Inter', system-ui, sans-serif; }}
        .stApp {{ background-color: {SURFACE}; }}
        .block-container {{ padding-top: 4rem; padding-bottom: 3rem; max-width: 1440px; }}
        section[data-testid="stSidebar"] {{ background-color: {SURFACE_LOWEST}; border-right: 1px solid {OUTLINE_VARIANT}; width: 260px !important; }}
        section[data-testid="stSidebar"] .block-container {{ padding-top: 1.2rem; }}
        .brand {{ display:flex; align-items:center; gap:10px; margin-bottom:18px; }}
        .brand-mark {{ width:34px; height:34px; border-radius:8px; background:{PRIMARY_CONTAINER}; color:#fff; display:flex; align-items:center; justify-content:center; font-size:14px; font-weight:bold; }}
        .brand-text h1 {{ font-size:14px; font-weight:800; color:{PRIMARY}; margin:0; line-height:1.15; letter-spacing:-0.01em; }}
        .brand-text span {{ font-size:11px; color:{OUTLINE}; }}
        .filter-label {{ font-size:11px; font-weight:600; letter-spacing:0.06em; text-transform:uppercase; color:{ON_SURFACE_VARIANT}; margin: 4px 0 2px 0; }}
        .topbar {{ background:{SURFACE_LOWEST}; border:1px solid {OUTLINE_VARIANT}; border-radius:12px; padding:14px 22px; margin-bottom:22px; display:flex; align-items:center; justify-content:space-between; box-shadow:0 1px 3px rgba(15,23,42,0.06); }}
        .topbar h2 {{ margin:0; font-size:19px; font-weight:800; color:{ON_SURFACE}; }}
        .topbar .ctx {{ font-size:12px; color:{OUTLINE}; }}
        .card {{ background:{SURFACE_LOWEST}; border:1px solid {OUTLINE_VARIANT}; border-radius:12px; padding:20px 22px; box-shadow:0 1px 3px rgba(15,23,42,0.08); }}
        .kpi-head {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }}
        .kpi-label {{ font-size:11px; font-weight:600; letter-spacing:0.06em; text-transform:uppercase; color:{OUTLINE}; }}
        .kpi-icon {{ font-size:18px; }}
        .kpi-value {{ font-size:31px; font-weight:700; letter-spacing:-0.02em; color:{ON_SURFACE}; line-height:1.15; }}
        .kpi-foot {{ display:flex; align-items:center; justify-content:space-between; margin-top:6px; font-size:12px; color:{ON_SURFACE_VARIANT}; }}
        .kpi-delta-up {{ color:{ERROR}; font-weight:600; }}
        .kpi-delta-down {{ color:{POSITIVE}; font-weight:600; }}
        .kpi-accent {{ border-color:{PRIMARY}; }}
        .section-title {{ font-size:17px; font-weight:600; color:{ON_SURFACE}; margin:0 0 2px 0; }}
        .section-sub {{ font-size:12px; color:{OUTLINE}; margin:0 0 6px 0; }}
        .chart-shell {{ background:{SURFACE_LOWEST}; border:1px solid {OUTLINE_VARIANT}; border-radius:12px; padding:6px 14px 2px 14px; margin-bottom:6px; box-shadow:0 1px 3px rgba(15,23,42,0.08); }}
        .slideover {{ background:{SURFACE_LOWEST}; border:1px solid {PRIMARY}; border-left:5px solid {PRIMARY}; border-radius:12px; padding:18px 22px; margin-bottom:20px; box-shadow:0 8px 24px rgba(15,23,42,0.12); }}
        .slideover h3 {{ margin:0; font-size:17px; font-weight:700; color:{ON_SURFACE}; }}
        .slideover .meta {{ font-size:12px; color:{OUTLINE}; margin-top:2px; }}
        .assistant {{ background:{SURFACE_CONTAINER}; border:1px solid {OUTLINE_VARIANT}; border-radius:12px; padding:18px; margin-bottom:12px; }}
        .assistant-head {{ display:flex; align-items:center; gap:10px; }}
        .assistant-mark {{ width:26px; height:26px; border-radius:7px; background:{PRIMARY}; color:#fff; display:flex; align-items:center; justify-content:center; font-size:15px; font-weight:bold; }}
        .assistant-head h3 {{ margin:0; font-size:15px; font-weight:700; color:{ON_SURFACE}; }}
        .assistant p.sub {{ font-size:12px; color:{ON_SURFACE_VARIANT}; margin:8px 0 0 0; }}
        .bubble-ai {{ background:{SURFACE_LOWEST}; border:1px solid {OUTLINE_VARIANT}; border-radius:14px 14px 14px 4px; padding:11px 13px; font-size:13px; line-height:1.55; color:{ON_SURFACE}; margin-bottom:10px; }}
        .bubble-user {{ background:{PRIMARY}; color:#fff; border-radius:14px 14px 4px 14px; padding:11px 13px; font-size:13px; line-height:1.55; margin-bottom:10px; margin-left:38px; }}
        .bubble-role {{ font-size:10px; letter-spacing:0.07em; text-transform:uppercase; color:{OUTLINE}; margin-bottom:3px; }}
        .report-canvas {{ background:#fff; border:1px solid {OUTLINE_VARIANT}; border-radius:4px; box-shadow:0 10px 30px rgba(15,23,42,0.12); padding:46px 52px; margin:0 auto 22px auto; max-width:900px; }}
        .report-head {{ border-bottom:2px solid {PRIMARY}; padding-bottom:18px; margin-bottom:24px; }}
        .report-head h1 {{ font-size:25px; font-weight:700; color:{ON_SURFACE}; margin:10px 0 4px 0; }}
        .report-head .period {{ font-size:15px; color:{PRIMARY}; font-weight:500; }}
        .report-meta {{ font-size:11px; color:{OUTLINE}; text-align:right; }}
        .report-kpi {{ background:{SURFACE_CONTAINER_LOW}; border:1px solid {OUTLINE_VARIANT}; border-radius:8px; padding:14px; }}
        .report-kpi.filled {{ background:{PRIMARY}; border-color:{PRIMARY}; }}
        .report-kpi.filled .kpi-value, .report-kpi.filled .kpi-label {{ color:#fff; }}
        .eyebrow {{ font-size:11px; letter-spacing:0.06em; text-transform:uppercase; color:{OUTLINE}; border-left:2px solid {PRIMARY}; padding-left:8px; margin-bottom:10px; }}
        .recommend {{ background:#f0fdfa; border-left:4px solid {PRIMARY_CONTAINER}; border-radius:0 8px 8px 0; padding:18px 20px; }}
        .footer-strip {{ border-top:1px solid {OUTLINE_VARIANT}; margin-top:26px; padding-top:12px; display:flex; justify-content:space-between; font-size:10px; text-transform:uppercase; color:{OUTLINE}; }}
        .stButton > button {{ border-radius:8px; border:1px solid {OUTLINE_VARIANT}; font-weight:500; font-size:13px; }}
        .stButton > button[kind="primary"] {{ background:{PRIMARY}; border-color:{PRIMARY}; }}
        div[data-testid="stDataFrame"] {{ border-radius:8px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# 7. FILTERING & CALCULATIONS
# ---------------------------------------------------------------------------
def apply_filters(df: pd.DataFrame, year, scope_option: str, plants: list) -> pd.DataFrame:
    out = df[(df[COL_YEAR] == year) & (df[COL_SOURCE].isin(plants))]
    if scope_option != "Both":
        out = out[out[COL_SCOPE] == scope_option]
    return out

def compute_kpis(df_current: pd.DataFrame, df_prev: pd.DataFrame) -> dict:
    s1 = to_number(df_current.loc[df_current[COL_SCOPE] == "Scope 1", COL_ANNUAL]).sum()
    s2 = to_number(df_current.loc[df_current[COL_SCOPE] == "Scope 2", COL_ANNUAL]).sum()
    combined = to_number(df_current[COL_ANNUAL]).sum()
    prev_total = to_number(df_prev[COL_ANNUAL]).sum() if not df_prev.empty else 0.0

    prev_s1 = to_number(df_prev.loc[df_prev[COL_SCOPE] == "Scope 1", COL_ANNUAL]).sum() if not df_prev.empty else 0.0
    prev_s2 = to_number(df_prev.loc[df_prev[COL_SCOPE] == "Scope 2", COL_ANNUAL]).sum() if not df_prev.empty else 0.0

    def pct(new, old):
        return ((new - old) / old * 100) if old > 0 else None

    return {
        "scope1": s1,
        "scope2": s2,
        "combined": combined,
        "prev_total": prev_total,
        "yoy": pct(combined, prev_total),
        "yoy_s1": pct(s1, prev_s1),
        "yoy_s2": pct(s2, prev_s2),
    }

def monthly_breakdown(df_current: pd.DataFrame, months: list) -> pd.DataFrame:
    if df_current.empty or not months:
        return pd.DataFrame(columns=["Month", COL_SCOPE, "Emissions"])
    melted = df_current.melt(
        id_vars=[COL_SCOPE], value_vars=months,
        var_name="Month", value_name="Emissions",
    )
    melted["Emissions"] = to_number(melted["Emissions"])
    grouped = melted.groupby(["Month", COL_SCOPE], as_index=False)["Emissions"].sum()
    grouped["Month"] = pd.Categorical(grouped["Month"], categories=months, ordered=True)
    return grouped.sort_values("Month")

def to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0)

# ---------------------------------------------------------------------------
# 8. CHART BUILDERS
# ---------------------------------------------------------------------------
SCOPE_COLORS = {"Scope 1": SCOPE1_COLOR, "Scope 2": SCOPE2_COLOR}

def base_layout(fig, height=300, legend=True):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=PLOT_FONT,
        hoverlabel=dict(bgcolor="white", bordercolor=OUTLINE_VARIANT, font_size=12, font_family="Inter"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None) if legend else None,
        showlegend=legend,
    )
    fig.update_xaxes(showgrid=False, linecolor=OUTLINE_VARIANT, ticks="outside", tickcolor=OUTLINE_VARIANT, title=None)
    fig.update_yaxes(showgrid=True, gridcolor="#e9edf5", zeroline=False, linecolor="rgba(0,0,0,0)")
    return fig

def chart_monthly_trend(df_monthly: pd.DataFrame):
    fig = px.line(df_monthly, x="Month", y="Emissions", color=COL_SCOPE, markers=True, color_discrete_map=SCOPE_COLORS)
    fig.update_traces(line=dict(width=2.6), marker=dict(size=7), hovertemplate="%{x} · %{y:,.1f}<extra>%{fullData.name}</extra>")
    fig = base_layout(fig, height=310)
    fig.update_yaxes(title=None)
    return fig

def chart_scope_donut(df_current: pd.DataFrame):
    summary = (df_current.assign(**{COL_ANNUAL: to_number(df_current[COL_ANNUAL])}).groupby(COL_SCOPE, as_index=False)[COL_ANNUAL].sum())
    total = summary[COL_ANNUAL].sum()
    fig = px.pie(summary, values=COL_ANNUAL, names=COL_SCOPE, hole=0.68, color=COL_SCOPE, color_discrete_map=SCOPE_COLORS)
    fig.update_traces(textinfo="none", hovertemplate="%{label}<br>%{value:,.0f} · %{percent}<extra></extra>", marker=dict(line=dict(color="#fff", width=2)))
    fig = base_layout(fig, height=250, legend=False)
    label = f"{total/1000:,.1f}k" if total >= 1000 else f"{total:,.0f}"
    fig.add_annotation(text=f"<span style='font-size:11px;color:{OUTLINE}'>TOTAL</span><br><b style='font-size:21px;color:{ON_SURFACE}'>{label}</b>", x=0.5, y=0.5, showarrow=False)
    return fig, summary, total

def chart_plant_source(df_current: pd.DataFrame):
    summary = (df_current.assign(**{COL_ANNUAL: to_number(df_current[COL_ANNUAL])}).groupby(COL_SOURCE, as_index=False)[COL_ANNUAL].sum().sort_values(COL_ANNUAL, ascending=True))
    fig = px.bar(summary, x=COL_ANNUAL, y=COL_SOURCE, orientation="h", color_discrete_sequence=[PRIMARY])
    fig.update_traces(marker=dict(cornerradius=6), hovertemplate="%{y}<br>%{x:,.0f} " + EMISSION_UNIT + "<extra></extra>")
    fig = base_layout(fig, height=310, legend=False)
    fig.update_xaxes(title=EMISSION_UNIT, showgrid=True, gridcolor="#e9edf5")
    fig.update_yaxes(title=None, showgrid=False)
    return fig, summary

def chart_annual_comparison(df: pd.DataFrame, plants: list):
    subset = df[df[COL_SOURCE].isin(plants)].copy()
    subset[COL_ANNUAL] = to_number(subset[COL_ANNUAL])
    annual = subset.groupby([COL_YEAR, COL_SCOPE], as_index=False)[COL_ANNUAL].sum()
    annual[COL_YEAR] = annual[COL_YEAR].astype(str)
    fig = px.bar(annual, x=COL_YEAR, y=COL_ANNUAL, color=COL_SCOPE, barmode="group", color_discrete_map=SCOPE_COLORS)
    fig.update_traces(marker=dict(cornerradius=6), hovertemplate="%{x} · %{y:,.0f} " + EMISSION_UNIT + "<extra>%{fullData.name}</extra>")
    fig = base_layout(fig, height=310)
    fig.update_yaxes(title=EMISSION_UNIT)
    return fig, annual

# ---------------------------------------------------------------------------
# 9. UI COMPONENTS & AI LOGIC
# ---------------------------------------------------------------------------
def kpi_card(label: str, value: str, unit: str, icon: str, delta=None, accent=False) -> str:
    if delta is None: delta_html = f"<span style='color:{OUTLINE}'>no prior-year data</span>"
    else:
        cls = "kpi-delta-up" if delta >= 0 else "kpi-delta-down"
        arrow = "UP" if delta >= 0 else "DOWN"
        delta_html = f"<span class='{cls}'>{arrow} {abs(delta):.1f}%</span>"
    return f"""
    <div class="card {'kpi-accent' if accent else ''}">
      <div class="kpi-head"><span class="kpi-label">{label}</span><span class="kpi-icon"></span></div>
      <div class="kpi-value">{value}</div><div class="kpi-foot"><span>{unit}</span>{delta_html}</div>
    </div>
    """

def selection_labels(event, field: str) -> list:
    if not event: return []
    try:
        selection = event.get("selection", {}) if isinstance(event, dict) else event.selection
        points = selection.get("points", []) if isinstance(selection, dict) else selection.points
    except Exception: return []
    labels = []
    for p in points or []:
        val = p.get(field) if isinstance(p, dict) else None
        if val is not None and val not in labels: labels.append(val)
    return labels

def open_drill(kind: str, title: str, subtitle: str, records: pd.DataFrame) -> None:
    st.session_state.drill = {"kind": kind, "title": title, "subtitle": subtitle, "records": records}
def close_drill() -> None: st.session_state.pop("drill", None)

def render_drill_panel(slot, months: list) -> None:
    drill = st.session_state.get("drill")
    if not drill: return
    records: pd.DataFrame = drill["records"]
    with slot.container():
        st.markdown(f"""<div class="slideover"><h3>Emission details — {drill['title']}</h3><div class="meta">{drill['subtitle']} · {len(records)} record(s)</div></div>""", unsafe_allow_html=True)
        if records.empty: st.info("No underlying records match this selection.")
        else: st.dataframe(records, use_container_width=True, hide_index=True, height=min(90 + 35 * len(records), 380))
        c1, c2, _ = st.columns([1, 1, 4])
        with c1:
            st.download_button("Export CSV", data=records.to_csv(index=False).encode("utf-8"), file_name=f"emission_details_{drill['title'].replace(' ', '_')}.csv", mime="text/csv", use_container_width=True, key="drill_export")
        with c2:
            if st.button("Close panel", use_container_width=True, key="drill_close"):
                close_drill()
                st.rerun()
        st.markdown(f"<hr style='margin:18px 0;border:none;border-top:1px solid {OUTLINE_VARIANT}'>", unsafe_allow_html=True)

SUGGESTED_QUESTIONS = ["Why did emissions change in the selected year?", "Identify the top Scope 2 emission drivers.", "Compare emissions between selected plants."]

def render_assistant_panel(context: str, k: dict, df_current: pd.DataFrame) -> None:
    st.markdown(f"""<div class="assistant"><div class="assistant-head"><div class="assistant-mark">AI</div><h3>GHG Analytics Assistant</h3></div><p class="sub">Answers will be grounded in your current filters.</p></div>""", unsafe_allow_html=True)
    st.caption(f"Active context: {context}")
    if "chat" not in st.session_state: st.session_state.chat = []
        
    def generate_chat_reply(user_query):
        if not MODEL: return "Error: Gemini API is missing or not configured correctly."
        
        # THE FIX: Convert the active Excel data into a hidden table for the AI to read!
        csv_data = df_current.to_csv(index=False)
        
        context_data = (
            f"Active Filters: {context}\n"
            f"KPI Summary:\n"
            f"- Scope 1 Total: {k['scope1']:,.0f} tCO2e\n"
            f"- Scope 2 Total: {k['scope2']:,.0f} tCO2e\n"
            f"- Combined Total: {k['combined']:,.0f} tCO2e\n\n"
            f"Raw Database Table (CSV Format):\n{csv_data}\n"
        )
        
        system_prompt = f"You are a professional Sustainability Assistant. Answer the user's question based strictly on the provided dashboard data and Raw Database Table.\n\n{context_data}\n\nUser Question: {user_query}\nIf asked to calculate or compare specific plants/months, look at the Raw Database Table to do the math. Keep your answer brief, insightful, and formatted cleanly."
        try:
            return MODEL.generate_content(system_prompt).text
        except Exception as e:
            return f"API Error: {str(e)}"

    st.markdown("<div class='bubble-role'>Suggested questions</div>", unsafe_allow_html=True)
    for i, q in enumerate(SUGGESTED_QUESTIONS):
        if st.button(q, key=f"chip_{i}", use_container_width=True):
            st.session_state.chat.append(("user", q))
            with st.spinner("Analyzing..."): ai_reply = generate_chat_reply(q)
            st.session_state.chat.append(("ai", ai_reply))
            st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    convo = st.container(height=320, border=False)
    with convo:
        if not st.session_state.chat:
            st.markdown(f"<div class='bubble-ai'>Ask a question about the filtered emissions data, or pick one of the suggestions above.</div>", unsafe_allow_html=True)
        for role, text in st.session_state.chat:
            css, who = ("bubble-user", "You") if role == "user" else ("bubble-ai", "Assistant")
            st.markdown(f"<div class='bubble-role'>{who}</div><div class='{css}'>{text}</div>", unsafe_allow_html=True)

    prompt = st.text_area("Message", key="chat_input", height=80, placeholder="Ask the assistant about this data...", label_visibility="collapsed")
    send, clear = st.columns([3, 1])
    with send:
        if st.button("Send", type="primary", use_container_width=True, key="chat_send"):
            if prompt and prompt.strip():
                st.session_state.chat.append(("user", prompt.strip()))
                with st.spinner("Analyzing..."): ai_reply = generate_chat_reply(prompt.strip())
                st.session_state.chat.append(("ai", ai_reply))
                st.rerun()
    with clear:
        if st.button("Clear", use_container_width=True, key="chat_clear"):
            st.session_state.chat = []
            st.rerun()

# ---------------------------------------------------------------------------
# 10. SIDEBAR
# ---------------------------------------------------------------------------
def render_sidebar(df: pd.DataFrame) -> tuple:
    st.markdown("""<style>[data-testid="collapsedControl"] {display: block;}</style>""", unsafe_allow_html=True)
    st.sidebar.markdown("""<div class="brand"><div class="brand-mark">ECO</div><div class="brand-text"><h1>PETROCHEMICAL</h1><span>COMPANY NAME</span></div></div>""", unsafe_allow_html=True)
    
    st.sidebar.markdown(f"Welcome back, **{st.session_state['username']}**")
    st.sidebar.caption(st.session_state.get('role', 'Sustainability Officer'))
    if st.sidebar.button("Logout", key="logout_btn", use_container_width=True):
        st.session_state.clear()
        st.rerun()
        
    st.sidebar.markdown("---")

    page = st.sidebar.radio("Navigation", ["Data Management", "Emissions Analytics", "Report Generation"], label_visibility="collapsed")
    st.sidebar.markdown("---")

    years = sorted(df[COL_YEAR].dropna().unique(), reverse=True)
    plants = sorted(df[COL_SOURCE].dropna().astype(str).unique())

    if "filters" not in st.session_state:
        st.session_state.filters = {"year": years[0] if years else None, "scope": "Both", "plants": plants}

    if page == "Emissions Analytics":
        st.sidebar.markdown("<div class='filter-label'>Analysis filters</div>", unsafe_allow_html=True)
        with st.sidebar.form("filter_form", border=False):
            year = st.selectbox("Reporting year", years, index=years.index(st.session_state.filters["year"]) if st.session_state.filters["year"] in years else 0)
            scope = st.radio("Emission scope", ["Both", "Scope 1", "Scope 2"], horizontal=True, index=["Both", "Scope 1", "Scope 2"].index(st.session_state.filters["scope"]))
            chosen = st.multiselect("Plant ID", plants, default=st.session_state.filters["plants"])
            applied = st.form_submit_button("Apply filters", type="primary", use_container_width=True)
        if applied:
            st.session_state.filters = {"year": year, "scope": scope, "plants": chosen if chosen else plants}
            close_drill()

    return page, st.session_state.filters


# ---------------------------------------------------------------------------
# 11A. PAGE — DATA MANAGEMENT
# ---------------------------------------------------------------------------
def page_data_management(df: pd.DataFrame) -> None:
    st.markdown(
        """<div class="topbar">
             <h2>Data Management Engine</h2>
             <div class="ctx">Append new operational telemetry rows</div>
           </div>""",
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs(["Manual Entry", "AI Smart Entry", "Bulk Upload"])

    with tab1:
        st.markdown("<p class='section-title'>Standard 12-Month Telemetry Form</p>", unsafe_allow_html=True)
        st.markdown("<p class='section-sub'>Fill in the source details and enter the calculated emissions (tCO2e) for each month. This adds a complete row to your database.</p>", unsafe_allow_html=True)
        
        with st.form("manual_entry_form"):
            st.markdown("**1. Source Identification**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                input_year = st.number_input("Reference Year", min_value=2020, max_value=2030, value=datetime.now().year, step=1)
            with col2:
                plants_list = sorted(df[COL_SOURCE].dropna().astype(str).unique())
                input_plant = st.selectbox("Source ID", plants_list + ["+ Add New"])
                if input_plant == "+ Add New":
                    input_plant = st.text_input("Enter New Source ID")
            with col3:
                input_scope = st.selectbox("Scope Category", ["Scope 1", "Scope 2"])
            with col4:
                input_desc = st.text_input("Source Description")
                
            st.markdown("**2. Activity Details**")
            col5, col6, col7 = st.columns(3)
            with col5:
                input_activity = st.text_input("Activity Data")
            with col6:
                input_unit = st.text_input("Units (e.g. Liters, kWh)")
            with col7:
                input_ef = st.number_input("Emission Factor", value=0.0, format="%.9f")
                
            st.markdown(f"**3. Monthly Emissions ({EMISSION_UNIT})**")
            m_cols = st.columns(6)
            month_vals = {}
            for i, month in enumerate(MONTHS):
                with m_cols[i % 6]:
                    month_vals[month] = st.number_input(month, value=0.0, format="%.2f")
                
            st.markdown("---")
            submit_manual = st.form_submit_button("Save Full Row to Database", type="primary", use_container_width=True)
            
            if submit_manual:
                if not input_plant or input_plant == "+ Add New":
                    st.error("Please provide a valid Source ID.")
                else:
                    new_record = {
                        "Reference Year": input_year,
                        "Source ID": input_plant,
                        "Scope": input_scope,
                        "Source Description": input_desc,
                        "Activity Data": input_activity,
                        "Units": input_unit,
                        "Emission Factor": input_ef
                    }
                    new_record.update(month_vals)
                    
                    if append_to_excel_full(new_record):
                        st.success(f"Success! Record for {input_plant} ({input_year}) inserted into the database.")

    with tab2:
        st.markdown("<p class='section-title'>AI Natural Language Ingestion</p>", unsafe_allow_html=True)
        st.info("Describe the yearly or monthly fuel/electricity consumption. The AI will extract it into a perfect 12-month JSON row structure ready for the database.")
        
        ai_input = st.text_area("Describe the operational activity:", placeholder="e.g., In 2024, Plant B consumed 8000 liters of diesel (Scope 1). Emission factor is 2.68. The usage was 4000 in Jan, and 4000 in Feb.", height=100)
        
        if st.button("Analyze & Preview", type="primary", use_container_width=True):
            if not MODEL:
                st.error("Gemini API not configured.")
            elif not ai_input.strip():
                st.warning("Please enter some text to analyze.")
            else:
                with st.spinner("Gemini is structuring the data..."):
                    prompt = f"""
                    You are an ESG Data Extraction Assistant. Analyze the text and extract the emission data into a strict JSON format. 
                    Calculate the final emission in tonnes of CO2 equivalent (tCO2e). Distribute the emissions among the months mentioned. If no specific month is mentioned, assign the total calculated emission to "Jan".
                    
                    Text: "{ai_input}"
                    
                    Return ONLY raw JSON in exactly this structure (no markdown tags):
                    {{
                        "Reference Year": <YYYY integer>,
                        "Source ID": <"Plant A", etc.>,
                        "Scope": <"Scope 1" or "Scope 2">,
                        "Source Description": <Short text description>,
                        "Activity Data": <Activity category string, e.g. "Stationary Combustion", "Flaring", "Venting", "Fugitive Emission">,
                        "Units": <e.g. "liters">,
                        "Emission Factor": <Standard factor used, float>,
                        "Jan": <tCO2e float>, "Feb": <tCO2e float>, "Mar": <tCO2e float>, "Apr": <tCO2e float>, "May": <tCO2e float>, "Jun": <tCO2e float>, 
                        "Jul": <tCO2e float>, "Aug": <tCO2e float>, "Sep": <tCO2e float>, "Oct": <tCO2e float>, "Nov": <tCO2e float>, "Dec": <tCO2e float>
                    }}
                    """
                    try:
                        response = MODEL.generate_content(prompt).text
                        match = re.search(r'\{.*\}', response.replace('\n', ''), re.DOTALL)
                        if match:
                            ai_data = json.loads(match.group(0))
                            st.session_state['ai_preview_data'] = ai_data
                        else:
                            st.error("Failed to parse AI output. Try rephrasing.")
                    except Exception as e:
                        st.error(f"API Error: {str(e)}")

        if 'ai_preview_data' in st.session_state:
            preview = st.session_state['ai_preview_data']
            st.markdown("<p class='section-title' style='margin-top:20px;'>Extraction Preview</p>", unsafe_allow_html=True)
            st.json(preview)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Discard", use_container_width=True):
                    del st.session_state['ai_preview_data']
                    st.rerun()
            with col2:
                if st.button("Confirm & Save to Database", type="primary", use_container_width=True):
                    if append_to_excel_full(preview):
                        st.success("Successfully injected AI-generated row into the database.")
                        del st.session_state['ai_preview_data']

    with tab3:
        st.markdown("<p class='section-title'>Bulk Excel Integration</p>", unsafe_allow_html=True)
        st.markdown("<p class='section-sub'>Download the exact required template, fill in multiple rows offline, and drag-and-drop the file back here to append all records to your database instantly.</p>", unsafe_allow_html=True)
        
        output = io.BytesIO()
        template_df = pd.DataFrame(columns=df.columns)
        template_df.to_excel(output, index=False, sheet_name=SHEET_NAME)
        
        st.download_button("1. Download Blank Data Template", data=output.getvalue(), file_name="EcoTrack_Bulk_Template.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("2. Upload Populated Template", type=["xlsx", "xls"])
        
        if uploaded_file and st.button("Merge Data into Database", type="primary"):
            try:
                new_data = pd.read_excel(uploaded_file)
                df_disk = pd.read_excel(DATA_FILE, sheet_name=SHEET_NAME)
                
                df_combined = pd.concat([df_disk, new_data], ignore_index=True)
                
                avail_months = available_months(df_combined)
                df_combined[COL_ANNUAL] = df_combined[avail_months].apply(pd.to_numeric, errors='coerce').fillna(0).sum(axis=1)
                
                df_combined.to_excel(DATA_FILE, sheet_name=SHEET_NAME, index=False)
                st.cache_data.clear()
                st.success(f"Successfully appended {len(new_data)} records. State synchronization complete.")
            except Exception as e:
                st.error(f"Error processing file: {e}")


# ---------------------------------------------------------------------------
# 11B. PAGE — EMISSIONS ANALYTICS
# ---------------------------------------------------------------------------
def page_analytics(df: pd.DataFrame, filters: dict) -> None:
    months = available_months(df)
    year, scope_option, plants = filters["year"], filters["scope"], filters["plants"]

    df_current = apply_filters(df, year, scope_option, plants)
    
    try:
        prev_year = int(year) - 1
    except (ValueError, TypeError):
        prev_year = None
    
    df_prev = apply_filters(df, prev_year, scope_option, plants) if prev_year is not None \
        else df.iloc[0:0]

    st.markdown(
        f"""<div class="topbar">
              <h2>Emissions Analytics Dashboard</h2>
              <div class="ctx">{year} · {scope_option} · {len(plants)} plant(s) selected</div>
            </div>""",
        unsafe_allow_html=True,
    )

    if df_current.empty:
        st.warning("No records match the current filters. Adjust the filters and apply again.")
        return

    k = compute_kpis(df_current, df_prev)
    main_col, chat_col = st.columns([7, 3], gap="large")

    with chat_col:
        render_assistant_panel(f"{year} · {scope_option} · {len(plants)} plant(s)", k, df_current)

    with main_col:
        drill_slot = st.empty()
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(kpi_card("Scope 1 total", f"{k['scope1']:,.0f}", EMISSION_UNIT, "", k["yoy_s1"]), unsafe_allow_html=True)
        with c2: st.markdown(kpi_card("Scope 2 total", f"{k['scope2']:,.0f}", EMISSION_UNIT, "", k["yoy_s2"]), unsafe_allow_html=True)
        with c3: st.markdown(kpi_card("Combined total", f"{k['combined']:,.0f}", f"{EMISSION_UNIT} total", "", k["yoy"], accent=True), unsafe_allow_html=True)
        with c4:
            yoy_txt = f"{k['yoy']:+.1f}%" if k["yoy"] is not None else "n/a"
            st.markdown(kpi_card("Year-over-year change", yoy_txt, f"vs. {prev_year}", "", None), unsafe_allow_html=True)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        r1c1, r1c2 = st.columns([6, 4], gap="medium")

        with r1c1:
            st.markdown("<p class='section-title'>Monthly GHG emission trend</p>", unsafe_allow_html=True)
            st.markdown("<p class='section-sub'>Use the month selector below to open the underlying records.</p>", unsafe_allow_html=True)
            df_monthly = monthly_breakdown(df_current, months)
            fig_trend = chart_monthly_trend(df_monthly)

            st.plotly_chart(fig_trend, use_container_width=True)
            sc1, sc2 = st.columns([3, 2])
            with sc1: month_pick = st.selectbox("Month", months, key="month_pick", label_visibility="collapsed")
            with sc2:
                if st.button("View month details", use_container_width=True, key="btn_month"):
                    show_month_detail(df_current, month_pick, months, year, scope_option)
                    st.rerun()

        with r1c2:
            st.markdown("<p class='section-title'>Scope 1 vs Scope 2 contribution</p>", unsafe_allow_html=True)
            st.markdown("<p class='section-sub'>Share of the combined annual total.</p>", unsafe_allow_html=True)
            fig_donut, scope_summary, total = chart_scope_donut(df_current)
            st.plotly_chart(fig_donut, use_container_width=True, key="chart_donut")

            cols = st.columns(max(len(scope_summary), 1))
            for i, row in enumerate(scope_summary.itertuples()):
                share = (getattr(row, "_2") / total * 100) if total else 0
                colour = SCOPE_COLORS.get(getattr(row, "Scope"), PRIMARY)
                with cols[i]:
                    st.markdown(
                        f"""<div style="text-align:center;padding:10px;border-radius:8px;background:{SURFACE_CONTAINER_LOW};border:1px solid {OUTLINE_VARIANT}">
                              <div class="kpi-label">{getattr(row, 'Scope')}</div>
                              <div style="font-size:16px;font-weight:700;color:{colour}">{share:.0f}%</div>
                            </div>""", unsafe_allow_html=True)
                    if st.button("Details", key=f"btn_scope_{i}", use_container_width=True):
                        show_scope_detail(df_current, getattr(row, "Scope"), year)
                        st.rerun()

        st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
        r2c1, r2c2 = st.columns(2, gap="medium")

        with r2c1:
            st.markdown("<p class='section-title'>Emission by plant source</p>", unsafe_allow_html=True)
            st.markdown("<p class='section-sub'>Use the selector below for plant records.</p>", unsafe_allow_html=True)
            fig_plant, plant_summary = chart_plant_source(df_current)

            st.plotly_chart(fig_plant, use_container_width=True)
            pc1, pc2 = st.columns([3, 2])
            with pc1: plant_pick = st.selectbox("Plant", plant_summary[COL_SOURCE].tolist(), key="plant_pick", label_visibility="collapsed")
            with pc2:
                if st.button("View plant details", use_container_width=True, key="btn_plant"):
                    show_plant_detail(df_current, plant_pick, year, scope_option)
                    st.rerun()

        with r2c2:
            st.markdown("<p class='section-title'>Annual emission comparison</p>", unsafe_allow_html=True)
            st.markdown("<p class='section-sub'>All reporting years for the selected plants.</p>", unsafe_allow_html=True)
            fig_annual, annual = chart_annual_comparison(df, plants)
            st.plotly_chart(fig_annual, use_container_width=True)

        render_drill_panel(drill_slot, months)

def show_month_detail(df_current, month, months, year, scope_option) -> None:
    if month not in df_current.columns: return
    cols = detail_columns(df_current)
    records = df_current[cols + ([month] if month not in cols else [])].copy()
    records[month] = to_number(records[month])
    records = records[records[month] != 0].sort_values(month, ascending=False)
    records = records.rename(columns={month: f"{month} value"})
    open_drill("month", f"{month} {year}", f"Monthly trend · scope filter: {scope_option}", records)

def show_plant_detail(df_current, plant, year, scope_option) -> None:
    cols = detail_columns(df_current)
    records = df_current[df_current[COL_SOURCE].astype(str) == str(plant)][cols].copy()
    if COL_ANNUAL in records.columns:
        records[COL_ANNUAL] = to_number(records[COL_ANNUAL])
        records = records.sort_values(COL_ANNUAL, ascending=False)
    open_drill("plant", f"{plant} · {year}", f"Plant source breakdown · scope filter: {scope_option}", records)

def show_scope_detail(df_current, scope, year) -> None:
    cols = detail_columns(df_current)
    records = df_current[df_current[COL_SCOPE] == scope][cols].copy()
    if COL_ANNUAL in records.columns:
        records[COL_ANNUAL] = to_number(records[COL_ANNUAL])
        records = records.sort_values(COL_ANNUAL, ascending=False)
    open_drill("scope", f"{scope} · {year}", "Contribution breakdown", records)

def show_year_detail(df, year_label, plants) -> None:
    try: year_val = int(year_label)
    except (TypeError, ValueError): return
    cols = detail_columns(df)
    records = df[(df[COL_YEAR] == year_val) & (df[COL_SOURCE].isin(plants))][cols].copy()
    if COL_ANNUAL in records.columns:
        records[COL_ANNUAL] = to_number(records[COL_ANNUAL])
        records = records.sort_values(COL_ANNUAL, ascending=False)
    open_drill("year", f"Reporting year {year_val}", "Annual comparison · all selected plants", records)


# ---------------------------------------------------------------------------
# 11C. PAGE — REPORT GENERATION
# ---------------------------------------------------------------------------
def page_report(df: pd.DataFrame) -> None:
    months = available_months(df)
    years = sorted(df[COL_YEAR].dropna().unique(), reverse=True)

    st.markdown(
        """<div class="topbar">
             <h2>Report Generation</h2>
             <div class="ctx">Scope 1 &amp; 2 GHG emissions summary</div>
           </div>""",
        unsafe_allow_html=True,
    )

    cfg1, cfg2, cfg3, cfg4 = st.columns([2, 2, 3, 2])
    with cfg1: year = st.selectbox("Reporting year", years)
    with cfg2: scope_option = st.selectbox("Emission scope", ["Both", "Scope 1", "Scope 2"])
    with cfg3: plants = st.multiselect("Plant ID", sorted(df[COL_SOURCE].dropna().astype(str).unique()), default=sorted(df[COL_SOURCE].dropna().astype(str).unique()))
    with cfg4:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        generate = st.button("Generate report", type="primary", use_container_width=True)

    if generate: st.session_state.report_ready = True
    if not st.session_state.get("report_ready"):
        st.info("Choose the reporting parameters above, then select **Generate report** to build the preview.")
        return

    plants = plants or sorted(df[COL_SOURCE].dropna().astype(str).unique())
    df_current = apply_filters(df, year, scope_option, plants)
    
    try: prev_year = int(year) - 1
    except (ValueError, TypeError): prev_year = None
    df_prev = apply_filters(df, prev_year, scope_option, plants) if prev_year is not None else df.iloc[0:0]

    if df_current.empty:
        st.warning("No records match these parameters.")
        return

    k = compute_kpis(df_current, df_prev)
    generated_on = datetime.now().strftime("%d %b %Y")

    if generate:
        if MODEL:
            with st.spinner("Generating AI Analysis and Recommendations..."):
                context_data = (
                    f"Reporting Year: {year}, Scope: {scope_option}, Plants Evaluated: {len(plants)}\n"
                    f"Scope 1 Total: {k['scope1']:,.0f} tCO2e\n"
                    f"Scope 2 Total: {k['scope2']:,.0f} tCO2e\n"
                    f"Combined Total: {k['combined']:,.0f} tCO2e (YoY Change: {k.get('yoy')}%)\n"
                )
                try:
                    combined_prompt = f"""Based on this GHG emissions data:
{context_data}

Task 1: Write a concise 2-paragraph executive AI analysis summary explaining the performance.
Task 2: Provide 3 concise recommended strategic actions to reduce emissions.

Format your output EXACTLY like this:
SUMMARY:
<your 2-paragraph summary here>

ACTIONS:
- <action 1>
- <action 2>
- <action 3>
"""
                    response_text = MODEL.generate_content(combined_prompt).text
                    if "ACTIONS:" in response_text:
                        parts = response_text.split("ACTIONS:")
                        st.session_state.ai_summary = parts[0].replace("SUMMARY:", "").strip()
                        st.session_state.ai_actions = [line.strip().lstrip('*- ') for line in parts[1].strip().split('\n') if line.strip()]
                    else:
                        st.session_state.ai_summary = response_text
                        st.session_state.ai_actions = ["Implement real-time energy monitoring.", "Transition Scope 2 procurement to RECs.", "Conduct targeted equipment maintenance."]
                except Exception as e:
                    st.session_state.ai_summary = f"API Error: {str(e)}"
                    st.session_state.ai_actions = ["Error generating recommendations."]
        else:
            st.session_state.ai_summary = "Error: Gemini API not configured."
            st.session_state.ai_actions = ["Error: Gemini API not configured."]

    ai_summary_text = st.session_state.get("ai_summary", "Generating AI Summary...")
    ai_actions_list = st.session_state.get("ai_actions", ["Generating recommendations..."])

    st.markdown('<div class="report-canvas">', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="report-head">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div style="font-size:26px; font-weight: bold; color: #005c55;">ECO</div>
                <div class="report-meta">Report ID: GHG-{year}-{len(df_current):04d}<br>Generated: {generated_on}</div>
              </div>
              <h1>Scope 1 &amp; Scope 2 GHG emissions summary report</h1>
              <div class="period">Reporting period: January {year} – December {year} · {scope_option} · {len(plants)} plant(s)</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='eyebrow'>Emission summary</div>", unsafe_allow_html=True)
    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1: st.markdown(f"""<div class="report-kpi"><div class="kpi-label">Scope 1 (direct)</div><div class="kpi-value" style="font-size:24px">{k['scope1']:,.0f}</div><div style="font-size:11px;color:{OUTLINE}">{EMISSION_UNIT}</div></div>""", unsafe_allow_html=True)
    with rc2: st.markdown(f"""<div class="report-kpi"><div class="kpi-label">Scope 2 (indirect)</div><div class="kpi-value" style="font-size:24px">{k['scope2']:,.0f}</div><div style="font-size:11px;color:{OUTLINE}">{EMISSION_UNIT}</div></div>""", unsafe_allow_html=True)
    with rc3: st.markdown(f"""<div class="report-kpi filled"><div class="kpi-label">Total emissions</div><div class="kpi-value" style="font-size:24px">{k['combined']:,.0f}</div><div style="font-size:11px;color:#dff5f1">{EMISSION_UNIT}</div></div>""", unsafe_allow_html=True)
    with rc4:
        yoy_txt = f"{k['yoy']:+.1f}%" if k["yoy"] is not None else "n/a"
        st.markdown(f"""<div class="report-kpi"><div class="kpi-label">Change vs {year-1}</div><div class="kpi-value" style="font-size:24px;color:{PRIMARY}">{yoy_txt}</div><div style="font-size:11px;color:{OUTLINE}">previous year</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    vc1, vc2 = st.columns(2, gap="medium")
    with vc1:
        st.markdown("<div class='eyebrow'>Emission trend (12 months)</div>", unsafe_allow_html=True)
        fig_trend = chart_monthly_trend(monthly_breakdown(df_current, months))
        st.plotly_chart(fig_trend, use_container_width=True, key="rep_trend")
    with vc2:
        st.markdown("<div class='eyebrow'>Contribution by scope</div>", unsafe_allow_html=True)
        fig_donut, _, _ = chart_scope_donut(df_current)
        st.plotly_chart(fig_donut, use_container_width=True, key="rep_donut")

    st.markdown("<div class='eyebrow'>AI analysis summary</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:13px;color:{ON_SURFACE_VARIANT};line-height:1.7'>{ai_summary_text}</p>", unsafe_allow_html=True)

    items = "".join(f"<li style='margin-bottom:6px'>{r}</li>" for r in ai_actions_list[:3])
    st.markdown(
        f"""<div class="recommend">
              <div style="font-size:13px;font-weight:700;color:{PRIMARY_CONTAINER};text-transform:uppercase;letter-spacing:0.04em;margin-bottom:8px">Recommended actions</div>
              <ul style="font-size:13px;color:{ON_SURFACE_VARIANT};padding-left:18px;margin:0">{items}</ul>
            </div>""", unsafe_allow_html=True)

    st.markdown(
        f"""<div class="footer-strip">
              <span>Proprietary &amp; confidential</span><span>Page 1 of 1</span><span>Generated {generated_on}</span>
            </div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    e1, e2, _ = st.columns([2, 2, 6])
    with e1:
        st.download_button("Download report (HTML)", data=build_report_html(year, scope_option, plants, k, fig_trend, fig_donut, generated_on, ai_summary_text, ai_actions_list), file_name=f"GHG_Report_{year}.html", mime="text/html", use_container_width=True)
    with e2:
        st.download_button("Download data (CSV)", data=df_current.to_csv(index=False).encode("utf-8"), file_name=f"GHG_data_{year}.csv", mime="text/csv", use_container_width=True)

def build_report_html(year, scope_option, plants, k, fig_trend, fig_donut, generated_on, ai_summary, ai_actions) -> str:
    trend_html = fig_trend.to_html(full_html=False, include_plotlyjs="cdn")
    donut_html = fig_donut.to_html(full_html=False, include_plotlyjs=False)
    yoy_txt = f"{k['yoy']:+.1f}%" if k["yoy"] is not None else "n/a"
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<title>GHG Emissions Report {year}</title>
<style>
 body {{ font-family:Inter,system-ui,sans-serif; color:{ON_SURFACE}; margin:0; background:#f1f5f9; }}
 .page {{ max-width:900px; margin:28px auto; background:#fff; padding:48px; box-shadow:0 8px 28px rgba(15,23,42,.12); }}
 h1 {{ font-size:24px; margin:8px 0 4px; }}
 .period {{ color:{PRIMARY}; font-weight:500; }}
 .head {{ border-bottom:2px solid {PRIMARY}; padding-bottom:16px; margin-bottom:24px; }}
 .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:26px; }}
 .kpi {{ border:1px solid {OUTLINE_VARIANT}; border-radius:8px; padding:12px; background:{SURFACE_CONTAINER_LOW}; }}
 .kpi.filled {{ background:{PRIMARY}; color:#fff; border-color:{PRIMARY}; }}
 .kpi .l {{ font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:{OUTLINE}; }}
 .kpi.filled .l {{ color:#d9f2ee; }}
 .kpi .v {{ font-size:22px; font-weight:700; }}
 .eyebrow {{ font-size:11px; letter-spacing:.06em; text-transform:uppercase; color:{OUTLINE}; border-left:2px solid {PRIMARY}; padding-left:8px; margin:22px 0 10px; }}
 .note {{ font-size:13px; line-height:1.7; color:{ON_SURFACE_VARIANT}; }}
 .rec {{ background:#f0fdfa; border-left:4px solid {PRIMARY_CONTAINER}; padding:16px 20px; font-size:13px; }}
 footer {{ margin-top:28px; border-top:1px solid {OUTLINE_VARIANT}; padding-top:10px; font-size:10px; text-transform:uppercase; color:{OUTLINE}; display:flex; justify-content:space-between; }}
</style></head><body><div class="page">
<div class="head">
  <div style="font-size:11px;text-transform:uppercase;color:{OUTLINE}">Generated {generated_on}</div>
  <h1>Scope 1 &amp; Scope 2 GHG Emissions Summary Report</h1>
  <div class="period">Reporting period: January {year} – December {year} · {scope_option} · {len(plants)} plant(s)</div>
</div>
<div class="kpis">
  <div class="kpi"><div class="l">Scope 1</div><div class="v">{k['scope1']:,.0f}</div><div class="l">{EMISSION_UNIT}</div></div>
  <div class="kpi"><div class="l">Scope 2</div><div class="v">{k['scope2']:,.0f}</div><div class="l">{EMISSION_UNIT}</div></div>
  <div class="kpi filled"><div class="l">Total</div><div class="v">{k['combined']:,.0f}</div><div class="l">{EMISSION_UNIT}</div></div>
  <div class="kpi"><div class="l">Change vs {year-1}</div><div class="v">{yoy_txt}</div><div class="l">previous year</div></div>
</div>
<div class="eyebrow">Emission trend</div>{trend_html}
<div class="eyebrow">Contribution by scope</div>{donut_html}
<div class="eyebrow">AI analysis summary</div>
<p class="note">{ai_summary}</p>
<div class="eyebrow">Recommended actions</div>
<div class="rec"><ul>{''.join(f'<li>{r}</li>' for r in ai_actions[:3])}</ul></div>
<footer><span>Proprietary &amp; confidential</span><span>Page 1 of 1</span></footer>
</div></body></html>"""

# ---------------------------------------------------------------------------
# 13. MAIN
# ---------------------------------------------------------------------------
def main() -> None:
    init_user_db()
    
    if not st.session_state.get("logged_in", False):
        render_auth_page()
        st.stop()

    inject_css()

    try:
        df = load_data()
    except FileNotFoundError:
        st.error(f"Dataset not found. Place **{DATA_FILE}** in the same folder as app.py.")
        st.stop()
        return

    page, filters = render_sidebar(df)

    if page == "Data Management":
        page_data_management(df)
    elif page == "Emissions Analytics":
        page_analytics(df, filters)
    elif page == "Report Generation":
        page_report(df)

if __name__ == "__main__":
    main()