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
        report = "# 🚀 AI TPC Field Pulse\n\n"
        report += "The following updates have been synthesized for the field team:\n\n"
        
        # Roadmap Section
        report += "## 🌉 Roadmap Bridge\n\n"
        roadmap_items = [k for k in knowledge if k['category'] == 'roadmap' or 'release' in k['source']]
        if not roadmap_items:
            report += "_No major roadmap shifts detected today._\n\n"
        else:
            for item in roadmap_items:
                title = item.get('title', '').lower()
                bridge = "New roadmap update detected. Review impacts on developer velocity."
                if any(term in title for term in ["agent", "builder"]):
                    bridge = "CRITICAL: Enhances Agent Builder. Focus on 'Low-Code to Pro-Code' transition story."
                elif any(term in title for term in ["gemini", "ge"]):
                    bridge = "GE UPDATE: New Gemini features. Highlight Context Window and Reasoning Engine."
                elif any(term in title for term in ["security", "compliance"]):
                    bridge = "GOVERNANCE: Addresses Enterprise Security. Use to unblock FinServ/Healthcare deals."
                elif any(term in title for term in ["claude", "anthropic", "opus"]):
                    bridge = "PARTNER DEPTH: New Claude models on Vertex. Crucial for customers requesting model-diversity."

                report += f"### [{item['source'].upper()}] {item['title']}\n"
                report += f"**🚀 Field Impact:** {bridge}\n\n"
                report += f"> {item.get('summary', '')[:500]}...\n\n"
                report += f"[🔗 Open Documentation]({item.get('source_url', '#')})\n\n---\n"

        # Trends Section
        report += "\n## 💡 AI Knowledge & Market Trends\n\n"
        trend_items = [k for k in knowledge if k['category'] != 'roadmap']
        for item in trend_items:
            report += f"### {item.get('title', 'Unknown Update')}\n"
            report += f"*Source: {item.get('description', item.get('source', 'Unknown'))}*\n\n"
            report += f"{item.get('summary', '')[:500]}...\n\n"
            report += f"[🔗 Read Full Update]({item.get('source_url', '#')})\n\n---\n"

        report += "\n\n_Synthesized by **AI TPC Agent** via GitHub Actions_"
        return report
