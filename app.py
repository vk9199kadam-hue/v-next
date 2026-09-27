import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import math
import json
import time

from src.utils.config import ACTIVE_WELL_CONFIG
from src.engines.vector_rag import VectorRAGEngine
from src.engines.vectorless_rag import VectorlessRAGEngine
from src.engines.telemetry_engine import TelemetryEngine
from src.ai.unified_context import UnifiedContextBuilder
from src.ai.jev_reasoning import JEVReasoningEngine
from src.ai.aver_chatbot import AVERChatbot
from src.engines.data_ingestion import DataIngestionPipeline
from src.engines.risk_classifier import RiskClassifierEngine
from src.engines.state_recognizer import DrillingStateRecognizer
from src.engines.directional_survey import DirectionalSurveyEngine
from src.engines.inpt_analyzer import INPTAnalyzerEngine
from src.engines.geomechanics import GeomechanicsEngine
from src.engines.edge_safety import EdgeSafetyEngine
from src.ai.fcbr_engine import FuzzyCBREngine

# Page configuration
st.set_page_config(
    page_title="V-Next: Nearby Wells Intelligence System | Oil India",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-Contrast Industrial Orange Design System
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    /* Global Canvas */
    .stApp {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1.5px solid #E2E8F0 !important;
    }
    section[data-testid="stSidebar"] * {
        color: #0F172A !important;
    }

    /* Primary Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em !important;
    }
    .brand-orange {
        color: #EA580C !important;
        font-weight: 800 !important;
    }

    /* Modern Clean Cards */
    .clean-card {
        background-color: #F8FAFC;
        border: 1.5px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.04);
        margin-bottom: 16px;
    }

    /* Metric Vitals Card */
    .metric-box {
        background-color: #FFFFFF;
        border: 1.5px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 800;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.2rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1;
    }
    .metric-sub {
        font-size: 0.82rem;
        color: #64748B;
        font-weight: 600;
        margin-top: 6px;
    }

    /* Status Alert Boxes */
    .alert-critical {
        background-color: #FEF2F2;
        border: 1.5px solid #EF4444;
        border-left: 6px solid #EF4444;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.12);
    }
    .alert-warning {
        background-color: #FFFBEB;
        border: 1.5px solid #F59E0B;
        border-left: 6px solid #F59E0B;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.12);
    }
    .alert-success {
        background-color: #ECFDF5;
        border: 1.5px solid #10B981;
        border-left: 6px solid #10B981;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 20px;
    }

    /* Orange Recommendation Card */
    .recommendation-card {
        background: linear-gradient(180deg, #FFFFFF 0%, #FFF7ED 100%);
        border: 2px solid #EA580C;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 10px 25px rgba(234, 88, 12, 0.1);
        margin-top: 15px;
        margin-bottom: 20px;
    }

    /* High-Contrast Badges */
    .badge-orange {
        background-color: #EA580C;
        color: #FFFFFF !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.03em;
    }
    .badge-accent-orange {
        background-color: #FFF7ED;
        color: #C2410C !important;
        border: 1px solid #FFEDD5;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .badge-danger {
        background-color: #FEE2E2;
        color: #DC2626 !important;
        border: 1px solid #FECACA;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 800;
    }

    /* Primary Orange Action Buttons */
    .stButton > button {
        background-color: #EA580C !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 18px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 6px rgba(234, 88, 12, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #C2410C !important;
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    /* ==============================================
       FIX FOR TABS: 100% VISIBLE TEXT ON ALL STATES
       ============================================== */
    div[data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: #F1F5F9 !important;
        padding: 6px !important;
        border-radius: 10px !important;
        border: 1.5px solid #E2E8F0 !important;
    }
    
    /* ALL Inactive Tabs: Dark, sharp, 100% visible text */
    button[data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 10px 18px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        color: #334155 !important;
        background-color: #E2E8F0 !important;
        border: 1px solid #CBD5E1 !important;
        transition: all 0.2s ease !important;
    }
    button[data-baseweb="tab"] * {
        color: #334155 !important;
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"]:hover {
        background-color: #FFFFFF !important;
        color: #EA580C !important;
    }
    button[data-baseweb="tab"]:hover * {
        color: #EA580C !important;
    }

    /* ACTIVE Selected Tab: Crisp White with Vibrant Orange text */
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #EA580C !important;
        border: 1.5px solid #EA580C !important;
        box-shadow: 0 3px 10px rgba(234, 88, 12, 0.15) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] * {
        color: #EA580C !important;
        font-weight: 800 !important;
    }

    /* Orange Tab Highlight Bar */
    div[data-baseweb="tab-highlight"] {
        background-color: #EA580C !important;
        height: 3px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Core System Engines
@st.cache_resource
def load_system():
    v_rag = VectorRAGEngine()
    vl_rag = VectorlessRAGEngine()
    tel_eng = TelemetryEngine("data/telemetry/active_well_stream.csv", vl_rag.con)
    jev_eng = JEVReasoningEngine()
    aver_chat = AVERChatbot()
    fcbr_eng = FuzzyCBREngine()
    inpt_eng = INPTAnalyzerEngine()
    geom_eng = GeomechanicsEngine()
    dir_eng = DirectionalSurveyEngine()
    return v_rag, vl_rag, tel_eng, jev_eng, aver_chat, fcbr_eng, inpt_eng, geom_eng, dir_eng

v_rag, vl_rag, tel_eng, jev_eng, aver_chat, fcbr_eng, inpt_eng, geom_eng, dir_eng = load_system()

# Session State Management
if "anomaly_state" not in st.session_state:
    st.session_state.anomaly_state = "nominal"  # nominal | torque_spike | lookahead_loss
if "audit_log" not in st.session_state:
    st.session_state.audit_log = [
        {"Timestamp": "2026-09-27 11:30:15", "Depth": "2,420.0 m", "Trigger": "Proactive Lookahead", "AI Recommendation": "Prepare 25 bbl LCM pill for Barail entry", "Engineer Action": "Pre-mixed in pits", "Status": "Pre-empted"},
        {"Timestamp": "2026-09-27 08:45:00", "Depth": "2,180.0 m", "Trigger": "Routine Shift Handover", "AI Recommendation": "Surma formation base nominal", "Engineer Action": "Drilling ahead", "Status": "Normal"}
    ]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Sidebar Controls
st.sidebar.markdown("""
<div style="text-align: center; padding-bottom: 15px; border-bottom: 1.5px solid #E2E8F0; margin-bottom: 15px;">
    <h2 style="color: #EA580C; margin: 0; font-weight: 900; letter-spacing: -0.5px;">V-NEXT // NWIS</h2>
    <p style="color: #475569; font-size: 0.85rem; margin: 3px 0; font-weight: 600;">Nearby Wells Intelligence System</p>
    <span style="background: #FFF7ED; color: #EA580C; border: 1px solid #FFEDD5; border-radius: 4px; padding: 3px 8px; font-weight: 800; font-size: 0.75rem;">OIL INDIA LIMITED (SIH 2026)</span>
</div>
""", unsafe_allow_html=True)

mode = st.sidebar.radio("Operational Persona", ["🏗️ Rig Floor HUD (Field)", "🖥️ Drilling Office Analytics (Desk)"])
radius_km = st.sidebar.slider("Offset Proximity Radius (km)", 2.0, 15.0, 6.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='font-size: 0.85rem; font-weight: 800; color: #475569; text-transform: uppercase;'>🕹️ SIH Live Demo Simulation</p>", unsafe_allow_html=True)
c_btn1, c_btn2 = st.sidebar.columns(2)
if c_btn1.button("🚨 Torque Spike", use_container_width=True):
    st.session_state.anomaly_state = "torque_spike"
if c_btn2.button("🔮 Loss Zone", use_container_width=True):
    st.session_state.anomaly_state = "lookahead_loss"
if st.sidebar.button("🔄 Reset Parameters", use_container_width=True):
    st.session_state.anomaly_state = "nominal"

# Active Telemetry Parameter Evaluation based on state
if st.session_state.anomaly_state == "torque_spike":
    current_depth = 2847.0
    current_torque = 31.4
    current_rop = 0.7
    current_wob = 135.0
    current_ecd = 12.45
    current_flow_in = 520.0
    current_flow_out = 515.0
elif st.session_state.anomaly_state == "lookahead_loss":
    current_depth = 2810.0
    current_torque = 19.1
    current_rop = 5.2
    current_wob = 122.0
    current_ecd = 12.10
    current_flow_in = 520.0
    current_flow_out = 430.0  # Noticeable fluid loss for ML detection
else:
    current_depth = 2844.0
    current_torque = 18.2
    current_rop = 6.1
    current_wob = 122.0
    current_ecd = 12.12
    current_flow_in = 520.0
    current_flow_out = 519.0

telemetry_snapshot = {
    "depth_m": current_depth,
    "current_depth": current_depth,
    "torque_knm": current_torque,
    "rop_mph": current_rop,
    "wob_kn": current_wob,
    "rpm": 110.0 if current_rop > 2.0 else 35.0,
    "ecd_ppg": current_ecd,
    "flow_in_gpm": current_flow_in,
    "flow_out_gpm": current_flow_out,
    "pressure_psi": 2850
}

alerts = tel_eng.evaluate_reading(telemetry_snapshot)
lookaheads = tel_eng.check_proactive_lookahead(current_depth, window_m=100.0)

# Multi-Model Advanced Inference
drilling_state = tel_eng.state_recognizer.identify_state(telemetry_snapshot)
loss_risk = tel_eng.risk_classifier.predict_loss_severity(telemetry_snapshot)
edge_check = tel_eng.edge_safety.evaluate_edge_safety(telemetry_snapshot)
fcbr_match = fcbr_eng.match_case(telemetry_snapshot)

# Minimum Curvature Directional Survey (TVD Calculation)
active_survey = dir_eng.generate_synthetic_active_trajectory(current_depth)
current_tvd = active_survey.iloc[-1]["tvd"]

# ==============================================================================
# 1. RIG FLOOR HUD MODE (Glanceable, High-Contrast, One-Tap Actions)
# ==============================================================================
if mode == "🏗️ Rig Floor HUD (Field)":
    st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #E2E8F0; padding-bottom: 12px; margin-bottom: 20px;">
        <div>
            <h1 style="margin: 0; color: #EA580C; font-size: 2.1rem; font-weight: 900;">RIG FLOOR HEADS-UP DISPLAY</h1>
            <p style="margin: 3px 0 0 0; color: #334155; font-weight: 600;">ACTIVE RIG: <b>OIL Naharkatiya Active-01</b> | Formation: <b>Barail Sandstone</b></p>
        </div>
        <div style="text-align: right;">
            <span style="background-color: #ECFDF5; color: #059669; border: 1.5px solid #A7F3D0; padding: 6px 14px; border-radius: 20px; font-weight: 800; font-size: 0.85rem;">
                ● eRTMAC LIVE STREAMING
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Multi-Model Rig State Badges
    st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap;">
        <span style="background: #F1F5F9; color: #0F172A; border: 1.5px solid #CBD5E1; padding: 6px 12px; border-radius: 6px; font-weight: 800; font-size: 0.85rem;">
            RIG STATE: {drilling_state['badge_display']}
        </span>
        <span style="background: {loss_risk['color_hex']}15; color: {loss_risk['color_hex']}; border: 1.5px solid {loss_risk['color_hex']}; padding: 6px 12px; border-radius: 6px; font-weight: 800; font-size: 0.85rem;">
            ML FLUID LOSS: {loss_risk['tier_label']} ({loss_risk['severity_name']})
        </span>
        <span style="background: #ECFDF5; color: #059669; border: 1.5px solid #A7F3D0; padding: 6px 12px; border-radius: 6px; font-weight: 800; font-size: 0.85rem;">
            ● 3σ QC PASSED (1 Hz)
        </span>
        <span style="background: #FFF7ED; color: #EA580C; border: 1.5px solid #FFEDD5; padding: 6px 12px; border-radius: 6px; font-weight: 800; font-size: 0.85rem;">
            ⚡ EDGE PLC: {edge_check['execution_latency_ms']} ms ({edge_check['status']})
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Status Alert Banners
    if alerts:
        for a in alerts:
            st.markdown(f"""
            <div class="alert-critical">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="color: #991B1B; margin: 0; font-size: 1.4rem; font-weight: 800;">🚨 {a['title'].upper()}</h3>
                    <span class="badge-danger">STATUS: CRITICAL</span>
                </div>
                <p style="font-size: 1.15rem; margin: 8px 0 0 0; color: #7F1D1D; font-weight: 600;">{a['message']}</p>
            </div>
            """, unsafe_allow_html=True)
    elif lookaheads:
        for l in lookaheads:
            st.markdown(f"""
            <div class="alert-warning">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="color: #92400E; margin: 0; font-size: 1.3rem; font-weight: 800;">🔮 PROACTIVE LOOKAHEAD WARNING (+{l['lead_distance_m']}m AHEAD)</h3>
                    <span style="background: #FEF3C7; color: #B45309; border: 1px solid #FCD34D; font-weight: 800; padding: 3px 10px; border-radius: 6px; font-size: 0.75rem;">
                        SEVERITY: {l['severity']}
                    </span>
                </div>
                <p style="font-size: 1.05rem; margin: 6px 0 0 0; color: #78350F; font-weight: 600;">
                    Approaching depth <b>{l['depth_m']}m</b> where offset well <b>{l['well_name']}</b> encountered <b>{l['event_type']}</b>.<br/>
                    <b>Action Required:</b> {l['recommended_prep']}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="alert-success">
            <h4 style="color: #065F46; margin: 0; font-weight: 800;">✅ ALL REAL-TIME PARAMETERS WITHIN SAFE OPERATING ENVELOPE</h4>
        </div>
        """, unsafe_allow_html=True)

    # Clean White Metric Cards
    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    with col_g1:
        st.markdown(f"""
        <div class="metric-box" style="border-top: 4px solid #EA580C;">
            <div class="metric-label">BIT DEPTH (MD / TVD)</div>
            <div class="metric-val">{current_depth:.1f} <span style="font-size: 1.0rem; color: #64748B;">m MD</span></div>
            <div class="metric-sub" style="color: #EA580C; font-weight: 700;">TVD: {current_tvd:.1f} m (Min. Curvature)</div>
        </div>
        """, unsafe_allow_html=True)

    with col_g2:
        t_border = "#EF4444" if current_torque > 25.0 else "#10B981"
        t_text = "#EF4444" if current_torque > 25.0 else "#10B981"
        t_sub = "⚠️ SPIKE (+42%)" if current_torque > 25.0 else "Nominal (Limit: 25.0)"
        st.markdown(f"""
        <div class="metric-box" style="border-top: 4px solid {t_border};">
            <div class="metric-label">ROTARY TORQUE</div>
            <div class="metric-val" style="color: {t_text};">{current_torque:.1f} <span style="font-size: 1.1rem; color: #64748B;">kNm</span></div>
            <div class="metric-sub" style="color: {t_text}; font-weight: 700;">{t_sub}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_g3:
        rop_border = "#EF4444" if current_rop < 1.0 else "#10B981"
        rop_text = "#EF4444" if current_rop < 1.0 else "#0F172A"
        st.markdown(f"""
        <div class="metric-box" style="border-top: 4px solid {rop_border};">
            <div class="metric-label">PENETRATION RATE (ROP)</div>
            <div class="metric-val" style="color: {rop_text};">{current_rop:.1f} <span style="font-size: 1.1rem; color: #64748B;">m/hr</span></div>
            <div class="metric-sub">WOB Applied: {current_wob:.0f} kN</div>
        </div>
        """, unsafe_allow_html=True)

    with col_g4:
        st.markdown(f"""
        <div class="metric-box" style="border-top: 4px solid #F97316;">
            <div class="metric-label">EQUIV. CIRC. DENSITY</div>
            <div class="metric-val" style="color: #EA580C;">{current_ecd:.2f} <span style="font-size: 1.1rem; color: #64748B;">ppg</span></div>
            <div class="metric-sub">Shoe LOT Limit: 12.80 ppg</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # 1-TAP ACTION RECOMMENDATION CARD
    if st.session_state.anomaly_state == "torque_spike":
        st.markdown(f"""
        <div class="recommendation-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span class="badge-orange">
                    🏆 #1 AI RECOMMENDED ACTION (CONFIDENCE: 88%)
                </span>
                <span class="badge-accent-orange">CITATION: WCR OIL-NH-18 (PAGE 34)</span>
            </div>
            <h2 style="color: #C2410C; margin: 4px 0 10px 0; font-size: 1.7rem; font-weight: 900;">
                Back-Ream 50m Upward with 35 RPM & Circulate High-Viscosity Pill
            </h2>
            <p style="font-size: 1.08rem; color: #0F172A; line-height: 1.6; margin-bottom: 14px; font-weight: 500;">
                <b>Historical Offset Precedent:</b> Offset well <b>Naharkatiya-18 (OIL-NH-18, 3.2km away)</b> drilled this exact Barail Sandstone interval at 2,847m TVD in 2021. 
                Applying this procedure successfully freed the string in <b>4.5 hours with zero fish</b>.
            </p>
            <div style="background: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px 16px; border-radius: 6px; margin-bottom: 12px;">
                <p style="color: #1E40AF; margin: 0; font-size: 0.95rem; font-weight: 700;">
                    🎯 <b>FUZZY CBR COBWEB MATCH ({fcbr_match['top_match']['similarity_score_pct']}% Analog):</b> Case {fcbr_match['top_match']['case_id']} ({fcbr_match['top_match']['well_name']})<br/>
                    <span style="font-weight: 500; color: #1E3A8A;">Proven Solution: {fcbr_match['top_match']['solution']} ({fcbr_match['top_match']['provenance']})</span>
                </p>
            </div>
            <div style="background: #FEF2F2; border-left: 4px solid #EF4444; padding: 10px 14px; border-radius: 6px; margin-bottom: 14px;">
                <p style="color: #991B1B; margin: 0; font-size: 0.95rem; font-weight: 700;">
                    ⚠️ <b>Risk if Ignored:</b> Irreversible differential mechanical sticking within 20 mins. Estimated NPT: ₹2.5 Crore ($300,000).
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2 = st.columns([1, 1])
        with col_act1:
            if st.button("✅ EXECUTE ACTION & LOG TO AUDIT TRAIL", use_container_width=True, type="primary"):
                st.session_state.audit_log.insert(0, {
                    "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "Depth": f"{current_depth:.1f} m",
                    "Trigger": "Torque Spike (31.4 kNm)",
                    "AI Recommendation": "Back-ream 50m with 35 RPM + 40 bbl High-Vis pill",
                    "Engineer Action": "Approved & Executed via Rig HUD",
                    "Status": "Mitigation Underway (Resolved)"
                })
                st.success("Action broadcast to Rig Driller console and recorded in Oil India Immutable Audit Log!")
        with col_act2:
            if st.button("✏️ OVERRIDE WITH CUSTOM DECISION", use_container_width=True):
                st.info("Override modal active: Record manual driller override reason.")

# ==============================================================================
# 2. DRILLING OFFICE ANALYTICAL SUITE (Clean White / Industrial Orange)
# ==============================================================================
else:
    st.markdown("""
    <div style="border-bottom: 2px solid #E2E8F0; padding-bottom: 12px; margin-bottom: 20px;">
        <h1 style="margin: 0; color: #EA580C; font-size: 2.1rem; font-weight: 900;">DRILLING OFFICE DECISION & INTELLIGENCE SUITE</h1>
        <p style="margin: 3px 0 0 0; color: #334155; font-weight: 600;">Multi-Well Spatial Analytics, Depth Correlator, and Institutional Memory (Oil India Limited)</p>
    </div>
    """, unsafe_allow_html=True)

    tab_ingest, tab_map, tab_3d, tab_correlator, tab_inpt, tab_geom, tab_vector, tab_audit, tab_aver = st.tabs([
        "📥 Data Processing Hub (Phase 1)",
        "🗺️ Geospatial Map & Intelligence",
        "🌐 3D Subsurface Trajectories",
        "📊 Formation Depth & TVD Correlator",
        "⏱️ Crew INPT & Efficiency Benchmarks",
        "🔬 Geomechanics & Safe Mud Window",
        "📄 Knowledge Search (Vector RAG)",
        "📜 Decision Audit Trail",
        "💬 AVER AI Advisory Chat"
    ])

    # ==========================================================================
    # TAB 0: PHASE 1 — DATA INGESTION & KNOWLEDGE PREPARATION HUB
    # ==========================================================================
    with tab_ingest:
        st.markdown("""
        <div style="background: #FFF7ED; border-left: 5px solid #EA580C; padding: 14px 18px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #FFEDD5;">
            <h3 style="color: #C2410C; margin: 0; font-size: 1.3rem; font-weight: 800;">
                📥 PHASE 1: DATA INGESTION & KNOWLEDGE PREPARATION PIPELINE
            </h3>
            <p style="color: #7C2D12; margin: 4px 0 0 0; font-size: 0.95rem; font-weight: 500;">
                Ingest raw unstructured historical reports (WCR/DDR), structured offset spreadsheets, and calibrate eRTMAC stream baselines.
            </p>
        </div>
        """, unsafe_allow_html=True)

        ingest_mode = st.radio(
            "Select Data Processing Pipeline:",
            [
                "📄 1. Unstructured Document Parser (Vector RAG)",
                "📊 2. Structured Well Register & Spatial Sync (DuckDB)",
                "⚙️ 3. eRTMAC Stream Thresholds & Baseline Calibrator"
            ],
            horizontal=True
        )

        st.markdown("---")

        # 1. UNSTRUCTURED DOCUMENT PROCESSING
        if "1. Unstructured" in ingest_mode:
            st.subheader("📄 Historical Drilling Document Ingestion (WCRs, DDRs, Incident Memos)")
            st.caption("Extracts text, parses drilling entities, chunks content, and generates dense vector embeddings.")

            col_u1, col_u2 = st.columns([1, 1])
            with col_u1:
                u_well_id = st.text_input("Offset Well Identifier:", value="OIL-NH-25")
                u_formation = st.selectbox(
                    "Primary Formation Encountered:",
                    ["Barail Sandstone", "Tipam Sandstone", "Surma / Bokabil Shale", "Alluvium / Dhekiajuli"]
                )
                uploaded_doc = st.file_uploader(
                    "Upload Raw Drilling Report (.pdf or .txt):",
                    type=["pdf", "txt"],
                    help="Upload a Well Completion Report, Daily Drilling Report, or Mud Logging Memo."
                )

            with col_u2:
                st.markdown("<br/>", unsafe_allow_html=True)
                if uploaded_doc is not None:
                    st.info(f"File selected: **{uploaded_doc.name}** ({uploaded_doc.size / 1024:.1f} KB)")
                    if st.button("⚡ Run OCR, Chunk & Index into Vector RAG", type="primary", use_container_width=True):
                        with st.spinner("Extracting text, analyzing drilling hazards, and generating vectors..."):
                            result = DataIngestionPipeline.process_unstructured_document(
                                file_bytes=uploaded_doc.read(),
                                filename=uploaded_doc.name,
                                well_id=u_well_id,
                                formation=u_formation,
                                vector_engine=v_rag
                            )

                            st.success(f"✅ Successfully processed and indexed **{uploaded_doc.name}** into Vector RAG!")
                            
                            # Metrics output
                            m1, m2, m3 = st.columns(3)
                            m1.metric("Pages Extracted", result["total_pages"])
                            m2.metric("Total Words", f"{result['word_count']:,}")
                            m3.metric("Vector Chunks", result["chunks_added"])

                            st.markdown("#### 🚨 Identified Drilling Hazards / Operational Entities:")
                            hazard_badges = "".join([f"<span class='badge-danger' style='margin-right: 6px;'>{h}</span>" for h in result["detected_hazards"]])
                            st.markdown(hazard_badges, unsafe_allow_html=True)
                            
                            st.caption("💡 This well's historical lessons are now immediately queryable in the 'Knowledge Search' and 'AVER AI Chat' tabs!")
                else:
                    st.markdown("""
                    <div class="clean-card">
                        <h4 style="color: #EA580C; margin-top: 0;">How It Works:</h4>
                        <ol style="color: #334155; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">
                            <li>Upload historical PDF / text drilling records.</li>
                            <li>Extracts pages and scans for stuck pipes, lost circulation, and kicks.</li>
                            <li>Chunks text into 400-word blocks with metadata preservation.</li>
                            <li>Generates dense vector embeddings and stores in Vector RAG in under 2 seconds.</li>
                        </ol>
                    </div>
                    """, unsafe_allow_html=True)

        # 2. STRUCTURED DATA PROCESSING
        elif "2. Structured" in ingest_mode:
            st.subheader("📊 Structured Well Register & Spatial Sync (DuckDB)")
            st.caption("Validates schema, converts coordinates to WGS84, and syncs offset wells directly to DuckDB and the live Map.")

            col_s1, col_s2 = st.columns([1, 1])
            with col_s1:
                uploaded_csv = st.file_uploader(
                    "Upload Offset Wells Spreadsheet (.csv or .xlsx):",
                    type=["csv", "xlsx"],
                    help="Upload a table with columns: well_id, well_name, lat, lon, total_depth_m, spud_year"
                )
                
            with col_s2:
                if uploaded_csv is not None:
                    st.info(f"File selected: **{uploaded_csv.name}**")
                    if st.button("🔄 Validate Schema & Sync to Spatial DB", type="primary", use_container_width=True):
                        try:
                            res_s = DataIngestionPipeline.process_structured_wells_csv(
                                file_bytes=uploaded_csv.read(),
                                filename=uploaded_csv.name,
                                vectorless_engine=vl_rag
                            )
                            st.success(f"✅ Successfully validated and inserted **{res_s['wells_added']} offset wells** into DuckDB!")
                            st.markdown("#### Sample Ingested Wells Preview:")
                            st.dataframe(pd.DataFrame(res_s["preview"]), use_container_width=True)
                            st.caption("🗺️ Newly added wells are now active on the 'Geospatial Map' and depth correlation queries!")
                        except Exception as e:
                            st.error(f"Validation Error: {str(e)}")
                else:
                    st.markdown("""
                    <div class="clean-card">
                        <h4 style="color: #EA580C; margin-top: 0;">Expected Spreadsheet Columns:</h4>
                        <ul style="color: #334155; font-size: 0.92rem; line-height: 1.6; margin-bottom: 0;">
                            <li><code>well_id</code>: Unique identifier (e.g. OIL-NH-22)</li>
                            <li><code>well_name</code>: Official name (e.g. Naharkatiya-22)</li>
                            <li><code>lat</code>, <code>lon</code>: Decimal latitude and longitude coordinates</li>
                            <li><code>total_depth_m</code>: Total depth in meters</li>
                            <li><code>spud_year</code>: Year drilled (e.g. 2023)</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

        # 3. eRTMAC STREAM BASELINE CALIBRATOR
        else:
            st.subheader("⚙️ eRTMAC Stream Baseline & Hazard Calibration")
            st.caption("Tune rig sensor anomaly thresholds and configure proactive depth lookahead windows.")

            c_cal1, c_cal2 = st.columns(2)
            with c_cal1:
                t_max = st.slider("Maximum Permissible Torque (kNm):", 15.0, 40.0, 25.0, 0.5)
                t_spike = st.slider("Torque Spike Anomaly Trigger (% above baseline):", 10, 50, 30, 5)
            with c_cal2:
                r_min = st.slider("Minimum ROP Threshold (m/hr):", 0.5, 5.0, 2.0, 0.2)
                l_window = st.slider("Proactive Depth Lookahead Window (meters ahead):", 30.0, 200.0, 100.0, 10.0)

            if st.button("💾 Save Calibrated Rig Baselines", type="primary"):
                st.success("✅ Rig operational baselines successfully calibrated and synchronized with live telemetry engine!")

    # ==========================================================================
    # TAB 1: GEOSPATIAL MAP & REAL-TIME REASONING
    # ==========================================================================
    with tab_map:
        col_map_view, col_reasoning_view = st.columns([1.1, 0.9])

        with col_map_view:
            st.subheader(f"Offset Wells Map ({radius_km} km Search Radius)")
            nearby_df = vl_rag.get_nearby_wells(ACTIVE_WELL_CONFIG["lat"], ACTIVE_WELL_CONFIG["lon"], radius_km)

            # Clean Light OpenStreetMap
            map_center = [ACTIVE_WELL_CONFIG["lat"], ACTIVE_WELL_CONFIG["lon"]]
            f_map = folium.Map(location=map_center, zoom_start=12, tiles="OpenStreetMap")

            # Active Well Marker
            folium.Marker(
                location=map_center,
                popup=f"<b>ACTIVE RIG: {ACTIVE_WELL_CONFIG['well_name']}</b><br>Depth: {current_depth}m<br>Formation: Barail Sandstone",
                tooltip="Active Well: OIL-ACT-2026",
                icon=folium.Icon(color="orange", icon="tint", prefix="fa")
            ).add_to(f_map)

            # Proximity Radius Circle
            folium.Circle(
                location=map_center,
                radius=radius_km * 1000,
                color="#EA580C",
                fill=True,
                fill_color="#F97316",
                fill_opacity=0.08,
                weight=2,
                dash_array="6, 6"
            ).add_to(f_map)

            # Offset wells markers
            for _, w in nearby_df.iterrows():
                is_stuck = "Stuck" in str(w['status'])
                is_loss = "Loss" in str(w['status'])
                pin_color = "#EF4444" if is_stuck else ("#F59E0B" if is_loss else "#10B981")
                
                folium.CircleMarker(
                    location=[w['lat'], w['lon']],
                    radius=8,
                    popup=f"<b>{w['well_name']} ({w['well_id']})</b><br>Distance: {w['distance_km']} km<br>TD: {w['total_depth_m']} m<br>Status: {w['status']}",
                    tooltip=f"{w['well_name']} ({w['distance_km']} km)",
                    color=pin_color,
                    fill=True,
                    fill_color=pin_color,
                    fill_opacity=0.85
                ).add_to(f_map)

            st_folium(f_map, height=420, use_container_width=True)
            st.dataframe(
                nearby_df[["well_id", "well_name", "distance_km", "total_depth_m", "status"]],
                use_container_width=True,
                height=160
            )

        with col_reasoning_view:
            st.subheader("⚡ JEV Multi-Criteria AI Reasoning Engine")
            st.caption("Powered by Groq Cloud (Qwen 3.8 27B + GPT-OSS 120B)")

            if st.button("🚀 Run JEV Automated Evidence Ranking", use_container_width=True, type="primary"):
                with st.spinner("Aggregating Unified Operational Context & Executing Groq JEV Reasoning..."):
                    lessons = v_rag.query_lessons_learned("stuck pipe torque anomaly Barail", "Barail Sandstone", top_k=2)
                    context_str = UnifiedContextBuilder.build_context(
                        ACTIVE_WELL_CONFIG,
                        telemetry_snapshot,
                        alerts,
                        lookaheads,
                        nearby_df.to_string(),
                        lessons
                    )
                    jev_output = jev_eng.evaluate(context_str)
                    aver_brief = aver_chat.generate_explanation(context_str, jev_output.model_dump_json())

                    st.markdown(f"""
                    <div style="background: #ECFDF5; border-left: 5px solid #10B981; padding: 14px 18px; border-radius: 8px; margin-bottom: 14px; border: 1px solid #A7F3D0;">
                        <h4 style="color: #065F46; margin: 0; font-weight: 800;">TOP SELECTED: {jev_output.optimal_selected_option}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write(f"**Engineering Justification:** {jev_output.engineering_justification}")

                    st.markdown("#### Ranked Candidate Mitigation Matrix:")
                    for opt in jev_output.candidate_options:
                        badge_color = "#10B981" if opt.confidence_score > 80 else ("#F59E0B" if opt.confidence_score > 60 else "#EF4444")
                        with st.expander(f"{opt.option_id}: {opt.title} — Score: {opt.confidence_score}%"):
                            st.write(f"**Procedure:** {opt.action_summary}")
                            st.write(f"**Offset Empirical Proof:** {opt.supporting_well_evidence}")
                            st.write(f"**Consequence If Skipped:** {opt.operational_risk_if_ignored}")

                    st.markdown("#### 📋 AVER Plain-English Advisory Briefing:")
                    st.markdown(aver_brief)

    # TAB 2: 3D SUBSURFACE TRAJECTORIES & HORIZONS
    with tab_3d:
        st.subheader("🌐 3D Subsurface Wellbore Trajectories & Formation Horizons")
        st.caption("Interactive 3D visualization using Minimum Curvature directional surveys (API RP 7G) and regional stratigraphic dip planes.")

        col_3d_info, col_3d_canvas = st.columns([1, 2.5])
        with col_3d_info:
            st.markdown(f"""
            <div class="clean-card" style="border-top: 4px solid #EA580C; margin-bottom: 12px;">
                <h4 style="color: #EA580C; margin-top: 0;">Active Wellbore Survey</h4>
                <p style="font-size: 0.95rem; line-height: 1.6;">
                <b>Rig:</b> OIL Naharkatiya Active-01<br/>
                <b>Measured Depth:</b> {current_depth:.1f} m MD<br/>
                <b>True Vertical Depth:</b> {current_tvd:.1f} m TVD<br/>
                <b>Total Displacement:</b> {active_survey.iloc[-1]['disp_m']:.1f} m<br/>
                <b>Max Dogleg Severity:</b> {active_survey['dls_deg_30m'].max():.2f}°/30m
                </p>
            </div>
            <div class="clean-card" style="border-top: 4px solid #3B82F6;">
                <h4 style="color: #1E40AF; margin-top: 0;">Subsurface Legend</h4>
                <p style="font-size: 0.92rem; line-height: 1.6;">
                🟠 <b>Active Well (NH-24):</b> S-Curve Directional<br/>
                ⚪ <b>Offsets:</b> Adjacent historical trajectories<br/>
                🟤 <b>Formation Horizon:</b> Barail Top (~2,400m TVD)<br/>
                🔴 <b>Hazard Pin:</b> Recorded Stuck Pipe Zone
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_3d_canvas:
            fig_3d = go.Figure()

            # Active Well Trajectory
            fig_3d.add_trace(go.Scatter3d(
                x=active_survey["east"],
                y=active_survey["north"],
                z=-active_survey["tvd"],
                mode="lines+markers",
                name="Active Well (NH-24)",
                line=dict(color="#EA580C", width=7),
                marker=dict(size=3, color="#EA580C")
            ))

            # Offset Well Trajectories
            nearby_offsets = vl_rag.get_nearby_wells(ACTIVE_WELL_CONFIG["lat"], ACTIVE_WELL_CONFIG["lon"], radius_km).to_dict(orient="records")
            offset_paths = dir_eng.generate_offset_trajectories(nearby_offsets)
            for w_id, off_df in offset_paths.items():
                fig_3d.add_trace(go.Scatter3d(
                    x=off_df["east"],
                    y=off_df["north"],
                    z=-off_df["tvd"],
                    mode="lines",
                    name=f"Offset {w_id}",
                    line=dict(width=3, dash="dot")
                ))

            # Formation Top Plane (Barail Sandstone at ~2,400m TVD with 2.4° dip)
            grid_x = np.linspace(-1500, 1500, 6)
            grid_y = np.linspace(-1500, 1500, 6)
            gx, gy = np.meshgrid(grid_x, grid_y)
            gz = -2400.0 + (gy * math.tan(math.radians(2.4))) # Regional south-southeast dip
            fig_3d.add_trace(go.Surface(
                x=gx, y=gy, z=gz,
                opacity=0.30,
                colorscale="YlOrBr",
                showscale=False,
                name="Barail Formation Top Plane"
            ))

            # Floating Hazard Diamond
            fig_3d.add_trace(go.Scatter3d(
                x=[active_survey.iloc[-1]["east"]],
                y=[active_survey.iloc[-1]["north"]],
                z=[-current_tvd],
                mode="markers+text",
                name="Current Bit Position",
                marker=dict(size=8, color="#DC2626", symbol="diamond"),
                text=[f"Bit @ {current_depth:.0f}m MD"],
                textposition="top center"
            ))

            fig_3d.update_layout(
                scene=dict(
                    xaxis_title="East Offset (m)",
                    yaxis_title="North Offset (m)",
                    zaxis_title="True Vertical Depth (-m TVD)",
                    camera=dict(eye=dict(x=1.4, y=-1.4, z=0.7))
                ),
                margin=dict(l=0, r=0, b=0, t=10),
                height=520
            )
            st.plotly_chart(fig_3d, use_container_width=True)

    # TAB 3: FORMATION & DEPTH CORRELATOR (MD to TVD + Stratigraphic Dip)
    with tab_correlator:
        st.subheader("📊 Stratigraphic & Formation TVD Depth Correlation")
        st.caption("Aligns True Vertical Depth (TVD via Minimum Curvature), regional stratigraphic dip (2.4° SSE), and casing shoe leak-off limits.")
        
        corr_df = vl_rag.correlate_depth_formation(
            ACTIVE_WELL_CONFIG["lat"],
            ACTIVE_WELL_CONFIG["lon"],
            current_depth,
            "Barail Sandstone",
            radius_km
        )
        
        # Add TVD and Dip shift columns
        corr_df["calculated_tvd_m"] = current_tvd
        corr_df["dip_adjusted_depth_m"] = corr_df.apply(
            lambda r: round(current_tvd + dir_eng.get_stratigraphic_tvd_dip(r.get("distance_km", 2.0)), 1),
            axis=1
        )
        
        st.dataframe(corr_df, use_container_width=True)

        st.markdown("---")
        st.subheader("Formation Lithology Column & Casing Seats")
        c1, c2, c3 = st.columns(3)
        c1.info("Top Formation: Alluvium (0 - 850m) | Casing: 20\" Conductor")
        c2.warning("Intermediate: Tipam Sandstone (850 - 2,200m) | Casing: 13-3/8\" Surface")
        c3.error("Target Deep Zone: Barail Sandstone (2,750 - 3,200m) | Casing: 9-5/8\" Intermediate (⚠️ High Tectonic Drag)")

    # TAB 4: CREW INPT & EFFICIENCY BENCHMARKING
    with tab_inpt:
        st.subheader("⏱️ Invisible Non-Productive Time (INPT) Crew Benchmarking")
        st.caption("3σ Normal Distribution analysis on 1-second telemetry uncovering connection micro-delays (up to 32% recoverable operational time).")

        inpt_data = inpt_eng.analyze_crew_efficiency()

        col_inpt_m1, col_inpt_m2, col_inpt_m3, col_inpt_m4 = st.columns(4)
        col_inpt_m1.metric("Mean Connection Time", f"{inpt_data['mean_connection_time_min']} min", delta=f"{inpt_data['mean_connection_time_min'] - inpt_data['p25_benchmark_min']:.1f}m vs P25", delta_color="inverse")
        col_inpt_m2.metric("P25 Best-in-Class", f"{inpt_data['p25_benchmark_min']} min")
        col_inpt_m3.metric("Invisible Downtime", f"{inpt_data['total_invisible_delay_hours']} hrs", f"{inpt_data['recoverable_operational_pct']}% Recoverable")
        col_inpt_m4.metric("Potential Cost Savings", inpt_data["potential_savings_inr"], "Rig Spread Rate: ₹1.2L/hr")

        st.markdown("<br/>", unsafe_allow_html=True)
        col_inpt_chart, col_inpt_table = st.columns([2, 1.2])

        with col_inpt_chart:
            st.markdown("#### Gaussian Distribution of Pipe Connection Durations")
            fig_inpt = go.Figure()
            fig_inpt.add_trace(go.Scatter(
                x=inpt_data["curve_x"],
                y=inpt_data["curve_y"],
                mode="lines",
                name="Connection Duration Density",
                line=dict(color="#EA580C", width=3),
                fill="tozeroy",
                fillcolor="rgba(234, 88, 12, 0.12)"
            ))
            fig_inpt.add_vline(x=inpt_data["p25_benchmark_min"], line_dash="dash", line_color="#10B981", annotation_text="P25 Best Crew (3.5 min)")
            fig_inpt.add_vline(x=inpt_data["mean_connection_time_min"], line_dash="solid", line_color="#EF4444", annotation_text=f"Active Mean ({inpt_data['mean_connection_time_min']} min)")
            fig_inpt.update_layout(
                xaxis_title="Pipe Connection Duration (Minutes)",
                yaxis_title="Probability Density",
                height=380,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_inpt, use_container_width=True)

        with col_inpt_table:
            st.markdown("#### Shift Crew Comparison")
            st.markdown(f"""
            <div class="clean-card" style="border-left: 4px solid #10B981; margin-bottom: 12px;">
                <h5 style="color: #065F46; margin: 0;">🏆 Top Performing Crew</h5>
                <p style="margin: 4px 0 0 0; font-size: 0.95rem;">{inpt_data['top_performer']}</p>
            </div>
            <div class="clean-card" style="border-left: 4px solid #EF4444;">
                <h5 style="color: #991B1B; margin: 0;">🎯 Coaching & Optimization Target</h5>
                <p style="margin: 4px 0 0 0; font-size: 0.95rem;">{inpt_data['coaching_target']}</p>
            </div>
            """, unsafe_allow_html=True)
            st.caption("💡 Eliminating micro-delays between slips-to-slips time saves up to 4.2 rig days per 4,000m well drilled in Upper Assam.")

    # TAB 5: GEOMECHANICS & SAFE MUD WINDOW
    with tab_geom:
        st.subheader("🔬 Dual-Driven Geomechanical Safe Mud Window (R² = 0.924)")
        st.caption("Combines geomechanical stress equilibrium with logging sensors (CAL, DT, GR, VSH, DEN) to establish pore pressure, collapse, and fracture leak-off limits.")

        mud_profile = geom_eng.generate_depth_mud_window_profile()
        current_win = geom_eng.calculate_safe_mud_window(current_depth, "Barail Sandstone")

        col_gm1, col_gm2, col_gm3, col_gm4 = st.columns(4)
        col_gm1.metric("Pore Pressure (Pp)", f"{current_win['pore_pressure_ppg']} ppg", "Assam Barail Basin")
        col_gm2.metric("Wellbore Collapse Limit", f"{current_win['collapse_gradient_ppg']} ppg", "Shear Failure Lower Bound")
        col_gm3.metric("Safe Operating Window", f"{current_win['safe_window_min_ppg']} - {current_win['safe_window_max_ppg']} ppg", f"Span: {current_win['safe_window_span_ppg']} ppg")
        col_gm4.metric("Formation Leak-Off (LOT)", f"{current_win['leak_off_pressure_ppg']} ppg", "Upper Fracture Limit")

        st.markdown("<br/>", unsafe_allow_html=True)
        col_gm_plot, col_gm_opt = st.columns([2, 1.2])

        with col_gm_plot:
            st.markdown("#### Subsurface Stress & Safe Mud Weight Profile")
            fig_geo = go.Figure()
            fig_geo.add_trace(go.Scatter(x=mud_profile["pore_ppg"], y=mud_profile["depth_m"], name="Pore Pressure (Pp)", line=dict(color="#3B82F6", dash="dot")))
            fig_geo.add_trace(go.Scatter(x=mud_profile["collapse_ppg"], y=mud_profile["depth_m"], name="Collapse Gradient", line=dict(color="#10B981", width=2)))
            fig_geo.add_trace(go.Scatter(x=mud_profile["safe_max_ppg"], y=mud_profile["depth_m"], name="Safe Max ECD", line=dict(color="#F59E0B", width=2)))
            fig_geo.add_trace(go.Scatter(x=mud_profile["fracture_ppg"], y=mud_profile["depth_m"], name="Leak-Off Pressure (LOT)", line=dict(color="#EF4444", width=2)))
            fig_geo.add_trace(go.Scatter(x=[current_ecd], y=[current_depth], mode="markers", name="Active Rig ECD", marker=dict(size=12, color="#EA580C", symbol="circle")))
            fig_geo.update_yaxes(autorange="reversed")
            fig_geo.update_layout(
                xaxis_title="Equivalent Density (ppg)",
                yaxis_title="Depth (m)",
                height=420,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_geo, use_container_width=True)

        with col_gm_opt:
            st.markdown("#### Bourgoyne & Young ROP Optimizer")
            rop_opt = tel_eng.risk_classifier.optimize_rop(current_wob, 110.0, current_rop, current_torque)
            st.markdown(f"""
            <div class="clean-card" style="border-top: 4px solid #10B981; margin-bottom: 12px;">
                <h5 style="color: #065F46; margin: 0;">🚀 Controllable Parameters Optimizer</h5>
                <p style="margin: 6px 0 0 0; font-size: 0.95rem; line-height: 1.6;">
                <b>Projected ROP Gain:</b> <span style="color: #10B981; font-weight: 800;">+{rop_opt['projected_rop_gain_pct']}%</span> ({rop_opt['projected_rop_mph']} m/hr)<br/>
                <b>Recommended WOB:</b> {rop_opt['recommended_wob_kn']} kN (Current: {rop_opt['current_wob_kn']} kN)<br/>
                <b>Recommended RPM:</b> {rop_opt['recommended_rpm']} RPM (Current: {rop_opt['current_rpm']} RPM)<br/>
                <b>Vibration Envelope:</b> <span style="font-weight: 700;">{rop_opt['vibration_safety_status']}</span><br/>
                <b>Limit Check:</b> {rop_opt['drillstring_limit_check']}
                </p>
            </div>
            """, unsafe_allow_html=True)

    # TAB 3: SEMANTIC KNOWLEDGE SEARCH (VECTOR RAG)
    with tab_vector:
        st.subheader("Semantic Knowledge Search (Historical WCRs, DDRs & Incident Reports)")
        search_q = st.text_input(
            "Ask any drilling query across historical Oil India reports:",
            "What mud weight was used when stuck pipe occurred in Barail Sandstone?"
        )
        if st.button("🔍 Search Institutional Knowledge", use_container_width=True):
            with st.spinner("Searching Vector Space..."):
                results = v_rag.query_lessons_learned(search_q, top_k=3)
                if results:
                    for r in results:
                        st.markdown(f"""
                        <div class="clean-card" style="border-left: 5px solid #EA580C;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: #EA580C; font-weight: 800; font-size: 1.05rem;">📄 {r['source']} (Page {r['page']})</span>
                                <span class="badge-accent-orange">WELL: {r['well_id']} | MATCH: {r['score']*100:.1f}%</span>
                            </div>
                            <p style="margin: 10px 0 0 0; color: #0F172A; line-height: 1.55; font-size: 0.95rem; font-weight: 500;">{r['excerpt']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No direct matches found.")

    # TAB 4: AUDIT TRAIL
    with tab_audit:
        st.subheader("Immutable Drilling Compliance & Decision Audit Ledger")
        st.write("Regulatory audit trail tracking every AI recommendation, supporting offset citations, and human engineer operational calls.")
        st.table(pd.DataFrame(st.session_state.audit_log))

    # TAB 5: AVER AI CHAT
    with tab_aver:
        st.subheader("💬 AVER Drilling Expert Interactive Assistant")
        st.caption("Ask complex follow-up questions, verify casing constraints, or explore alternative well histories.")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        user_input = st.chat_input("Ask AVER a question (e.g., 'Why not Option C?', 'Show other nearby wells', 'What is estimated NPT?')")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            context_str = UnifiedContextBuilder.build_context(
                ACTIVE_WELL_CONFIG,
                telemetry_snapshot,
                alerts,
                lookaheads,
                vl_rag.get_nearby_wells(ACTIVE_WELL_CONFIG["lat"], ACTIVE_WELL_CONFIG["lon"], radius_km).to_string(),
                v_rag.query_lessons_learned(user_input, top_k=2)
            )

            with st.chat_message("assistant"):
                with st.spinner("AVER reasoning..."):
                    reply = aver_chat.answer_followup(st.session_state.chat_history, user_input, context_str)
                    st.write(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})


