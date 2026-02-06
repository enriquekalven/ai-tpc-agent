import pytest
from ai_tpc_agent.core.watcher import fetch_recent_updates, clean_version
from unittest.mock import MagicMock, patch

def test_clean_version():
    assert clean_version("v1.2.3") == "1.2.3"
    assert clean_version("Release 1.24.0") == "1.24.0"
    assert clean_version("Version 2.0") == "2.0"
    assert clean_version("no version here") == "no version here"

@patch("urllib.request.urlopen")
def test_fetch_from_feed_atom(mock_urlopen):
    import io
    # Mock Atom XML with multiple entries
    atom_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <title>Test Update 1</title>
        <updated>2026-02-06T12:00:00Z</updated>
        <link href="https://example.com/1" />
        <summary>Summary 1</summary>
      </entry>
      <entry>
        <title>Test Update 2</title>
        <updated>2026-02-05T12:00:00Z</updated>
        <link href="https://example.com/2" />
        <summary>Summary 2</summary>
      </entry>
    </feed>
    """
    mock_response = io.BytesIO(atom_xml)
    mock_response.getcode = MagicMock(return_value=200)
    mock_response.__enter__ = MagicMock(return_value=mock_response)
    mock_response.__exit__ = MagicMock(return_value=None)
    mock_urlopen.return_value = mock_response

    updates = fetch_recent_updates("https://example.com/feed.atom", max_items=2)
    
    assert len(updates) == 2
    assert updates[0]['title'] == "Test Update 1"
    assert updates[1]['title'] == "Test Update 2"
    assert updates[0]['source_url'] == "https://example.com/1"

@patch("urllib.request.urlopen")
def test_fetch_from_html(mock_urlopen):
    # Mock Google Cloud Docs HTML
    html_content = b"""
    <html>
      <body>
        <h2 id="February_06_2026">February 06, 2026</h2>
        <div>Feature: New AI Agent</div>
        <p>This is a test summary for the new agent.</p>
        <h2 id="February_05_2026">February 05, 2026</h2>
        <div>Announcement: Security fix</div>
      </body>
    </html>
    """
    mock_response = MagicMock()
    mock_response.read.return_value = html_content
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    updates = fetch_recent_updates("https://docs.cloud.google.com/test-notes", max_items=2)
    
    assert len(updates) >= 1
    # Check if first update title matches expected logic
    assert "New AI Agent" in updates[0]['title']
    assert "2026-02-06" in updates[0]['date']
