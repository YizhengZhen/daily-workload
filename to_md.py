#!/usr/bin/env python3
"""
Standalone script to convert JSONL data to Markdown for Obsidian.
This can be used on other servers or for manual processing.
"""

import os
import json
import yaml
import sys
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def load_jsonl_data(data_file: str) -> List[Dict]:
    """Load JSONL data file."""
    data = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def generate_markdown_content(data: List[Dict], date_str: str) -> str:
    """Generate Markdown content for Obsidian."""
    lines = []
    
    # Frontmatter
    lines.append("---")
    lines.append(f"title: \"Research Papers - {date_str}\"")
    lines.append(f"date: {date_str}")
    lines.append(f"source: \"Daily Research Tracker\"")
    lines.append("tags:")
    lines.append("  - research")
    lines.append("  - papers")
    lines.append("  - daily")
    lines.append("---\n")
    
    # Header
    lines.append(f"# Research Papers - {date_str}\n")
    
    # Statistics
    total_papers = len(data)
    recommended = sum(1 for item in data if item.get('AI', {}).get('recommendation', False))
    avg_score = sum(item.get('AI', {}).get('score', 0.0) for item in data) / total_papers if total_papers > 0 else 0.0
    
    lines.append(f"**Total Papers**: {total_papers}")
    lines.append(f"**Recommended**: {recommended}")
    lines.append(f"**Average Score**: {avg_score:.2f}/10\n")
    
    # Papers list
    for idx, item in enumerate(data, 1):
        ai = item.get('AI', {})
        title = item.get('title', 'Untitled')
        link = item.get('link', '#')
        source = item.get('source', 'Unknown')
        category = item.get('category', '')
        published = item.get('published', '')
        authors = item.get('authors', [])
        
        score = ai.get('score', 0.0)
        recommendation = ai.get('recommendation', False)
        tldr = ai.get('tldr', 'No summary available')
        
        lines.append(f"## {idx}. {title}")
        lines.append("")
        
        # Basic info
        lines.append(f"**Score**: {score:.1f}/10")
        if recommendation:
            lines.append("**Recommendation**: ✅ Recommended")
        else:
            lines.append("**Recommendation**: ⚠️ Not recommended")
        
        lines.append(f"**Source**: {source}")
        if category:
            lines.append(f"**Category**: {category}")
        if published:
            lines.append(f"**Published**: {published}")
        if authors:
            lines.append(f"**Authors**: {', '.join(authors)}")
        
        lines.append(f"**Link**: [View paper]({link})")
        
        # Add PDF link for arXiv papers
        if 'arxiv.org' in link:
            pdf_link = link.replace('abs/', 'pdf/') + '.pdf'
            lines.append(f"**PDF**: [Download]({pdf_link})")
        
        lines.append(f"\n**Summary**: {tldr}")
        
        # Optional AI analysis sections
        motivation = ai.get('motivation', '').strip()
        method = ai.get('method', '').strip()
        result = ai.get('result', '').strip()
        conclusion = ai.get('conclusion', '').strip()
        reasoning = ai.get('reasoning', '').strip()
        
        if reasoning:
            lines.append(f"\n**Reasoning**: {reasoning}")
        
        if motivation:
            lines.append(f"\n**Motivation**: {motivation}")
        
        if method:
            lines.append(f"\n**Method**: {method}")
        
        if result:
            lines.append(f"\n**Result**: {result}")
        
        if conclusion:
            lines.append(f"\n**Conclusion**: {conclusion}")
        
        # Key contributions if present
        contributions = ai.get('key_contributions', '').strip()
        if contributions:
            lines.append(f"\n**Key Contributions**: {contributions}")
        
        # Tags for Obsidian
        tags = []
        if source:
            tags.append(f"#{source}")
        if category:
            tags.append(f"#{category.replace('.', '_')}")
        if recommendation:
            tags.append("#recommended")
        if score >= 8.0:
            tags.append("#high_score")
        
        if tags:
            lines.append(f"\n**Tags**: {' '.join(tags)}")
        
        lines.append("\n---\n")
    
    return '\n'.join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Convert JSONL to Markdown for Obsidian")
    parser.add_argument("--data", type=str, required=True, help="JSONL data file")
    parser.add_argument("--config", type=str, default="config.yaml", help="Configuration file")
    parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format (default: extract from filename or today)")
    parser.add_argument("--output", type=str, help="Output Markdown file path")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Determine date
    if args.date:
        date_str = args.date
    else:
        # Extract date from filename if possible
        import re
        match = re.search(r'(\d{4}-\d{2}-\d{2})', args.data)
        if match:
            date_str = match.group(1)
        else:
            date_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # Load data
    data = load_jsonl_data(args.data)
    print(f"Loaded {len(data)} papers for {date_str}", file=sys.stderr)
    
    # Generate Markdown
    markdown_content = generate_markdown_content(data, date_str)
    
    # Determine output path
    if args.output:
        output_file = args.output
    else:
        obsidian_dir = config.get('output', {}).get('obsidian_dir', 'obsidian')
        os.makedirs(obsidian_dir, exist_ok=True)
        output_file = os.path.join(obsidian_dir, f'{date_str}.md')
    
    # Save Markdown file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"Generated Markdown file: {output_file}", file=sys.stderr)
    
    # Print statistics
    recommended = sum(1 for item in data if item.get('AI', {}).get('recommendation', False))
    avg_score = sum(item.get('AI', {}).get('score', 0.0) for item in data) / len(data) if data else 0.0
    
    print(f"\nStatistics:", file=sys.stderr)
    print(f"  Total papers: {len(data)}", file=sys.stderr)
    print(f"  Recommended: {recommended}", file=sys.stderr)
    print(f"  Average score: {avg_score:.2f}/10", file=sys.stderr)


if __name__ == "__main__":
    main()