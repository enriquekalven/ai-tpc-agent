import typer
import os
from typing import Optional
from .core.agent import TPCAgent
from .core.chat_bridge import GoogleChatBridge

app = typer.Typer(help="AI TPC Agent: Browsing and Promoting AI Knowledge")

@app.command()
def report():
    """Generate the AI Field Promotion Report locally."""
    agent = TPCAgent()
    knowledge = agent.browse_knowledge()
    agent.promote_learnings(knowledge)

@app.command()
def chat(
    webhook_url: str = typer.Option(None, "--webhook-url", envvar="GCHAT_WEBHOOK_URL", help="Google Chat Webhook URL")
):
    """Scan and post the report to Google Chat."""
    if not webhook_url:
        typer.echo("Error: Webhook URL must be provided via --webhook-url or GCHAT_WEBHOOK_URL env var.")
        raise typer.Exit(code=1)
    
    agent = TPCAgent()
    knowledge = agent.browse_knowledge()
    
    bridge = GoogleChatBridge(webhook_url)
    bridge.post_report(knowledge)

@app.command()
def version():
    """Show version."""
    typer.echo("AI TPC Agent v0.1.0")

if __name__ == "__main__":
    app()
