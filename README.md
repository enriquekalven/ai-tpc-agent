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

## Scheduling (Field Pulse)
The repository includes a GitHub Action (`.github/workflows/pulse.yml`) to automatically post updates to Google Chat every Monday and Wednesday.

**Setup:**
1. Go to your repository **Settings** > **Secrets and variables** > **Actions**.
2. Add a new **Repository secret**:
   - **Name**: `GCHAT_WEBHOOK_URL`
   - **Value**: Your Google Chat Space webhook URL.

### Bridging targets
- Agent Builder
- Gemini / GE
- Cloud AI Platform
