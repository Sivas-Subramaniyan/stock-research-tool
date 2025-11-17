"""
FastAPI backend for Research Tool
Provides REST API endpoints for frontend integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Optional, List
import uvicorn
import os
import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
import asyncio

# Fix Windows encoding issues
if sys.platform == 'win32':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

from company_selector import CompanySelector
from research_agent import ResearchAgent
from summarization_agent import SummarizationAgent
from research_orchestrator import ResearchOrchestrator

# Initialize FastAPI app
app = FastAPI(title="Stock Picker and Research Tool API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
frontend_path = Path(__file__).parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Global state management for research jobs
research_jobs: Dict[str, Dict] = {}

# Configuration - must be from environment variables
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY environment variable is required")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
RESEARCH_OUTPUT_DIR = "research_output"
REPORTS_DIR = "reports"

# Initialize agents (lazy loading)
company_selector = None
research_agent = None
summarization_agent = None
orchestrator = None


def get_company_selector():
    global company_selector
    if company_selector is None:
        company_selector = CompanySelector()
    return company_selector


def get_orchestrator():
    global orchestrator
    if orchestrator is None:
        orchestrator = ResearchOrchestrator(
            tavily_api_key=TAVILY_API_KEY,
            openai_api_key=OPENAI_API_KEY,
            research_output_dir=RESEARCH_OUTPUT_DIR,
            reports_dir=REPORTS_DIR
        )
    return orchestrator


# Pydantic models for request/response
class ResearchRequest(BaseModel):
    company_name: str
    company_rank: Optional[int] = None


class ResearchStatus(BaseModel):
    research_id: str
    status: str
    company_name: str
    progress: Dict
    current_step: str
    error: Optional[str] = None


class CompanyInfo(BaseModel):
    rank: int
    name: str
    market_cap: str
    pe_ratio: str
    roce: str
    investment_score: str


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - Serve frontend HTML"""
    frontend_file = Path(__file__).parent / "frontend" / "index.html"
    if frontend_file.exists():
        with open(frontend_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    else:
        # Fallback to API info if frontend not found
        return {
            "message": "Stock Research Tool API",
            "version": "1.0.0",
            "endpoints": {
                "/companies": "GET - List ranked companies",
                "/scoring-algorithm": "GET - Get scoring algorithm details",
                "/research/start": "POST - Start research for a company",
                "/research/status/{research_id}": "GET - Get research status",
                "/research/results/{research_id}": "GET - Get research results",
                "/reports/{company_name}": "GET - Download report"
            },
            "note": "Frontend not found. Please ensure frontend/index.html exists."
        }


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Stock Research Tool API",
        "version": "1.0.0",
        "endpoints": {
            "/companies": "GET - List ranked companies",
            "/scoring-algorithm": "GET - Get scoring algorithm details",
            "/research/start": "POST - Start research for a company",
            "/research/status/{research_id}": "GET - Get research status",
            "/research/results/{research_id}": "GET - Get research results",
            "/reports/{company_name}": "GET - Download report"
        }
    }


@app.get("/companies", response_model=List[CompanyInfo])
async def get_companies(top_n: Optional[int] = None):
    """Get list of ranked companies"""
    try:
        selector = get_company_selector()
        df = selector.list_companies(top_n=top_n)
        
        companies = []
        for _, row in df.iterrows():
            companies.append(CompanyInfo(
                rank=int(row['rank']),
                name=str(row['Name']),
                market_cap=str(row.get('Mar Cap Rs.Cr.', 'N/A')),
                pe_ratio=str(row.get('P/E', 'N/A')),
                roce=str(row.get('ROCE %', 'N/A')),
                investment_score=str(row.get('investment_score', 'N/A'))
            ))
        
        return companies
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scoring-algorithm")
async def get_scoring_algorithm():
    """Get scoring algorithm details"""
    try:
        # Read scoring algorithm from score_companies.py
        algorithm_info = {
            "weights": {
                "roce": 0.20,
                "fcf_3y": 0.20,
                "debt_eq": 0.10,
                "valuation": 0.10,
                "cf_op_3y": 0.10,
                "opm": 0.10,
                "prom_hold": 0.05,
                "wc_efficiency": 0.15
            },
            "description": "The scoring algorithm uses a weighted scoring system across multiple financial metrics. Each metric is normalized and weighted according to importance for investment decisions.",
            "metrics": {
                "roce": "Return on Capital Employed - Higher is better (20% weight)",
                "fcf_3y": "Free Cash Flow over 3 years - Higher is better (20% weight)",
                "debt_eq": "Debt to Equity ratio - Lower is better (10% weight, inverted)",
                "valuation": "P/E vs Industry P/E ratio - Lower is better (10% weight, inverted)",
                "cf_op_3y": "Cash Flow from Operations over 3 years - Higher is better (10% weight)",
                "opm": "Operating Profit Margin - Higher is better (10% weight)",
                "prom_hold": "Promoter Holding % - Higher is better (5% weight)",
                "wc_efficiency": "Working Capital Efficiency (combines WC Days and Cash Cycle) - Lower is better (15% weight, inverted)"
            },
            "process": [
                "1. Load financial data from screener results",
                "2. Normalize each metric to 0-1 scale",
                "3. Apply winsorization to handle outliers",
                "4. Invert metrics where lower is better",
                "5. Calculate weighted sum",
                "6. Rank companies by investment score"
            ]
        }
        return algorithm_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/research/start")
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """Start research for a selected company"""
    try:
        selector = get_company_selector()
        
        # Get company data
        if request.company_rank:
            company_data = selector.get_company_by_rank(request.company_rank)
        else:
            company_data = selector.get_company_by_name(request.company_name)
        
        if not company_data:
            raise HTTPException(status_code=404, detail=f"Company not found: {request.company_name}")
        
        # Generate research ID
        research_id = str(uuid.uuid4())
        
        # Initialize job status
        research_jobs[research_id] = {
            "research_id": research_id,
            "status": "started",
            "company_name": company_data["company_name"],
            "financial_data": company_data["financial_data"],
            "progress": {
                "step": "Initializing",
                "current": 0,
                "total": 5,
                "message": "Starting research workflow..."
            },
            "current_step": "initializing",
            "error": None,
            "started_at": datetime.now().isoformat(),
            "results": None
        }
        
        # Start background task (run in thread pool for blocking operations)
        import threading
        thread = threading.Thread(target=run_research_workflow_sync, args=(research_id, company_data))
        thread.daemon = True
        thread.start()
        
        return {
            "research_id": research_id,
            "status": "started",
            "company_name": company_data["company_name"],
            "message": "Research started successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_research_workflow_sync(research_id: str, company_data: Dict):
    """Sync wrapper for research workflow"""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_research_workflow(research_id, company_data))
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        if research_id in research_jobs:
            job = research_jobs[research_id]
            job["status"] = "error"
            job["error"] = str(e)
            job["error_details"] = error_details
            job["current_step"] = "error"
            job["progress"] = {
                "step": "Error",
                "current": job.get("progress", {}).get("current", 0),
                "total": 5,
                "message": f"Error: {str(e)}"
            }
        print(f"Error in research workflow: {error_details}")
    finally:
        if 'loop' in locals():
            loop.close()


async def run_research_workflow(research_id: str, company_data: Dict):
    """Background task to run research workflow"""
    try:
        job = research_jobs[research_id]
        company_name = company_data["company_name"]
        financial_data = company_data["financial_data"]
        
        orchestrator = get_orchestrator()
        
        # Update status
        job["status"] = "running"
        job["progress"] = {
            "step": "Step 1: Company Selection",
            "current": 1,
            "total": 5,
            "message": f"Selected: {company_name}"
        }
        job["current_step"] = "company_selected"
        
        # Step 1: Company selected (already done)
        await asyncio.sleep(0.5)
        
        # Step 2: Run research
        job["progress"] = {
            "step": "Step 2: Running Research Agent",
            "current": 2,
            "total": 5,
            "message": "Gathering evidence from web sources..."
        }
        job["current_step"] = "research_agent"
        
        research_agent = ResearchAgent(
            tavily_api_key=TAVILY_API_KEY,
            output_dir=RESEARCH_OUTPUT_DIR
        )
        
        # Define progress callback
        def research_progress_callback(progress_info):
            job["progress"]["details"] = progress_info
            if progress_info.get("category"):
                job["progress"]["message"] = progress_info.get("message", "Processing...")
                if progress_info.get("subtopic"):
                    job["progress"]["message"] = f"[{progress_info.get('category', '').replace('_', ' ').title()}] {progress_info.get('message', 'Searching...')}"
                else:
                    job["progress"]["message"] = progress_info.get("message", "Processing category...")
        
        saved_files = research_agent.run_research(
            company_name=company_name,
            financial_data=financial_data,
            progress_callback=research_progress_callback
        )
        
        # Step 3: Load research data and generate report
        job["progress"] = {
            "step": "Step 3: Generating Analyst Report",
            "current": 3,
            "total": 4,
            "message": "Loading research data and creating comprehensive analyst report..."
        }
        job["current_step"] = "report_generation"
        
        summarization_agent = SummarizationAgent(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-4o-mini"
        )
        
        # Load research data
        research_data = summarization_agent.load_research_outputs(
            research_output_dir=RESEARCH_OUTPUT_DIR,
            company_name=company_name
        )
        
        if not research_data:
            raise Exception("No research data found to generate report")
        
        try:
            report = summarization_agent.create_analyst_report(
                company_name=company_name,
                financial_data=financial_data,
                research_data=research_data
            )
            if not report or report.startswith("Error"):
                raise Exception(f"Report generation failed: {report}")
        except Exception as e:
            raise Exception(f"Error generating report: {str(e)}")
        
        # Step 4: Validation
        job["progress"] = {
            "step": "Step 4: Validating Buy/Avoid Decision",
            "current": 4,
            "total": 4,
            "message": "Validating investment decision with 40% return threshold..."
        }
        job["current_step"] = "validation"
        
        try:
            validation = summarization_agent.validate_buy_avoid(
                company_name=company_name,
                financial_data=financial_data,
                research_data=research_data,
                report=report
            )
            if not validation or validation.get("recommendation") == "ERROR":
                raise Exception(f"Validation failed: {validation.get('error', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"Error validating decision: {str(e)}")
        
        # Save report
        try:
            report_path = summarization_agent.save_report(
                company_name=company_name,
                report=report,
                validation=validation,
                output_dir=REPORTS_DIR
            )
        except Exception as e:
            raise Exception(f"Error saving report: {str(e)}")
        
        # Update job with results
        job["status"] = "completed"
        job["progress"] = {
            "step": "Completed",
            "current": 4,
            "total": 4,
            "message": "Research completed successfully"
        }
        job["current_step"] = "completed"
        job["results"] = {
            "report": report,
            "validation": validation,
            "report_path": report_path,
            "recommendation": validation.get("recommendation", "N/A"),
            "confidence": validation.get("confidence", "N/A")
        }
        job["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        job["status"] = "error"
        job["error"] = str(e)
        job["error_details"] = error_details
        job["current_step"] = "error"
        job["progress"] = {
            "step": "Error",
            "current": job["progress"].get("current", 0),
            "total": 5,
            "message": f"Error: {str(e)}"
        }
        print(f"Error in research workflow: {error_details}")


@app.get("/research/status/{research_id}", response_model=ResearchStatus)
async def get_research_status(research_id: str):
    """Get status of a research job"""
    if research_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Research ID not found")
    
    job = research_jobs[research_id]
    return ResearchStatus(
        research_id=job["research_id"],
        status=job["status"],
        company_name=job["company_name"],
        progress=job["progress"],
        current_step=job["current_step"],
        error=job.get("error")
    )


@app.get("/research/results/{research_id}")
async def get_research_results(research_id: str):
    """Get research results"""
    if research_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Research ID not found")
    
    job = research_jobs[research_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Research not completed. Status: {job['status']}")
    
    return job["results"]


@app.get("/reports/{company_name}")
async def download_report(company_name: str):
    """Download markdown report for a company"""
    try:
        # Find latest report for company
        reports_dir = Path(REPORTS_DIR)
        company_safe = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
        
        # Find matching report files
        report_files = list(reports_dir.glob(f"{company_safe}_Analyst_Report_*.md"))
        
        if not report_files:
            raise HTTPException(status_code=404, detail=f"No report found for {company_name}")
        
        # Get most recent report
        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
        
        return FileResponse(
            path=latest_report,
            filename=latest_report.name,
            media_type="text/markdown"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports/list")
async def list_reports():
    """List all available reports"""
    try:
        reports_dir = Path(REPORTS_DIR)
        report_files = list(reports_dir.glob("*_Analyst_Report_*.md"))
        
        reports = []
        for report_file in report_files:
            reports.append({
                "filename": report_file.name,
                "company_name": report_file.name.split("_Analyst_Report_")[0].replace("_", " "),
                "date": report_file.name.split("_Analyst_Report_")[1].replace(".md", ""),
                "size": report_file.stat().st_size,
                "modified": datetime.fromtimestamp(report_file.stat().st_mtime).isoformat()
            })
        
        return {"reports": sorted(reports, key=lambda x: x["modified"], reverse=True)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

