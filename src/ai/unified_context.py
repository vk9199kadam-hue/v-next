from typing import Dict, Any, List

class UnifiedContextBuilder:
    """
    Combines live eRTMAC sensor readings, proactive lookaheads,
    structured offset well correlations, and vector lessons-learned excerpts
    into a structured context prompt for Groq LLMs.
    """
    @staticmethod
    def build_context(
        active_well: Dict[str, Any],
        telemetry: Dict[str, float],
        alerts: List[Dict[str, Any]],
        lookaheads: List[Dict[str, Any]],
        offset_df_summary: str,
        vector_lessons: List[Dict[str, Any]]
    ) -> str:
        # Format lessons citations
        lessons_text = ""
        if vector_lessons:
            for l in vector_lessons:
                lessons_text += f"- [{l['well_id']} | Source: {l['source']}, Page {l['page']} | Formation: {l['formation']}]:\n  \"{l['excerpt']}\"\n\n"
        else:
            lessons_text = "No direct historical text excerpts found.\n"

        # Format alerts
        alert_text = "\n".join([f"⚠️ [{a['severity']}] {a['title']}: {a['message']}" for a in alerts]) if alerts else "No active sensor thresholds exceeded."

        # Format lookaheads
        lookahead_text = "\n".join([
            f"🔮 At {lk['depth_m']}m (+{lk['lead_distance_m']}m ahead) in {lk['well_name']}: [{lk['event_type']}] - {lk['description']} | Mitigation: {lk['recommended_prep']}"
            for lk in lookaheads
        ]) if lookaheads else "No historical offset hazards logged within upcoming 100m interval."

        return f"""
======================================================================
UNIFIED OPERATIONAL CONTEXT — OIL INDIA LIMITED (V-NEXT NWIS)
======================================================================
ACTIVE RIG: {active_well['well_name']} ({active_well['well_id']})
LOCATION: {active_well['field']} (Lat: {active_well['lat']}, Lon: {active_well['lon']})
TARGET DEPTH: {active_well['target_depth_m']} m | CURRENT BIT DEPTH: {telemetry.get('depth_m', active_well['current_depth_m'])} m
CURRENT FORMATION: {active_well['current_formation']}

[1. REAL-TIME eRTMAC TELEMETRY SNAPSHOT]
• Weight on Bit (WOB): {telemetry.get('wob_kn', 120.0)} kN
• Surface Torque: {telemetry.get('torque_knm', 18.0)} kNm
• Rate of Penetration (ROP): {telemetry.get('rop_mph', 5.5)} m/hr
• Rotary Speed (RPM): {telemetry.get('rpm', 110)} RPM
• Equivalent Circulating Density (ECD): {telemetry.get('ecd_ppg', 12.1)} ppg
• Standpipe Pressure: {telemetry.get('pressure_psi', 2850)} psi
• Flow In / Flow Out: {telemetry.get('flow_in_gpm', 520)} gpm / {telemetry.get('flow_out_gpm', 520)} gpm

ACTIVE SENSOR ALERTS:
{alert_text}

[2. PROACTIVE DEPTH LOOKAHEAD (+100 METERS AHEAD)]
{lookahead_text}

[3. STRUCTURED OFFSET WELL CORRELATION (VECTORLESS RAG)]
{offset_df_summary}

[4. HISTORICAL DRILLING LESSONS & WCR REPORTS (VECTOR RAG)]
{lessons_text}
======================================================================
"""
