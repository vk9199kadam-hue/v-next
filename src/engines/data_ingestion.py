import os
import io
import re
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from pypdf import PdfReader
from src.utils.config import BASE_DIR

class DataIngestionPipeline:
    """
    Phase 1: Ingestion and processing engine for:
    1. Unstructured documents (WCR/DDR PDFs and text logs into Vector RAG)
    2. Structured spreadsheets (Offset well registers and trajectories into DuckDB)
    3. eRTMAC Telemetry stream calibrator and baseline tuner
    """

    @staticmethod
    def process_unstructured_document(
        file_bytes: bytes,
        filename: str,
        well_id: str,
        formation: str,
        vector_engine
    ) -> Dict[str, Any]:
        """
        Extracts, analyzes, chunks, and indexes an uploaded PDF or TXT report into Vector RAG.
        """
        extracted_text = ""
        total_pages = 1

        if filename.lower().endswith(".pdf"):
            reader = PdfReader(io.BytesIO(file_bytes))
            total_pages = len(reader.pages)
            for page in reader.pages:
                extracted_text += (page.extract_text() or "") + "\n\n"
        else:
            extracted_text = file_bytes.decode("utf-8", errors="ignore")

        # Entity & Hazard Detection
        hazard_keywords = [
            "stuck pipe", "lost circulation", "mud loss", "kick",
            "tight hole", "overpull", "packoff", "torque spike",
            "back-ream", "high-vis pill", "lcm pill", "fishing"
        ]
        detected_hazards = []
        for kw in hazard_keywords:
            matches = len(re.findall(re.escape(kw), extracted_text, re.IGNORECASE))
            if matches > 0:
                detected_hazards.append(f"{kw.title()} ({matches}x)")

        # Save to disk for persistence
        save_path = BASE_DIR / "data" / "historical_reports" / filename
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        # Index into Vector RAG
        chunks_added = vector_engine.add_document_content(
            text=extracted_text,
            well_id=well_id,
            formation=formation,
            filename=filename
        )

        word_count = len(extracted_text.split())

        return {
            "filename": filename,
            "well_id": well_id,
            "formation": formation,
            "total_pages": total_pages,
            "word_count": word_count,
            "chunks_added": chunks_added,
            "detected_hazards": detected_hazards or ["None detected (Normal Drilling Log)"],
            "status": "SUCCESS"
        }

    @staticmethod
    def process_structured_wells_csv(
        file_bytes: bytes,
        filename: str,
        vectorless_engine
    ) -> Dict[str, Any]:
        """
        Validates, normalizes, and syncs an uploaded Offset Wells spreadsheet into DuckDB.
        """
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
        else:
            df = pd.read_excel(io.BytesIO(file_bytes))

        # Standardize column names
        col_map = {}
        for col in df.columns:
            clean_col = col.lower().strip()
            if clean_col in ["well_id", "wellid", "well"]:
                col_map[col] = "well_id"
            elif clean_col in ["well_name", "wellname", "name"]:
                col_map[col] = "well_name"
            elif clean_col in ["lat", "latitude", "y"]:
                col_map[col] = "lat"
            elif clean_col in ["lon", "longitude", "long", "x"]:
                col_map[col] = "lon"
            elif clean_col in ["total_depth_m", "td", "depth", "total_depth"]:
                col_map[col] = "total_depth_m"
            elif clean_col in ["spud_year", "year", "spud_date"]:
                col_map[col] = "spud_year"
            elif clean_col in ["field", "area", "block"]:
                col_map[col] = "field"
            elif clean_col in ["status", "well_status", "condition"]:
                col_map[col] = "status"

        df = df.rename(columns=col_map)
        required = ["well_id", "well_name", "lat", "lon"]
        for req in required:
            if req not in df.columns:
                raise ValueError(f"Missing required column: '{req}'. Detected columns: {list(df.columns)}")

        # Fill default values if missing
        if "total_depth_m" not in df.columns:
            df["total_depth_m"] = 3800.0
        if "spud_year" not in df.columns:
            df["spud_year"] = 2024
        if "field" not in df.columns:
            df["field"] = "Naharkatiya"
        if "status" not in df.columns:
            df["status"] = "Active Offset Log"

        added_count = 0
        for _, row in df.iterrows():
            try:
                vectorless_engine.add_offset_well(
                    well_id=str(row["well_id"]),
                    well_name=str(row["well_name"]),
                    lat=float(row["lat"]),
                    lon=float(row["lon"]),
                    total_depth_m=float(row["total_depth_m"]),
                    spud_year=int(row["spud_year"]),
                    field=str(row["field"]),
                    status=str(row["status"])
                )
                added_count += 1
            except Exception:
                pass

        # Append to CSV file on disk for persistence
        save_csv_path = BASE_DIR / "data" / "structured" / "offset_wells_master.csv"
        if save_csv_path.exists():
            existing_df = pd.read_csv(save_csv_path)
            combined_df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates(subset=["well_id"])
            combined_df.to_csv(save_csv_path, index=False)

        return {
            "filename": filename,
            "rows_processed": len(df),
            "wells_added": added_count,
            "preview": df[["well_id", "well_name", "lat", "lon"]].head(5).to_dict(orient="records"),
            "status": "SUCCESS"
        }
