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
            self.context_cache = ContextCacheConfig(ttl_seconds=3600)

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

        # Color Mapping System
        color_map = {
            'Gemini': '#4f46e5',   # Indigo
            'Vertex': '#0ea5e9',   # Sky Blue
            'Security': '#e11d48', # Rose/Red
            'Agent': '#10b981',    # Emerald
            'Infrastructure': '#64748b', # Slate
            'Search': '#f59e0b'    # Amber
        }

        sections = ''
        for source, items in grouped_knowledge.items():
            # Determine section color
            card_color = '#4285F4' # Default Google Blue
            for key, val in color_map.items():
                if key.lower() in source.lower():
                    card_color = val
                    break

            sections += f'\n            <div style="margin-top: 40px; margin-bottom: 20px;">\n                <h2 style="color: {card_color}; font-size: 1.1em; text-transform: uppercase; letter-spacing: 1px; border-bottom: 3px solid {card_color}33; padding-bottom: 8px;">\n                    📦 {source}\n                </h2>\n            </div>\n            '
            for item in items:
                bridge = item.get('bridge', 'New roadmap update detected.')
                # Tag color logic
                tags_html = ''
                item_tags = item.get('tags', [])
                for t in item_tags:
                    tag_bg = '#f1f3f4'
                    tag_text = '#5f6368'
                    if 'Security' in t: tag_bg, tag_text = '#fee2e2', '#b91c1c'
                    elif 'Governance' in t: tag_bg, tag_text = '#e0e7ff', '#4338ca'
                    elif 'Performance' in t: tag_bg, tag_text = '#ecfdf5', '#047857'
                    
                    tags_html += f'<span style="background-color: {tag_bg}; color: {tag_text}; padding: 3px 10px; border-radius: 12px; font-size: 0.75em; margin-right: 5px; font-weight: 500;">{t}</span>'

                # Premium Flashcard Layout (Interactive Expand)
                sections += f'''
                <div style="margin-bottom: 25px; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; overflow: hidden; transition: transform 0.2s;">
                    <div style="border-top: 6px solid {card_color}; padding: 25px;">
                        <h3 style="margin: 0 0 12px 0; color: #111827; font-size: 1.2em; font-weight: 600;">{item['title']}</h3>
                        <div style="margin-bottom: 18px;">{tags_html}</div>
                        
                        <!-- Front of Card: Actionable Insight -->
                        <div style="background-color: {card_color}08; padding: 15px; border-radius: 8px; border-left: 4px solid {card_color}; margin-bottom: 0;">
                            <p style="margin: 0; font-weight: 700; color: {card_color}; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px;">🚀 FIELD IMPACT</p>
                            <p style="margin: 8px 0 0 0; color: #374151; font-weight: 500; line-height: 1.5;">{bridge}</p>
                        </div>

                        <!-- Interactive Back of Card (Expandable Section) -->
                        <details style="margin-top: 15px; cursor: pointer;">
                            <summary style="font-size: 0.85em; font-weight: 600; color: {card_color}; outline: none; list-style: none;">
                                <span style="display: inline-block; padding: 6px 12px; border: 1px solid {card_color}4d; border-radius: 6px; background-color: white;">
                                    🔄 Flip for Technical Specs
                                </span>
                            </summary>
                            <div style="margin-top: 15px; padding: 15px; background-color: #f9fafb; border-radius: 8px; border: 1px dashed #d1d5db; color: #4b5563; font-size: 0.9em; line-height: 1.6; white-space: pre-wrap;">
                                {item.get('summary', 'Technical specifications for this update are being finalized.')}
                            </div>
                        </details>

                        <div style="margin-top: 20px;">
                            <a href="{item.get('source_url', '#')}" style="display: inline-block; padding: 10px 20px; background-color: {card_color}; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 0.9em; box-shadow: 0 2px 4px {card_color}33;">Open Full Documentation</a>
                        </div>
                    </div>
                </div>
                '''

        tldr_sec = f'''
        <div style="background-color: #fffbeb; border: 1px solid #fde68a; padding: 25px; border-radius: 12px; margin-bottom: 40px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">
            <h2 style="margin: 0 0 12px 0; color: #92400e; font-size: 1.1em; display: flex; align-items: center;">
                <span style="font-size: 1.4em; margin-right: 10px;">🎯</span> Executive Synthesis
            </h2>
            <p style="margin: 0; color: #451a03; font-weight: 400; line-height: 1.6; font-size: 1em;">{tldr}</p>
        </div>
        ''' if tldr else ''

        date_line = f"<p style='margin: 12px 0 0 0; font-size: 0.95em; opacity: 0.85; font-weight: 300;'>Pulse Period: {date_range}</p>" if date_range else ''

        return f"""
        <html>
            <head>
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
                    body {{ font-family: 'Inter', system-ui, -apple-system, sans-serif !important; }}
                    summary::-webkit-details-marker {{ display: none; }}
                </style>
            </head>
            <body style="font-family: 'Inter', sans-serif; line-height: 1.6; color: #111827; background-color: #f3f4f6; padding: 20px;">
                <div style="max-width: 800px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);">
                    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); color: white; padding: 50px 40px; text-align: center;">
                        <h1 style="margin: 0; font-size: 2.2em; font-weight: 800; letter-spacing: -1px;">📡 AI TPC FIELD PULSE</h1>
                        <p style="margin: 12px 0 0 0; font-size: 1.1em; font-weight: 400; opacity: 0.9;">Premium Intel for Google Cloud Architects</p>
                        {date_line}
                    </div>
                    <div style="padding: 50px 40px;">
                        {tldr_sec}
                        <p style="color: #6b7280; margin-bottom: 35px; font-weight: 500;">Hello Team, the TPC Agent has synthesized the following high-impact shifts in the ecosystem:</p>
                        {sections}
                    </div>
                    <div style="background-color: #f9fafb; padding: 40px; text-align: center; border-top: 1px solid #e5e7eb;">
                        <p style="margin: 0; font-size: 0.9em; color: #4b5563;">
                            Synthesized by <strong style="color: #1a73e8;">AI TPC Agent</strong> using Gemini 2.5 Flash
                        </p>
                        <p style="margin: 12px 0 0 0; font-size: 0.8em; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px;">
                            Mission Critical • Confidential • Field Pulse
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """