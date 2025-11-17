"""
Evidence-Gathering Research Agent
Performs web searches using Tavily API and accumulates evidence across 10 predefined categories.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import requests
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == 'win32':
    # Set stdout encoding to UTF-8 on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


class ResearchAgent:
    """
    Evidence-gathering research agent that searches the web and accumulates
    factual evidence about companies mapped to predefined business principles.
    """
    
    def __init__(self, tavily_api_key: str, output_dir: str = "research_output"):
        """
        Initialize the research agent.
        
        Args:
            tavily_api_key: Tavily API key for web search
            output_dir: Directory to store research results
        """
        self.tavily_api_key = tavily_api_key
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.company_name = ""
        self.financial_data = {}
        self.retrieval_date = datetime.now().strftime("%Y-%m-%d")
        
        # Define search categories with their subtopics
        self.search_categories = self._define_search_categories()
    
    def _define_search_categories(self) -> Dict[str, List[str]]:
        """Define all 10 search categories with their subtopics."""
        return {
    "1_business_fundamentals_and_model_stability": [
        "core business description and primary value proposition",
        "segment-wise revenue and profit breakdown (product, geography, customer type)",
        "revenue concentration — top customers >10% share, stability of key contracts",
        "business model repeatability — recurring vs transactional revenue proportion",
        "competitive landscape — primary competitors, differentiation factors",
        "industry structure and cyclicality (barriers to entry, supplier/customer power)"
    ],

    "2_financial_strength_and_quality_of_earnings": [
        "5-year trend — revenue, EBITDA, operating profit, PAT",
        "cash flow consistency — CFO vs PAT comparison, FCF sustainability",
        "ROE, ROCE, ROA — trend and consistency vs industry averages",
        "margin stability — gross, operating, net margins over 5 years",
        "quality of earnings — one-offs, restatements, extraordinary items",
        "working capital cycle efficiency — receivable days, inventory, payables trend"
    ],

    "3_balance_sheet_health_and_liquidity": [
        "debt-to-equity ratio, interest coverage ratio, leverage trend",
        "cash and liquid assets vs short-term obligations",
        "capital expenditure trend — maintenance vs growth capex",
        "contingent liabilities, off-balance sheet exposures, guarantees",
        "credit ratings (if available), debt maturity profile"
    ],

    "4_intrinsic_value_and_market_positioning": [
        "current market price, market cap, enterprise value, valuation timestamp",
        "analyst target price range, consensus valuation estimates",
        "institutional holding trend — top holders, changes over last 4 quarters",
        "DCF or comparable-based fair value estimation (P/E, EV/EBITDA, P/B)",
        "valuation premium/discount vs historical and sector averages"
    ],

    "5_economic_moat_and_durability": [
        "sources of moat — brand equity, IP, patents, regulatory licenses, switching costs",
        "evidence of pricing power — gross margin resilience, market share stability",
        "distribution advantages, customer loyalty indicators, renewal rates",
        "network effects, ecosystem lock-ins, data advantage",
        "moat sustainability — evidence of erosion or strengthening"
    ],

    "6_management_integrity_and_capital_allocation": [
        "key management bios — track record, tenure, competence",
        "insider ownership and recent insider trading (buy/sell trends)",
        "capital allocation track record — acquisitions, buybacks, dividends, debt repayment",
        "governance indicators — board independence, audit quality, disclosures",
        "transparency — investor communication, accounting conservatism"
    ],

    "7_growth_drivers_and_future_visibility": [
        "strategic initiatives — expansion plans, R&D, product pipeline, partnerships",
        "industry growth projections and tailwinds (sources: McKinsey, CRISIL, IBIS, etc.)",
        "company’s growth guidance vs historical delivery rate",
        "long-term scalability and reinvestment opportunities",
        "technological disruption risk — readiness for innovation"
    ],

    "8_macro_and_regional_sensitivity": [
        "dependence on domestic vs export markets, FX sensitivity",
        "regulatory dependencies, policy changes, taxation impact",
        "economic cyclicality exposure (interest rate, commodity price linkages)",
        "country risk, trade barriers, geopolitical exposure"
    ],

    "9_behavioral_and_market_sentiment": [
        "12-month major news — litigation, fraud, leadership change, contracts won/lost",
        "analyst rating distribution and changes",
        "short interest, retail sentiment (social chatter, trend spikes)",
        "FII/DII flow trends and volatility of institutional confidence"
    ],

    "10_risks_and_downside_scenarios": [
        "structural industry risks — technology obsolescence, policy threats",
        "execution risks — management capability, delays in capex or product rollout",
        "financial risks — leverage, liquidity crunch, credit events",
        "governance or compliance risks — audit issues, insider conflicts",
        "fraud/malpractice indicators — investigations, whistleblower complaints"
    ],

    "11_integrity_and_governance_health": [
        "related-party transactions, promoter pledging trends",
        "corporate governance ratings (if any), regulatory penalties or SEBI actions",
        "litigation record and material legal exposures",
        "ESG disclosures, environmental or social controversies"
    ],

    "12_overall_fundamental_conviction_score": [
        "stability across cycles — earnings resilience in past downturns",
        "cash flow predictability and margin durability",
        "management credibility and governance trust level",
        "valuation comfort vs fundamentals",
        "net upside-to-risk trade-off — prudent Buy/Avoid recommendation basis"
    ]
}

    def search_tavily(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a search using Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with metadata
        """
        url = "https://api.tavily.com/search"
        
        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": "advanced",
            "include_answer": False,
            "include_raw_content": False,
            "max_results": max_results,
            "include_domains": [],
            "exclude_domains": []
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for result in data.get("results", []):
                evidence_item = {
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "source_domain": self._extract_domain(result.get("url", "")),
                    "retrieval_date": self.retrieval_date,
                    "excerpt": self._truncate_excerpt(result.get("content", ""), max_words=100),
                    "confidence": self._assess_confidence(result),
                    "raw_content": result.get("content", "")[:2000]  # First 2000 chars for reference
                }
                results.append(evidence_item)
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching Tavily: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc or ""
        except:
            return ""
    
    def _truncate_excerpt(self, text: str, max_words: int = 200) -> str:
        """Truncate text to max_words and append '...' if longer."""
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]) + "..."
    
    def _assess_confidence(self, result: Dict[str, Any]) -> str:
        """
        Assess confidence level based on source authority and recency.
        
        Returns: 'high', 'medium', or 'low'
        """
        url = result.get("url", "").lower()
        domain = self._extract_domain(url).lower()
        
        # High confidence sources
        high_confidence_domains = [
            "sec.gov", "edgar", "sebi.gov.in", "mca.gov.in", "xbrl",
            "bloomberg.com", "reuters.com", "factset.com", "finance.yahoo.com",
            "company website", "investor relations", "annual report"
        ]
        
        # Medium confidence sources
        medium_confidence_domains = [
            "seekingalpha.com", "morningstar.com", "yahoo.com/finance",
            "financial times", "wall street journal", "economic times"
        ]
        
        # Check domain
        for high_domain in high_confidence_domains:
            if high_domain in domain or high_domain in url:
                return "high"
        
        for med_domain in medium_confidence_domains:
            if med_domain in domain or med_domain in url:
                return "medium"
        
        # Default to medium for unknown sources
        return "medium"
    
    def search_category(self, category_name: str, subtopics: List[str], progress_callback: Optional[callable] = None) -> Dict[str, Any]:
        """
        Search all subtopics for a category and accumulate results.
        
        Args:
            category_name: Name of the search category
            subtopics: List of subtopic search queries
            
        Returns:
            Dictionary containing all evidence for this category
        """
        print(f"\n{'='*60}")
        print(f"Searching Category: {category_name}")
        print(f"{'='*60}")
        
        category_results = {
            "category": category_name,
            "company_name": self.company_name,
            "retrieval_date": self.retrieval_date,
            "financial_data_provided": self.financial_data,
            "subtopics": {}
        }
        
        for i, subtopic in enumerate(subtopics, 1):
            print(f"\n[{i}/{len(subtopics)}] Searching: {subtopic}")
            
            # Report subtopic progress
            if progress_callback:
                progress_callback({
                    "category": category_name,
                    "subtopic": subtopic,
                    "subtopic_number": i,
                    "total_subtopics": len(subtopics),
                    "message": f"Searching: {subtopic}"
                })
            
            # Enhance query with company name
            enhanced_query = f"{self.company_name} {subtopic}"
            
            # Perform search - more results for risk/fraud categories
            if "risk" in category_name.lower() or "fraud" in category_name.lower() or "red_flag" in category_name.lower():
                max_results = 10
            else:
                max_results = 10
            
            try:
                results = self.search_tavily(enhanced_query, max_results=max_results)
                
                category_results["subtopics"][subtopic] = {
                    "query": enhanced_query,
                    "results_count": len(results),
                    "evidence": results
                }
                
                print(f"  Found {len(results)} results")
                
                # Report results found
                if progress_callback:
                    progress_callback({
                        "category": category_name,
                        "subtopic": subtopic,
                        "subtopic_number": i,
                        "total_subtopics": len(subtopics),
                        "results_found": len(results),
                        "message": f"Found {len(results)} results for: {subtopic}"
                    })
            except Exception as e:
                print(f"  Error searching {subtopic}: {e}")
                if progress_callback:
                    progress_callback({
                        "category": category_name,
                        "subtopic": subtopic,
                        "error": str(e),
                        "message": f"Error searching {subtopic}: {str(e)}"
                    })
                category_results["subtopics"][subtopic] = {
                    "query": enhanced_query,
                    "results_count": 0,
                    "evidence": [],
                    "error": str(e)
                }
        
        return category_results
    
    def save_category_results(self, category_name: str, results: Dict[str, Any]) -> str:
        """
        Save category results to a JSON file.
        
        Args:
            category_name: Name of the category
            results: Results dictionary to save
            
        Returns:
            Path to saved file
        """
        # Create safe filename - ensure company_name is set
        if not self.company_name or self.company_name.strip() == "":
            raise ValueError(f"Company name is empty! Cannot save results for category: {category_name}")
        
        safe_company_name = "".join(c for c in self.company_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_company_name = safe_company_name.replace(' ', '_')
        
        if not safe_company_name:
            raise ValueError(f"Company name '{self.company_name}' resulted in empty safe filename!")
        
        filename = f"{category_name}_{safe_company_name}_{self.retrieval_date}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Saved results to: {filepath}")
        return str(filepath)
    
    def run_research(self, company_name: str, financial_data: Optional[Dict] = None, progress_callback: Optional[callable] = None) -> Dict[str, str]:
        """
        Run complete research across all categories.
        
        Args:
            company_name: Name of the company to research
            financial_data: Optional dictionary of financial data
            
        Returns:
            Dictionary mapping category names to file paths
        """
        self.company_name = company_name
        self.financial_data = financial_data or {}
        
        print(f"\n{'#'*60}")
        print(f"Starting Research for: {company_name}")
        print(f"Date: {self.retrieval_date}")
        print(f"{'#'*60}\n")
        
        saved_files = {}
        
        # Process each category sequentially
        total_categories = len(self.search_categories)
        for cat_idx, (category_name, subtopics) in enumerate(self.search_categories.items(), 1):
            try:
                # Report progress
                if progress_callback:
                    progress_callback({
                        "category": category_name,
                        "category_number": cat_idx,
                        "total_categories": total_categories,
                        "subtopic": None,
                        "subtopic_number": 0,
                        "total_subtopics": len(subtopics),
                        "message": f"Processing category {cat_idx}/{total_categories}: {category_name.replace('_', ' ').title()}"
                    })
                
                # Search category with progress reporting
                results = self.search_category(category_name, subtopics, progress_callback)
                
                # Save results
                filepath = self.save_category_results(category_name, results)
                saved_files[category_name] = filepath
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"\n[ERROR] Error processing {category_name}: {e}")
                if progress_callback:
                    progress_callback({
                        "category": category_name,
                        "error": str(e),
                        "message": f"Error processing {category_name}: {str(e)}"
                    })
                saved_files[category_name] = None
        
        # Create summary file - ensure company_name is set
        if not self.company_name or self.company_name.strip() == "":
            raise ValueError("Company name is empty! Cannot create summary file.")
        
        safe_company_name = "".join(c for c in self.company_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_company_name = safe_company_name.replace(' ', '_')
        
        if not safe_company_name:
            raise ValueError(f"Company name '{self.company_name}' resulted in empty safe filename!")
        
        summary = {
            "company_name": self.company_name,
            "research_date": self.retrieval_date,
            "financial_data": self.financial_data,
            "categories_completed": len([f for f in saved_files.values() if f]),
            "category_files": saved_files
        }
        
        summary_path = self.output_dir / f"summary_{safe_company_name}_{self.retrieval_date}.json"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'#'*60}")
        print(f"Research Complete!")
        print(f"Summary saved to: {summary_path}")
        print(f"{'#'*60}\n")
        
        return saved_files


def main():
    """Main entry point for the research agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evidence-Gathering Research Agent")
    parser.add_argument("--company", required=True, help="Company name to research")
    parser.add_argument("--api-key", required=True, help="Tavily API key")
    parser.add_argument("--output-dir", default="research_output", help="Output directory for results")
    parser.add_argument("--financial-data", help="Path to JSON file with financial data (optional)")
    
    args = parser.parse_args()
    
    # Load financial data if provided
    financial_data = {}
    if args.financial_data:
        with open(args.financial_data, 'r') as f:
            financial_data = json.load(f)
    
    # Initialize agent
    agent = ResearchAgent(
        tavily_api_key=args.api_key,
        output_dir=args.output_dir
    )
    
    # Run research
    agent.run_research(
        company_name=args.company,
        financial_data=financial_data
    )


if __name__ == "__main__":
    main()

