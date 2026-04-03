# Daily Research Tracker (RSS-based)

A fully automated research paper tracking system that monitors arXiv and major journals via RSS feeds only (no crawlers, no email parsing, no HTML parsing). Features AI-powered semantic scoring and English summarization, with outputs synchronized to GitHub Pages, Aliyun, and Obsidian.

## ✨ Key Features

- **RSS-Only Pipeline**: Uses only RSS feeds—no web crawling, email parsing, or HTML scraping.
- **AI Semantic Scoring**: Leverages OpenAI‑compatible LLMs (e.g., DeepSeek) to score papers (0–10) based on your research directions.
- **English Summaries**: Generates concise one‑sentence summaries in English.
- **Fully Automated**: Runs daily via GitHub Actions.
- **Multiple Outputs**:
  - Static website (GitHub Pages) with search/filter capabilities.
  - JSONL data for external consumption.
  - Markdown files for Obsidian integration.
  - Optional sync to Aliyun (OSS, Qdrant/Milvus).
- **Easy Configuration**: Define RSS feeds in `rss_sources.txt` and research interests in `research_directions.md`.

## 📁 Project Structure

```
.
├── rss_sources.txt                # List of RSS feed URLs
├── config.yaml                    # Main configuration
├── research_directions.md         # Research directions for semantic scoring
├── fetch_rss.py                   # Fetches & normalizes RSS entries
├── enhance.py                     # AI‑based semantic analysis
├── generate_output.py             # Creates JSONL & Markdown outputs
├── .github/workflows/daily.yml    # GitHub Actions workflow
├── website/                       # Static site for GitHub Pages
├── data/                          # Generated JSONL & Markdown files
└── README.md
```

## 🚀 Quick Start

1. **Fork this repository** to your own GitHub account.
2. **Configure RSS feeds** by editing `rss_sources.txt` (one RSS URL per line).
3. **Set up research directions** in `research_directions.md`.
4. **Add secrets** in your repository settings:
   - `OPENAI_API_KEY`: Your OpenAI‑compatible API key (e.g., DeepSeek).
   - `OPENAI_BASE_URL`: The base URL for the API (e.g., `https://api.deepseek.com`).
5. **Enable GitHub Pages** from the `main` branch (root folder `website/`).
6. **Run the workflow** manually from the Actions tab to test.

The workflow will run daily, fetching new papers, scoring them, and updating the website and data files.

## ⚙️ Configuration

### `rss_sources.txt`
One RSS URL per line. Examples:
```
http://export.arxiv.org/rss/cs.CL
http://export.arxiv.org/rss/cs.CV
https://journals.aps.org/rss/prl
https://www.nature.com/subjects/physics/nphys.rss
```

### `config.yaml`
```yaml
llm:
  model_name: "deepseek-chat"
  base_url: "https://api.deepseek.com"
  temperature: 0.3
  max_tokens: 1000

scoring:
  threshold: 6.0          # Minimum score to recommend
  fields: "research_directions.md"

output:
  language: "English"
  timezone: "UTC"
  website_dir: "website"
  data_dir: "data"
  obsidian_dir: "obsidian"
```

### `research_directions.md`
Define your research interests in natural language. The AI will use this to score papers. Example:
```
- Machine learning for computer vision
- Large language model fine‑tuning
- Quantum computing algorithms
- High‑energy physics simulations
```

## 🔧 Workflow Details

1. **Fetch RSS** (`fetch_rss.py`): Downloads all feeds, normalizes metadata, deduplicates by `(title + published)`.
2. **AI Enhancement** (`enhance.py`): For each paper’s abstract, calls the LLM to produce:
   - One‑sentence summary (English)
   - Score (0–10) based on relevance to research directions
   - Recommendation (yes/no)
   - Structured JSON output
3. **Generate Outputs** (`generate_output.py`):
   - Creates `data/YYYY-MM-DD.jsonl` with all papers
   - Creates `data/YYYY-MM-DD.md` for Obsidian
   - Updates the static website’s data files
4. **Commit & Push**: Updates the `data` branch and the main branch (website).
5. **GitHub Pages**: Serves the `website/` folder as a static site.

## 🌐 Website Features

The static website (`website/`) provides:
- List of papers with title, summary, score, recommendation, and source
- Filter by score, source (arXiv, PRL, Nature, etc.), and category
- Search box for keyword matching
- Click a paper to open a mini‑page with links (URL, PDF)
- Optional semantic search (if Aliyun Qdrant/Milvus is configured)

## 📱 Obsidian Integration

Markdown files are generated in `obsidian/` (or a folder of your choice). Each file contains:
- Paper metadata
- AI‑generated summary and score
- Links to the paper and PDF
- Tags based on source and category

You can sync this folder with your Obsidian vault using Git or a file‑sync service.

## 🚨 Caveats

- **RSS limitations**: Some journals may not provide full abstracts via RSS; the system works with whatever metadata the RSS feed supplies.
- **API costs**: Using a paid LLM API will incur costs (estimated ~0.2–0.5 CNY per day with DeepSeek).
- **Rate limiting**: Respect the RSS providers’ and LLM API’s rate limits.

## 📄 License

MIT

## 🙏 Acknowledgments

Inspired by [daily-arXiv-ai-enhanced](https://github.com/dw-dengwei/daily-arXiv-ai-enhanced).