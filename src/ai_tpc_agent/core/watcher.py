from tenacity import retry, wait_exponential, stop_after_attempt
import urllib.request
import xml.etree.ElementTree as ET
import re
from typing import Dict, Optional

def clean_version(v_str: str) -> str:
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
            
            # Robust namespace handling
            ns_match = re.match(r'\{(.*)\}', root.tag)
            ns = {'ns': ns_match.group(1)} if ns_match else {}
            
            def find_node(parent, tag):
                if not ns:
                    return parent.find(tag)
                return parent.find(f'ns:{tag}', ns)

            latest_entry = find_node(root, 'entry')
            if latest_entry is not None:
                title_node = find_node(latest_entry, 'title')
                updated_node = find_node(latest_entry, 'updated')
                content_node = find_node(latest_entry, 'content') or find_node(latest_entry, 'summary')
                link_node = find_node(latest_entry, 'link')

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
                return {
                    'version': clean_version(raw_v) if '==' in title else "N/A",
                    'date': updated,
                    'title': title,
                    'summary': summary,
                    'source_url': source_url
                }
    except Exception:
        # Fallback for RSS
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
