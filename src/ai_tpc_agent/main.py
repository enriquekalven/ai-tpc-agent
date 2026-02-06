import typer
import os
from typing import Optional
from .core.agent import TPCAgent
from .core.chat_bridge import GoogleChatBridge
from .core.email_bridge import EmailBridge

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
def email(
    recipient: str = typer.Argument(..., help="Recipient email address"),
    sender: str = typer.Option(None, "--sender", envvar="TPC_SENDER_EMAIL", help="Sender email address"),
    password: str = typer.Option(None, "--password", envvar="TPC_SENDER_PASSWORD", help="Sender email password/token")
):
    """Scan and send the report via Email."""
    agent = TPCAgent()
    knowledge = agent.browse_knowledge()
    
    bridge = EmailBridge(recipient, sender, password)
    bridge.post_report(knowledge)

@app.command()
def serve():
    """Launch the ADK Agent as a local service (for Gemini integration)."""
    from google import adk
    from .core.agent import tpc_agent
    typer.echo("🚀 Launching AI TPC Agent via Google ADK...")
    adk.run(tpc_agent)

@app.command()
def version():
    """Show version."""
    typer.echo("AI TPC Agent v0.1.0 (ADK Powered)")

if __name__ == "__main__":
    app()
