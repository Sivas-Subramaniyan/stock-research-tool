# Stock Research Tool - API & Frontend

## Overview

This application provides a web-based interface for the Stock Research Tool with FastAPI backend and HTML/CSS/JavaScript frontend.

## Architecture

- **Backend**: FastAPI REST API (`api.py`)
- **Frontend**: Static HTML/CSS/JavaScript (`frontend/`)
- **Communication**: REST API endpoints

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (optional):
```bash
export TAVILY_API_KEY="your-tavily-key"
export OPENAI_API_KEY="your-openai-key"
export API_HOST="0.0.0.0"  # Default
export API_PORT="8000"     # Default
```

## Running the Application

### Option 1: Using run_api.py
```bash
python run_api.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Option 3: Using FastAPI CLI
```bash
fastapi dev api.py
```

## Accessing the Application

1. **API Server**: http://localhost:8000
2. **API Documentation**: http://localhost:8000/docs (Swagger UI)
3. **Alternative API Docs**: http://localhost:8000/redoc (ReDoc)
4. **Frontend**: Open `frontend/index.html` in your browser

## API Endpoints

### Core Endpoints

- `GET /` - API information and available endpoints
- `GET /companies` - Get list of ranked companies (optional `?top_n=20`)
- `GET /scoring-algorithm` - Get scoring algorithm details
- `POST /research/start` - Start research for a company
- `GET /research/status/{research_id}` - Get research status
- `GET /research/results/{research_id}` - Get research results
- `GET /reports/{company_name}` - Download markdown report
- `GET /reports/list` - List all available reports

### Example API Calls

```bash
# Get top 20 companies
curl http://localhost:8000/companies?top_n=20

# Start research
curl -X POST http://localhost:8000/research/start \
  -H "Content-Type: application/json" \
  -d '{"company_name": "Reliance Industries", "company_rank": 1}'

# Get research status
curl http://localhost:8000/research/status/{research_id}
```

## Frontend Features

### 1. Ranked Companies Tab
- Display ranked companies in a table
- Filter by top N companies
- Select company directly from table
- View key financial metrics

### 2. Scoring Algorithm Tab
- View algorithm description
- See weight distribution
- Understand processing steps

### 3. Research Analysis Tab
- Select company by name or rank
- Start research workflow
- Real-time status updates
- Progress visualization
- View and download reports

## Development

### API Development
- API code: `api.py`
- Uses FastAPI with async/await
- Background tasks for research execution
- State management for research jobs

### Frontend Development
- HTML: `frontend/index.html`
- CSS: `frontend/styles.css`
- JavaScript: `frontend/script.js`
- API communication via Fetch API

### Adding New Endpoints

1. Add endpoint in `api.py`:
```python
@app.get("/your-endpoint")
async def your_endpoint():
    return {"message": "Hello"}
```

2. Update frontend JavaScript if needed:
```javascript
async function callYourEndpoint() {
    const response = await fetch(`${API_BASE_URL}/your-endpoint`);
    const data = await response.json();
    // Handle data
}
```

## Deployment

### Local Deployment
1. Run API server: `python run_api.py`
2. Open `frontend/index.html` in browser
3. Update `API_BASE_URL` in `frontend/script.js` if needed

### Production Deployment

#### Option 1: Deploy FastAPI with Uvicorn
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Option 2: Use Gunicorn with Uvicorn workers
```bash
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Option 3: Docker (create Dockerfile)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### GitHub Pages (Frontend Only)

1. Update `API_BASE_URL` in `frontend/script.js` to your API URL
2. Push `frontend/` directory to GitHub
3. Enable GitHub Pages in repository settings
4. Access frontend via GitHub Pages URL

### Full Stack Deployment

1. Deploy FastAPI backend to:
   - Heroku
   - AWS Elastic Beanstalk
   - Google Cloud Run
   - DigitalOcean App Platform
   - Railway
   - Render

2. Deploy frontend to:
   - GitHub Pages
   - Netlify
   - Vercel
   - AWS S3 + CloudFront

3. Update CORS settings in `api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    # ...
)
```

## Troubleshooting

### CORS Errors
- Update `allow_origins` in `api.py` CORS middleware
- Ensure frontend URL is whitelisted

### API Connection Issues
- Check `API_BASE_URL` in `frontend/script.js`
- Verify API server is running
- Check firewall/network settings

### Research Not Starting
- Verify API keys are set (TAVILY_API_KEY, OPENAI_API_KEY)
- Check API server logs for errors
- Ensure `ranked_companies.csv` exists

## File Structure

```
.
├── api.py                    # FastAPI backend
├── run_api.py               # API server runner
├── frontend/
│   ├── index.html           # Frontend HTML
│   ├── styles.css           # Frontend CSS
│   └── script.js            # Frontend JavaScript
├── research_agent.py        # Research agent
├── summarization_agent.py   # Summarization agent
├── company_selector.py      # Company selector
├── research_orchestrator.py # Orchestrator
├── requirements.txt         # Python dependencies
└── README_API.md           # This file
```

## Next Steps

1. Test locally with `python run_api.py`
2. Open `frontend/index.html` in browser
3. Test all features
4. Deploy to production
5. Update CORS and API URLs for production

