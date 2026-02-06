# AI TPC Agent 🚀

Technical Program Consultant (TPC) Agent designed to browse, track, and promote AI knowledge and product roadmaps for field teams.

## Features
- **Ecosystem Watcher**: Tracks Vertex AI, Generative AI, and Industry Blogs.
- **Roadmap Bridger**: Translates technical roadmap updates into Field-ready talk tracks.
- **Automated Reporting**: Generates high-fidelity promotion reports.

## Installation
```bash
pip install .
```

## Usage
### Local Report
```bash
tpc-agent report
```

### Google Chat Broadcast
```bash
tpc-agent chat --webhook-url "YOUR_WEBHOOK_URL"
```

### Email Promotion
```bash
# Uses TPC_SENDER_EMAIL and TPC_SENDER_PASSWORD env vars
tpc-agent email "ai-tpc-agent@google.com"
```
### GitHub Issues Broadcast
```bash
# Uses GITHUB_TOKEN and GITHUB_REPOSITORY env vars
tpc-agent github
```

## Sample Terminal Output
```text
🚀 AI TPC AGENT: FIELD PROMOTION REPORT (Last 2 Days)

🌉 ROADMAP BRIDGE: FIELD TALK TRACKS
╭─────────────────────────────────────────── [VERTEX-AI-RELEASES] ───────────────────────────────────────────╮
│ Feature: Claude 3.5 Sonnet on Vertex AI                                                                    │
│ Field Impact: PARTNER DEPTH: New Claude models on Vertex. Crucial for customers requesting model-diversity. │
│ Action: Open Documentation                                                                                 │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭────────────────────────────────────────────── [GOOGLE-ADK] ────────────────────────────────────────────────╮
│ Feature: v1.24.0 Release                                                                                   │
│ Field Impact: DEV EXPERIENCE: ADK Update. Promotes standardized agent building. Essential for              │
│ 'Agent-First' architecture talks.                                                                          │
│ Action: Open Documentation                                                                                 │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

💡 AI KNOWLEDGE & MARKET TRENDS
### Google Cloud AI Blog: Sovereign AI in 2026
Source: Google Cloud AI Blog - Market Trends & Innovations
Actionable Insight: New regulatory trends in EMEA are driving demand for local-residency AI models...
[🔗 Read Full Update]

---
```

## Scheduling (Field Pulse)
The repository includes a GitHub Action (`.github/workflows/pulse.yml`) to automatically process updates.

**Secure Channel Options:**
1. **GitHub Issues (Default)**: Reports are posted as issues in the current repo. Zero-config (uses `GITHUB_TOKEN`).
2. **Google Chat**: Add `GCHAT_WEBHOOK_URL` to GitHub Secrets.
3. **Email**: Add `TPC_SENDER_EMAIL` and `TPC_SENDER_PASSWORD` (App Password) to GitHub Secrets.

## Alternative: Markdown Persistence
If communication channels are restricted, you can run the agent to append to a local log:
```bash
tpc-agent report >> FIELD_PILOT_LOG.md
```

## Bridging Targets
- **Agent Builder**: Low-code to Pro-code transition stories.
- **Gemini / GE**: Context window and reasoning engine improvements.
- **Claude / Anthropic**: Model diversity and partner depth.
- **ADK / A2A / A2UI**: Standardization and UX revolution.
- **Security & Compliance**: Unblocking enterprise deals.
