from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio
import json

from src.utils.config import ACTIVE_WELL_CONFIG
from src.engines.vector_rag import VectorRAGEngine
from src.engines.vectorless_rag import VectorlessRAGEngine
from src.engines.telemetry_engine import TelemetryEngine
from src.ai.unified_context import UnifiedContextBuilder
from src.ai.jev_reasoning import JEVReasoningEngine
from src.ai.aver_chatbot import AVERChatbot
from src.engines.directional_survey import DirectionalSurveyEngine
from src.engines.inpt_analyzer import INPTAnalyzerEngine
from src.engines.geomechanics import GeomechanicsEngine
from src.ai.fcbr_engine import FuzzyCBREngine

app = FastAPI(
    title="V-Next: Nearby Wells Intelligence System (NWIS) API",
    description="Oil India Limited eRTMAC Standalone Decision Support Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
v_rag = VectorRAGEngine()
vl_rag = VectorlessRAGEngine()
tel_eng = TelemetryEngine("data/telemetry/active_well_stream.csv", vl_rag.con)
jev_eng = JEVReasoningEngine()
aver_chat = AVERChatbot()
dir_eng = DirectionalSurveyEngine()
inpt_eng = INPTAnalyzerEngine()
geom_eng = GeomechanicsEngine()
fcbr_eng = FuzzyCBREngine()

class QueryRequest(BaseModel):
    query: str
    radius_km: float = 6.0
    formation: str = "Barail Sandstone"

@app.get("/")
def root():
    return {
        "status": "ONLINE",
        "system": "V-Next NWIS (Oil India Limited)",
        "active_rig": ACTIVE_WELL_CONFIG["well_name"],
        "engines": ["Vector RAG", "Vectorless SQL Geo", "eRTMAC Telemetry", "Groq JEV+AVER"]
    }

@app.get("/api/nearby-wells")
def get_nearby_wells(radius_km: float = 6.0):
    df = vl_rag.get_nearby_wells(ACTIVE_WELL_CONFIG["lat"], ACTIVE_WELL_CONFIG["lon"], radius_km)
    return df.to_dict(orient="records")

@app.get("/api/correlate-depth")
def correlate_depth(depth_m: float = 2847.0, formation: str = "Barail Sandstone", radius_km: float = 6.0):
    df = vl_rag.correlate_depth_formation(
        ACTIVE_WELL_CONFIG["lat"], ACTIVE_WELL_CONFIG["lon"], depth_m, formation, radius_km
    )
    return df.to_dict(orient="records")

@app.post("/api/semantic-search")
def search_knowledge(request: QueryRequest):
    results = v_rag.query_lessons_learned(request.query, request.formation, top_k=3)
    return {"results": results}

@app.post("/api/evaluate-decision")
def evaluate_decision(telemetry_data: Dict[str, float]):
    alerts = tel_eng.evaluate_reading(telemetry_data)
    lookaheads = tel_eng.check_proactive_lookahead(telemetry_data.get("depth_m", 2847.0))
    nearby_df = vl_rag.get_nearby_wells(ACTIVE_WELL_CONFIG["lat"], ACTIVE_WELL_CONFIG["lon"], 6.0)
    lessons = v_rag.query_lessons_learned("stuck pipe torque anomaly Barail", "Barail Sandstone", top_k=2)

    context = UnifiedContextBuilder.build_context(
        ACTIVE_WELL_CONFIG,
        telemetry_data,
        alerts,
        lookaheads,
        nearby_df.to_string(),
        lessons
    )
    jev_result = jev_eng.evaluate(context)
    aver_brief = aver_chat.generate_explanation(context, jev_result.model_dump_json())

    return {
        "alerts": alerts,
        "lookaheads": lookaheads,
        "jev_evaluation": jev_result.model_dump(),
        "aver_briefing": aver_brief
    }

@app.get("/api/directional-survey")
def get_directional_survey(depth_m: float = 2847.2):
    traj_df = dir_eng.generate_synthetic_active_trajectory(depth_m)
    return traj_df.to_dict(orient="records")

@app.get("/api/geomechanics-window")
def get_geomechanics_window(depth_m: float = 2847.2, formation: str = "Barail Sandstone"):
    return geom_eng.calculate_safe_mud_window(depth_m, formation)

@app.get("/api/inpt-benchmarks")
def get_inpt_benchmarks():
    return inpt_eng.analyze_crew_efficiency()

@app.post("/api/predict-fluid-loss")
def predict_fluid_loss(telemetry_data: Dict[str, float]):
    loss_pred = tel_eng.risk_classifier.predict_loss_severity(telemetry_data)
    rop_opt = tel_eng.risk_classifier.optimize_rop(
        telemetry_data.get("wob_kn", 125.0),
        telemetry_data.get("rpm", 110.0),
        telemetry_data.get("rop_mph", 14.2),
        telemetry_data.get("torque_knm", 18.4)
    )
    return {
        "fluid_loss_classification": loss_pred,
        "rop_optimization": rop_opt
    }

@app.post("/api/fcbr-match")
def match_fcbr_case(telemetry_data: Dict[str, float]):
    return fcbr_eng.match_case(telemetry_data)

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    stream_df = tel_eng.stream_df
    try:
        for _, row in stream_df.iterrows():
            reading = row.to_dict()
            alerts = tel_eng.evaluate_reading(reading)
            payload = {
                "reading": reading,
                "alerts": alerts
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass

