import adk
from typing import List, Dict, Any
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from .watcher import fetch_latest_from_atom

console = Console()
WATCHLIST_PATH = os.path.join(os.path.dirname(__file__), 'watchlist.json')

class TPCTools:
    @adk.tool
    def browse_ai_knowledge(self) -> List[Dict[str, Any]]:
        """
        Scans official Google Cloud AI release notes, blogs, and roadmap repositories.
        Returns a list of recent updates with titles, dates, and summaries.
        """
        if not os.path.exists(WATCHLIST_PATH):
            return []
        
        with open(WATCHLIST_PATH, 'r') as f:
            watchlist = json.load(f)
            
        knowledge_base = []
        sources = watchlist.get('ai_knowledge_hub', {}).copy()
        sources.update(watchlist.get('roadmap_trackers', {}))

        for name, info in sources.items():
            latest = fetch_latest_from_atom(info['feed'])
            if latest:
                latest['source'] = name
                latest['category'] = info.get('category', 'general')
                latest['description'] = info['description']
                knowledge_base.append(latest)
        return knowledge_base

    @adk.tool
    def bridge_roadmap_to_field(self, knowledge_item: Dict[str, Any]) -> str:
        """
        Translates a technical roadmap update into a field-ready 'Talk Track'.
        Use this to bridge the gap for product roadmaps like Agent Builder or GE.
        """
        title = knowledge_item.get('title', '').lower()
        
        bridge_context = "This update improves developer velocity and aligns with the 2026 Sovereign AI themes."
        if any(term in title for term in ["agent", "builder"]):
            bridge_context = "CRITICAL: Enhances Agent Builder. Field should focus on 'Low-Code to Pro-Code' transition stories."
        elif any(term in title for term in ["gemini", "ge", "generative engine"]):
            bridge_context = "GE UPDATE: New Gemini models/features. Highlight 'Context Window' and 'Reasoning Engine' improvements."
        elif any(term in title for term in ["security", "compliance", "governance"]):
            bridge_context = "GOVERNANCE: Directly addresses Enterprise Security concerns. Use to unblock FinServ/Healthcare deals."
            
        return bridge_context

# Define the ADK Agent
tpc_agent = adk.Agent(
    name="AI TPC Agent",
    instructions="""
    You are a Technical Program Consultant (TPC) for Google Cloud AI.
    Your mission is to bridge the visibility gap between product roadmaps (Agent Builder, GE) and the field teams.
    
    1. Use 'browse_ai_knowledge' to stay updated on the latest AI trends and roadmap items.
    2. Use 'bridge_roadmap_to_field' to translate technical updates into actionable insights.
    3. Promote these learnings to help field teams understand product direction and market shifts.
    """,
    tools=[TPCTools().browse_ai_knowledge, TPCTools().bridge_roadmap_to_field]
)

class TPCAgentLegacy:
    """
    Legacy wrapper to maintain compatibility with existing CLI commands.
    """
    def __init__(self):
        self.tools = TPCTools()

    def browse_knowledge(self) -> List[Dict[str, Any]]:
        return self.tools.browse_ai_knowledge()

    def promote_learnings(self, knowledge: List[Dict[str, Any]]):
        console.print(Panel.fit("🚀 [bold green]AI TPC AGENT: FIELD PROMOTION REPORT[/bold green]", border_style="green"))
        if not knowledge:
            console.print("[yellow]No new insights found today.[/yellow]")
            return

        knowledge.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        # Internal call to bridging for the report
        console.print("\n🌉 [bold cyan]ROADMAP BRIDGE: FIELD TALK TRACKS[/bold cyan]")
        roadmap_items = [k for k in knowledge if k['category'] == 'roadmap' or 'release' in k['source']]
        for item in roadmap_items[:5]:
            bridge = self.tools.bridge_roadmap_to_field(item)
            panel_content = f"**Feature:** {item['title']}\n**Field Impact:** {bridge}\n**Action:** [Link]({item.get('source_url', '#')})"
            console.print(Panel(Markdown(panel_content), title=f"[{item['source'].upper()}]", border_style="cyan"))

        console.print("\n💡 [bold magenta]AI KNOWLEDGE & MARKET TRENDS[/bold magenta]")
        trend_items = [k for k in knowledge if k['category'] != 'roadmap']
        for item in trend_items[:5]:
            self._print_item(item)

    def _print_item(self, item: Dict[str, Any]):
        promotion_msg = f"### {item['title']}\n*Source: {item['description']}*\n\n**Actionable Insight:**\n{item.get('summary', '')[:300]}...\n---\n"
        console.print(Markdown(promotion_msg))
