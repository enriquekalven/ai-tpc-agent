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

    def post_report(self, knowledge: List[Dict[str, Any]], tldr: str = None, date_range: str = None):
        """
        Posts the synthesized report as a new GitHub Issue.
        """
        if not self.repo or not self.token:
            console.print("[yellow]Skipping GitHub Issue: GITHUB_TOKEN or GITHUB_REPOSITORY not set.[/yellow]")
            return

        if not knowledge:
            return

        date_suffix = f" ({date_range})" if date_range else ""
        title = f"🚀 AI TPC Pulse: {len(knowledge)} New Updates{date_suffix}"
        
        body = self._format_markdown_report(knowledge, tldr, date_range)

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

    def _format_markdown_report(self, knowledge: List[Dict[str, Any]], tldr: str = None, date_range: str = None) -> str:
        report = "# 🚀 AI TPC Field Pulse\n"
        if date_range:
            report += f"**Pulse Period:** {date_range}\n\n"
        report += f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PST\n\n"
        report += "---\n\n"
        report += "## 🎯 Executive Synthesis\n"
        
        if tldr:
            report += f"> {tldr}\n\n"
        else:
            roadmap_items = [k for k in knowledge if k['category'] == 'roadmap' or 'release' in k['source']]
            if roadmap_items:
                report += f"Found **{len(roadmap_items)}** major roadmap shifts. "
                report += "Key focus areas: **Agent Standardization (ADK)** and **Partner Model Depth (Vertex AI)**.\n\n"
            else:
                report += "No major roadmap shifts detected. Review industry trends below for market context.\n\n"

        report += "---\n\n"
        
        # Roadmap Section
        report += "## 🌉 Roadmap & Release Bridge\n"
        report += "*Synthesized for Field Promotion*\n\n"
        
        if not roadmap_items:
            report += "> _No recent roadmap items to bridge._\n\n"
        else:
            for item in roadmap_items:
                bridge = item.get('bridge', "New tech detected. Review impacts on developer velocity.")
                
                report += f"### [{item['source'].upper()}] {item['title']}\n"
                report += f"**🚀 Field Impact:** {bridge}\n\n"
                report += f"{item.get('summary', '')[:800]}\n\n"
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
                report += f"{item.get('summary', '')[:600]}\n\n"
                report += f"**[🔗 Read Full Update]({item.get('source_url', '#')})**\n\n"
                report += "---\n"

        report += "\n\n**Note:** This report is synthesized by the **AI TPC Agent** based on live documentation and release feeds.\n"
        return report

# Add missing import for datetime
from datetime import datetime
