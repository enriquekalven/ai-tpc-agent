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
    def post_report(self, knowledge: List[Dict[str, Any]], tldr: str=None, date_range: str=None, infographic_path: str=None, gaps: str=None):
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

            html_content = self._format_html_report(knowledge, tldr, date_range, infographic_cid=infographic_cid, gaps=gaps)
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

    def _format_html_report(self, knowledge: List[Dict[str, Any]], tldr: str=None, date_range: str=None, infographic_cid: str=None, gaps: str=None) -> str:
        grouped_knowledge = {}
        for item in knowledge:
            source = item.get('source', 'General Update').replace('-', ' ').title()
            if source not in grouped_knowledge:
                grouped_knowledge[source] = []
            grouped_knowledge[source].append(item)

        # Designer Color Palette
        color_map = {
            'Gemini': '#6366f1',   # Indigo 500
            'Vertex': '#0ea5e9',   # Sky 500
            'Security': '#f43f5e', # Rose 500
            'Agent': '#10b981',    # Emerald 500
            'Infrastructure': '#64748b', # Slate 500
            'Search': '#f59e0b',   # Amber 500
            'Openai': '#10a37f',   # OpenAI Green
            'Anthropic': '#cc785c' # Anthropic Tan/Orange
        }

        sections = ''
        for source, items in grouped_knowledge.items():
            card_color = '#3b82f6' # Blue 500
            for key, val in color_map.items():
                if key.lower() in source.lower():
                    card_color = val
                    break

            sections += f'''
            <div style="margin-top: 40px; margin-bottom: 20px;">
                <h2 style="color: {card_color}; font-size: 0.85rem; text-transform: uppercase; font-weight: 800; letter-spacing: 0.1em; margin: 0; display: inline-block; padding-bottom: 4px; border-bottom: 2px solid {card_color};">
                    {source}
                </h2>
            </div>
            '''
            for item in items:
                bridge = item.get('bridge', 'Strategizing field alignment...')
                tags_html = ''
                item_tags = item.get('tags', [])
                
                # Priority Logic
                p_bg, p_fg, p_label = '#f1f5f9', '#64748b', 'Standard'
                if any(x in str(item_tags) for x in ['Security', 'Governance']):
                    p_bg, p_fg, p_label = '#fff1f2', '#e11d48', 'Mission Critical'
                elif 'Performance' in str(item_tags):
                    p_bg, p_fg, p_label = '#fffbeb', '#d97706', 'High Impact'

                for t in item_tags:
                    tags_html += f'<span style="background-color: #f8fafc; color: #475569; padding: 2px 8px; border-radius: 9999px; font-size: 10px; margin-right: 4px; font-weight: 600; text-transform: uppercase; border: 1px solid #e2e8f0;">{t}</span>'

                sections += f'''
                <div style="margin-bottom: 24px; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 1px 3px 0 rgba(0,0,0,0.1);">
                    <div style="padding: 24px;">
                        <div style="margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                             <span style="font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em; color: {p_fg}; background-color: {p_bg}; padding: 2px 8px; border-radius: 4px;">{p_label}</span>
                             <div style="display: flex;">{tags_html}</div>
                        </div>
                        <h3 style="margin: 0 0 16px 0; color: #0f172a; font-size: 1.1rem; font-weight: 700; line-height: 1.3;">{item['title']}</h3>
                        
                        <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid {card_color};">
                             <p style="margin: 0; color: #334155; font-size: 0.95rem; font-weight: 500; line-height: 1.6;">{bridge}</p>
                        </div>

                        <div style="color: #64748b; font-size: 0.85rem; line-height: 1.6; margin-bottom: 20px;">
                            {item.get('summary', 'Technical analysis in progress.')}
                        </div>

                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <a href="{item.get('source_url', '#')}" style="font-size: 0.8rem; font-weight: 700; color: {card_color}; text-decoration: none; text-transform: uppercase; letter-spacing: 0.05em;">Engineering Docs &rarr;</a>
                            <span style="font-size: 10px; color: #94a3b8; font-weight: 500;">{item.get('date', '')[:10]}</span>
                        </div>
                    </div>
                </div>
                '''

        infographic_sec = f'''
        <div style="margin-bottom: 32px; border-radius: 12px; overflow: hidden; border: 1px solid #e2e8f0; background-color: #f8fafc;">
            <div style="padding: 12px 20px; border-bottom: 1px solid #e2e8f0; background-color: #ffffff; display: flex; align-items: center;">
                <span style="font-size: 14px; margin-right: 8px;">📊</span>
                <span style="font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #64748b;">Perspective: Strategic Infographic</span>
            </div>
            <img src="cid:{infographic_cid}" alt="Strategic Synthesis" style="width: 100%; display: block; max-height: 500px; object-fit: contain;">
        </div>
        ''' if infographic_cid else ''

        tldr_sec = f'''
        <div style="background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%); border: 1px solid #fde68a; padding: 24px; border-radius: 12px; margin-bottom: 32px;">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 18px; margin-right: 12px;">🎯</span>
                <h2 style="margin: 0; color: #92400e; font-size: 1rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;">Executive Synthesis</h2>
            </div>
            <p style="margin: 0; color: #78350f; font-weight: 500; line-height: 1.6; font-size: 1rem; font-style: italic;">{tldr}</p>
        </div>
        ''' if tldr else ''

        gaps_sec = f'''
        <div style="background: linear-gradient(135deg, #fdf2f2 0%, #fee2e2 100%); border: 1px solid #fecaca; padding: 24px; border-radius: 12px; margin-bottom: 32px;">
            <div style="display: flex; align-items: center; margin-bottom: 12px;">
                <span style="font-size: 18px; margin-right: 12px;">🛡️</span>
                <h2 style="margin: 0; color: #991b1b; font-size: 1rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.05em;">Strategic Battlecard: Gaps & Advantages</h2>
            </div>
            <div style="margin: 0; color: #7f1d1d; font-weight: 600; line-height: 1.6; font-size: 0.95rem;">
                {gaps.replace('\n', '<br>')}
            </div>
        </div>
        ''' if gaps else ''

        date_line = f"<div style='margin-top: 12px; opacity: 0.7; font-size: 0.8rem; font-weight: 500;'>{date_range}</div>" if date_range else ''

        return f"""
        <html>
            <head>
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=JetBrains+Mono&display=swap" rel="stylesheet">
            </head>
            <body style="font-family: 'Outfit', sans-serif; line-height: 1.6; color: #1e293b; background-color: #f1f5f9; padding: 20px; margin: 0;">
                <div style="max-width: 640px; margin: 0 auto;">
                    <header style="background-color: #0f172a; border-radius: 16px 16px 0 0; padding: 48px 32px; color: #ffffff; text-align: left;">
                        <div style="font-size: 10px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.2em; color: #38bdf8; margin-bottom: 12px;">Field Intelligence Report</div>
                        <h1 style="margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1;">AI TPC PULSE</h1>
                        {date_line}
                    </header>
                    <main style="background-color: #ffffff; padding: 32px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                        {infographic_sec}
                        {tldr_sec}
                        {gaps_sec}
                        <div style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #94a3b8; margin-bottom: 16px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;">Technical Roadmap Transitions</div>
                        {sections}
                    </main>
                    <footer style="padding: 40px 32px; text-align: center;">
                        <p style="margin: 0; font-size: 12px; color: #64748b; font-weight: 500;">
                            Synthesized by <strong>AI TPC Agent</strong> v0.1.2 • Powered by <strong>Gemini 2.5 Pro & Flash</strong>
                        </p>
                        <div style="margin-top: 16px; font-size: 9px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.2em; font-weight: 700;">
                            Google Cloud Confidential • Internal Use Only
                        </div>
                    </footer>
                </div>
            </body>
        </html>
        """