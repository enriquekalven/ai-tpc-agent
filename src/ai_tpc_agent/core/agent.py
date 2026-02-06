from typing import List, Dict, Any
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from .watcher import fetch_latest_from_atom

console = Console()
WATCHLIST_PATH = os.path.join(os.path.dirname(__file__), 'watchlist.json')

class TPCAgent:
    """
    Technical Program Consultant (TPC) Agent.
    Browses AI knowledge and bridges roadmap gaps for field teams.
    """
    def __init__(self):
        self.watchlist = self._load_watchlist()

    def _load_watchlist(self) -> Dict[str, Any]:
        if not os.path.exists(WATCHLIST_PATH):
            return {}
        with open(WATCHLIST_PATH, 'r') as f:
            return json.load(f)

    def browse_knowledge(self) -> List[Dict[str, Any]]:
        knowledge_base = []
        sources = self.watchlist.get('ai_knowledge_hub', {}).copy()
        sources.update(self.watchlist.get('roadmap_trackers', {}))

        for name, info in sources.items():
            with console.status(f"[dim]Checking {name}..."):
                latest = fetch_latest_from_atom(info['feed'])
                if latest:
                    latest['source'] = name
                    latest['category'] = info.get('category', 'general')
                    latest['description'] = info['description']
                    knowledge_base.append(latest)
        return knowledge_base

    def bridge_roadmap_gap(self, knowledge: List[Dict[str, Any]]):
        console.print("\n🌉 [bold cyan]ROADMAP BRIDGE: FIELD TALK TRACKS[/bold cyan]")
        roadmap_items = [k for k in knowledge if k['category'] == 'roadmap' or 'release' in k['source']]
        
        if not roadmap_items:
            console.print("[dim]No significant roadmap updates to bridge today.[/dim]")
            return

        for item in roadmap_items:
            source_btn = item['source'].upper()
            title = item['title']
            
            bridge_context = "This update improves developer velocity and aligns with the 2026 Sovereign AI themes."
            if any(term in title.lower() for term in ["agent", "builder"]):
                bridge_context = "CRITICAL: Enhances Agent Builder capabilities. Field should focus on 'Low-Code to Pro-Code' transition stories."
            elif any(term in title.lower() for term in ["gemini", "ge"]):
                bridge_context = "GE UPDATE: New Gemini models/features. Highlight 'Context Window' and 'Reasoning Engine' improvements."
            elif any(term in title.lower() for term in ["security", "compliance"]):
                bridge_context = "GOVERNANCE: Directly addresses Enterprise Security concerns. Use to unblock FinServ/Healthcare deals."

            panel_content = f"""
**Feature:** {title}
**Field Impact:** {bridge_context}
**Action:** [Link to Doc]({item.get('source_url', '#')})
"""
            console.print(Panel(Markdown(panel_content), title=f"[{source_btn}] Roadmap Bridger", border_style="cyan"))

    def promote_learnings(self, knowledge: List[Dict[str, Any]]):
        console.print(Panel.fit("🚀 [bold green]AI TPC AGENT: FIELD PROMOTION REPORT[/bold green]", border_style="green"))
        if not knowledge:
            console.print("[yellow]No new insights found today.[/yellow]")
            return

        knowledge.sort(key=lambda x: x.get('date', ''), reverse=True)
        self.bridge_roadmap_gap(knowledge)

        console.print("\n💡 [bold magenta]AI KNOWLEDGE & MARKET TRENDS[/bold magenta]")
        trend_items = [k for k in knowledge if k['category'] != 'roadmap']
        for item in trend_items[:5]:
             self._print_item(item)

    def _print_item(self, item: Dict[str, Any]):
        title = item.get('title', 'Unknown Title')
        date = item.get('date', 'Unknown Date')
        source = item.get('description', item.get('source', 'Unknown Source'))
        
        promotion_msg = f"""
### {title}
*Source: {source} | Date: {date}*

**Actionable Insight:** 
{item.get('summary', 'New update detected. Review source for full details.')}

---
"""
        console.print(Markdown(promotion_msg))
