"""
Directional Surveying & Minimum Curvature Engine (API RP 7G)
eRTMAC-NWIS | Oil India Limited (OIL)

Converts Measured Depth (MD) to True Vertical Depth (TVD), North, East coordinates,
and calculates Dogleg Severity (DLS) and Stratigraphic Horizon Dip Alignment.
"""

import math
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple


class DirectionalSurveyEngine:
    """
    Computes 3D wellbore trajectory coordinates using the industry-standard
    Minimum Curvature Method (API RP 7G).
    """

    @staticmethod
    def calculate_minimum_curvature(surveys: List[Dict[str, float]]) -> pd.DataFrame:
        """
        Takes a list of survey stations: [{"md": float, "inc_deg": float, "azi_deg": float}]
        Returns DataFrame with [md, inc_deg, azi_deg, tvd, north, east, dls_deg_30m, disp_m]
        """
        if not surveys:
            return pd.DataFrame()

        df = pd.DataFrame(surveys).sort_values("md").reset_index(drop=True)
        n = len(df)

        tvd = np.zeros(n)
        north = np.zeros(n)
        east = np.zeros(n)
        dls = np.zeros(n)

        # Station 0 is at surface (RKB = 0, 0, 0)
        for i in range(1, n):
            md1 = df.loc[i - 1, "md"]
            inc1 = math.radians(df.loc[i - 1, "inc_deg"])
            azi1 = math.radians(df.loc[i - 1, "azi_deg"])

            md2 = df.loc[i, "md"]
            inc2 = math.radians(df.loc[i, "inc_deg"])
            azi2 = math.radians(df.loc[i, "azi_deg"])

            delta_md = md2 - md1
            if delta_md <= 0:
                tvd[i] = tvd[i - 1]
                north[i] = north[i - 1]
                east[i] = east[i - 1]
                continue

            # Dogleg angle (beta)
            cos_beta = math.cos(inc2 - inc1) - (math.sin(inc1) * math.sin(inc2) * (1.0 - math.cos(azi2 - azi1)))
            cos_beta = max(-1.0, min(1.0, cos_beta))
            beta = math.acos(cos_beta)

            # Ratio factor (RF)
            if abs(beta) < 1e-6:
                rf = 1.0
            else:
                rf = (2.0 / beta) * math.tan(beta / 2.0)

            # Incremental displacements
            delta_tvd = (delta_md / 2.0) * (math.cos(inc1) + math.cos(inc2)) * rf
            delta_north = (delta_md / 2.0) * (math.sin(inc1) * math.cos(azi1) + math.sin(inc2) * math.cos(azi2)) * rf
            delta_east = (delta_md / 2.0) * (math.sin(inc1) * math.sin(azi1) + math.sin(inc2) * math.sin(azi2)) * rf

            tvd[i] = tvd[i - 1] + delta_tvd
            north[i] = north[i - 1] + delta_north
            east[i] = east[i - 1] + delta_east

            # Dogleg severity per 30m
            dls[i] = (math.degrees(beta) / delta_md) * 30.0 if delta_md > 0 else 0.0

        df["tvd"] = np.round(tvd, 2)
        df["north"] = np.round(north, 2)
        df["east"] = np.round(east, 2)
        df["disp_m"] = np.round(np.sqrt(north**2 + east**2), 2)
        df["dls_deg_30m"] = np.round(dls, 2)
        return df

    @classmethod
    def generate_synthetic_active_trajectory(cls, target_md: float = 2847.2) -> pd.DataFrame:
        """
        Builds a realistic "S-Type / J-Type" directional trajectory for active well Naharkatiya-24:
        - Vertical to Kickoff Point (KOP = 1200m)
        - Build section to 28° inclination at 1800m
        - Hold section to 2847.2m MD
        """
        stations = [
            {"md": 0.0, "inc_deg": 0.0, "azi_deg": 45.0},
            {"md": 600.0, "inc_deg": 0.0, "azi_deg": 45.0},
            {"md": 1200.0, "inc_deg": 0.0, "azi_deg": 45.0},   # KOP
            {"md": 1400.0, "inc_deg": 9.2, "azi_deg": 48.0},
            {"md": 1600.0, "inc_deg": 18.5, "azi_deg": 50.0},
            {"md": 1800.0, "inc_deg": 28.0, "azi_deg": 52.0},  # End of Build
            {"md": 2200.0, "inc_deg": 28.0, "azi_deg": 52.0},
            {"md": 2600.0, "inc_deg": 27.8, "azi_deg": 52.5},
            {"md": target_md, "inc_deg": 27.5, "azi_deg": 52.5}
        ]
        return cls.calculate_minimum_curvature(stations)

    @classmethod
    def generate_offset_trajectories(cls, offsets: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
        """
        Generates 3D spatial paths for offset wells relative to active rig origin.
        """
        trajectories = {}
        for off in offsets:
            w_id = off["well_id"]
            # Convert offset lat/lon delta to approximate North/East meters (1 deg lat ~ 111,000m)
            ref_lat = 27.3000
            ref_lon = 95.3500
            delta_n = (off["lat"] - ref_lat) * 111000.0
            delta_e = (off["lon"] - ref_lon) * 111000.0 * math.cos(math.radians(ref_lat))
            td = float(off.get("total_depth_m", 3800.0))

            # Vertical or slightly deviated offset
            inc = 3.5 if "NH" in w_id else (14.0 if "KGT" in w_id else 1.0)
            azi = 110.0 if "NH" in w_id else 220.0

            stations = [
                {"md": 0.0, "inc_deg": 0.0, "azi_deg": azi},
                {"md": td * 0.4, "inc_deg": inc * 0.5, "azi_deg": azi},
                {"md": td * 0.7, "inc_deg": inc, "azi_deg": azi},
                {"md": td, "inc_deg": inc, "azi_deg": azi}
            ]
            df = cls.calculate_minimum_curvature(stations)
            # Offset the surface location
            df["north"] += delta_n
            df["east"] += delta_e
            trajectories[w_id] = df

        return trajectories

    @staticmethod
    def get_stratigraphic_tvd_dip(distance_km: float, dip_angle_deg: float = 2.4) -> float:
        """
        Computes vertical formation shift due to regional structural dip.
        Upper Assam Brahmaputra shelf dip is typically 2° to 3.5° towards south-southeast.
        """
        dip_rad = math.radians(dip_angle_deg)
        vertical_shift_m = (distance_km * 1000.0) * math.tan(dip_rad)
        return round(vertical_shift_m, 1)
