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
