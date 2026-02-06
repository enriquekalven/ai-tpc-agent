from tenacity import retry, wait_exponential, stop_after_attempt
import urllib.request
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Optional
from datetime import datetime, timezone
import os

def clean_version(v_str: str) -> str:
    match = re.search('(\\d+\\.\\d+(?:\\.\\d+)?(?:[a-zA-Z]+\\d+)?)', v_str)
    if match:
        return match.group(1)
    return v_str.strip().lstrip('v')

def parse_html_date(date_str: str) -> Optional[datetime]:
    """Parses dates like 'February 06, 2026' or 'Feb 06, 2026'."""
    formats = ["%B %d, %Y", "%b %d, %Y"]
    clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str).strip()
    for fmt in formats:
        try:
            return datetime.strptime(clean_date, fmt).replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def fetch_recent_updates(url: str, max_items: int = 5) -> List[Dict[str, str]]:
    """
    Fetches the most recent updates from an Atom, RSS, or HTML page.
    """
    if any(url.endswith(ext) for ext in ['.xml', '.atom', '.rss']):
        return _fetch_from_feed(url, max_items)
    
    return _fetch_from_html(url, max_items)

def _fetch_from_feed(url: str, max_items: int = 5) -> List[Dict[str, str]]:
    updates = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            ns_match = re.match(r'\{(.*)\}', root.tag)
            ns = {'ns': ns_match.group(1)} if ns_match else {}
            
            def find_nodes(parent, tag):
                if not ns: return parent.findall(tag)
                return parent.findall(f'ns:{tag}', ns)

            def find_node(parent, tag):
                if not ns: return parent.find(tag)
                return parent.find(f'ns:{tag}', ns)

            # Check if it's Atom
            entries = find_nodes(root, 'entry')
            if entries:
                for entry in entries[:max_items]:
                    title_node = find_node(entry, 'title')
                    updated_node = find_node(entry, 'updated')
                    content_node = find_node(entry, 'content') or find_node(entry, 'summary')
                    link_node = find_node(entry, 'link')

                    title = title_node.text if title_node is not None else "Untitled Update"
                    updated = updated_node.text if updated_node is not None else "N/A"
                    summary = "".join(content_node.itertext()).strip()[:500] if content_node is not None else ""
                    source_url = link_node.get('href', url) if link_node is not None else url

                    updates.append({
                        'version': "N/A",
                        'date': updated,
                        'title': title,
                        'summary': summary,
                        'source_url': source_url
                    })
                return updates
            
            # Check if it's RSS
            channel = root.find('channel')
            if channel is not None:
                items = channel.findall('item')
                for item in items[:max_items]:
                    title = item.find('title').text if item.find('title') is not None else "Untitled"
                    date = item.find('pubDate').text if item.find('pubDate') is not None else "N/A"
                    summary = item.find('description').text if item.find('description') is not None else ""
                    summary = re.sub('<[^>]+>', '', summary).strip()[:500]
                    link = item.find('link').text if item.find('link') is not None else url
                    
                    updates.append({
                        'title': title,
                        'date': date,
                        'summary': summary,
                        'source_url': link,
                        'version': "N/A"
                    })
                return updates
    except Exception:
        pass
    return []

def _fetch_from_html(url: str, max_items: int = 5) -> List[Dict[str, str]]:
    updates = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')
            
            # Identify date headers
            date_pattern = r'([A-Z][a-z]+\s+\d{1,2},\s+\d{4})'
            
            # Find all potential date strings in the page
            all_dates = []
            for m in re.finditer(date_pattern, content):
                date_str = m.group(1)
                dt = parse_html_date(date_str)
                if dt and date_str not in [d[0] for d in all_dates]:
                    all_dates.append((date_str, dt, m.start()))

            # Sort by position in document
            all_dates.sort(key=lambda x: x[2])
            
            for i in range(len(all_dates)):
                date_str, dt, start_pos = all_dates[i]
                end_pos = all_dates[i+1][2] if i+1 < len(all_dates) else len(content)
                
                block = content[start_pos:end_pos]
                # Clean block
                clean_block = re.sub(r'<(?:script|style)[^>]*>.*?</(?:script|style)>', '', block, flags=re.DOTALL)
                clean_block = re.sub(r'<[^>]+>', '\n', clean_block)
                lines = [l.strip() for l in clean_block.split('\n') if l.strip()]
                
                if len(lines) > 1:
                    # Skip the date line itself if it matches
                    first_line = lines[0]
                    if date_str in first_line:
                        lines = lines[1:]
                    
                    if not lines: continue
                    
                    title = lines[0]
                    # If title is just a category, combine with next
                    if title.lower() in ["feature", "announcement", "changed", "fixed", "deprecated"] and len(lines) > 1:
                        title = f"{title}: {lines[1]}"
                        summary = " ".join(lines[2:10])[:500]
                    else:
                        summary = " ".join(lines[1:10])[:500]
                    
                    updates.append({
                        'title': title,
                        'date': dt.isoformat(),
                        'summary': summary,
                        'source_url': f"{url}#{date_str.replace(' ', '_').replace(',', '')}",
                        'version': "N/A"
                    })
                    if len(updates) >= max_items: break
        return updates
    except Exception:
        return []

def fetch_latest_from_atom(url: str) -> Optional[Dict[str, str]]:
    updates = fetch_recent_updates(url, max_items=1)
    return updates[0] if updates else None
