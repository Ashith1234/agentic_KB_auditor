# 🔥 Agentic Knowledge Base Auditor (Enterprise Edition)

A production-ready, deployable enterprise platform that establishes **absolute control over AI behavior** in production environments. This isn't just an "AI feature"; it is an end-to-end multi-agent system that monitors, audits, automatically heals, and manages RAG chatbots.

## 🚀 The Core Philosophy

**If you don't control the AI, you don't have a product.**
This system ensures your KB do3b. Data Enrichment & Feature Engineeringesn't rot, hallucinate, or spiral out of control by deploying a rigorous pipeline:
`Install → Scan → Approve → Inject Middleware → Monitor → Feedback → Auto-Heal (Agents) → Manager Oversight`

---

## 🛠️ Complete System Flow

1. **User installs plugin** (`rag install .`)
2. **Scanner runs** (Detects KB, Vector DB, Backend, LLM)
3. **Integration request created**
4. **Manager approves** via Dashboard
5. **Middleware injected** seamlessly
6. **Worker uses dashboard** for queries
7. **Response & source documents** shown with Confidence Scores
8. **Worker submits feedback** (e.g., `OUTDATED`, `VERSION_MISMATCH`)
9. **Agents trigger automatically** to resolve the issue (or System rolls back)
10. **Manager monitors system** (Heatmaps, Audits, Approvals)

---

## 📦 How to Use This System

### 1. Installation & Auto-Scanning

Instead of manually hooking into your chatbot, use the CLI installer:

```bash
# In the root of your existing application, run:
python -m src.installer.installer install .
```

- The **Auto-Scan Engine** will probe up to 4 directories deep to detect your `docs/`, `kb/`, Vector DBs (FAISS/Qdrant), LLMs, and Backend APIs (FastAPI/Flask).
- An **Integration Request** is generated with a confidence score.
- *Wait for Manager Approval.*

### 2. The Three-Dashboard Ecosystem

Start the dashboard hub:
```bash
streamlit run src/interfaces/dashboard/main_hub.py
```
*(You can also directly run `worker.py` and `manager.py` located in `src/interfaces/dashboard/pages/`)*

* **Download Hub:** Secure entry point to download the plugin.
* **Manager Dashboard:** Your command center. Approve/Reject pending Integration Requests, view Failure Heatmaps, track KB health, and monitor agent performance.
* **Worker Dashboard:** Where users interact with the RAG. See the real LLM response, source docs, and confidence scores.

### 3. The Actionable Feedback System

When workers use the dashboard, they can provide granular feedback:
* 👍 **Like:** Logs successful retrieval.
* 👎 **Dislike:** Triggers a specific reason (`OUTDATED`, `WRONG`, `IRRELEVANT`, `VERSION_MISMATCH`).

**What happens on Dislike?**
- `OUTDATED` / `VERSION_MISMATCH` → Triggers **Version Agent** to archive the old doc.
- `WRONG` → Triggers **Retrieval/Learning Agent** to fetch correct sources.

### 4. Rollback & Auto-Healing

If a recently injected document breaks the system, the **Version Registry** intercepts a `VERSION_MISMATCH` feedback:
1. It checks the last update.
2. It actively **Rolls Back** the specific document chunk.
3. It re-runs the retrieval.

### 5. API Layer & Middleware

The system automatically intercepts user queries matching your tracked routes (`/chat`, `/ask`, `/query`) using the **RAG Auditor Plugin Middleware**.
It features user-session tracking (`X-User-ID`), PII masking, and API Key protection to ensure security before logs ever touch the database.

Start the core API Server to handle the background processing:
```bash
uvicorn src.interfaces.api.app:app --reload
```

---

## 📂 Project Structure

```
RAG1/
├── configs/           # Output modes (Chatbot vs Dashboard)
├── data/              # KB documents, Vector DBs
├── src/
│   ├── installer/     # CLI, Auto-Detector, Middleware Injector
│   ├── feedback/      # Feedback Logic & Agent Triggers
│   ├── core/          # Security, Scanner, Session Manager
│   ├── agents/        # Orchestrators (Version, Retrieval, etc.)
│   ├── infrastructure/# DBs (Audit Logs, Integration Requests, Feedback, Versions)
│   ├── interfaces/    # API routes & Streamlit Dashboard Ecosystem
│   ├── plugin/        # Auditor Middleware Plugin
│   └── main.py
└── scripts/           # Execution scripts
```

## 🔐 Security & Audit Trails

- **Security Layer:** Automatically masks phone numbers, emails, and OpenAI (`sk-`) keys in memory.
- **Audit Logs:** Every single query, triggered agent list, and confidence score is meticulously tracked in the `AuditLogsDB`.

## ⚙️ Configuration Control

Toggle outputs via `configs/config.yaml`:
```yaml
output_mode:
  chatbot: false
  dashboard: true
```

---

## 🏃 Quick Start / How to Run

To run the complete system, you need to spin up both the **API Server** (for the backend endpoints and agent logic) and the **Streamlit Dashboard** (for the UI). Open two separate terminal windows:

### 1. Start the Backend API Server
```bash
uvicorn src.interfaces.api.app:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the UI Dashboard Ecosystem
```bash
streamlit run src/interfaces/dashboard/main_hub.py
```
*(From the main hub, you can navigate the entire system including the Manager and Worker views.)*

### 3. Run the CLI Auto-Installer (Optional test)
To test the automatic project scanner and middleware injector:
```bash
python -m src.installer.installer install .
```

---
**This is enterprise-grade control.** Let the agents work for you.
