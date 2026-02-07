from google import adk
from typing import List, Dict, Any
import os
import json
from datetime import datetime, timedelta, timezone
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from .watcher import fetch_recent_updates

console = Console()
WATCHLIST_PATH = os.path.join(os.path.dirname(__file__), 'watchlist.json')

class TPCTools:
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
        hub = watchlist.get('ai_knowledge_hub', {})
        roads = watchlist.get('roadmap_trackers', {})
        
        sources = hub.copy()
        sources.update(roads)

        for name, info in sources.items():
            recent_items = fetch_recent_updates(info['feed'], max_items=10)
            for item in recent_items:
                item['source'] = name
                item['category'] = info.get('category', 'general')
                item['description'] = info['description']
                knowledge_base.append(item)
        return knowledge_base

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
        elif any(term in title for term in ["claude", "anthropic", "opus"]):
            bridge_context = "PARTNER DEPTH: New Claude models on Vertex. Crucial for customers requesting model-diversity."
        elif "adk" in title or "agent development kit" in title:
            bridge_context = "DEV EXPERIENCE: ADK Update. Promotes standardized agent building. Essential for 'Agent-First' architecture talks."
        elif "a2ui" in title:
            bridge_context = "UX REVOLUTION: Agent-Driven UI (A2UI). Allows agents to render native UI components. Key for premium client demos."
        elif "a2a" in title:
            bridge_context = "INTEROPERABILITY: A2A Protocol. Standardizes how different agents talk to each other. Sell the 'Agentic Ecosystem' story."
            
        return bridge_context

def parse_date(date_str: str) -> datetime:
    """Very basic date parsing for Atom/RSS/ISO formats."""
    try:
        # ISO 8601 (from our scraper or Atom)
        if 'T' in date_str:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        # RSS RFC 2822
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except Exception:
        # Secondary attempt for simple YYYY-MM-DD
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except:
            return datetime.now(timezone.utc) - timedelta(days=365)

class TPCAgent:
    """
    Wrapper to maintain compatibility with existing CLI commands.
    """
    def __init__(self):
        self.tools = TPCTools()
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                pass

    def browse_knowledge(self) -> List[Dict[str, Any]]:
        return self.tools.browse_ai_knowledge()

    def synthesize_reports(self, knowledge: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Enriches the knowledge list with Gemini-powered summaries, bridges, and tags.
        Returns a dictionary containing:
        - 'items': The enriched list of items
        - 'tldr': A high-level executive summary of all updates
        """
        if not knowledge:
            return {"items": [], "tldr": "No new updates found for this period."}

        # Enrich individual items
        console.print("[cyan]✨ Synthesizing reports with Gemini...[/cyan]")
        for item in knowledge:
            if not self.client:
                item['bridge'] = self.tools.bridge_roadmap_to_field(item)
                item['tags'] = []
                continue

            # Generate Field Impact Bridge
            item['bridge'] = self._summarize_with_gemini(item)
            
            # Generate Tags (e.g., Governance, Security, Performance)
            try:
                tag_prompt = f"Categorize this technical update with 1-2 keywords (e.g. Governance, Security, UX, Performance, Scalability). Update: {item['title']}. Return only keywords separated by commas."
                tag_resp = self.client.models.generate_content(model='gemini-2.0-flash-exp', contents=tag_prompt)
                item['tags'] = [t.strip() for t in tag_resp.text.split(',')]
            except Exception:
                item['tags'] = []

            # Refine Summary
            if len(item.get('summary', '')) > 300:
                try:
                    refine_prompt = f"Summarize this for a business audience in 2 sentences focus on impact: {item['summary']}"
                    resp = self.client.models.generate_content(model='gemini-2.0-flash-exp', contents=refine_prompt)
                    item['summary'] = resp.text.strip()
                except Exception:
                    pass

        # Generate Executive TLDR
        tldr = "Review the technical roadmap updates below for recent shifts in Vertex AI and the Agent Ecosystem."
        if self.client and knowledge:
            try:
                titles = "\n".join([f"- {k['title']} ({k['source']})" for k in knowledge[:10]])
                tldr_prompt = f"""
                You are a Lead Technical Program Consultant.
                Provide a high-level 'Executive TLDR' (2-3 sentences) summarizing the theme of these recent AI updates:
                {titles}
                
                Focus on the collective impact for the field team and customers.
                """
                resp = self.client.models.generate_content(model='gemini-2.0-flash-exp', contents=tldr_prompt)
                tldr = resp.text.strip()
            except Exception:
                pass

        return {"items": knowledge, "tldr": tldr}

    def promote_learnings(self, synthesized_content: Dict[str, Any], days: int = 1):
        items = synthesized_content.get('items', [])
        tldr = synthesized_content.get('tldr', '')
        
        console.print(Panel.fit(f"🚀 [bold green]AI TPC AGENT: FIELD PROMOTION REPORT (Last {days} Days)[/bold green]", border_style="green"))
        
        if tldr:
            console.print(Panel(tldr, title="🎯 Executive TLDR", border_style="yellow"))

        now = datetime.now(timezone.utc)
        cutoff = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        if not items:
            console.print(f"[yellow]No new insights found in the last {days} days.[/yellow]")
            return

        items.sort(key=lambda x: parse_date(x.get('date', '')), reverse=True)
        
        console.print("\n🌉 [bold cyan]ROADMAP BRIDGE: FIELD TALK TRACKS[/bold cyan]")
        roadmap_items = [k for k in items if k['category'] == 'roadmap' or 'release' in k['source']]
        for item in roadmap_items:
            panel_content = f"**Feature:** {item['title']}\n**Field Impact:** {item.get('bridge', '')}\n**Action:** [Open Documentation]({item.get('source_url', '#')})"
            console.print(Panel(Markdown(panel_content), title=f"[{item['source'].upper()}]", border_style="cyan"))

        console.print("\n💡 [bold magenta]AI KNOWLEDGE & MARKET TRENDS[/bold magenta]")
        trend_items = [k for k in items if k['category'] != 'roadmap']
        for item in trend_items:
            self._print_item(item)

    def _summarize_with_gemini(self, item: Dict[str, Any]) -> str:
        """Uses Gemini to generate a field-ready talk track if API key is present."""
        if not self.client:
            return self.tools.bridge_roadmap_to_field(item)
        
        try:
            prompt = f"""
            You are a Technical Program Consultant (TPC) for Google Cloud AI.
            Translate the following technical update into a 'Field Talk Track' for sales and architects.
            
            Update Title: {item['title']}
            Source: {item['description']}
            Raw Content: {item.get('summary', '')[:1000]}
            
            Format: One concise, high-impact sentence explaining WHY this matters for customers and what the sales play is.
            """
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return self.tools.bridge_roadmap_to_field(item)

    def _print_item(self, item: Dict[str, Any]):
        title = item.get('title', 'Unknown Title')
        source = item.get('description', item.get('source', 'Unknown Source'))
        
        # If Gemini is available, refine the summary
        summary = item.get('summary', '')[:500]
        if self.client:
            try:
                refine_prompt = f"Summarize this for a business audience in 2 sentences focus on impact: {summary}"
                resp = self.client.models.generate_content(model='gemini-2.0-flash-exp', contents=refine_prompt)
                summary = resp.text.strip()
            except Exception:
                pass
                
        url = item.get('source_url', '#')
        promotion_msg = f"### {title}\n*Source: {source}*\n\n**Actionable Insight:**\n{summary}\n\n[🔗 Read Full Update]({url})\n---\n"
        console.print(Markdown(promotion_msg))
