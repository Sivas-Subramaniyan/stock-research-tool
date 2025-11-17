# Evidence-Gathering Research Agent

A comprehensive research agent that uses Tavily API to search the web and accumulate factual evidence about companies across 10 predefined business principle categories.

## Features

- **Evidence-Based Research**: Collects primary facts, public filings, numbers, quotes, and citations
- **10 Search Categories**: Covers business understanding, financial quality, economic moat, management quality, and more
- **Structured Output**: Saves each category's results in separate JSON files
- **Confidence Scoring**: Automatically assesses source authority (high/medium/low)
- **Metadata Capture**: Records URL, title, source domain, retrieval date, and excerpts for each evidence item

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Get a Tavily API key:
   - Visit https://tavily.com
   - Sign up and get your API key

3. Set your API key:
   - Option 1: Set environment variable
     ```bash
     export TAVILY_API_KEY="your-api-key-here"
     ```
   - Option 2: Update `run_research.py` directly

## Usage

### Method 1: Using the example script

```bash
python run_research.py
```

Edit `run_research.py` to change the company name and financial data.

### Method 2: Using command line

```bash
python research_agent.py --company "Company Name" --api-key "your-api-key" --output-dir "research_output"
```

Optional: Provide financial data via JSON file:
```bash
python research_agent.py --company "Company Name" --api-key "your-api-key" --financial-data "financial_data.json"
```

### Method 3: Using as a Python module

```python
from research_agent import ResearchAgent

agent = ResearchAgent(
    tavily_api_key="your-api-key",
    output_dir="research_output"
)

financial_data = {
    "market_cap": "1500000",
    "pe_ratio": "25.5",
    "roce": "18.5"
}

saved_files = agent.run_research(
    company_name="Reliance Industries",
    financial_data=financial_data
)
```

## Search Categories

The agent searches across 10 categories:

1. **Business Understanding**: Company description, segments, revenue streams, customers, competitors
2. **Financial Quality & Cash Flow**: Revenue, EBITDA, FCF, ROE, ROCE, margins, capex trends
3. **Intrinsic Value Inputs**: Market price, analyst targets, institutional ownership
4. **Economic Moat**: Patents, brand metrics, recurring revenue, pricing power
5. **Management Quality**: Executive bios, insider ownership, capital allocation, governance
6. **Long-Term Growth Drivers & Risks**: Management guidance, industry forecasts, risks
7. **Valuation vs Peer Evidence**: Peer multiples, relative rankings
8. **Behavioral / Market Sentiment**: Recent news, short interest, sentiment signals
9. **Regional / Macro Context**: Regulatory notices, policy changes, macro indicators
10. **Other Material Categories**: ESG incidents, legal proceedings, contingent liabilities

## Output Structure

Results are saved in the `research_output` directory (or your specified directory):

- `{category}_{company_name}_{date}.json` - Individual category results
- `summary_{company_name}_{date}.json` - Summary of all research

Each category file contains:
- Category name and metadata
- Financial data provided
- Subtopics with search queries
- Evidence items with:
  - URL
  - Title
  - Source domain
  - Retrieval date
  - Excerpt (≤25 words)
  - Confidence level (high/medium/low)

## Important Notes

- **No Investment Advice**: This agent only gathers evidence. It does not perform valuations or provide investment recommendations.
- **Rate Limiting**: The agent includes a 1-second delay between categories to avoid rate limiting. Adjust if needed.
- **Source Priority**: The agent prioritizes authoritative sources (SEC filings, company websites, Bloomberg, Reuters) over general web sources.
- **Date Ranges**: For fast-moving facts, focuses on last 3 years. For durability/history, captures up to 10 years if available.

## Example Financial Data JSON

```json
{
  "market_cap": "1500000",
  "pe_ratio": "25.5",
  "roce": "18.5",
  "sales": "500000",
  "opm": "15.2",
  "debt_eq": "0.3",
  "fcf_3y": "25000"
}
```

## Troubleshooting

- **API Key Error**: Ensure your Tavily API key is set correctly
- **No Results**: Check your internet connection and API key validity
- **Rate Limiting**: Increase the delay between searches if you encounter rate limit errors

