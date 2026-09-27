import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# AI Models (Active on your Groq Account)
GROQ_FAST_MODEL = "qwen/qwen3.8-27b"             # Fast candidate generation
GROQ_REASONING_MODEL = "openai/gpt-oss-120b"       # Deep reasoning (120B model)

# Active Well Rig Configuration (Upper Assam Basin - Oil India Field)
ACTIVE_WELL_CONFIG = {
    "well_id": "OIL-ACT-2026",
    "well_name": "OIL Naharkatiya Active-01",
    "lat": 27.2915,
    "lon": 95.3482,
    "field": "Naharkatiya Oilfield, Assam",
    "target_depth_m": 3800.0,
    "current_depth_m": 2845.0,
    "current_formation": "Barail Sandstone"
}

# eRTMAC Operational Baselines & Anomaly Thresholds
TELEMETRY_THRESHOLDS = {
    "torque_max_knm": 25.0,
    "torque_spike_percent": 30.0,
    "rop_min_mph": 2.0,
    "flow_loss_threshold_percent": 10.0,
    "lookahead_window_m": 100.0
}
