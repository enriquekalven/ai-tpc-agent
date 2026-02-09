# 🗺️ AI TPC Agent Roadmap

This roadmap tracks the evolution of the AI TPC Agent from a "Pulse Dispatcher" to a full-scale "Intelligence Hub" as outlined in the [TPC Cloud AI Agent PRD].

## 🎯 Current Status: "Pulse Phase" (v0.1.0)
- ✅ **Retrieve**: Scrapers for Vertex AI, Gemini Enterprise, GitHub, and PyPI.
- ✅ **Synthesize**: Gemini 2.0 Flash integration for Talk Tracks and business summaries.
- ✅ **Promote**: Automated broadcasting via Email, GitHub Issues, and Google Chat.
- ✅ **Reliability**: Integrated regression test suite and GitHub Actions automation.
- ✅ **Hardening (v0.1.1)**: Implemented PII Scrubber, Prompt Injection Validation, and Semantic Caching.

---

## 🚀 Future Milestones

### 🏗️ Phase 1: RAG & Persistence (Q1 2026)
*Goal: Move from "What's new today" to "Ask me anything about AI Roadmaps."*

- [x] **Vector Database Integration**: Implement persistent storage (Vertex AI RAG Engine) to store every historical pulse.
- [x] **Retrieval Augmented Generation (RAG)**: Enable users to query the agent about historical shifts.
- [x] **Serving Layer**: Finalized `tpc-agent serve` command exposing a FastAPI endpoint.
- [ ] **Gemini Enterprise Registration**: Register the agent as a tool in the corporate Gemini UI.

### 📁 Phase 2: Internal Knowledge Ingestion (Q1-Q2 2026)
*Goal: Ingest private Google data sources identified in the PRD.*

- [ ] **Google Workspace Connectors**: Implement authenticated ingestion for Google Drive folders and GCS Buckets.
- [ ] **Semantic Scrapers for `go/` links**: specialized scrapers for internal sites like `go/ai-seminars` and `go/prompt-live-replays`.
- [ ] **Asset Management Sheets**: Integrate with TPC educator sheets for manual asset promotion.

### 📅 Phase 3: TPC Community Integration (Q2 2026)
*Goal: Full integration with the TPC Community and Educators.*

- [ ] **Event Calendar Sync**: Connect to `go/ai-sessions-cal` to broadcast upcoming seminars.
- [ ] **Session Recording Summarization**: Use Gemini 1.5 Pro (long context) to ingest and summarize 60-minute seminar recordings.
- [ ] **Learner analytics**: Track MAU and Query Volume to measure field upskilling success.

---

## 🛠️ Infrastructure Gaps to Close
1. **Authenticated Ingestion**: Shifting from public feed scraping to internal OAuth-based data retrieval.
2. **Horizontal Scaling**: Transitioning from GitHub Actions (Batch) to Cloud Run (Service) architecture.
3. **Multi-Model Routing**: Using Flash for pulses and Pro for deep semantic session summaries.
