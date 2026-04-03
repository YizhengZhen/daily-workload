#!/usr/bin/env python3
"""
Generate output files from AI-enhanced JSONL:
1. Markdown file for Obsidian (YYYY-MM-DD.md)
2. JSON data file for website
3. Update website index/data files
"""
import os
import json
import yaml
import sys
from datetime import datetime, timezone
from typing import List, Dict, Any
import argparse
import shutil


def load_config(config_path: str = "config.yaml") -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def load_enhanced_data(data_file: str) -> List[Dict]:
    """Load AI-enhanced JSONL data."""
    data = []
    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def generate_markdown(data: List[Dict], config: Dict, date_str: str) -> str:
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
    lines.append(f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*\n")
    
    # Summary statistics
    recommended = sum(1 for item in data if item.get('AI', {}).get('recommendation', False))
    avg_score = sum(item.get('AI', {}).get('score', 0.0) for item in data) / len(data) if data else 0.0
    
    lines.append("## 📊 Summary")
    lines.append(f"- **Total papers**: {len(data)}")
    lines.append(f"- **Recommended**: {recommended} ({recommended/len(data)*100:.1f}%)")
    lines.append(f"- **Average score**: {avg_score:.2f}/10\n")
    
    # Papers by source
    sources = {}
    for item in data:
        source = item.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1
    
    if sources:
        lines.append("## 📈 Sources")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{source}**: {count}")
        lines.append("")
    
    # Papers list
    lines.append("## 📄 Papers")
    
    # Sort by score (highest first)
    sorted_data = sorted(data, key=lambda x: x.get('AI', {}).get('score', 0.0), reverse=True)
    
    for i, item in enumerate(sorted_data, 1):
        ai = item.get('AI', {})
        title = item.get('title', 'Untitled')
        link = item.get('link', '#')
        source = item.get('source', 'Unknown')
        category = item.get('category', '')
        score = ai.get('score', 0.0)
        recommendation = ai.get('recommendation', False)
        tldr = ai.get('tldr', 'No summary available')
        
        # Determine emoji for recommendation
        rec_emoji = "✅" if recommendation else "➖"
        
        lines.append(f"\n### {i}. {rec_emoji} {title}")
        lines.append(f"**Score**: {score:.1f}/10 | **Source**: {source} | **Category**: {category}")
        lines.append(f"**Link**: [Open]({link})")
        
        # PDF link if available (arXiv specific)
        pdf_link = ""
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
    
    return '\n'.join(lines)


def generate_website_data(data: List[Dict], config: Dict) -> List[Dict[str, Any]]:
    """Generate simplified data for website consumption."""
    website_data = []
    
    for item in data:
        ai = item.get('AI', {})
        website_item = {
            'id': item.get('id', ''),
            'title': item.get('title', 'Untitled'),
            'summary': ai.get('tldr', 'No summary available'),
            'link': item.get('link', '#'),
            'source': item.get('source', 'Unknown'),
            'category': item.get('category', ''),
            'score': ai.get('score', 0.0),
            'recommendation': ai.get('recommendation', False),
            'published': item.get('published', ''),
            'authors': item.get('authors', []),
            # Additional fields for filtering
            'score_int': int(round(ai.get('score', 0.0))),
            'year': item.get('published', '')[:4] if item.get('published') else ''
        }
        
        # Add PDF link for arXiv
        if 'arxiv.org' in website_item['link']:
            website_item['pdf_link'] = website_item['link'].replace('abs/', 'pdf/') + '.pdf'
        
        website_data.append(website_item)
    
    return website_data


def update_website_files(website_data: List[Dict], config: Dict, date_str: str):
    """Update website data files and indices."""
    website_dir = config.get('output', {}).get('website_dir', 'website')
    data_dir = config.get('output', {}).get('data_dir', 'data')
    
    # Ensure website directory structure
    os.makedirs(os.path.join(website_dir, 'data'), exist_ok=True)
    os.makedirs(os.path.join(website_dir, 'js'), exist_ok=True)
    os.makedirs(os.path.join(website_dir, 'css'), exist_ok=True)
    
    # 1. Save daily data file
    daily_file = os.path.join(website_dir, 'data', f'{date_str}.json')
    with open(daily_file, 'w', encoding='utf-8') as f:
        json.dump(website_data, f, ensure_ascii=False, indent=2)
    
    # 2. Update index of available dates
    index_file = os.path.join(website_dir, 'data', 'index.json')
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {'dates': [], 'latest': ''}
    
    if date_str not in index['dates']:
        index['dates'].append(date_str)
        index['dates'].sort(reverse=True)
    
    index['latest'] = date_str
    index['updated'] = datetime.now(timezone.utc).isoformat()
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    # 3. Copy essential website files if not present
    website_files = {
        'index.html': 'Basic HTML structure',
        'js/app.js': 'Main application logic',
        'css/styles.css': 'Styling',
        'js/data-loader.js': 'Data loading utilities'
    }
    
    # Check if we need to create basic website files
    index_html_path = os.path.join(website_dir, 'index.html')
    if not os.path.exists(index_html_path):
        create_basic_website(website_dir, config)
    
    print(f"Updated website files in {website_dir}", file=sys.stderr)


def create_basic_website(website_dir: str, config: Dict):
    """Create basic website files if they don't exist."""
    # index.html
    index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Research Tracker</title>
    <link rel="stylesheet" href="css/styles.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-newspaper"></i> Daily Research Tracker</h1>
            <p class="subtitle">AI-curated research papers from arXiv and major journals</p>
            <div class="controls">
                <div class="date-selector">
                    <label for="date-select">Date:</label>
                    <select id="date-select">
                        <option value="">Loading dates...</option>
                    </select>
                </div>
                <div class="filters">
                    <input type="text" id="search-box" placeholder="Search papers...">
                    <select id="source-filter">
                        <option value="">All Sources</option>
                    </select>
                    <select id="score-filter">
                        <option value="">All Scores</option>
                        <option value="8">8+</option>
                        <option value="6">6+</option>
                        <option value="4">4+</option>
                    </select>
                    <button id="recommended-toggle" class="btn-toggle">
                        <i class="fas fa-star"></i> Recommended Only
                    </button>
                </div>
            </div>
        </header>
        
        <main>
            <div class="stats-bar">
                <div class="stat">
                    <span class="stat-label">Papers Today:</span>
                    <span id="paper-count" class="stat-value">0</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Recommended:</span>
                    <span id="recommended-count" class="stat-value">0</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Avg Score:</span>
                    <span id="avg-score" class="stat-value">0.0</span>
                </div>
            </div>
            
            <div id="loading" class="loading">
                <i class="fas fa-spinner fa-spin"></i> Loading papers...
            </div>
            
            <div id="papers-container" class="papers-container">
                <!-- Papers will be inserted here -->
            </div>
            
            <div id="no-results" class="no-results" style="display: none;">
                <i class="fas fa-search"></i> No papers match your filters.
            </div>
        </main>
        
        <footer>
            <p>Generated by <a href="https://github.com/your-username/daily-research-tracker" target="_blank">Daily Research Tracker</a></p>
            <p class="timestamp">Last updated: <span id="update-time">-</span></p>
        </footer>
    </div>
    
    <!-- Paper Detail Modal -->
    <div id="paper-modal" class="modal">
        <div class="modal-content">
            <span class="close">&times;</span>
            <div id="modal-content"></div>
        </div>
    </div>
    
    <script src="js/data-loader.js"></script>
    <script src="js/app.js"></script>
</body>
</html>'''
    
    with open(os.path.join(website_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    # styles.css
    styles_css = '''/* Basic styles for Daily Research Tracker */
:root {
    --primary-color: #2563eb;
    --secondary-color: #3b82f6;
    --accent-color: #10b981;
    --danger-color: #ef4444;
    --warning-color: #f59e0b;
    --bg-color: #f8fafc;
    --card-bg: #ffffff;
    --text-color: #1e293b;
    --border-color: #e2e8f0;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    background-color: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: var(--shadow);
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

header h1 i {
    margin-right: 10px;
}

.subtitle {
    opacity: 0.9;
    margin-bottom: 1.5rem;
}

.controls {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    align-items: center;
}

.date-selector, .filters {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

select, input[type="text"] {
    padding: 8px 12px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-size: 1rem;
    background-color: white;
}

.btn-toggle {
    padding: 8px 16px;
    background-color: rgba(255, 255, 255, 0.2);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 5px;
    transition: background-color 0.2s;
}

.btn-toggle:hover {
    background-color: rgba(255, 255, 255, 0.3);
}

.btn-toggle.active {
    background-color: var(--accent-color);
    border-color: var(--accent-color);
}

.stats-bar {
    display: flex;
    gap: 2rem;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background-color: var(--card-bg);
    border-radius: 8px;
    box-shadow: var(--shadow);
}

.stat {
    display: flex;
    flex-direction: column;
}

.stat-label {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 4px;
}

.stat-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
}

.papers-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 1.5rem;
}

.paper-card {
    background-color: var(--card-bg);
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: var(--shadow);
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
    border: 2px solid transparent;
}

.paper-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.paper-card.recommended {
    border-color: var(--accent-color);
}

.paper-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.paper-title {
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    flex: 1;
}

.paper-score {
    background-color: var(--primary-color);
    color: white;
    padding: 4px 8px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: bold;
    min-width: 50px;
    text-align: center;
}

.paper-meta {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    color: #64748b;
}

.paper-summary {
    margin-bottom: 1rem;
    line-height: 1.5;
}

.paper-actions {
    display: flex;
    gap: 0.5rem;
}

.btn {
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 5px;
    text-decoration: none;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}

.btn-secondary {
    background-color: var(--border-color);
    color: var(--text-color);
}

.loading, .no-results {
    text-align: center;
    padding: 3rem;
    font-size: 1.2rem;
    color: #64748b;
}

.loading i {
    margin-right: 10px;
}

footer {
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border-color);
    text-align: center;
    color: #64748b;
}

footer a {
    color: var(--primary-color);
    text-decoration: none;
}

.timestamp {
    margin-top: 0.5rem;
    font-size: 0.9rem;
}

/* Modal styles */
.modal {
    display: none;
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
    background-color: var(--card-bg);
    margin: 5% auto;
    padding: 2rem;
    border-radius: 12px;
    width: 90%;
    max-width: 800px;
    max-height: 80vh;
    overflow-y: auto;
    position: relative;
}

.close {
    position: absolute;
    right: 1.5rem;
    top: 1rem;
    font-size: 1.5rem;
    cursor: pointer;
    color: #64748b;
}

@media (max-width: 768px) {
    .papers-container {
        grid-template-columns: 1fr;
    }
    
    .controls {
        flex-direction: column;
        align-items: stretch;
    }
    
    .date-selector, .filters {
        flex-direction: column;
        align-items: stretch;
    }
}'''
    
    with open(os.path.join(website_dir, 'css', 'styles.css'), 'w', encoding='utf-8') as f:
        f.write(styles_css)
    
    # data-loader.js
    data_loader_js = '''// Data loading utilities for Daily Research Tracker
class DataLoader {
    constructor() {
        this.baseUrl = window.location.origin + window.location.pathname;
        this.dataCache = {};
    }

    async loadDateIndex() {
        try {
            const response = await fetch(`${this.baseUrl}data/index.json`);
            if (!response.ok) throw new Error('Failed to load date index');
            return await response.json();
        } catch (error) {
            console.error('Error loading date index:', error);
            return { dates: [], latest: '' };
        }
    }

    async loadDateData(date) {
        // Check cache first
        if (this.dataCache[date]) {
            return this.dataCache[date];
        }

        try {
            const response = await fetch(`${this.baseUrl}data/${date}.json`);
            if (!response.ok) throw new Error(`Failed to load data for ${date}`);
            const data = await response.json();
            this.dataCache[date] = data;
            return data;
        } catch (error) {
            console.error(`Error loading data for ${date}:`, error);
            return [];
        }
    }

    async loadLatestData() {
        const index = await this.loadDateIndex();
        if (index.latest) {
            return await this.loadDateData(index.latest);
        }
        return [];
    }
}

// Initialize global data loader
window.dataLoader = new DataLoader();'''
    
    with open(os.path.join(website_dir, 'js', 'data-loader.js'), 'w', encoding='utf-8') as f:
        f.write(data_loader_js)
    
    print(f"Created basic website structure in {website_dir}", file=sys.stderr)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, required=True, help="AI-enhanced JSONL data file")
    parser.add_argument("--config", type=str, default="config.yaml", help="Configuration file path")
    parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format (default: today)")
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
    data = load_enhanced_data(args.data)
    print(f"Loaded {len(data)} enhanced papers for {date_str}", file=sys.stderr)
    
    # 1. Generate Markdown for Obsidian
    if config.get('obsidian', {}).get('enabled', True):
        obsidian_dir = config.get('output', {}).get('obsidian_dir', 'obsidian')
        os.makedirs(obsidian_dir, exist_ok=True)
        
        markdown_content = generate_markdown(data, config, date_str)
        markdown_file = os.path.join(obsidian_dir, f'{date_str}.md')
        
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Generated Markdown file: {markdown_file}", file=sys.stderr)
    
    # 2. Generate website data and update website
    website_data = generate_website_data(data, config)
    update_website_files(website_data, config, date_str)
    
    # 3. Also save JSONL to data directory (for backup/other uses)
    data_dir = config.get('output', {}).get('data_dir', 'data')
    jsonl_file = os.path.join(data_dir, f'{date_str}_final.jsonl')
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Saved final JSONL: {jsonl_file}", file=sys.stderr)
    print(f"Output generation complete for {date_str}", file=sys.stderr)


if __name__ == "__main__":
    main()