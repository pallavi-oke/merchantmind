# Sentinel Vantage: Voice-First Rewards Governance

Sentinel Vantage is a high-fidelity pilot demonstrating the next generation of AI-driven corporate rewards management. It moves beyond traditional dashboards by combining **Voice-First Agentic Reasoning** with **Hard-Enforced Governance Guardrails**.

### 🎥 The Experience
A program manager interacts with the dashboard using natural voice commands. Sentinel orchestrates multiple specialized agents to provide analytical insights while ensuring that sensitive employee data (PII) is never exposed.

---

### 🛡️ The "Multi-Agent" Architecture
Sentinel uses a polyglot agentic strategy, routing tasks to the best-suited model family for each micro-task:

*   **Victoria (The AI Analyst)**: Powered by **Gemini 2.5 Pro** (via an Auto-Discovery failover loop). Victoria performs deep-dive analysis on rewards data, identifies spending trends, and generates predictive fiscal forecasts.
*   **Mike (The AI Sheriff)**: Powered by **Claude Opus 4.5** (claude-opus-4-5-20251101). Mike acts as the strict governance gatekeeper. He intercepts queries that touch on cross-team PII using a full corporate roster evaluation.
*   **The Voice Persona**: Powered by **ElevenLabs**. Both agents have distinct, high-fidelity voices (Victoria the professional analyst, Mike the authoritative guardrail).

---

### 🚀 Key Technical Features
- **Intelligent Orchestration**: Sub-second routing logic that determines when to trigger analytical reasoning vs. governance interventions.
- **Model Auto-Discovery**: A self-healing loop that interrogates the API at runtime to lock onto the strongest available Gemini 2.5 model, eliminating 404 sync errors.
- **Context-Aware Guardrails**: The "Sheriff" doesn't just block; he evaluates requests against a full strict company roster mapping, providing a "Governance Guardrail" that reroutes the user from restricted PII to valuable team-level insights.
- **Model Diversity**: A polyglot approach using Gemini for analytics and Claude Opus for independent security audits, avoiding the "correlated blind spots" of a single-model system.

---

### 🛠️ Tech Stack
- **Frontend**: Streamlit (SaaS-grade Dark Mode)
- **Agentic Reasoning**: Google Gemini 2.5 Pro & Anthropic Claude Opus 4.5
- **Voice Synthesis**: ElevenLabs (eleven_turbo_v2_5)
- **Data Engine**: Pandas-driven synthetic rewards database

---

### 🎨 Presentation Assets
The repository includes high-fidelity assets for professional demonstrations:
- `sentinel_slide.html`: An interactive, browser-rendered presentation slide featuring crisp typography and dark-mode styling.
- `nanobanana_flowchart_dark_mode.png`: A high-contrast architectural diagram optimized for video editing overlays.

---
*Last Updated: April 30, 2026*
