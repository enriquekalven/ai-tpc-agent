import typer
import os
from typing import Optional
from .core.agent import TPCAgent
from .core.chat_bridge import GoogleChatBridge
from .core.email_bridge import EmailBridge
from .core.github_bridge import GitHubBridge
app = typer.Typer(help='AI TPC Agent: Browsing and Promoting AI Knowledge')

@app.command()
def report(days: int=typer.Option(1, '--days', '-d', help='Number of days to look back')):
    """Generate the AI Field Promotion Report locally."""
    agent = TPCAgent()
    knowledge = agent.browse_knowledge()
    from .core.agent import parse_date
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    filtered = [item for item in knowledge if parse_date(item.get('date', '')) >= cutoff]
    synthesized = agent.synthesize_reports(filtered)
    agent.promote_learnings(synthesized, days=days)

@app.command()
def chat(webhook_url: str=typer.Option(None, '--webhook-url', envvar='GCHAT_WEBHOOK_URL', help='Google Chat Webhook URL'), days: int=typer.Option(1, '--days', '-d', help='Number of days to look back')):
    """Scan and post the report to Google Chat."""
    if not webhook_url:
        typer.echo('Error: Webhook URL must be provided via --webhook-url or GCHAT_WEBHOOK_URL env var.')
        raise typer.Exit(code=1)
    agent = TPCAgent()
    knowledge = agent.browse_knowledge()
    from .core.agent import parse_date
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    filtered = [item for item in knowledge if parse_date(item.get('date', '')) >= cutoff]
    synthesized = agent.synthesize_reports(filtered)
    bridge = GoogleChatBridge(webhook_url)
    bridge.post_report(synthesized.get('items', []))

@app.command()
def email(recipient: str=typer.Argument(..., help='Recipient email address'), sender: str=typer.Option(None, '--sender', envvar='TPC_SENDER_EMAIL', help='Sender email address'), password: str=typer.Option(None, '--password', envvar='TPC_SENDER_PASSWORD', help='Sender email password/token'), days: int=typer.Option(1, '--days', '-d', help='Number of days to look back')):
    """Scan and send the report via Email."""
    agent = TPCAgent()
    knowledge = agent.browse_knowledge()
    from .core.agent import parse_date
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    filtered = [item for item in knowledge if parse_date(item.get('date', '')) >= cutoff]
    synthesized = agent.synthesize_reports(filtered)
    start_date = cutoff.strftime('%Y-%m-%d')
    end_date = now.strftime('%Y-%m-%d')
    date_range = f'{start_date} to {end_date}'
    bridge = EmailBridge(recipient, sender, password)
    bridge.post_report(synthesized.get('items', []), tldr=synthesized.get('tldr'), date_range=date_range)

@app.command()
def github(days: int=typer.Option(1, '--days', '-d', help='Number of days to look back')):
    """Dispatch the AI Field Promotion Report as a GitHub Issue."""
    agent = TPCAgent()
    knowledge = agent.browse_knowledge()
    from .core.agent import parse_date
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=days)).replace(hour=0, minute=0, second=0, microsecond=0)
    filtered = [item for item in knowledge if parse_date(item.get('date', '')) >= cutoff]
    synthesized = agent.synthesize_reports(filtered)
    start_date = cutoff.strftime('%Y-%m-%d')
    end_date = now.strftime('%Y-%m-%d')
    date_range = f'{start_date} to {end_date}'
    bridge = GitHubBridge()
    bridge.post_report(synthesized.get('items', []), tldr=synthesized.get('tldr'), date_range=date_range)

@app.command()
def serve():
    """Launch the AI Agent service."""
    typer.echo("Service mode is currently under maintenance. Use 'report' for local testing.")

@app.command()
def version():
    """Show version."""
    typer.echo('AI TPC Agent v0.1.0 (ADK Powered)')
if __name__ == '__main__':
    app()