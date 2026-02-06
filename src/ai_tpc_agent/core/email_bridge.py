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
        rows = ""
        for item in knowledge:
            bridge = self._get_bridge_context(item['title'])
            rows += f"""
            <div style="margin-bottom: 20px; padding: 15px; border-left: 5px solid #4285F4; background-color: #f8f9fa;">
                <h3 style="margin-top: 0; color: #1a73e8;">{item['title']}</h3>
                <p style="font-size: 0.9em; color: #666;">Source: {item['description']} | Category: {item['category'].upper()}</p>
                <p><strong>Field Impact:</strong> {bridge}</p>
                <p>{item.get('summary', '')[:300]}...</p>
                <a href="{item.get('source_url', '#')}" style="display: inline-block; padding: 10px 15px; background-color: #4285F4; color: white; text-decoration: none; border-radius: 4px;">Open Documentation</a>
            </div>
            """

        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #0d6efd;">🚀 AI TPC Field Promotion Report</h2>
                <p>The following updates have been synthesized for the field team:</p>
                <hr>
                {rows}
                <br>
                <p style="font-size: 0.8em; color: #999;">Synthesized by AI TPC Agent | {os.name}</p>
            </body>
        </html>
        """

    def _get_bridge_context(self, title: str) -> str:
        title_lower = title.lower()
        if any(term in title_lower for term in ["agent", "builder"]):
            return "CRITICAL: Enhances Agent Builder. Focus on 'Low-Code to Pro-Code' transition story."
        if any(term in title_lower for term in ["gemini", "ge"]):
            return "GE UPDATE: New Gemini features. Highlight Context Window and Reasoning Engine."
        if any(term in title_lower for term in ["security", "compliance"]):
            return "GOVERNANCE: Addresses Enterprise Security. Use to unblock FinServ/Healthcare deals."
        return "New roadmap update detected. Review impacts on developer velocity."
