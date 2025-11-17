# Research Workflow Orchestrator

Complete LangGraph orchestration for company research, analysis, and buy/avoid recommendations.

## Overview

This system orchestrates a complete research workflow:
1. **Company Selection**: Select a company from `ranked_companies.csv`
2. **Research Agent**: Gather evidence across 10 categories using Tavily API
3. **Summarization Agent**: Create comprehensive analyst report using OpenAI GPT-4.1
4. **Validation Agent**: Validate buy/avoid decision based on 40% return threshold
5. **Report Generation**: Save final markdown report

## Architecture

```
┌─────────────────┐
│ Company Selector │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│ Research Agent  │ (Tavily API)
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│ Summarization   │ (OpenAI GPT-4.1)
│ Agent           │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│ Validation      │ (40% return check)
│ Agent           │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│ Report Generator│ (Markdown)
└─────────────────┘
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set API keys:
```bash
export TAVILY_API_KEY="your-tavily-key"
export OPENAI_API_KEY="your-openai-key"
```

Or update `run_orchestrator.py` directly.

## Usage

### Method 1: Using the simple runner

```bash
python run_orchestrator.py
```

### Method 2: Using the orchestrator directly

```python
from research_orchestrator import ResearchOrchestrator

orchestrator = ResearchOrchestrator(
    tavily_api_key="your-tavily-key",
    openai_api_key="your-openai-key",
    research_output_dir="research_output",
    reports_dir="reports"
)

final_state = orchestrator.run()
```

### Method 3: Command line

```bash
python research_orchestrator.py \
    --tavily-key "your-key" \
    --openai-key "your-key" \
    --research-dir "research_output" \
    --reports-dir "reports"
```

## Workflow Steps

### Step 1: Company Selection
- Interactive selection from `ranked_companies.csv`
- Options:
  - Search by company name (partial match)
  - Select by rank number
- Extracts financial data automatically

### Step 2: Research Agent
- Searches web using Tavily API
- Gathers evidence across 10 categories:
  1. Business Understanding
  2. Financial Quality & Cash Flow
  3. Intrinsic Value Inputs
  4. Economic Moat
  5. Management Quality
  6. Long-Term Growth Drivers & Risks
  7. Valuation vs Peer Evidence
  8. Behavioral / Market Sentiment
  9. Regional / Macro Context
  10. Other Material Categories
- Saves each category to separate JSON file

### Step 3: Summarization
- Loads all research outputs
- Uses OpenAI GPT-4.1 to create comprehensive analyst report
- Summarizes evidence by category and subtopic
- Extracts key findings, numbers, and quotes

### Step 4: Validation
- Validates if company can achieve 40%+ return in 3 years
- Assesses probability (high/medium/low)
- Identifies key drivers and risks
- Makes BUY/AVOID recommendation with confidence level

### Step 5: Report Generation
- Combines analyst report and validation
- Saves as markdown file: `{Company_Name}_Analyst_Report_{Date}.md`
- Includes:
  - Executive summary
  - Detailed analysis by category
  - Recommendation with reasoning
  - Key drivers and risks

## Output Files

### Research Outputs
- `{category}_{company_name}_{date}.json` - Individual category research
- `summary_{company_name}_{date}.json` - Research summary

### Final Report
- `{company_name}_Analyst_Report_{date}.md` - Complete analyst report

## LangGraph Integration

The workflow uses LangGraph for orchestration:
- **State Management**: TypedDict for state tracking
- **Node Execution**: Each step is a graph node
- **Error Handling**: Errors propagate through state
- **Checkpointing**: Memory-based checkpointing for state persistence

If LangGraph is not available, the system falls back to sequential execution.

## Configuration

### OpenAI Model
Default: `gpt-4o` (can be changed to `gpt-4-turbo` or `gpt-4`)

Edit `summarization_agent.py`:
```python
self.summarization_agent = SummarizationAgent(
    openai_api_key=openai_api_key,
    model="gpt-4-turbo"  # Change here
)
```

### Return Threshold
Default: 40% over 3 years

Edit validation prompt in `summarization_agent.py` if needed.

## Example Output

```
RESEARCH WORKFLOW ORCHESTRATOR
============================================================

STEP 1: Company Selection
============================================================
✓ Selected: Transformers and Rectifiers India Limited
  Rank: 1
  Investment Score: 0.7795

STEP 2: Running Research Agent
============================================================
✓ Research completed
  Categories processed: 10

STEP 3: Summarizing Research
============================================================
✓ Analyst report generated

STEP 4: Validating Buy/Avoid Decision
============================================================
✓ Validation completed
  Recommendation: BUY
  Confidence: high
  Expected Return: 45-55%

STEP 5: Saving Final Report
============================================================
✓ Final report saved: reports/Transformers_and_Rectifiers_India_Limited_Analyst_Report_2025-11-14.md

WORKFLOW COMPLETED
============================================================
Company: Transformers and Rectifiers India Limited
Recommendation: BUY
Report: reports/Transformers_and_Rectifiers_India_Limited_Analyst_Report_2025-11-14.md
```

## Troubleshooting

- **LangGraph Import Error**: System will use sequential execution as fallback
- **API Key Errors**: Check environment variables or update script directly
- **No Research Data**: Ensure research agent completed successfully
- **OpenAI Rate Limits**: Add delays between API calls if needed

## Dependencies

- `requests`: HTTP requests for Tavily API
- `pandas`: CSV reading and data manipulation
- `openai`: OpenAI API client
- `langgraph`: Workflow orchestration (optional, has fallback)
- `langchain`: LangGraph dependency (optional)

