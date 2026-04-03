#!/usr/bin/env python3
"""
Fetch RSS feeds, normalize metadata, and deduplicate entries.
Outputs JSONL file with all papers for the current day.
"""
import feedparser
import requests
import yaml
import json
import re
import sys
import time
from datetime import datetime, timezone
from dateutil import parser as date_parser
from typing import List, Dict, Set
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def load_rss_sources(sources_path: str = "rss_sources.txt") -> List[str]:
    """Load RSS feed URLs, ignoring comments and empty lines."""
    urls = []
    with open(sources_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    return urls


def extract_source_from_url(url: str) -> str:
    """Extract source name from RSS URL."""
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    
    # Known sources mapping
    if 'arxiv.org' in netloc:
        return 'arXiv'
    elif 'aps.org' in netloc:
        return 'APS'
    elif 'nature.com' in netloc:
        return 'Nature'
    elif 'sciencemag.org' in netloc or 'science.org' in netloc:
        return 'Science'
    elif 'springer.com' in netloc or 'link.springer.com' in netloc:
        return 'Springer'
    elif 'ieee.org' in netloc or 'ieeexplore.ieee.org' in netloc:
        return 'IEEE'
    elif 'acm.org' in netloc or 'dl.acm.org' in netloc:
        return 'ACM'
    elif 'elsevier.com' in netloc:
        return 'Elsevier'
    else:
        # Use domain name as fallback
        return netloc.split('.')[-2] if '.' in netloc else netloc


def extract_category_from_url(url: str) -> str:
    """Extract category from arXiv RSS URLs."""
    if 'arxiv.org' in url:
        # Pattern: /rss/cs.CL or /rss/physics.comp-ph
        match = re.search(r'/rss/([\w\.\-]+)', url)
        if match:
            return match.group(1)
    return ""


def normalize_date(date_str: str) -> str:
    """Parse various date formats and return ISO format string."""
    if not date_str:
        return ""
    try:
        # Try feedparser's parsed date
        if hasattr(date_str, 'parsed'):
            dt = date_str.parsed
        else:
            dt = date_parser.parse(date_str)
        
        # Ensure timezone awareness
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt.isoformat()
    except Exception as e:
        logger.warning(f"Failed to parse date '{date_str}': {e}")
        return ""


def normalize_entry(entry, feed_url: str, config: Dict) -> Dict:
    """Normalize a single RSS entry to common format."""
    # Extract basic fields
    title = entry.get('title', '').strip()
    link = entry.get('link', '').strip()
    
    # Extract summary/description
    summary = ""
    if 'summary' in entry:
        summary = entry.summary
    elif 'description' in entry:
        summary = entry.description
    
    # Clean HTML tags from summary
    if summary:
        summary = re.sub(r'<[^>]+>', '', summary)
        summary = summary.strip()
    
    # Extract published date
    published = ""
    if 'published' in entry:
        published = entry.published
    elif 'updated' in entry:
        published = entry.updated
    elif 'pubDate' in entry:
        published = entry.pubDate
    
    published_iso = normalize_date(published)
    
    # Generate unique ID
    # Use arXiv ID if available, otherwise create hash from title+published
    entry_id = entry.get('id', link)
    if 'arxiv.org' in link:
        # Extract arXiv ID from link
        match = re.search(r'abs/(\d+\.\d+)', link)
        if match:
            entry_id = f"arxiv:{match.group(1)}"
        else:
            match = re.search(r'/(\d+\.\d+)', link)
            if match:
                entry_id = f"arxiv:{match.group(1)}"
    
    source = extract_source_from_url(feed_url)
    category = extract_category_from_url(feed_url)
    
    # Try to extract authors
    authors = []
    if 'authors' in entry:
        authors = [a.get('name', '') for a in entry.authors if a.get('name')]
    elif 'author' in entry:
        authors = [entry.author]
    
    return {
        'id': entry_id,
        'title': title,
        'summary': summary,
        'link': link,
        'published': published_iso,
        'source': source,
        'category': category,
        'authors': authors,
        'feed_url': feed_url,
        'fetched_at': datetime.now(timezone.utc).isoformat(),
    }


def fetch_feed(feed_url: str, config: Dict) -> List[Dict]:
    """Fetch and parse a single RSS feed."""
    headers = {
        'User-Agent': config.get('rss', {}).get('user_agent', 'DailyResearchTracker/1.0')
    }
    timeout = config.get('rss', {}).get('timeout', 30)
    
    try:
        logger.info(f"Fetching {feed_url}")
        response = requests.get(feed_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Parse with feedparser
        feed = feedparser.parse(response.content)
        
        if feed.bozo and feed.bozo_exception:
            logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")
        
        max_entries = config.get('rss', {}).get('max_entries_per_feed', 50)
        entries = feed.entries[:max_entries]
        
        normalized = []
        for entry in entries:
            try:
                normalized_entry = normalize_entry(entry, feed_url, config)
                normalized.append(normalized_entry)
            except Exception as e:
                logger.error(f"Failed to normalize entry in {feed_url}: {e}")
        
        logger.info(f"Fetched {len(normalized)} entries from {feed_url}")
        return normalized
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {feed_url}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching {feed_url}: {e}")
        return []


def deduplicate_entries(entries: List[Dict], config: Dict) -> List[Dict]:
    """Deduplicate entries based on configuration."""
    dedup_key = config.get('processing', {}).get('deduplication_key', 'title+published')
    
    if dedup_key == 'id':
        seen = set()
        unique = []
        for entry in entries:
            if entry['id'] not in seen:
                seen.add(entry['id'])
                unique.append(entry)
        return unique
    else:  # 'title+published'
        seen = set()
        unique = []
        for entry in entries:
            key = f"{entry['title']}|{entry['published']}"
            if key not in seen:
                seen.add(key)
                unique.append(entry)
        return unique


def main():
    """Main entry point."""
    config = load_config()
    feed_urls = load_rss_sources()
    
    if not feed_urls:
        logger.error("No RSS feeds found in rss_sources.txt")
        sys.exit(1)
    
    all_entries = []
    
    # Fetch all feeds
    for feed_url in feed_urls:
        entries = fetch_feed(feed_url, config)
        all_entries.extend(entries)
        # Be polite to servers
        time.sleep(0.5)
    
    logger.info(f"Total entries before deduplication: {len(all_entries)}")
    
    # Deduplicate
    unique_entries = deduplicate_entries(all_entries, config)
    logger.info(f"Total entries after deduplication: {len(unique_entries)}")
    
    # Sort by published date (newest first)
    unique_entries.sort(key=lambda x: x.get('published', ''), reverse=True)
    
    # Generate output filename
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    data_dir = config.get('output', {}).get('data_dir', 'data')
    output_file = f"{data_dir}/{today}.jsonl"
    
    # Write JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for entry in unique_entries:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    logger.info(f"Saved {len(unique_entries)} entries to {output_file}")
    
    # Print summary
    sources_summary = {}
    for entry in unique_entries:
        source = entry.get('source', 'Unknown')
        sources_summary[source] = sources_summary.get(source, 0) + 1
    
    logger.info("Sources summary:")
    for source, count in sources_summary.items():
        logger.info(f"  {source}: {count}")
    
    return output_file


if __name__ == '__main__':
    main()