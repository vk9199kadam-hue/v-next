# 🏗️ eRTMAC-NWIS: Upgraded Technical Architecture Diagram & Specification Report
**Project:** eRTMAC-NWIS (Nearby Wells Intelligence System)  
**Problem Statement ID:** SIH26121 | **Team ID:** 146366 | **Team Name:** SixBitss  
**Client / Domain:** Oil India Limited (OIL) — Upstream Drilling Intelligence  
**Format:** 1-to-1 Structural Mapping to Original Architecture Slide (Top 3 Pillars + Central Router + 6 Pipeline Blocks + Infrastructure Bar)

---

## Executive Summary: Old vs. New Architecture Comparison

The original architecture slide contained **generic big-data buzzwords** (*Apache Flink, Spark Streaming, Kafka, TimescaleDB, Feast, React/Next.js, LangGraph, CrewAI*) that did not reflect the real, tested mathematical models running in your prototype. 

The **New Technical Architecture** retains the exact visual layout and box hierarchy of your slide, but transforms every component into the **rig-tested, production-ready implementation** containing your high-value innovations:
1. **DuckDB In-Memory OLAP** (<5ms Haversine spatial SQL) replacing complex, slow databases.
2. **1D Discrete Kalman Filter** rejecting sensor noise (<5% false alarms) on high-frequency live streams.
3. **Deterministic Edge Safety Interlock** executing in **0.008 ms** (100% offline rig-floor safety).
4. **API RP 7G Minimum Curvature Method** with 2.4° SSE formation dip for sub-meter 3D trajectory tracking.
5. **Machine Learning Engines**: 5-Class Random Forest Fluid Loss (98% Acc) + SVM 4-State Driller Recognizer (>95% Acc) + Bourgoyne & Young ROP Optimizer (+14%).
6. **Dual-Role Interface**: High-contrast Rig Floor HUD + 9-Tab Superintendent Drilling Office Analytics with Plotly 3D interactive wellbore visualizer.

---

## 🖼️ Architecture Diagram (Mermaid Layout Matching Your Slide)

```mermaid
flowchart TD
    %% Styling Classes
    classDef unstructured fill:#fdebd0,stroke:#d35400,stroke-width:2px,color:#111;
    classDef structured fill:#d4efdf,stroke:#27ae60,stroke-width:2px,color:#111;
    classDef telemetry fill:#d6eaf8,stroke:#2980b9,stroke-width:2px,color:#111;
    classDef centerLayer fill:#e8daef,stroke:#8e44ad,stroke-width:3px,color:#111;
    classDef flow1 fill:#a3e4d7,stroke:#16a085,stroke-width:2px,color:#111;
    classDef flow2 fill:#aed6f1,stroke:#2980b9,stroke-width:2px,color:#111;
    classDef flow3 fill:#f9e79f,stroke:#f39c12,stroke-width:2px,color:#111;
    classDef flow4 fill:#f5b7b1,stroke:#c0392b,stroke-width:2px,color:#111;
    classDef flow5 fill:#d7bde2,stroke:#8e44ad,stroke-width:2px,color:#111;
    classDef flow6 fill:#abebc6,stroke:#27ae60,stroke-width:2px,color:#111;
    classDef infra fill:#eaeded,stroke:#7f8c8d,stroke-width:2px,color:#111;

    %% Top Layer: 3 Data Ingestion & Storage Pillars
    subgraph TOP_PILLARS ["DATA INGESTION & KNOWLEDGE PREPARATION (PHASE 1)"]
        subgraph COL1 ["Unstructured Data (Deep NLP & Vector RAG)"]
            P1_1["Parsing & RegEx: PyPDF, Tesseract, RegEx Denoising"]
            P1_2["Domain Normalizer: Driller Shorthand drlg, csg, bha, mTVD"]
            P1_3["Vector Engine: Sentence-Transformers (all-MiniLM-L6-v2), ChromaDB"]
        end
        class COL1,P1_1,P1_2,P1_3 unstructured;

        subgraph COL2 ["Structured Data (DuckDB Vectorless RAG)"]
            P2_1["Storage Engine: DuckDB In-Memory OLAP + Geo Extension + Parquet"]
            P2_2["Trajectory Math: API RP 7G Minimum Curvature (MD to TVD) + 2.4° Dip"]
            P2_3["Offset Retrieval: Haversine Spatial Indexing (sub-5ms, 10km Radius)"]
        end
        class COL2,P2_1,P2_2,P2_3 structured;

        subgraph COL3 ["eRTMAC Live Telemetry (Stream Processing & Edge Safety)"]
            P3_1["Stream Ingestion: WITSML / ASCII 0.5s Real-Time Poller"]
            P3_2["Signal Conditioning: 1D Discrete Kalman Filter (Noise Rejection <5% FA)"]
            P3_3["Microsecond Interlock: Edge Safety Rules Engine (0.008 ms Offline Failsafe)"]
        end
        class COL3,P3_1,P3_2,P3_3 telemetry;
    end

    %% Middle Layer: Unified Context Layer
    UNIFIED["Unified Operational Context Layer<br/><b>FastAPI ASGI Router + Context Synchronizer (Live Telemetry + 100m Lookahead Offset Window)</b>"]
    class UNIFIED centerLayer;

    COL1 --> UNIFIED
    COL2 --> UNIFIED
    COL3 --> UNIFIED

    %% Bottom Pipeline: 6 Sequential Stages
    subgraph BOTTOM_PIPELINE ["PHASE 2: REAL-TIME INFERENCE, AI REASONING & HUMAN-IN-THE-LOOP DECISION"]
        S1["<b>1. Query & Lookahead Intake</b><br/>Proactive 100m Depth Trigger +<br/>Driller Voice/Text Query"]
        S2["<b>2. Automated State & Lithology</b><br/>SVM 4-State Recognizer (>95%) +<br/>Geomechanics Window (R²=0.924)"]
        S3["<b>3. JEV & FCBR Reasoning</b><br/>Fuzzy Case-Based Reasoning +<br/>Cobweb Polygon Similarity Engine"]
        S4["<b>4. Risk & ROP ML Output</b><br/>5-Class Random Forest (98% Acc) +<br/>Bourgoyne & Young (+14% ROP)"]
        S5["<b>5. AVER Explainable LLM</b><br/>Groq LLaMA-3.3-70B / Qwen-27B +<br/>WCR Evidence Citations & 'Why'"]
        S6["<b>6. Dual-Role Dashboard</b><br/>Rig Floor HUD (3s Glanceable) &<br/>Office 3D Plotly Trajectory (9-Tab)"]
    end
    class S1 flow1;
    class S2 flow2;
    class S3 flow3;
    class S4 flow4;
    class S5 flow5;
    class S6 flow6;

    UNIFIED --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
    S5 --> S6
    UNIFIED -. Continuous Lookahead Data Sync .-> S3
    UNIFIED -. Offset History Reference .-> S5

    %% Cross-Cutting Infrastructure Bar
    subgraph INFRA ["Cross-Cutting Enterprise & Edge Infrastructure"]
        INFRA_TXT["<b>Backend:</b> Python 3.11+, FastAPI (ASGI), DuckDB, NumPy, Scikit-Learn | <b>Edge Deployment:</b> Standalone Rig-Edge Lightweight Wheel / Docker (100% Offline Capable)<br/><b>Security & Integrity:</b> Dual-Role RBAC (Driller vs Superintendent), Audit Logging, SHA-256 Telemetry Verification | <b>Testing & CI/CD:</b> Pytest Automated Test Suite & GitHub Actions"]
    end
    class INFRA,INFRA_TXT infra;

    BOTTOM_PIPELINE --- INFRA
```

---

## 📋 Exact Slide Box-by-Box Specification (Drop-in Slide Replacement)

You can copy and paste the following tables directly into your PowerPoint deck to replace the old blocks:

### 🟧 Top Row: 3 Data Ingestion & Knowledge Preparation Pillars

| Slide Box Title | Old Content (To Delete) | New Content (To Put In Slide) | Technical Justification |
| :--- | :--- | :--- | :--- |
| **Pillar 1: Unstructured Data (Deep NLP & Vector RAG)** | • Tesseract, Azure Doc Intelligence, spaCy<br>• LangChain, LlamaIndex, BGE/E5, OpenAI<br>• Qdrant, Pinecone, pgvector | **• NLP & Ingestion:** PyPDF, Tesseract OCR, RegEx Formatting Cleaner<br>**• Domain Normalizer:** Driller Shorthand Canonicalizer (`drlg`, `csg`, `bha`, `mTVD`)<br>**• Sequential Miner:** EVENT-SYMPTOM-ACTION Pattern Extraction<br>**• Vector Index:** Sentence-Transformers (`all-MiniLM-L6-v2`) + ChromaDB | Real drilling logs use extreme abbreviations and unstandardized syntax; our domain normalizer ensures 100% keyword match against historical WCRs. |
| **Pillar 2: Structured Data (Vectorless DuckDB RAG)** *(Fix typo: was Vectorlace)* | • PostgreSQL, PostGIS, Delta Lake<br>• SQL filters, pgvector semantic search<br>• PostGIS, Elasticsearch geo, Kepler.gl | **• Storage Engine:** In-Memory DuckDB OLAP + Geospatial Extension + Parquet<br>**• 3D Trajectory Math:** API RP 7G Minimum Curvature Method (MD $\rightarrow$ TVD conversion)<br>**• Structural Geology:** 2.4° SSE Stratigraphic Dip Adjustment<br>**• Offset Retrieval:** Sub-5ms Haversine Radial Search (<10 km offset cluster) | Replaced heavy Postgres/Elasticsearch clusters with DuckDB, which executes analytical spatial queries in **under 5 milliseconds** directly in-memory. |
| **Pillar 3: eRTMAC Live Data (Stream & Edge Safety)** | • WITSML/WITSO, Kafka, MQTT<br>• Apache Flink, Spark Structured Streaming<br>• TimescaleDB, InfluxDB, Redis, Feast | **• Stream Ingestion:** WITSML / ASCII 0.5s Real-Time Poller & Buffer<br>**• Signal Conditioning:** 1D Discrete Kalman Filter (rejection of false sensor spikes, <5% false alarms)<br>**• Edge Safety Interlock:** Deterministic Rule-Based Kill-Switch (**0.008 ms latency**, 100% offline rig-safe) | Flink/Spark/Kafka are overkill and fail in offline rig environments. A 1D Kalman filter combined with microsecond local edge rules guarantees safety. |

---

### 🟪 Middle Row: Central Context Orchestrator

| Box Title | Old Content | New Content | Technical Justification |
| :--- | :--- | :--- | :--- |
| **Unified Operational Context Layer** | FastAPI + LangChain multi-retriever router | **FastAPI ASGI Router + Real-Time Context Synchronizer**<br>• Ingests live Kalman-filtered WOB, Torque, RPM, Standpipe Pressure<br>• Correlates active bit depth with 100m offset lookahead slice<br>• Synchronizes real-time geomechanical pore pressure bounds | Unifies live streaming parameters, historical lessons learned, and 3D offset trajectories into a single JSON payload every 500 milliseconds. |

---

### 🟩 Bottom Row: 6 Sequential Operational Stages

| Stage # & Title | Old Content | New Content | Technical Justification |
| :--- | :--- | :--- | :--- |
| **Stage 1: Query & Lookahead Intake** | React/Next.js, Whisper, LangChain router | **Proactive 100m Lookahead Trigger + Driller Voice/Text Query**<br>• Automatic trigger: Fires when bit enters hazardous lithology zone<br>• Driller on-demand input: High-contrast touch or speech-to-text | Not just reactive chat; continuously looks ahead 100 meters to alert the driller before reaching dangerous zones. |
| **Stage 2: Automated State & Geomechanics** *(Replaces generic SLM)* | Llama-3-8B, Mistral-7B, LoRA/QLoRA, vLLM/Ollama | **Automated State Recognizer & Geomechanical Model**<br>• SVM Multi-Class State Classifier: Rotary / Slide / Ream / Connection (>95% Acc)<br>• Dual-Driven Pore & Fracture Pressure Model ($R^2 = 0.924$) | Eliminates manual state logging; accurately detects current drilling action and calculates safe mud weight drilling margins. |
| **Stage 3: JEV & FCBR Reasoning Engine** | LangGraph/CrewAI, Search $\rightarrow$ Compare $\rightarrow$ Evaluate $\rightarrow$ Validate $\rightarrow$ Select, Weighted scoring | **Fuzzy Case-Based Reasoning (FCBR) + Cobweb Polygon Matching**<br>• Multi-dimensional similarity scoring across depth, torque, and lithology<br>• Generates 4 graded interventions: (A) Tuning, (B) Mud/LCM, (C) Ream, (D) POOH | Replaces black-box CrewAI agents with transparent, deterministic petroleum engineering case matching backed by SPE literature. |
| **Stage 4: Predictive Risk & Optimization Output** | Pydantic JSON, Scikit-learn, XGBoost | **5-Class Loss ML + Bourgoyne & Young ROP Optimizer + INPT Analyzer**<br>• Random Forest (150 trees): None, Seepage, Partial, Severe, Total (98% Acc)<br>• ROP Optimization: +14% penetration rate improvement<br>• Invisible NPT (INPT): 3$\sigma$ Crew Benchmark (32% recoverable delay) | Delivers concrete machine learning predictions for lost circulation and calculates connection micro-delays (INPT) saving ₹2.4 Lakhs/shift. |
| **Stage 5: AVER Explainable AI Agent** | GPT-4/Claude/Llama 70B, LangChain function-calling | **AVER Explainable LLM Reasoning Agent**<br>• Groq LLaMA-3.3-70B-Versatile / Qwen-2.5-32B Engine<br>• Explains "Why Selected", cites exact WCR offset well pages, provides contingency plans | Provides total transparency: drillers never blindly trust AI; they read exact historical evidence and verified operating procedures. |
| **Stage 6: Dual-Role Engineer Dashboard** | React/Next.js, Mapbox/Kepler.gl, Plotly/D3, WebSockets | **Dual-Role Operational UI & Plotly 3D Trajectory Engine**<br>• **Rig Floor HUD**: High-contrast, 3-second glanceable, tactile alerts<br>• **Office Analytics**: 9-Tab deep intelligence portal, Plotly 3D directional surveys, historical lithology logs | Specifically engineered for rig floor harsh environments (HUD) while giving office superintendents 3D visualization and deep analytics. |

---

### ⬜ Bottom Bar: Cross-Cutting Infrastructure

| Infrastructure Domain | Old Slide Text | New Production-Ready Architecture |
| :--- | :--- | :--- |
| **Backend Core** | Python, FastAPI, LangChain/LangGraph | **Python 3.11+, FastAPI ASGI, DuckDB In-Memory OLAP, NumPy, Scikit-Learn** |
| **Edge Deployment** | Docker + Kubernetes on AWS/Azure | **Lightweight Rig-Edge Python Wheel / Docker** (Runs on local rig PC, 100% offline capable when satellite link drops) |
| **Security & Compliance** | OAuth2, JWT, RBAC, Audit Logging | **Role-Based Dual Access Control (Rig Driller vs Office Superintendent), SHA-256 Telemetry Verification, Tamper-proof Audit Trail** |
| **Quality & MLOps** | MLflow, Weights & Biases | **Pytest Automated Verification Suite (`main.py --check`), 100% Synthetic & Real Well Data Validation, GitHub Actions CI/CD** |

---

## 🎯 Key Presentation Speaking Points for this Slide

When presenting this revised technical architecture slide to the evaluators, highlight these three distinct talking points:

1. **"We eliminated cloud dependencies on the rig floor."**
   > *"Notice our stream processing layer: instead of requiring multi-node Apache Flink or Kafka clusters which are impossible on remote Assam rigs, we built a 1D Discrete Kalman Filter that conditions telemetry locally and executes a deterministic safety interlock in 0.008 milliseconds, 100% offline."*

2. **"We do true directional mathematics, not 2D estimations."**
   > *"Our structured data pillar uses the official API RP 7G Minimum Curvature Method to convert Measured Depth into True Vertical Depth while applying a 2.4° SSE stratigraphic dip. This allows sub-meter correlation between our active well and offset wells."*

3. **"Our ML is multi-tiered: deterministic physics + classical ML + generative explainability."**
   > *"We do not blindly send telemetry to an LLM. We run an SVM for drilling state classification, a 5-class Random Forest for lost circulation risk, Fuzzy Case-Based Reasoning for analog matching, and Bourgoyne & Young for ROP optimization. The AVER LLM acts only as the final explainability layer to tell the driller 'Why' and cite the exact offset well completion report."*
