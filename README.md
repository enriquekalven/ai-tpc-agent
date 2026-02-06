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
tpc-agent email "field-team@example.com"
```

## Scheduling (Field Pulse)
The repository includes a GitHub Action (`.github/workflows/pulse.yml`) to automatically process updates.

**Configuration:**
1. **GitHub Secrets**: Add `GCHAT_WEBHOOK_URL` for Chat or `TPC_SENDER_EMAIL`, `TPC_SENDER_PASSWORD`, and `RECIPIENT_EMAIL` for Email.

## Alternative: Markdown Persistence
If communication channels are restricted, you can run the agent to append to a local log:
```bash
tpc-agent report >> FIELD_PILOT_LOG.md
```

### Bridging targets
- Agent Builder
- Gemini / GE
- Cloud AI Platform
