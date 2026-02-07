from tenacity import retry, wait_exponential, stop_after_attempt
try:
    from google.adk.agents.context_cache_config import ContextCacheConfig
except ImportError:
    ContextCacheConfig = None
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

    def __init__(self, recipient: str, sender_email: str=None, sender_password: str=None, smtp_server: str='smtp.gmail.com', smtp_port: int=587):
        self.recipient = recipient
        self.sender_email = sender_email or os.environ.get('TPC_SENDER_EMAIL')
        self.sender_password = sender_password or os.environ.get('TPC_SENDER_PASSWORD')
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.context_cache = None
        if ContextCacheConfig:
            self.context_cache = ContextCacheConfig(ttl_seconds=3600, cache_type='semantic')

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def post_report(self, knowledge: List[Dict[str, Any]], tldr: str=None, date_range: str=None):
        """
        Formats and sends the report via Email.
        """
        if not self.sender_email or not self.sender_password:
            console.print('[red]Error: Email credentials (TPC_SENDER_EMAIL/TPC_SENDER_PASSWORD) not set.[/red]')
            return
        if not knowledge:
            return
        try:
            msg = MIMEMultipart()
            msg['From'] = f'AI TPC Agent <{self.sender_email}>'
            msg['To'] = self.recipient
            subject = f'📡 AI TPC Pulse: {len(knowledge)} New Technical Updates'
            if date_range:
                subject += f' ({date_range})'
            msg['Subject'] = subject
            html_content = self._format_html_report(knowledge, tldr, date_range)
            msg.attach(MIMEText(html_content, 'html'))
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=15)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            console.print(f'[green]Successfully emailed report to {self.recipient}.[/green]')
        except Exception as e:
            console.print(f'[red]Failed to send email: {e}[/red]')
            raise e

    def _format_html_report(self, knowledge: List[Dict[str, Any]], tldr: str=None, date_range: str=None) -> str:
        grouped_knowledge = {}
        for item in knowledge:
            source = item.get('source', 'General Update').replace('-', ' ').title()
            if source not in grouped_knowledge:
                grouped_knowledge[source] = []
            grouped_knowledge[source].append(item)
        sections = ''
        for source, items in grouped_knowledge.items():
            sections += f'\n            <div style="margin-top: 40px; margin-bottom: 20px;">\n                <h2 style="color: #5f6368; font-size: 1.1em; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #e8eaed; padding-bottom: 8px;">\n                    📦 {source}\n                </h2>\n            </div>\n            '
            for item in items:
                bridge = item.get('bridge', 'New roadmap update detected. Review impacts on developer velocity.')
                tags_html = ''.join([f'<span style="background-color: #f1f3f4; color: #5f6368; padding: 2px 8px; border-radius: 12px; font-size: 0.75em; margin-right: 5px; border: 1px solid #dadce0;">{t}</span>' for t in item.get('tags', [])])
                sections += f'''
                <div style="margin-bottom: 25px; padding: 20px; border-left: 6px solid #4285F4; background-color: #ffffff; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-top: 1px solid #f1f3f4; border-right: 1px solid #f1f3f4; border-bottom: 1px solid #f1f3f4;">
                    <h3 style="margin-top: 0; color: #1a73e8; font-size: 1.15em;">{item['title']}</h3>
                    <div style="margin-bottom: 15px;">{tags_html}</div>
                    <div style="background-color: #e8f0fe; padding: 12px; border-radius: 4px; border: 1px solid #d2e3fc; margin-bottom: 15px;">
                        <p style="margin: 0; font-weight: bold; color: #1967d2; font-size: 0.9em;">🚀 FIELD IMPACT:</p>
                        <p style="margin: 5px 0 0 0; color: #202124;">{bridge}</p>
                    </div>
                    <div style="color: #3c4043; line-height: 1.6; font-size: 0.95em; white-space: pre-wrap; margin-bottom: 15px;">{item.get('summary', '')}</div>
                    <div style="margin-top: 15px;">
                        <a href="{item.get('source_url', '#')}" style="display: inline-block; padding: 8px 16px; background-color: #1a73e8; color: white; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 0.9em;">Open Documentation</a>
                    </div>
                </div>
                '''
        tldr_sec = f'\n        <div style="background-color: #fff7e6; border: 1px solid #ffe7ba; padding: 20px; border-radius: 8px; margin-bottom: 30px;">\n            <h2 style="margin-top: 0; color: #d46b08; font-size: 1.1em;">🎯 Executive TLDR</h2>\n            <p style="margin: 0; color: #595959; font-style: italic; line-height: 1.5;">{tldr}</p>\n        </div>\n        ' if tldr else ''
        date_line = f"<p style='margin: 10px 0 0 0; font-size: 0.9em; opacity: 0.8;'>Pulse Period: {date_range}</p>" if date_range else ''
        return f"""\n        <html>\n            <body style="font-family: 'Google Sans', Roboto, Arial, sans-serif; line-height: 1.6; color: #202124; background-color: #f8f9fa; padding: 20px;">\n                <div style="max-width: 800px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">\n                    <div style="background-color: #1a73e8; color: white; padding: 40px 30px; text-align: center;">\n                        <h1 style="margin: 0; font-size: 2em; letter-spacing: -0.5px;">🚀 AI TPC Field Pulse</h1>\n                        <p style="margin: 10px 0 0 0; font-size: 1.1em; font-weight: 300; opacity: 0.9;">Synthesized Intel for Google Cloud AI Teams</p>\n                        {date_line}\n                    </div>\n                    <div style="padding: 40px 30px;">\n                        {tldr_sec}\n                        <p style="color: #5f6368; margin-bottom: 30px;">Hello Team, here are the latest synthesized updates grouped by service stream:</p>\n                        {sections}\n                    </div>\n                    <div style="background-color: #f8f9fa; padding: 30px; text-align: center; border-top: 1px solid #dadce0;">\n                        <p style="margin: 0; font-size: 0.85em; color: #70757a;">\n                            Synthesized by <strong>AI TPC Agent</strong> using Gemini 2.0 Flash\n                        </p>\n                        <p style="margin: 10px 0 0 0; font-size: 0.8em; color: #9aa0a6;">\n                            This is an automated field enablement pulse.\n                        </p>\n                    </div>\n                </div>\n            </body>\n        </html>\n        """