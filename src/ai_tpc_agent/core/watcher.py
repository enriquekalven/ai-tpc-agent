from tenacity import retry, wait_exponential, stop_after_attempt
import urllib.request
import xml.etree.ElementTree as ET
import re
from typing import Dict, Optional

def clean_version(v_str: str) -> str:
    """Extracts a clean version number from strings like 'v1.2.3', 'package==1.2.3', '2026-01-28 (v0.1.0)'"""
    match = re.search('(\\d+\\.\\d+(?:\\.\\d+)?(?:[a-zA-Z]+\\d+)?)', v_str)
    if match:
        return match.group(1)
    return v_str.strip().lstrip('v')

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def fetch_latest_from_atom(url: str) -> Optional[Dict[str, str]]:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            ns = {'ns': 'http://www.w3.org/2005/Atom', 'default': 'http://www.w3.org/2005/Atom'}
            
            # Try to handle both namespaced and non-namespaced Atom feeds
            latest_entry = root.find('ns:entry', ns) or root.find('entry')
            if latest_entry is not None:
                title_node = latest_entry.find('ns:title', ns) or latest_entry.find('title')
                updated_node = latest_entry.find('ns:updated', ns) or latest_entry.find('updated')
                content_node = latest_entry.find('ns:content', ns) or latest_entry.find('content')
                link_node = latest_entry.find('ns:link', ns) or latest_entry.find('link') or latest_entry.find("{http://www.w3.org/2005/Atom}link")

                title = title_node.text if title_node is not None else "Untitled"
                updated = updated_node.text if updated_node is not None else "N/A"
                
                summary = ""
                if content_node is not None:
                    summary = re.sub('<[^<]+?>', '', content_node.text or '')[:500].strip()
                    if len(summary) >= 500: summary += "..."
                
                source_url = ""
                if link_node is not None:
                    source_url = link_node.get('href', '')

                raw_v = title.strip().split()[-1]
                return {
                    'version': clean_version(raw_v) if '==' not in raw_v else clean_version(raw_v.split('==')[-1]),
                    'date': updated,
                    'title': title,
                    'summary': summary,
                    'source_url': source_url
                }
    except Exception as e:
        # Fallback for RSS feeds
        try:
             req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
             with urllib.request.urlopen(req, timeout=10) as response:
                 tree = ET.parse(response)
                 root = tree.getroot()
                 channel = root.find('channel')
                 if channel is not None:
                     item = channel.find('item')
                     if item is not None:
                         return {
                             'title': item.find('title').text,
                             'date': item.find('pubDate').text if item.find('pubDate') is not None else "N/A",
                             'summary': item.find('description').text[:500] if item.find('description') is not None else "",
                             'source_url': item.find('link').text if item.find('link') is not None else "",
                             'version': "N/A"
                         }
        except Exception:
             return None
    return None
