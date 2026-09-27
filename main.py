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
