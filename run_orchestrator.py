"""
Simple script to run the research orchestrator
"""

import os
from research_orchestrator import ResearchOrchestrator

# Configuration - must be from environment variables
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def main():
    if not OPENAI_API_KEY:
        print("ERROR: OpenAI API key not found!")
        print("Please set OPENAI_API_KEY environment variable or update the script.")
        print("\nTo get an API key, visit: https://platform.openai.com/api-keys")
        return
    
    if not TAVILY_API_KEY:
        print("ERROR: Tavily API key not found!")
        print("Please set TAVILY_API_KEY environment variable or update the script.")
        return
    
    # Initialize orchestrator
    orchestrator = ResearchOrchestrator(
        tavily_api_key=TAVILY_API_KEY,
        openai_api_key=OPENAI_API_KEY,
        research_output_dir="research_output",
        reports_dir="reports"
    )
    
    # Run complete workflow
    final_state = orchestrator.run()
    
    if final_state and not final_state.get("error"):
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"Company: {final_state.get('company_name')}")
        print(f"Recommendation: {final_state.get('validation_result', {}).get('recommendation', 'N/A')}")
        print(f"Report saved to: {final_state.get('report_file_path', 'N/A')}")
    else:
        print("\nWorkflow completed with errors. Check output above.")


if __name__ == "__main__":
    main()

