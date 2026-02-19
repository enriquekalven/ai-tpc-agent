from typing import Literal
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
    def post_report(self, knowledge: List[Dict[str, Any]], tldr: str=None, date_range: str=None, infographic_path: str=None):
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
            
            # Embed image if provided
            infographic_cid = None
            if infographic_path and os.path.exists(infographic_path):
                from email.mime.image import MIMEImage
                infographic_cid = 'infographic_image'
                with open(infographic_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header('Content-ID', f'<{infographic_cid}>')
                    img.add_header('Content-Disposition', 'inline', filename=os.path.basename(infographic_path))
                    msg.attach(img)

            html_content = self._format_html_report(knowledge, tldr, date_range, infographic_cid=infographic_cid)
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

    def _format_html_report(self, knowledge: List[Dict[str, Any]], tldr: str=None, date_range: str=None, infographic_cid: str=None) -> str:
        grouped_knowledge = {}
        for item in knowledge:
            source = item.get('source', 'General Update').replace('-', ' ').title()
            if source not in grouped_knowledge:
                grouped_knowledge[source] = []
            grouped_knowledge[source].append(item)

        # Enhanced Color Mapping
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
            card_color = '#4285F4' # Default Google Blue
            for key, val in color_map.items():
                if key.lower() in source.lower():
                    card_color = val
                    break

            sections += f'\n            <div style="margin-top: 50px; margin-bottom: 25px;">\n                <h2 style="color: {card_color}; font-size: 1.1em; text-transform: uppercase; font-weight: 800; letter-spacing: 2px; border-left: 5px solid {card_color}; padding-left: 15px;">\n                    {source}\n                </h2>\n            </div>\n            '
            for item in items:
                bridge = item.get('bridge', 'New roadmap update detected.')
                tags_html = ''
                item_tags = item.get('tags', [])
                
                # Priority Detection
                priority_color = '#64748b' # Default Slate
                priority_label = 'STANDARD'
                if any(x in str(item_tags) for x in ['Security', 'Governance']):
                    priority_color = '#e11d48'
                    priority_label = 'MISSION CRITICAL'
                elif 'Performance' in str(item_tags):
                    priority_color = '#f59e0b'
                    priority_label = 'HIGH IMPACT'

                for t in item_tags:
                    tags_html += f'<span style="background-color: #f1f3f4; color: #5f6368; padding: 4px 10px; border-radius: 4px; font-size: 0.7em; margin-right: 6px; font-weight: 700; text-transform: uppercase;">{t}</span>'

                # Premium Dual-Face Flashcard (Folded Design for maximum compatibility)
                sections += f'''
                <div style="margin-bottom: 40px; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border: 1px solid #e5e7eb; background-color: #ffffff;">
                    
                    <!-- TOP SECTION: THE FRONT (Sales/Field) -->
                    <div style="padding: 30px; border-top: 8px solid {card_color};">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
                            <h3 style="margin: 0; color: #111827; font-size: 1.3em; font-weight: 800; flex: 1; line-height: 1.2;">{item['title']}</h3>
                            <span style="background-color: {priority_color}15; color: {priority_color}; padding: 4px 8px; border-radius: 4px; font-size: 0.65em; font-weight: 900; letter-spacing: 0.05em; margin-left: 15px; border: 1px solid {priority_color}33;">{priority_label}</span>
                        </div>
                        <div style="margin-bottom: 20px;">{tags_html}</div>
                        
                        <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; border-left: 4px solid {card_color};">
                            <p style="margin: 0; font-weight: 800; color: {card_color}; font-size: 0.75em; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">🚀 FIELD FRONT: IMPACT & ACTION</p>
                            <p style="margin: 0; color: #1e293b; font-weight: 500; font-size: 1.1em; line-height: 1.5;">{bridge}</p>
                        </div>
                    </div>

                    <!-- REVERSE SECTION: THE BACK (Technical Deep Dive) -->
                    <div style="background-color: #1e293b; color: #e2e8f0; padding: 25px 30px;">
                        <div style="display: flex; align-items: center; margin-bottom: 15px; opacity: 0.9;">
                            <span style="font-size: 1.2em; margin-right: 10px;">⚙️</span>
                            <span style="font-size: 0.75em; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">TECHNICAL SPECIFICATIONS</span>
                        </div>
                        <div style="color: #94a3b8; font-size: 0.9em; line-height: 1.7; font-family: 'Roboto Mono', monospace;">
                            {item.get('summary', 'Detailed technical alignment for this release is currently being processed by the TPC Agent.')}
                        </div>
                        <div style="margin-top: 25px; border-top: 1px solid #334155; padding-top: 20px;">
                            <a href="{item.get('source_url', '#')}" style="display: inline-block; padding: 12px 24px; background-color: #384455; color: white; text-decoration: none; border-radius: 6px; font-weight: 700; font-size: 0.85em; border: 1px solid #475569; transition: background 0.2s;">Open Engineering Docs</a>
                        </div>
                    </div>
                </div>
                '''

        infographic_sec = f'''
        <div style="margin-bottom: 45px; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 2px solid #e2e8f0;">
            <div style="background-color: #f8fafc; padding: 15px 20px; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center;">
                <span style="font-size: 1.2em; margin-right: 10px;">📊</span>
                <span style="font-size: 0.75em; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; color: #64748b;">Visual Strategy Synthesis</span>
            </div>
            <img src="cid:{infographic_cid}" alt="Strategic Infographic" style="width: 100%; display: block; background-color: #f1f5f9;">
        </div>
        ''' if infographic_cid else ''

        tldr_sec = f'''
        <div style="background: linear-gradient(to right, #fffbeb, #fef3c7); border: 2px solid #fde68a; padding: 30px; border-radius: 16px; margin-bottom: 45px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <div style="background-color: #fbbf24; color: #92400e; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.4em; margin-right: 15px;">🎯</div>
                <h2 style="margin: 0; color: #92400e; font-size: 1.25em; font-weight: 800; letter-spacing: -0.5px;">Executive Synthesis</h2>
            </div>
            <p style="margin: 0; color: #451a03; font-weight: 500; line-height: 1.7; font-size: 1.1em; font-style: italic;">"{tldr}"</p>
        </div>
        ''' if tldr else ''

        date_line = f"<div style='margin-top: 15px; display: inline-block; background-color: rgba(255,255,255,0.15); padding: 5px 15px; border-radius: 20px; font-size: 0.85em; font-weight: 500;'>ACTIVE PULSE: {date_range}</div>" if date_range else ''

        return f"""
        <html>
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&family=Roboto+Mono&display=swap" rel="stylesheet">
            </head>
            <body style="font-family: 'Inter', -apple-system, sans-serif; line-height: 1.6; color: #111827; background-color: #f1f5f9; padding: 20px; margin: 0;">
                <div style="max-width: 800px; margin: 40px auto; background-color: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15);">
                    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%); color: white; padding: 60px 50px; text-align: left;">
                        <h1 style="margin: 0; font-size: 2.6em; font-weight: 800; letter-spacing: -1.5px; text-transform: uppercase;">📡 AI TPC FIELD PULSE</h1>
                        <p style="margin: 10px 0 0 0; font-size: 1.2em; font-weight: 300; opacity: 0.8; letter-spacing: 0.5px;">Synthesized Intel for High-Velocity Teams</p>
                        {date_line}
                    </div>
                    <div style="padding: 60px 50px;">
                        {infographic_sec}
                        {tldr_sec}
                        <p style="color: #64748b; margin-bottom: 40px; font-weight: 600; font-size: 1em; text-transform: uppercase; letter-spacing: 1.5px;">Latest Roadmap Transitions</p>
                        {sections}
                    </div>
                    <div style="background-color: #0f172a; padding: 50px; text-align: center; color: white;">
                        <p style="margin: 0; font-size: 0.9em; color: #94a3b8; font-weight: 500;">
                            Generated by <strong style="color: #3b82f6;">AI TPC Agent</strong> • Gemini 2.5 Flash Engine
                        </p>
                        <p style="margin: 15px 0 0 0; font-size: 0.75em; color: #475569; text-transform: uppercase; letter-spacing: 2.5px; font-weight: 700;">
                            MISSION CRITICAL • GOOGLE CLOUD CONFIDENTIAL
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """