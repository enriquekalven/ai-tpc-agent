from tenacity import retry, wait_exponential, stop_after_attempt
import urllib.request
import xml.etree.ElementTree as ET
import re
from typing import Dict, List, Optional
from datetime import datetime

def clean_version(v_str: str) -> str:
    match = re.search('(\\d+\\.\\d+(?:\\.\\d+)?(?:[a-zA-Z]+\\d+)?)', v_str)
    if match:
        return match.group(1)
    return v_str.strip().lstrip('v')

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def fetch_recent_updates(url: str, max_items: int = 5) -> List[Dict[str, str]]:
    """
    Fetches the most recent updates from an Atom or RSS feed.
    """
    updates = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            
            # Robust namespace handling
            ns_match = re.match(r'\{(.*)\}', root.tag)
            ns = {'ns': ns_match.group(1)} if ns_match else {}
            
            def find_nodes(parent, tag):
                if not ns:
                    return parent.findall(tag)
                return parent.findall(f'ns:{tag}', ns)

            def find_node(parent, tag):
                if not ns:
                    return parent.find(tag)
                return parent.find(f'ns:{tag}', ns)

            entries = find_nodes(root, 'entry')
            for entry in entries[:max_items]:
                title_node = find_node(entry, 'title')
                updated_node = find_node(entry, 'updated')
                content_node = find_node(entry, 'content') or find_node(entry, 'summary')
                link_node = find_node(entry, 'link')

                title = title_node.text if title_node is not None else "Untitled Update"
                updated = updated_node.text if updated_node is not None else "N/A"
                
                summary = ""
                if content_node is not None:
                    summary = re.sub('<[^<]+?>', '', content_node.text or '')[:500].strip()
                    if len(summary) >= 500: summary += "..."
                
                source_url = ""
                if link_node is not None:
                    source_url = link_node.get('href', '')

                raw_v = title.strip().split()[-1]
                updates.append({
                    'version': clean_version(raw_v) if '==' in title else "N/A",
                    'date': updated,
                    'title': title,
                    'summary': summary,
                    'source_url': source_url
                })
            
            if updates:
                return updates

    except Exception:
        # Fallback for RSS
        try:
             req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
             with urllib.request.urlopen(req, timeout=10) as response:
                 tree = ET.parse(response)
                 root = tree.getroot()
                 channel = root.find('channel')
                 if channel is not None:
                     items = channel.findall('item')
                     for item in items[:max_items]:
                         updates.append({
                             'title': item.find('title').text,
                             'date': item.find('pubDate').text if item.find('pubDate') is not None else "N/A",
                             'summary': item.find('description').text[:500] if item.find('description') is not None else "",
                             'source_url': item.find('link').text if item.find('link') is not None else "",
                             'version': "N/A"
                         })
                     return updates
        except Exception:
             return []
    return []

# Maintain backward compatibility
def fetch_latest_from_atom(url: str) -> Optional[Dict[str, str]]:
    updates = fetch_recent_updates(url, max_items=1)
    return updates[0] if updates else None
