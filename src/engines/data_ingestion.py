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
    1. Unstructured documents (WCR/DDR PDFs and text logs into Vector RAG with Deep NLP)
    2. Structured spreadsheets (Offset well registers and trajectories into DuckDB)
    3. eRTMAC Telemetry stream calibrator and baseline tuner
    """

    DRILLER_LEXICON_MAP = {
        r"\bdrlg\b": "drilling",
        r"\bdrld\b": "drilled",
        r"\bdrl\b": "drill",
        r"\bcsg\b": "casing",
        r"\bbha\b": "bottom_hole_assembly",
        r"\bassy\b": "assembly",
        r"\bmtvd\b": "true_vertical_depth",
        r"\bmmd\b": "measured_depth",
        r"\bwob\b": "weight_on_bit",
        r"\bspp\b": "standpipe_pressure",
        r"\bppg\b": "pounds_per_gallon",
        r"\blcm\b": "lost_circulation_material",
        r"\bpooh\b": "pull_out_of_hole",
        r"\brih\b": "run_in_hole",
        r"\brpm\b": "rotations_per_minute",
        r"\bgpm\b": "gallons_per_minute",
        r"\bknm\b": "kilonewton_meters",
        r"\bkn\b": "kilonewtons"
    }

    @classmethod
    def clean_and_denoise_text(cls, raw_text: str) -> str:
        """RegEx cleaning layer to purge formatting noise, non-ASCII symbols, and normalize units."""
        # Remove non-ASCII characters
        text = re.sub(r"[^\x00-\x7F]+", " ", raw_text)
        # Normalize fractional inches (e.g. 8-1/2" -> 8.5 inch)
        text = re.sub(r'(\d+)-1/2"', r"\1.5 inch", text)
        text = re.sub(r'(\d+)-1/4"', r"\1.25 inch", text)
        text = re.sub(r'(\d+)-3/4"', r"\1.75 inch", text)
        # Normalize whitespace
        text = re.sub(r"[\r\n\t]+", " ", text)
        text = re.sub(r"\s{2,}", " ", text)
        return text.strip()

    @classmethod
    def expand_driller_shorthand(cls, text: str) -> str:
        """Expands oilfield shorthand abbreviations into standardized technical vocabulary."""
        expanded = text
        for pattern, replacement in cls.DRILLER_LEXICON_MAP.items():
            expanded = re.sub(pattern, replacement, expanded, flags=re.IGNORECASE)
        return expanded

    @classmethod
    def extract_numerical_entities(cls, text: str) -> List[Dict[str, Any]]:
        """Extracts structured drilling parameters alongside their physical units."""
        patterns = [
            ("Depth", r"(\d+\.?\d*)\s*(m|meters|ft|feet|mTVD|mMD)"),
            ("Mud Weight", r"(\d+\.?\d*)\s*(ppg|sg|specific gravity|kg/m3)"),
            ("Flow Rate", r"(\d+\.?\d*)\s*(gpm|lpm|bph|m3/hr)"),
            ("WOB", r"(\d+\.?\d*)\s*(klbs|kn|tons|tonne)"),
            ("Torque", r"(\d+\.?\d*)\s*(knm|ft-lbs|kft-lb)"),
            ("SPP", r"(\d+\.?\d*)\s*(psi|bar|kpa)")
        ]
        entities = []
        for param, pat in patterns:
            matches = re.findall(pat, text, re.IGNORECASE)
            for val, unit in matches[:3]: # Cap at top 3 per parameter
                entities.append({"parameter": param, "value": float(val), "unit": unit})
        return entities

    @classmethod
    def mine_event_symptom_action(cls, text: str) -> Dict[str, List[str]]:
        """
        Classifies sentences in historical narrative into EVENT, SYMPTOM, and ACTION sequences.
        """
        sentences = re.split(r"[.!?]\s+", text)
        events = []
        symptoms = []
        actions = []

        for s in sentences:
            s_clean = s.strip()
            if not s_clean:
                continue
            lower = s_clean.lower()
            if any(k in lower for k in ["stuck pipe", "lost circulation", "blowout", "gas kick", "tight hole", "packoff"]):
                events.append(s_clean[:140])
            elif any(k in lower for k in ["torque spike", "pressure drop", "gain in pit", "plunge in rop", "erratic"]):
                symptoms.append(s_clean[:140])
            elif any(k in lower for k in ["spot", "pill", "ream", "jar", "weight up", "circulate", "squeeze", "cement"]):
                actions.append(s_clean[:140])

        return {
            "events": events[:3],
            "symptoms": symptoms[:3],
            "actions": actions[:3]
        }

    @classmethod
    def process_unstructured_document(
        cls,
        file_bytes: bytes,
        filename: str,
        well_id: str,
        formation: str,
        vector_engine
    ) -> Dict[str, Any]:
        """
        Extracts, denoises, expands driller shorthand, and indexes into Vector RAG.
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

        # 1. RegEx Denoising & Cleaning
        cleaned_text = cls.clean_and_denoise_text(extracted_text)

        # 2. Expand Driller Shorthand
        canonical_text = cls.expand_driller_shorthand(cleaned_text)

        # 3. Extract Numerical Entities & Parameters
        entities = cls.extract_numerical_entities(canonical_text)

        # 4. Mine Event-Symptom-Action Sequences
        esa_sequences = cls.mine_event_symptom_action(canonical_text)

        # 5. Entity & Hazard Detection
        hazard_keywords = [
            "stuck pipe", "lost circulation", "mud loss", "kick",
            "tight hole", "overpull", "packoff", "torque spike",
            "back-ream", "high-vis pill", "lcm pill", "fishing"
        ]
        detected_hazards = []
        for kw in hazard_keywords:
            matches = len(re.findall(re.escape(kw), canonical_text, re.IGNORECASE))
            if matches > 0:
                detected_hazards.append(f"{kw.title()} ({matches}x)")

        # Save raw to disk for persistence
        save_path = BASE_DIR / "data" / "historical_reports" / filename
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        # Index canonical text into Vector RAG
        chunks_added = vector_engine.add_document_content(
            text=canonical_text,
            well_id=well_id,
            formation=formation,
            filename=filename
        )

        word_count = len(canonical_text.split())

        return {
            "filename": filename,
            "well_id": well_id,
            "formation": formation,
            "total_pages": total_pages,
            "word_count": word_count,
            "chunks_added": chunks_added,
            "detected_hazards": detected_hazards or ["None detected (Normal Drilling Log)"],
            "numerical_entities_extracted": len(entities),
            "sample_entities": entities[:4],
            "event_symptom_action_sequences": esa_sequences,
            "shorthand_canonicalized": True,
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
