# Sentinel Architecture: Orchestrated Governance

This document describes the technical architecture of Sentinel Vantage, a pilot exploring the intersection of **Agentic AI** and **Deterministic Governance**.

---

### 📡 System Overview

Sentinel is built as a **Voice-First Command Center**. The system follows a "Route-Reason-Synthesize" pipeline:

1.  **Voice Input**: The user provides a natural language query via the Streamlit audio interface.
2.  **Transcription**: **Gemini 2.5 Pro** transcribes the audio with high fidelity (via the Auto-Discovery loop).
3.  **Orchestration Logic**: The system analyzes the query for "Governance Triggers."
    *   **Path A (Analytical)**: If the query is safe, it is routed to **Victoria (Analyst)**.
    *   **Path B (Governance)**: If PII (like employee names) is detected, it is routed to **Mike (Sheriff)**.
16.  **Agentic Reasoning**:
    *   **Victoria** uses Gemini 2.5 Pro to generate 1-2 sentence insights based on real-time data aggregations.
    *   **Mike** uses an independent logic layer (Claude Opus 4.5) with a full corporate roster to construct a diplomatic, privacy-safe alternative.
5.  **Data Visualization**: A heuristic engine selects the optimal Plotly chart type (Bar/Line) to accompany the insight.
6.  **Voice Synthesis**: **ElevenLabs** (Turbo v2.5) generates the distinct agent voices for the final response.

---

### 🧩 The Polyglot Agentic Layer

We deliberately use a multi-model family approach to maximize system integrity:

| Role | Model | Reason |
| :--- | :--- | :--- |
| **Storyteller / Analyst** | Gemini 2.5 Pro | High-speed reasoning over large data context with robust auto-discovery failover. |
| **Governance Auditor** | Claude Opus 4.5 | Independent audit path to avoid correlated blind spots in reasoning, utilizing full strict roster context. |
| **Voice Persona** | ElevenLabs v2.5 | Industry-leading low-latency synthesis for distinct human identities. |

---

### 🛡️ Governance Guardrails

Sentinel implements "Guardrails as a Service":

*   **Strict Roster PII Masking**: Hard-coded logic maps every employee uniquely to their team. Claude dynamically evaluates queries against this full roster to detect non-team identifiers before they reach the generative loop.
*   **The "Sheriff" Intervention**: When a breach is detected, the system bypasses the Analyst agent entirely. The Sheriff provides a pre-authorized, data-rich alternative that reports on team-level metrics instead of individual PII.
*   **Model-Level Redundancy**: By using Claude to audit Gemini-originated queries, the system ensures that "jailbreaks" or narrative inferences are caught by an independent reasoning engine.

---

### 📊 Data Visualization Engine

The dashboard utilizes a **Voice-to-Viz** agent that:
- Identifies the user's analytical intent from the query.
- Maps variables to X and Y axes dynamically.
- Selects the most effective chart type (e.g., using a Bar Chart for categorical spending vs. a Line Chart for temporal trends).
- Applies a consistent high-contrast dark-mode theme to all Plotly outputs.

---
*Last Updated: April 29, 2026 (6:15 PM PST)*
