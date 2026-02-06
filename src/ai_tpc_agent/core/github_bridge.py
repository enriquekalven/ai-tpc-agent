import os
import requests
from typing import List, Dict, Any
from rich.console import Console

console = Console()

class GitHubBridge:
    """
    Bridge to post AI TPC reports as GitHub Issues.
    This provides an automated notification channel without requiring email credentials.
    """
    def __init__(self, repo: str = None, token: str = None):
        self.repo = repo or os.environ.get('GITHUB_REPOSITORY')
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.api_url = f"https://api.github.com/repos/{self.repo}/issues"

    def post_report(self, knowledge: List[Dict[str, Any]]):
        """
        Posts the synthesized report as a new GitHub Issue.
        """
        if not self.repo or not self.token:
            console.print("[yellow]Skipping GitHub Issue: GITHUB_TOKEN or GITHUB_REPOSITORY not set.[/yellow]")
            return

        if not knowledge:
            return

        date_str = "".join(list(filter(lambda x: x.isdigit() or x == '-', str(knowledge[0].get('date', ''))))[:10])
        title = f"🚀 AI TPC Pulse: {len(knowledge)} New Updates ({date_str})"
        
        body = self._format_markdown_report(knowledge)

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "title": title,
                    "body": body,
                    "labels": ["pulse", "automated"]
                }
            )
            response.raise_for_status()
            console.print(f"[green]Successfully posted report to GitHub Issues: {response.json().get('html_url')}[/green]")
        except Exception as e:
            console.print(f"[red]Failed to post to GitHub: {e}[/red]")

    def _format_markdown_report(self, knowledge: List[Dict[str, Any]]) -> str:
        report = "# 🚀 AI TPC Field Pulse\n"
        report += f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PST\n\n"
        report += "--- \n\n"
        report += "## 🎯 Executive Synthesis\n"
        
        # Heuristic synthesis summary
        roadmap_items = [k for k in knowledge if k['category'] == 'roadmap' or 'release' in k['source']]
        if roadmap_items:
            report += f"Found **{len(roadmap_items)}** major roadmap shifts in the last 24 hours. "
            report += "Key focus areas should be **Agent Standardization (ADK)** and **Partner Model Depth (Vertex AI)**.\n\n"
        else:
            report += "No major roadmap shifts detected in the last 24 hours. Review industry trends below for market context.\n\n"

        report += "--- \n\n"
        
        # Roadmap Section
        report += "## 🌉 Roadmap & Release Bridge\n"
        report += "_How to talk about these updates to the field._\n\n"
        
        if not roadmap_items:
            report += "> _No recent roadmap items to bridge._\n\n"
        else:
            for item in roadmap_items:
                title = item.get('title', '').lower()
                bridge = "New tech detected. Review impacts on developer velocity."
                
                if any(term in title for term in ["agent", "builder"]):
                    bridge = "🔥 **CRITICAL**: Enhances Agent Builder. Focus on 'Low-Code to Pro-Code' transition story."
                elif any(term in title for term in ["gemini", "ge"]):
                    bridge = "🤖 **GE UPDATE**: New Gemini features. Highlight Context Window and Reasoning Engine."
                elif any(term in title for term in ["security", "compliance", "iam"]):
                    bridge = "🛡️ **GOVERNANCE**: Directly addresses Enterprise Security. Use to unblock FinServ/Healthcare deals."
                elif any(term in title for term in ["claude", "anthropic", "opus"]):
                    bridge = "🎨 **PARTNER DEPTH**: New Claude models on Vertex. Crucial for customers requesting model-diversity."
                elif "adk" in title:
                    bridge = "📦 **DEV EXPERIENCE**: ADK Update. Promotes standardized agent building across teams."
                elif "a2ui" in title:
                    bridge = "🖥️ **UX REVOLUTION**: Agent-Driven UI. Standardizing component rendering for agents."

                report += f"### 📦 [{item['source'].upper()}] {item['title']}\n"
                report += f"**🚀 Field Impact:** {bridge}\n\n"
                report += f"{item.get('summary', '')[:800]}...\n\n"
                report += f"**[🔗 Open Documentation]({item.get('source_url', '#')})**\n\n"
                report += "---\n"

        # Trends Section
        report += "\n## 💡 AI Knowledge & Market Trends\n"
        trend_items = [k for k in knowledge if k['category'] != 'roadmap']
        if not trend_items:
            report += "> _No new industry trends detected today._\n"
        else:
            for item in trend_items:
                report += f"### 📰 {item.get('title', 'Market Update')}\n"
                report += f"*Source: {item.get('description', item.get('source', 'Unknown'))}*\n\n"
                report += f"{item.get('summary', '')[:600]}...\n\n"
                report += f"**[🔗 Read Full Update]({item.get('source_url', '#')})**\n\n"
                report += "---\n"

        report += "\n\n> [!NOTE]\n"
        report += "> This report is synthesized by the **AI TPC Agent** based on live documentation and release feeds.\n"
        return report

# Add missing import for datetime
from datetime import datetime
