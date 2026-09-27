import os
from pathlib import Path
import duckdb
import pandas as pd
from typing import Dict, Any
from src.utils.config import BASE_DIR

class VectorlessRAGEngine:
    """
    Executes relational SQL analytics, depth-formation correlation, and
    geospatial Haversine proximity calculations over structured oilfield data.
    """
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = str(BASE_DIR / "data" / "structured")
        self.con = duckdb.connect(database=":memory:")
        
        # Ingest CSVs into fast in-memory analytical tables
        self.con.execute(f"CREATE TABLE offset_wells AS SELECT * FROM read_csv_auto('{data_dir}/offset_wells_master.csv');")
        self.con.execute(f"CREATE TABLE lithology AS SELECT * FROM read_csv_auto('{data_dir}/lithology_formations.csv');")
        self.con.execute(f"CREATE TABLE casing AS SELECT * FROM read_csv_auto('{data_dir}/casing_programs.csv');")
        self.con.execute(f"CREATE TABLE npt_events AS SELECT * FROM read_csv_auto('{data_dir}/npt_events.csv');")

    def get_nearby_wells(self, active_lat: float, active_lon: float, radius_km: float = 10.0) -> pd.DataFrame:
        query = f"""
        SELECT 
            well_id, 
            well_name, 
            lat, 
            lon, 
            total_depth_m, 
            spud_year, 
            field, 
            status,
            ROUND(2 * 6371 * asin(sqrt(
                power(sin(radians((lat - {active_lat}) / 2)), 2) +
                cos(radians({active_lat})) * cos(radians(lat)) *
                power(sin(radians((lon - {active_lon}) / 2)), 2)
            )), 2) AS distance_km
        FROM offset_wells
        WHERE ROUND(2 * 6371 * asin(sqrt(
                power(sin(radians((lat - {active_lat}) / 2)), 2) +
                cos(radians({active_lat})) * cos(radians(lat)) *
                power(sin(radians((lon - {active_lon}) / 2)), 2)
            )), 2) <= {radius_km}
        ORDER BY distance_km ASC;
        """
        return self.con.execute(query).df()

    def correlate_depth_formation(self, active_lat: float, active_lon: float, current_depth: float, formation_name: str, radius_km: float = 10.0) -> pd.DataFrame:
        query = f"""
        WITH nearby AS (
            SELECT 
                well_id, 
                well_name,
                ROUND(2 * 6371 * asin(sqrt(
                    power(sin(radians((lat - {active_lat}) / 2)), 2) +
                    cos(radians({active_lat})) * cos(radians(lat)) *
                    power(sin(radians((lon - {active_lon}) / 2)), 2)
                )), 2) AS distance_km
            FROM offset_wells
            WHERE ROUND(2 * 6371 * asin(sqrt(
                    power(sin(radians((lat - {active_lat}) / 2)), 2) +
                    cos(radians({active_lat})) * cos(radians(lat)) *
                    power(sin(radians((lon - {active_lon}) / 2)), 2)
                )), 2) <= {radius_km}
        )
        SELECT 
            n.well_name,
            n.distance_km,
            l.formation_name,
            l.top_depth_m,
            l.base_depth_m,
            c.casing_size_inch,
            c.shoe_depth_m,
            c.shoe_lot_ppg,
            e.event_type,
            e.severity,
            e.mitigation
        FROM nearby n
        JOIN lithology l ON n.well_id = l.well_id
        LEFT JOIN casing c ON n.well_id = c.well_id AND c.casing_stage = 'Intermediate'
        LEFT JOIN npt_events e ON n.well_id = e.well_id AND e.depth_m BETWEEN l.top_depth_m AND l.base_depth_m
        WHERE l.formation_name = '{formation_name}'
        ORDER BY n.distance_km ASC;
        """
        return self.con.execute(query).df()

    def add_offset_well(self, well_id: str, well_name: str, lat: float, lon: float, total_depth_m: float, spud_year: int, field: str, status: str):
        """
        Inserts a newly uploaded/registered offset well directly into DuckDB.
        """
        query = f"""
        INSERT INTO offset_wells VALUES (
            '{well_id}', '{well_name}', {lat}, {lon}, {total_depth_m}, {spud_year}, '{field}', '{status}', 'Barail Sandstone'
        );
        """
        self.con.execute(query)
