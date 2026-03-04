# Corporate Annual Report Analyzer

An LLM-powered system for automated analysis of Chinese corporate annual reports, built as a teaching demonstration tool.

## Features

- PDF annual report upload
- LLM-based financial metric extraction (revenue, net profit, total assets, ROE, etc.)
- Management Discussion & Analysis (MD&A) text extraction
- LLM-powered investment analysis and insights
- Interactive chart visualization

## Tech Stack

- **Frontend**: HTML5 + TailwindCSS + Chart.js
- **Backend**: Python + Flask + Gunicorn
- **PDF Processing**: PyMuPDF (fitz)
- **LLM**: Qwen (qwen-plus) via DashScope API

## How It Works

1. **PDF text extraction** — PyMuPDF extracts raw text from uploaded annual reports
2. **Financial metric extraction** — The LLM reads the financial summary section (主要财务指标/主要会计数据) and returns structured JSON with 10 key metrics, normalized to 亿元
3. **MD&A extraction** — Locates the management discussion section for qualitative context
4. **Investment analysis** — A second LLM call analyzes the extracted metrics and MD&A text, producing a structured report covering financial health, business prospects, and investment value

The LLM-based extraction handles varied report formats across different company types:
- Banks (e.g., ICBC) — units in 百万元, no gross margin, bank-specific line items
- Manufacturers (e.g., CATL) — units in 千元, standard A-share format
- Loss-making companies (e.g., Cambricon) — negative profits, units in 元

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API Key
export DASHSCOPE_API_KEY="your-api-key"

# Run with Gunicorn
gunicorn --bind 127.0.0.1:8504 --timeout 120 app:app
```

Open http://127.0.0.1:8504

## Directory Structure

```
corp-finance-analyzer/
├── app.py              # Flask application
├── analyzer.py         # Analysis engine (LLM extraction + analysis)
├── requirements.txt    # Python dependencies
├── templates/
│   ├── index.html      # Frontend page
│   ├── *.pdf           # Sample annual reports for testing
│   └── ...
├── static/
│   └── uploads/        # Uploaded files directory
└── README.md
```
