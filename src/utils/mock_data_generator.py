import os
from pathlib import Path
import pandas as pd

def generate_mock_datasets(base_path: str = "."):
    base_dir = Path(base_path)
    structured_dir = base_dir / "data" / "structured"
    historical_dir = base_dir / "data" / "historical_reports"
    telemetry_dir = base_dir / "data" / "telemetry"

    structured_dir.mkdir(parents=True, exist_ok=True)
    historical_dir.mkdir(parents=True, exist_ok=True)
    telemetry_dir.mkdir(parents=True, exist_ok=True)

    # 1. Offset Wells Master (Naharkatiya / Moran / Kumchai fields in Assam)
    offset_wells = pd.DataFrame([
        {
            "well_id": "OIL-NH-18",
            "well_name": "Naharkatiya-18",
            "lat": 27.3010,
            "lon": 95.3620,
            "total_depth_m": 4100.0,
            "spud_year": 2021,
            "field": "Naharkatiya",
            "status": "Stuck Pipe Incident (Resolved)",
            "primary_target": "Barail Sandstone"
        },
        {
            "well_id": "OIL-NH-12",
            "well_name": "Naharkatiya-12",
            "lat": 27.2850,
            "lon": 95.3350,
            "total_depth_m": 3950.0,
            "spud_year": 2019,
            "field": "Naharkatiya",
            "status": "Tight Hole / Overpressure (Resolved)",
            "primary_target": "Barail Sandstone"
        },
        {
            "well_id": "OIL-KGT-04",
            "well_name": "Kumchai-04",
            "lat": 27.3150,
            "lon": 95.3200,
            "total_depth_m": 3720.0,
            "spud_year": 2020,
            "field": "Kumchai",
            "status": "Severe Mud Loss Zone (Controlled)",
            "primary_target": "Barail Sandstone"
        },
        {
            "well_id": "OIL-MOR-07",
            "well_name": "Moran-07",
            "lat": 27.2600,
            "lon": 95.3700,
            "total_depth_m": 4200.0,
            "spud_year": 2023,
            "field": "Moran",
            "status": "Normal Production",
            "primary_target": "Tipam Sandstone"
        },
        {
            "well_id": "OIL-DGN-02",
            "well_name": "Dikom-02",
            "lat": 27.3300,
            "lon": 95.3850,
            "total_depth_m": 3650.0,
            "spud_year": 2022,
            "field": "Dikom",
            "status": "Gas Kick Encountered (Controlled)",
            "primary_target": "Barail Sandstone"
        }
    ])
    offset_wells.to_csv(structured_dir / "offset_wells_master.csv", index=False)

    # 2. Lithology & Formation Tops
    lithology = pd.DataFrame([
        {"well_id": "OIL-NH-18", "formation_name": "Alluvium / Dhekiajuli", "top_depth_m": 0, "base_depth_m": 850},
        {"well_id": "OIL-NH-18", "formation_name": "Tipam Sandstone", "top_depth_m": 850, "base_depth_m": 2200},
        {"well_id": "OIL-NH-18", "formation_name": "Surma / Bokabil Shale", "top_depth_m": 2200, "base_depth_m": 2750},
        {"well_id": "OIL-NH-18", "formation_name": "Barail Sandstone", "top_depth_m": 2750, "base_depth_m": 3200},
        
        {"well_id": "OIL-NH-12", "formation_name": "Tipam Sandstone", "top_depth_m": 820, "base_depth_m": 2180},
        {"well_id": "OIL-NH-12", "formation_name": "Surma / Bokabil Shale", "top_depth_m": 2180, "base_depth_m": 2730},
        {"well_id": "OIL-NH-12", "formation_name": "Barail Sandstone", "top_depth_m": 2730, "base_depth_m": 3150},

        {"well_id": "OIL-KGT-04", "formation_name": "Tipam Sandstone", "top_depth_m": 900, "base_depth_m": 2250},
        {"well_id": "OIL-KGT-04", "formation_name": "Surma / Bokabil Shale", "top_depth_m": 2250, "base_depth_m": 2780},
        {"well_id": "OIL-KGT-04", "formation_name": "Barail Sandstone", "top_depth_m": 2780, "base_depth_m": 3220}
    ])
    lithology.to_csv(structured_dir / "lithology_formations.csv", index=False)

    # 3. Casing & Cementing Records
    casing = pd.DataFrame([
        {"well_id": "OIL-NH-18", "casing_stage": "Surface", "casing_size_inch": "13-3/8", "shoe_depth_m": 950.0, "burst_psi": 3450, "shoe_lot_ppg": 13.5},
        {"well_id": "OIL-NH-18", "casing_stage": "Intermediate", "casing_size_inch": "9-5/8", "shoe_depth_m": 2600.0, "burst_psi": 4850, "shoe_lot_ppg": 12.8},
        {"well_id": "OIL-NH-18", "casing_stage": "Production Liner", "casing_size_inch": "7", "shoe_depth_m": 3650.0, "burst_psi": 6200, "shoe_lot_ppg": 14.2},
        
        {"well_id": "OIL-NH-12", "casing_stage": "Intermediate", "casing_size_inch": "9-5/8", "shoe_depth_m": 2580.0, "burst_psi": 4850, "shoe_lot_ppg": 12.7},
        {"well_id": "OIL-KGT-04", "casing_stage": "Intermediate", "casing_size_inch": "9-5/8", "shoe_depth_m": 2620.0, "burst_psi": 4900, "shoe_lot_ppg": 12.6}
    ])
    casing.to_csv(structured_dir / "casing_programs.csv", index=False)

    # 4. Historical NPT Events (Non-Productive Time)
    npt_events = pd.DataFrame([
        {
            "event_id": "EVT-2021-NH18-01",
            "well_id": "OIL-NH-18",
            "well_name": "Naharkatiya-18",
            "depth_m": 2847.0,
            "formation": "Barail Sandstone",
            "event_type": "Stuck Pipe",
            "severity": "CRITICAL_HIGH",
            "npt_hours": 18.5,
            "description": "Gradual torque buildup from 18 to 31 kNm followed by complete rotational lockup (mechanical differential sticking) due to micro-fractured reactive shale bands.",
            "mitigation": "Back-reamed 50m upward with 35 RPM, pumped 40 bbl high-viscosity bentonite pill with lubricant, verified returns, and resumed controlled drilling."
        },
        {
            "event_id": "EVT-2020-KGT04-01",
            "well_id": "OIL-KGT-04",
            "well_name": "Kumchai-04",
            "depth_m": 2890.0,
            "formation": "Barail Sandstone",
            "event_type": "Lost Circulation",
            "severity": "CRITICAL_HIGH",
            "npt_hours": 24.0,
            "description": "Encountered depleted sandstone sub-layer at 2,890m. Total mud loss of 220 bbl within 45 minutes when mud weight exceeded 12.2 ppg.",
            "mitigation": "Spotted 35 bbl coarse LCM pill (Mica flakes + Nut plug), reduced mud weight from 12.4 to 11.7 ppg, reduced pump discharge to 320 gpm."
        },
        {
            "event_id": "EVT-2019-NH12-01",
            "well_id": "OIL-NH-12",
            "well_name": "Naharkatiya-12",
            "depth_m": 2920.0,
            "formation": "Barail Sandstone",
            "event_type": "Tight Hole / Drag",
            "severity": "MEDIUM",
            "npt_hours": 6.5,
            "description": "Overpull of 45,000 lbs noticed during connection. Excessive cuttings accumulation and sloughing shale in Barail formation.",
            "mitigation": "Short trip of 150m to last casing shoe, increased flow rate by 12% to enhance annular cuttings velocity."
        }
    ])
    npt_events.to_csv(structured_dir / "npt_events.csv", index=False)

    # 5. Historical Unstructured Incident Reports (Simulated WCR/DDR text documents)
    report_nh18 = """
OIL INDIA LIMITED - WELL COMPLETION REPORT (WCR)
WELL: Naharkatiya-18 (OIL-NH-18) | YEAR: 2021 | FIELD: Naharkatiya, Assam
SECTION: Drilling Hazards & NPT Incident Log (Page 34)

Incident Summary:
At depth 2,847.0 meters TVD within the Barail Sandstone formation, the rig encountered severe erratic torque fluctuations spiking from 18.2 kNm to 31.4 kNm over a 12-minute interval. Simultaneous ROP dropped from 5.4 m/hr to 0.7 m/hr. 

Root Cause Analysis:
Micro-fractured reactive carbonaceous shale interbeds sloughed into the wellbore, causing severe bit balling and differential mechanical sticking of the bottom hole assembly (BHA).

Mitigation Procedure Implemented:
1. Did NOT apply maximum overpull to prevent parted drill string.
2. Engaged top drive at 35-40 RPM and carefully back-reamed 50 meters back to 2,797 meters.
3. Pumped a 40 bbl weighted high-viscosity pill treated with 4% liquid lubricant to free the stabilizer.
4. Circulated bottoms up for two complete cycles until shale cavings cleared over shaker screens.
5. Successfully resumed drilling at 2,847 meters with zero pipe loss. Total NPT was restricted to 4.5 hours.
Recommendation for offset wells: Always maintain high flow rates and prepare high-vis pill in advance when drilling between 2,800m and 2,900m in Barail Sandstone.
"""

    report_kgt04 = """
OIL INDIA LIMITED - DAILY DRILLING REPORT & LOSS REPORT
WELL: Kumchai-04 (OIL-KGT-04) | YEAR: 2020 | FIELD: Kumchai, Arunachal / Assam Foothills
SECTION: Lost Circulation Event Report (Page 67)

Incident Summary:
At depth 2,890.0 meters TVD, drill bit penetrated a sub-pressured permeable Barail sand interval. Active pit volume dropped by 180 barrels within 35 minutes. Return flow was reduced to 35% of pump-in volume.

Critical Constraint:
The intermediate 9-5/8 inch casing shoe at 2,620 meters has a leak-off test equivalent mud weight of 12.6 ppg. Attempting to overcome pore pressure by increasing mud weight above 12.1 ppg resulted in immediate hydraulic fracture of the formation.

Mitigation Executed:
1. Suspended forward drilling immediately.
2. Mixed and spotted a 30 bbl medium-grade LCM pill containing 25 ppb mica and shredded nut shells.
3. Allowed 2 hours soak time with low pump strokes (18 SPM).
4. Restored full mud returns and drilled ahead with 11.6 ppg mud weight.
Recommendation: Never exceed 11.9 ppg mud weight in this sub-zone; casing burst margin and fracture gradient are extremely narrow.
"""

    report_nh12 = """
OIL INDIA LIMITED - WELLSITE LESSONS LEARNED COMPENDIUM
WELL: Naharkatiya-12 (OIL-NH-12) | YEAR: 2019
SECTION: Hole Cleaning & Drag Management in Barail Sandstone (Page 42)

Lessons Learned:
Hole angle reached 28 degrees inclination at 2,920 meters. High drag on connections occurred due to cuttings beds accumulation on the low side of the hole. Short wiper trips every 120 meters and high-flow sweeping pills completely eliminated the tight hole tendencies.
"""

    with open(historical_dir / "OIL_NH18_WCR_2021.txt", "w") as f:
        f.write(report_nh18)

    with open(historical_dir / "OIL_KGT04_MudLoss_Report.txt", "w") as f:
        f.write(report_kgt04)

    with open(historical_dir / "OIL_NH12_WCR_2019.txt", "w") as f:
        f.write(report_nh12)

    # 6. eRTMAC Telemetry Stream Simulation (Normal drilling -> Gradual Drag -> 2:05 PM Torque Spike)
    stream_data = [
        {"timestamp": "14:00:00", "depth_m": 2842.5, "wob_kn": 120.0, "torque_knm": 17.5, "rop_mph": 6.8, "rpm": 110, "ecd_ppg": 12.10, "flow_in_gpm": 520, "flow_out_gpm": 520, "pressure_psi": 2820},
        {"timestamp": "14:02:00", "depth_m": 2844.0, "wob_kn": 122.0, "torque_knm": 18.2, "rop_mph": 6.1, "rpm": 110, "ecd_ppg": 12.12, "flow_in_gpm": 520, "flow_out_gpm": 519, "pressure_psi": 2835},
        {"timestamp": "14:04:00", "depth_m": 2845.5, "wob_kn": 128.0, "torque_knm": 22.8, "rop_mph": 4.2, "rpm": 105, "ecd_ppg": 12.20, "flow_in_gpm": 520, "flow_out_gpm": 517, "pressure_psi": 2890},
        {"timestamp": "14:05:00", "depth_m": 2847.0, "wob_kn": 135.0, "torque_knm": 31.2, "rop_mph": 0.8, "rpm": 75, "ecd_ppg": 12.45, "flow_in_gpm": 520, "flow_out_gpm": 515, "pressure_psi": 3050}
    ]
    pd.DataFrame(stream_data).to_csv(telemetry_dir / "active_well_stream.csv", index=False)
    print("✅ All realistic Oil India datasets created successfully.")

if __name__ == "__main__":
    generate_mock_datasets()
