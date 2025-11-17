# Stock Research Tool

An AI-powered stock research and analysis tool that performs comprehensive company research, generates analyst reports, and provides investment recommendations using web research and financial data analysis.

## Features

- **Company Ranking**: Rank companies based on financial metrics using a weighted scoring algorithm
- **Comprehensive Research**: Automated web research using Tavily API across 12 research categories
- **AI-Powered Analysis**: Generate detailed analyst reports using OpenAI GPT-4o-mini
- **Investment Validation**: Validate buy/avoid recommendations based on 40% return threshold
- **Real-time Progress**: Track research progress with detailed status updates
- **Markdown Reports**: Download and view formatted analyst reports
- **Responsive UI**: Modern, business-friendly interface that works on desktop and mobile

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI/ML**: OpenAI GPT-4o-mini, Tavily API
- **Orchestration**: LangGraph
- **Server**: Uvicorn

## Installation

### Prerequisites

- Python 3.8 or higher
- API Keys:
  - Tavily API Key (get from [Tavily](https://tavily.com))
  - OpenAI API Key (get from [OpenAI](https://platform.openai.com))

### Setup

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/01_Smallcap_stockpicker.git
cd 01_Smallcap_stockpicker
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Set up environment variables:
   - Create a `.env` file (optional) or set environment variables:
   - `TAVILY_API_KEY=your_tavily_key`
   - `OPENAI_API_KEY=your_openai_key`

## Usage

### Running the Application

1. Start the FastAPI server:
```bash
python run_api.py
```

2. Open your browser and navigate to:
   - Frontend: http://localhost:8000/
   - API Docs: http://localhost:8000/docs

### Using the Application

1. **View Ranked Companies**: Navigate to the "Ranked Companies" tab to see companies ranked by investment score
2. **Select a Company**: Choose a company from the list or enter a company name manually
3. **Start Research**: Click "Start Research" to begin the analysis
4. **Monitor Progress**: Watch real-time progress as the research agents work
5. **View Results**: Once complete, view the analyst report and download if needed

### Research Categories

The tool researches companies across 12 comprehensive categories:

1. Business Fundamentals and Model Stability
2. Financial Strength and Quality of Earnings
3. Balance Sheet Health and Liquidity
4. Intrinsic Value and Market Positioning
5. Economic Moat and Durability
6. Management Integrity and Capital Allocation
7. Growth Drivers and Future Visibility
8. Macro and Regional Sensitivity
9. Behavioral and Market Sentiment
10. Risks and Downside Scenarios
11. Integrity and Governance Health
12. Overall Fundamental Conviction Score

## Project Structure

```
.
├── api.py                      # FastAPI application and endpoints
├── company_selector.py         # Company selection from CSV
├── research_agent.py           # Web research using Tavily
├── summarization_agent.py      # Report generation and validation
├── research_orchestrator.py    # LangGraph workflow orchestration
├── score_companies.py          # Company scoring algorithm
├── run_api.py                  # Server startup script
├── requirements.txt            # Python dependencies
├── ranked_companies.csv        # Ranked company data
├── frontend/                   # Frontend files
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── research_output/            # Research data (generated)
└── reports/                    # Analyst reports (generated)
```

## API Endpoints

- `GET /companies` - Get list of ranked companies
- `GET /scoring-algorithm` - Get scoring algorithm details
- `POST /research/start` - Start research for a company
- `GET /research/status/{research_id}` - Get research status
- `GET /research/results/{research_id}` - Get research results
- `GET /reports/{company_name}` - Download report
- `GET /reports/list` - List all reports

## Configuration

### Scoring Algorithm

The investment score is calculated using weighted metrics:
- ROCE (Return on Capital Employed): 25%
- Free Cash Flow (3Y): 20%
- Debt-to-Equity: 15%
- P/E Ratio: 10%
- Market Cap: 10%
- Promoter Holding: 5%
- Working Capital Efficiency: 15%

### Research Parameters

- **Tavily Results**: Top 10 results per search query
- **Validation Threshold**: 40% minimum return in 3 years
- **Model**: GPT-4o-mini for report generation and validation

## Deployment

### Important Note on GitHub Pages

**GitHub Pages cannot host this application** because it requires a Python backend server. GitHub Pages only serves static files.

### Deployment Options

1. **Render** (Recommended):
   - Connect your GitHub repository
   - Select "Web Service"
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
   - Add environment variables for API keys

2. **Railway**:
   - Connect GitHub repository
   - Auto-detects FastAPI
   - Add environment variables

3. **Heroku**:
   - Use Heroku CLI or GitHub integration
   - Add `Procfile` with: `web: uvicorn api:app --host 0.0.0.0 --port $PORT`

4. **DigitalOcean App Platform**:
   - Connect repository
   - Configure as Python app
   - Add environment variables

### Environment Variables for Deployment

Set these in your hosting platform:
- `TAVILY_API_KEY`
- `OPENAI_API_KEY`
- `API_HOST` (optional, defaults to 0.0.0.0)
- `API_PORT` (optional, defaults to 8000)

## Development

### Running Tests

```bash
# Run the orchestrator directly
python run_orchestrator.py

# Run research for a specific company
python run_research.py
```

### Code Structure

- **Research Agent**: Handles web research using Tavily API
- **Summarization Agent**: Generates reports and validates recommendations
- **Orchestrator**: Manages the complete workflow using LangGraph
- **API**: FastAPI endpoints for frontend integration

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Tavily API for web research capabilities
- OpenAI for GPT-4o-mini model
- FastAPI for the web framework
- LangGraph for workflow orchestration

## Support

For issues and questions, please open an issue on GitHub.

