import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from rich.console import Console

console = Console()

class EmailBridge:
    """
    Bridge to send AI TPC reports via Email.
    """
    def __init__(self, recipient: str, sender_email: str = None, sender_password: str = None, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.recipient = recipient
        self.sender_email = sender_email or os.environ.get('TPC_SENDER_EMAIL')
        self.sender_password = sender_password or os.environ.get('TPC_SENDER_PASSWORD')
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def post_report(self, knowledge: List[Dict[str, Any]]):
        """
        Formats and sends the report via Email.
        """
        if not self.sender_email or not self.sender_password:
            console.print("[red]Error: Email credentials (TPC_SENDER_EMAIL/TPC_SENDER_PASSWORD) not set.[/red]")
            return

        if not knowledge:
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = f"AI TPC Agent <{self.sender_email}>"
            msg['To'] = self.recipient
            msg['Subject'] = f"🚀 AI TPC Pulse: {len(knowledge)} New Updates detected"

            # Create HTML content
            html_content = self._format_html_report(knowledge)
            msg.attach(MIMEText(html_content, 'html'))

            # Send Email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            console.print(f"[green]Successfully emailed report to {self.recipient}.[/green]")
        except Exception as e:
            console.print(f"[red]Failed to send email: {e}[/red]")

    def _format_html_report(self, knowledge: List[Dict[str, Any]]) -> str:
        # Use simple logic since TPCAgent logic is in core/agent.py
        # We'll just define a static helper or import it if possible
        # For simplicity and isolation, we redefine the enhanced heuristics here
        
        rows = ""
        for item in knowledge:
            bridge = item.get('bridge', "New roadmap update detected. Review impacts on developer velocity.")

            rows += f"""
            <div style="margin-bottom: 25px; padding: 20px; border-left: 6px solid #4285F4; background-color: #ffffff; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h3 style="margin-top: 0; color: #1a73e8; font-size: 1.2em;">{item['title']}</h3>
                <p style="font-size: 0.85em; color: #70757a; margin-bottom: 10px;">
                    <strong>Source:</strong> {item.get('description', item.get('source', 'Unknown'))} | 
                    <strong>Category:</strong> {item['category'].upper()}
                </p>
                <div style="background-color: #e8f0fe; padding: 12px; border-radius: 4px; border: 1px solid #d2e3fc; margin-bottom: 15px;">
                    <p style="margin: 0; font-weight: bold; color: #1967d2;">🚀 Field Impact:</p>
                    <p style="margin: 5px 0 0 0;">{bridge}</p>
                </div>
                <p style="color: #3c4043; line-height: 1.5;">{item.get('summary', '')[:500]}...</p>
                <div style="margin-top: 15px;">
                    <a href="{item.get('source_url', '#')}" style="display: inline-block; padding: 10px 20px; background-color: #1a73e8; color: white; text-decoration: none; border-radius: 4px; font-weight: bold;">Open Full Documentation</a>
                </div>
            </div>
            """

        return f"""
        <html>
            <body style="font-family: 'Google Sans', Roboto, Arial, sans-serif; line-height: 1.6; color: #202124; background-color: #f1f3f4; padding: 20px;">
                <div style="max-width: 800px; margin: 0 auto;">
                    <div style="background-color: #1a73e8; color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center;">
                        <h1 style="margin: 0;">🚀 AI TPC Field Pulse</h1>
                        <p style="margin: 10px 0 0 0; font-size: 1.1em;">Latest Google AI Roadmap & Market Trends</p>
                    </div>
                    <div style="background-color: #ffffff; padding: 30px; border-radius: 0 0 8px 8px;">
                        <p>Hello Team, here are the latest synthesized updates for the field:</p>
                        <hr style="border: 0; border-top: 1px solid #dadce0; margin: 25px 0;">
                        {rows}
                    </div>
                    <div style="text-align: center; margin-top: 20px; font-size: 0.8em; color: #70757a;">
                        <p>Synthesized by <strong>AI TPC Agent</strong></p>
                        <p>This is an automated report. For support, contact the TPC team.</p>
                    </div>
                </div>
            </body>
        </html>
        """
