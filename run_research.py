"""
Example script to run the research agent.
"""

from research_agent import ResearchAgent
import json
import os

# Configuration
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # Must be set via environment variable
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY environment variable is required")
COMPANY_NAME = "Transformers and Rectifiers India Limited"  # Change this to your target company

# Optional: Provide financial data if available
FINANCIAL_DATA = {
    "market_cap": "1500000",  # in crores
    "pe_ratio": "25.5",
    "roce": "18.5",
    # Add more financial metrics as needed
}

def main():
    if not TAVILY_API_KEY:
        print("ERROR: Tavily API key not found!")
        print("Please set TAVILY_API_KEY environment variable or update the script.")
        print("\nTo get an API key, visit: https://tavily.com")
        return
    
    # Initialize agent
    agent = ResearchAgent(
        tavily_api_key=TAVILY_API_KEY,
        output_dir="research_output"
    )
    
    # Run research
    saved_files = agent.run_research(
        company_name=COMPANY_NAME,
        financial_data=FINANCIAL_DATA
    )
    
    print("\nResearch completed! Files saved:")
    for category, filepath in saved_files.items():
        if filepath:
            print(f"  {category}: {filepath}")


if __name__ == "__main__":
    main()

