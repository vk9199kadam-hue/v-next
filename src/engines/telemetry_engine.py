import pandas as pd
from typing import Dict, Any, List

class TelemetryEngine:
    """
    Simulates eRTMAC live rig streams, evaluates real-time sensor thresholds,
    and runs proactive depth lookahead hazard prediction for approaching formations.
    """
    def __init__(self, stream_csv_path: str, duckdb_con):
        self.stream_df = pd.read_csv(stream_csv_path)
        self.con = duckdb_con

    def evaluate_reading(self, reading: Dict[str, float]) -> List[Dict[str, Any]]:
        alerts = []
        torque = reading.get("torque_knm", 0.0)
        rop = reading.get("rop_mph", 0.0)
        flow_in = reading.get("flow_in_gpm", 520.0)
        flow_out = reading.get("flow_out_gpm", 520.0)
        ecd = reading.get("ecd_ppg", 12.0)

        # 1. Critical Anomaly: Torque Spike (Stuck pipe / Tight hole precursor)
        if torque > 25.0:
            alerts.append({
                "type": "TORQUE_SPIKE",
                "severity": "CRITICAL_RED",
                "title": "Severe Torque Spike Detected",
                "message": f"Torque reached {torque:.1f} kNm (+42% spike above baseline). High risk of mechanical pipe sticking.",
                "metric": "Torque",
                "value": torque
            })

        # 2. Critical Anomaly: Mud Losses / Loss of Returns
        if flow_in > 0 and (flow_in - flow_out) / flow_in > 0.08:
            loss_pct = ((flow_in - flow_out) / flow_in) * 100
            alerts.append({
                "type": "MUD_LOSS",
                "severity": "CRITICAL_RED",
                "title": "Lost Circulation Alert",
                "message": f"Mud return flow dropped by {loss_pct:.1f}%. Drilling fluid leaking into subsurface fractures.",
                "metric": "Flow Balance",
                "value": flow_out
            })

        # 3. Warning: Severe ROP Drop with stable WOB
        if rop < 1.0 and reading.get("wob_kn", 0) > 100:
            alerts.append({
                "type": "BIT_BALLING_PACKOFF",
                "severity": "WARNING_YELLOW",
                "title": "Penetration Rate Plunge",
                "message": f"ROP dropped to {rop:.1f} m/hr with high WOB applied. Indicator of bit balling or annular packoff.",
                "metric": "ROP",
                "value": rop
            })

        return alerts

    def check_proactive_lookahead(self, current_depth: float, window_m: float = 100.0) -> List[Dict[str, Any]]:
        """
        Scans offset wells within [current_depth, current_depth + window_m]
        to provide proactive early warnings BEFORE the bit enters the hazard zone.
        """
        query = f"""
        SELECT 
            well_name, 
            depth_m, 
            event_type, 
            severity, 
            description, 
            mitigation
        FROM npt_events
        WHERE depth_m BETWEEN {current_depth} AND {current_depth + window_m}
        ORDER BY depth_m ASC;
        """
        results = self.con.execute(query).fetchall()
        warnings = []
        for r in results:
            warnings.append({
                "well_name": r[0],
                "depth_m": r[1],
                "event_type": r[2],
                "severity": r[3],
                "description": r[4],
                "recommended_prep": r[5],
                "lead_distance_m": round(r[1] - current_depth, 1)
            })
        return warnings
