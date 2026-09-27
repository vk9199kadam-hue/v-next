"""
Fuzzy Case-Based Reasoning (FCBR) Advisory Engine
eRTMAC-NWIS | Oil India Limited (OIL)

Uses Sigmoid Membership Functions and the Cobweb Polygon Area Model to evaluate
active drilling symptoms against historical problem-solving cases,
instantly recommending proven Lost Circulation Material (LCM) recipes and remediation steps.
"""

import math
import numpy as np
from typing import Dict, Any, List


class FuzzyCBREngine:
    """
    Fuzzy Case-Based Reasoning with Cobweb Area polygon matching.
    """

    def __init__(self):
        # Database of verified historical remediation cases from Upper Assam fields
        self.cases = [
            {
                "case_id": "CASE-OIL-NH18-01",
                "well_name": "Naharkatiya-18",
                "formation": "Barail Sandstone",
                "depth_m": 2845.0,
                "incident_type": "Mechanical Packoff & Torque Spike",
                "symptoms": {"torque_norm": 0.88, "rop_drop_norm": 0.90, "flow_loss_norm": 0.05, "ecd_norm": 0.65},
                "solution": "Controlled back-ream at 45 RPM with 25 bbl Hi-Vis Xanvis sweep (viscosity 65s). Reduce pump rate to 520 GPM.",
                "provenance": "WCR OIL-NH-18, Page 34",
                "success_rate_pct": 96.0
            },
            {
                "case_id": "CASE-OIL-KGT04-02",
                "well_name": "Kumchai-04",
                "formation": "Barail Sandstone",
                "depth_m": 3720.0,
                "incident_type": "Severe Mud Loss in Fractured Thief Zone",
                "symptoms": {"torque_norm": 0.25, "rop_drop_norm": 0.40, "flow_loss_norm": 0.92, "ecd_norm": 0.85},
                "solution": "Spot 35 bbl coarse walnut shell (30 ppb) + coarse calcium carbonate (25 ppb) pill. Hesitation squeeze at 250 psi.",
                "provenance": "WCR OIL-KGT-04, Page 67",
                "success_rate_pct": 94.5
            },
            {
                "case_id": "CASE-OIL-NH12-03",
                "well_name": "Naharkatiya-12",
                "formation": "Barail Sandstone",
                "depth_m": 3950.0,
                "incident_type": "Differential Sticking in Depleted Permeable Sand",
                "symptoms": {"torque_norm": 0.75, "rop_drop_norm": 0.85, "flow_loss_norm": 0.45, "ecd_norm": 0.80},
                "solution": "Spot 30 bbl Pipe-Lax oil-based soaking pill around BHA. Soak for 45 minutes; apply maximum safe downward jar (80 klbs).",
                "provenance": "WCR OIL-NH-12, Page 42",
                "success_rate_pct": 91.0
            },
            {
                "case_id": "CASE-OIL-MOR07-04",
                "well_name": "Moran-07",
                "formation": "Tipam Sandstone",
                "depth_m": 2150.0,
                "incident_type": "Shale Sloughing / Annular Bridging",
                "symptoms": {"torque_norm": 0.65, "rop_drop_norm": 0.60, "flow_loss_norm": 0.15, "ecd_norm": 0.55},
                "solution": "Increase mud weight by 0.3 ppg using potassium chloride (KCl/PHPA) polymer. Circulate bottom-up twice.",
                "provenance": "DDR OIL-MOR-07, Day 44",
                "success_rate_pct": 89.5
            }
        ]

    @staticmethod
    def _sigmoid_membership(val: float, center: float = 0.5, k: float = 8.0) -> float:
        """Sigmoid fuzzy membership function."""
        return 1.0 / (1.0 + math.exp(-k * (val - center)))

    def _calculate_cobweb_area(self, vector: List[float]) -> float:
        """
        Calculates the polygon area of an n-dimensional cobweb radar representation.
        Area = 0.5 * sin(2*pi/n) * sum(r_i * r_{i+1})
        """
        n = len(vector)
        if n < 3:
            return 0.0
        angle = (2.0 * math.pi) / n
        area = 0.0
        for i in range(n):
            r1 = vector[i]
            r2 = vector[(i + 1) % n]
            area += 0.5 * r1 * r2 * math.sin(angle)
        return abs(area)

    def match_case(self, telemetry: Dict[str, float]) -> Dict[str, Any]:
        """
        Evaluates active telemetry symptoms against historical cases and returns best match.
        """
        torque = float(telemetry.get("torque_knm", 18.4))
        rop = float(telemetry.get("rop_mph", 14.2))
        flow_in = float(telemetry.get("flow_in_gpm", 520.0))
        flow_out = float(telemetry.get("flow_out_gpm", 520.0))
        ecd = float(telemetry.get("ecd_ppg", 11.85))

        # Normalize symptoms into [0, 1] using fuzzy sigmoid
        torque_norm = self._sigmoid_membership(torque / 32.0, center=0.6, k=6.0)
        rop_drop_norm = self._sigmoid_membership(1.0 - min(rop / 25.0, 1.0), center=0.5, k=6.0)
        flow_loss_ratio = max(0.0, (flow_in - flow_out) / max(flow_in, 1.0))
        flow_loss_norm = self._sigmoid_membership(flow_loss_ratio, center=0.10, k=10.0)
        ecd_norm = self._sigmoid_membership(ecd / 13.0, center=0.85, k=6.0)

        active_vec = [torque_norm, rop_drop_norm, flow_loss_norm, ecd_norm]
        active_area = self._calculate_cobweb_area(active_vec)

        ranked_matches = []
        for case in self.cases:
            s = case["symptoms"]
            case_vec = [s["torque_norm"], s["rop_drop_norm"], s["flow_loss_norm"], s["ecd_norm"]]
            case_area = self._calculate_cobweb_area(case_vec)

            # Intersection / Union cobweb area ratio
            min_vec = [min(a, b) for a, b in zip(active_vec, case_vec)]
            max_vec = [max(a, b) for a, b in zip(active_vec, case_vec)]

            overlap_area = self._calculate_cobweb_area(min_vec)
            union_area = self._calculate_cobweb_area(max_vec)

            similarity = (overlap_area / max(union_area, 1e-6)) * 100
            similarity = min(98.5, max(15.0, similarity))

            ranked_matches.append({
                "case_id": case["case_id"],
                "well_name": case["well_name"],
                "incident_type": case["incident_type"],
                "similarity_score_pct": round(similarity, 1),
                "solution": case["solution"],
                "provenance": case["provenance"],
                "success_rate_pct": case["success_rate_pct"]
            })

        # Sort descending by similarity score
        ranked_matches.sort(key=lambda x: x["similarity_score_pct"], reverse=True)
        top_match = ranked_matches[0]

        return {
            "top_match": top_match,
            "all_ranked_cases": ranked_matches,
            "active_symptom_cobweb": {
                "Torque": round(torque_norm, 2),
                "ROP Drop": round(rop_drop_norm, 2),
                "Flow Loss": round(flow_loss_norm, 2),
                "ECD Overpressure": round(ecd_norm, 2)
            }
        }
