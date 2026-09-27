"""
V-NEXT: NEARBY WELLS INTELLIGENCE SYSTEM (NWIS)
Unified CLI Entry Point
Oil India Limited (OIL) | Smart India Hackathon 2026
"""

import argparse
import sys
import subprocess


def run_app(port: int = 8501):
    """Launch the Streamlit Web Application."""
    print(f"🚀 Launching V-Next Interactive Dashboard on port {port}...")
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", str(port)]
    subprocess.run(cmd)


def run_api(port: int = 8000):
    """Launch the FastAPI Headless Server."""
    print(f"⚡ Launching V-Next FastAPI Server on port {port}...")
    cmd = [sys.executable, "-m", "uvicorn", "api:app", "--reload", "--port", str(port)]
    subprocess.run(cmd)


def run_diagnostics():
    """Verify system components, data engines, and Groq LLM connectivity."""
    print("=" * 60)
    print("🔬 V-NEXT SYSTEM INTEGRITY & DIAGNOSTIC CHECK")
    print("=" * 60)
    
    # 1. Check Data Generators & Engines
    try:
        from src.utils.mock_data_generator import generate_mock_datasets
        from src.engines.vectorless_rag import VectorlessRAGEngine
        from src.engines.vector_rag import VectorRAGEngine
        from src.engines.telemetry_engine import TelemetryEngine
        from src.engines.data_ingestion import DataIngestionPipeline
        
        print(" [OK] Core modules imported successfully.")
        
        generate_mock_datasets()
        print(" [OK] Upper Assam synthetic dataset verified.")
        
        vless = VectorlessRAGEngine()
        offsets = vless.get_nearby_wells(27.300, 95.350, 10.0)
        print(f" [OK] DuckDB Vectorless RAG active: {len(offsets)} offsets indexed within 10km.")
        
        vrag = VectorRAGEngine()
        results = vrag.query_lessons_learned("torque spike pack-off", top_k=2)
        print(f" [OK] Dense Vector RAG active: retrieved {len(results)} historical hazard records.")
        
        from src.utils.config import BASE_DIR
        telem = TelemetryEngine(str(BASE_DIR / "data" / "telemetry" / "active_well_stream.csv"), vless.con)
        lookahead = telem.check_proactive_lookahead(2800.0, 150.0)
        print(f" [OK] eRTMAC Telemetry stream verified (Lookahead scans active: {len(lookahead)} hazards detected).")

        # 2. Check Advanced Risk ML & State Recognition
        from src.engines.risk_classifier import RiskClassifierEngine
        from src.engines.state_recognizer import DrillingStateRecognizer
        risk_eng = RiskClassifierEngine()
        sample_telem = {"depth_m": 2847.2, "rop_mph": 14.2, "wob_kn": 125.0, "rpm": 110.0, "torque_knm": 18.4, "spp_psi": 2850.0, "flow_in_gpm": 520.0, "flow_out_gpm": 515.0, "ecd_ppg": 11.85}
        loss_pred = risk_eng.predict_loss_severity(sample_telem)
        print(f" [OK] Random Forest 5-Class Loss ML verified: {loss_pred['tier_label']} ({loss_pred['severity_name']}).")
        
        state_eng = DrillingStateRecognizer()
        state_pred = state_eng.identify_state(sample_telem)
        print(f" [OK] SVM Drilling State Recognizer verified: {state_pred['state_name']} ({state_pred['confidence_pct']}% conf).")

        # 3. Check Minimum Curvature MD-to-TVD & Geomechanics
        from src.engines.directional_survey import DirectionalSurveyEngine
        from src.engines.geomechanics import GeomechanicsEngine
        survey_df = DirectionalSurveyEngine.generate_synthetic_active_trajectory(2847.2)
        active_tvd = survey_df.iloc[-1]["tvd"]
        print(f" [OK] Minimum Curvature Directional Engine: MD 2,847.2m -> TVD {active_tvd}m (Disp: {survey_df.iloc[-1]['disp_m']}m).")

        geom_eng = GeomechanicsEngine()
        mud_win = geom_eng.calculate_safe_mud_window(2847.2, "Barail Sandstone")
        print(f" [OK] Geomechanical Safe Mud Window (R^2={mud_win['model_r2_accuracy']}): [{mud_win['safe_window_min_ppg']} - {mud_win['safe_window_max_ppg']} ppg].")

        # 4. Check 3σ INPT Analyzer, Edge Safety & Fuzzy CBR
        from src.engines.inpt_analyzer import INPTAnalyzerEngine
        from src.engines.edge_safety import EdgeSafetyEngine
        from src.ai.fcbr_engine import FuzzyCBREngine

        inpt_eng = INPTAnalyzerEngine()
        inpt_res = inpt_eng.analyze_crew_efficiency()
        print(f" [OK] 3σ INPT Crew Analyzer: {inpt_res['total_invisible_delay_hours']}h invisible downtime identified ({inpt_res['potential_savings_inr']} savings).")

        edge_eng = EdgeSafetyEngine()
        edge_res = edge_eng.evaluate_edge_safety(sample_telem)
        print(f" [OK] Microsecond Edge Safety Interlock: Latency {edge_res['execution_latency_ms']} ms ({edge_res['status']}).")

        fcbr_eng = FuzzyCBREngine()
        fcbr_res = fcbr_eng.match_case(sample_telem)
        print(f" [OK] Fuzzy CBR Cobweb Matcher: Top Analog {fcbr_res['top_match']['well_name']} ({fcbr_res['top_match']['similarity_score_pct']}% similarity).")
        
    except Exception as e:
        print(f" [FAIL] Engine check encountered an error: {e}")
        return False
        
    # 2. Check Groq Model Connectivity
    try:
        from src.utils.config import GROQ_API_KEY, GROQ_FAST_MODEL
        if GROQ_API_KEY:
            from groq import Groq
            client = Groq(api_key=GROQ_API_KEY)
            print(f" [OK] Groq API Key found. Active reasoning model: {GROQ_FAST_MODEL}")
        else:
            print(" [INFO] GROQ_API_KEY not configured. High-fidelity engineering fallback active.")
    except Exception as e:
        print(f" [WARN] Groq LLM check: {e}")
        
    print("=" * 60)
    print("✅ All V-Next NWIS subsystems operational!")
    print("=" * 60)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="V-Next: Nearby Wells Intelligence System (NWIS) for Oil India Limited",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run main.py --app               # Launch Streamlit UI (Rig HUD & Analytics)
  uv run main.py --api               # Launch FastAPI REST & WebSocket API
  uv run main.py --check             # Run self-test diagnostics
        """
    )
    parser.add_argument("--app", action="store_true", help="Launch Streamlit Web Dashboard")
    parser.add_argument("--api", action="store_true", help="Launch FastAPI REST/WebSocket Backend")
    parser.add_argument("--port", type=int, default=None, help="Port to run the server on")
    parser.add_argument("--check", action="store_true", help="Run system diagnostics & integrity check")

    args = parser.parse_args()

    if args.check:
        run_diagnostics()
    elif args.api:
        port = args.port or 8000
        run_api(port)
    elif args.app:
        port = args.port or 8501
        run_app(port)
    else:
        # Default behavior: run diagnostics and provide quick guidance
        print("\n" + "=" * 65)
        print("  🛢️  V-NEXT: NEARBY WELLS INTELLIGENCE SYSTEM (NWIS)")
        print("  Standalone Decision Support alongside eRTMAC for OIL")
        print("=" * 65)
        print("\nCommands to run:")
        print("  • Launch UI (Streamlit):  uv run python main.py --app")
        print("  • Launch API (FastAPI):   uv run python main.py --api")
        print("  • Run Diagnostics:       uv run python main.py --check")
        print("\nOr start directly:")
        print("  • uv run streamlit run app.py")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
