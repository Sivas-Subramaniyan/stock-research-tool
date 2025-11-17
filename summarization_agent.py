"""
Summarization and Validation Agent
Uses OpenAI GPT-4o-mini to preprocess research outputs, extract core facts, and validate buy/avoid decision.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI
from datetime import datetime

# Fix Windows encoding issues
if sys.platform == 'win32':
    # Set stdout encoding to UTF-8 on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


class SummarizationAgent:
    """
    Agent that preprocesses research outputs, extracts core facts, and validates buy/avoid decision
    based on 40% return in 3 years minimum threshold.
    """
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize summarization agent.
        
        Args:
            openai_api_key: OpenAI API key
            model: OpenAI model to use (default: gpt-4o-mini)
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model
    
    def load_research_outputs(self, research_output_dir: str, company_name: str) -> Dict:
        """
        Load all research output JSON files for a company.
        
        Args:
            research_output_dir: Directory containing research outputs
            company_name: Company name to load research for
            
        Returns:
            Dictionary with all research categories
        """
        research_dir = Path(research_output_dir)
        company_safe = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
        
        research_data = {}
        
        # Load all category files
        for category_file in research_dir.glob(f"*_{company_safe}_*.json"):
            if category_file.name.startswith("summary_"):
                continue
            
            try:
                with open(category_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    category = data.get('category', 'unknown')
                    research_data[category] = data
            except Exception as e:
                print(f"Error loading {category_file}: {e}")
        
        return research_data
    
    def extract_category_essence(self, company_name: str, category_name: str, category_data: Dict) -> Dict:
        """
        Extract core facts and essence from a single research category using reasoning.
        
        Args:
            company_name: Company name
            category_name: Name of the category
            category_data: Full category data with evidence
            
        Returns:
            Dictionary with extracted core facts
        """
        print(f"  Processing category: {category_name}")
        
        # Prepare evidence for this category
        evidence_text = ""
        subtopics = category_data.get('subtopics', {})
        
        for subtopic, subtopic_data in subtopics.items():
            evidence_items = subtopic_data.get('evidence', [])
            evidence_text += f"\n\nSubtopic: {subtopic}\n"
            evidence_text += f"Query: {subtopic_data.get('query', '')}\n"
            evidence_text += f"Results: {subtopic_data.get('results_count', 0)}\n"
            evidence_text += "Evidence:\n"
            
            for i, item in enumerate(evidence_items[:10], 1):  # Limit to top 10 per subtopic
                evidence_text += f"\n{i}. Title: {item.get('title', 'N/A')}\n"
                evidence_text += f"   Source: {item.get('source_domain', 'N/A')}\n"
                evidence_text += f"   Confidence: {item.get('confidence', 'N/A')}\n"
                evidence_text += f"   Excerpt: {item.get('excerpt', 'N/A')}\n"
                if item.get('raw_content'):
                    # Include first 500 chars of raw content for context
                    evidence_text += f"   Content: {item.get('raw_content', '')[:500]}...\n"
        
        # Create reasoning prompt for essence extraction
        prompt = f"""You are a research analyst tasked with extracting CORE FACTS and ESSENCE from research evidence about {company_name}.

Category: {category_name}

Research Evidence:
{evidence_text}

INSTRUCTIONS:
1. Read and understand ALL the evidence provided
2. Use REASONING to identify the CORE FACTS - what are the most important, verifiable facts?
3. Extract KEY NUMBERS, DATES, NAMES, and QUOTES that are factual and verifiable
4. Identify RISKS, RED FLAGS, and CONCERNS (if any)
5. Identify STRENGTHS and POSITIVE INDICATORS (if any)
6. Note the CONFIDENCE LEVEL of sources (high/medium/low)
7. Focus on FACTS, not opinions or speculation
8. Be CRITICAL - if there are concerns, fraud, legal issues, highlight them prominently

Output your analysis in JSON format:
{{
    "category": "{category_name}",
    "core_facts": [
        "Fact 1 with source and date",
        "Fact 2 with source and date",
        ...
    ],
    "key_numbers": {{
        "metric1": "value with source",
        "metric2": "value with source",
        ...
    }},
    "risks_and_red_flags": [
        "Risk/red flag 1 with source",
        "Risk/red flag 2 with source",
        ...
    ],
    "strengths": [
        "Strength 1 with source",
        "Strength 2 with source",
        ...
    ],
    "key_quotes": [
        "Quote 1 with source",
        "Quote 2 with source",
        ...
    ],
    "source_quality": {{
        "high_confidence_sources": ["source1", "source2", ...],
        "medium_confidence_sources": ["source1", "source2", ...],
        "low_confidence_sources": ["source1", "source2", ...]
    }},
    "summary": "200 word summary of the most important findings from this category"
}}

Be THOROUGH but CONCISE. Extract only the most important facts. If no evidence found, indicate that clearly."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a research analyst expert at extracting core facts from evidence. You use reasoning to identify the most important, verifiable information. You are critical and focus on facts, not opinions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
                max_tokens=16384  # GPT-4o-mini max is 16384
            )
            
            essence = json.loads(response.choices[0].message.content)
            return essence
            
        except Exception as e:
            print(f"    Error extracting essence for {category_name}: {e}")
            return {
                "category": category_name,
                "core_facts": [],
                "key_numbers": {},
                "risks_and_red_flags": [],
                "strengths": [],
                "key_quotes": [],
                "source_quality": {},
                "summary": f"Error processing category: {str(e)}"
            }
    
    def preprocess_research_data(self, company_name: str, research_data: Dict, progress_callback: Optional[callable] = None) -> Dict:
        """
        Preprocess all research categories to extract core facts and essence.
        
        Args:
            company_name: Company name
            research_data: Full research data dictionary
            
        Returns:
            Dictionary with condensed core facts from all categories
        """
        print(f"\n{'='*60}")
        print(f"Preprocessing Research Data for: {company_name}")
        print(f"{'='*60}")
        print(f"Processing {len(research_data)} categories...\n")
        
        condensed_data = {
            "company_name": company_name,
            "categories_processed": len(research_data),
            "category_essences": {}
        }
        
        # Process each category
        total_categories = len(research_data)
        for cat_idx, (category_name, category_data) in enumerate(research_data.items(), 1):
            if progress_callback:
                progress_callback({
                    "category": category_name,
                    "category_number": cat_idx,
                    "total_categories": total_categories,
                    "message": f"Extracting core facts from category {cat_idx}/{total_categories}: {category_name.replace('_', ' ').title()}"
                })
            
            try:
                essence = self.extract_category_essence(company_name, category_name, category_data)
                condensed_data["category_essences"][category_name] = essence
                print(f"  [OK] Extracted essence from {category_name}")
            except Exception as e:
                print(f"  [ERROR] Error extracting essence from {category_name}: {e}")
                if progress_callback:
                    progress_callback({
                        "category": category_name,
                        "error": str(e),
                        "message": f"Error processing {category_name}: {str(e)}"
                    })
                condensed_data["category_essences"][category_name] = {
                    "category": category_name,
                    "core_facts": [],
                    "key_numbers": {},
                    "risks_and_red_flags": [],
                    "strengths": [],
                    "key_quotes": [],
                    "source_quality": {},
                    "summary": f"Error processing: {str(e)}"
                }
        
        print(f"\n[OK] Preprocessing complete. Extracted core facts from {len(research_data)} categories.")
        
        return condensed_data
    
    def create_analyst_report(self, company_name: str, financial_data: Dict, research_data: Dict) -> str:
        """
        Create comprehensive analyst report using full research data.
        
        Args:
            company_name: Company name
            financial_data: Financial data dictionary
            research_data: Full research data dictionary
            
        Returns:
            Markdown formatted analyst report
        """
        # Prepare research summary for prompt
        research_summary = self._prepare_research_summary(research_data)
        
        # Prepare financial data summary
        financial_summary = self._prepare_financial_summary(financial_data)
        
        # Create prompt
        prompt = f"""You are a STRICT and CRITICAL equity research analyst. Your task is to create a comprehensive analyst report with EXTREME SCRUTINY. You must be CONSERVATIVE and focus heavily on RISKS, FRAUD, MALPRACTICES, and PAST TRACK RECORDS. Default to AVOID unless there is STRONG EVIDENCE for BUY.

Company: {company_name}

Financial Data:
{financial_summary}

Research Evidence (by Category):
{research_summary}

CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. Start with **BUY** or **AVOID** recommendation in bold at the top
2. Be EXTREMELY STRINGENT - default to AVOID unless overwhelming evidence supports BUY
3. PRIORITIZE RISK ANALYSIS:
   - Scrutinize ALL fraud cases, scams, investigations, regulatory actions
   - Examine ALL pending legal cases, lawsuits, litigation history
   - Check for SEBI violations, penalties, enforcement actions
   - Look for corporate governance issues, management malpractices
   - Identify accounting irregularities, restatements, auditor qualifications
   - Check for insider trading violations, market manipulation
   - Review regulatory warnings, notices from stock exchanges
   - Analyze past track record failures, business failures
   - Check credit rating downgrades, debt defaults
   - Look for whistleblower complaints, corporate scandals

4. FINANCIAL RED FLAGS - CHECK THOROUGHLY:
   - Declining promoter holdings (check if promoter_hold < 50% is a concern)
   - FII/DII exits (negative changes in FII/DII holdings are red flags)
   - Related party transactions, questionable deals
   - Auditor changes, frequent CFO changes
   - Working capital issues, cash flow problems
   - Debt restructuring, loan defaults
   - Pledged shares, promoter share pledging

5. PAST TRACK RECORD - BE CRITICAL:
   - Analyze historical performance over 5-10 years
   - Look for consistent patterns of poor performance
   - Check for volatility in financial metrics
   - Examine management's track record of capital allocation

6. For each category, use the core facts provided to build your analysis
7. Extract and present factual data, numbers, and quotes with proper citations
8. Identify weaknesses FIRST, then strengths
9. Assess competitive position, financial health, management quality with SKEPTICISM
10. Determine if company can achieve 40%+ return over 3 years - be CONSERVATIVE
11. Provide detailed risk factors - be COMPREHENSIVE
12. Determine growth opportunities but also identify what could go wrong

OUTPUT FORMAT:
- Start with **BUY** or **AVOID** in bold
- Use markdown formatting
- Include sections for each research category
- PRIORITIZE sections on risks, fraud, malpractices, red flags
- Provide clear reasoning - if BUY, explain why risks are manageable
- Include confidence level in the recommendation
- Cite sources where applicable

REMEMBER: 
- Be CONSERVATIVE - it's better to AVOID a good stock than BUY a bad one
- Default to AVOID unless there is STRONG, COMPELLING evidence for BUY
- Focus on what could go WRONG, not just what could go right
- Past track record and management integrity are CRITICAL factors"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a STRICT and CRITICAL equity research analyst with expertise in fundamental analysis and valuation. You are EXTREMELY CONSERVATIVE and default to AVOID unless there is OVERWHELMING evidence for BUY. You prioritize risk management, fraud detection, and past track record analysis over potential returns. You provide evidence-based investment recommendations with extreme scrutiny."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=16384  # GPT-4o-mini max is 16384
            )
            
            report = response.choices[0].message.content
            return report
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def validate_buy_avoid(self, company_name: str, financial_data: Dict, research_data: Dict, report: str) -> Dict:
        """
        Validate buy/avoid decision based on 40% return threshold using full research data.
        
        Args:
            company_name: Company name
            financial_data: Financial data
            research_data: Full research data
            report: Generated analyst report
            
        Returns:
            Dictionary with validation results
        """
        # Extract key financial metrics
        current_price = financial_data.get('CMP Rs.', financial_data.get('current_price', ''))
        pe_ratio = financial_data.get('pe_ratio', '')
        roce = financial_data.get('roce', '')
        market_cap = financial_data.get('market_cap', '')
        
        # Extract financial metrics for validation
        promoter_hold = financial_data.get('prom_hold', '')
        chg_fii = financial_data.get('chg_fii', '')
        chg_dii = financial_data.get('chg_dii', '')
        debt_eq = financial_data.get('debt_eq', '')
        fcf_3y = financial_data.get('fcf_3y', '')
        wc_days = financial_data.get('wc_days', '')
        cash_cycle = financial_data.get('cash_cycle', '')
        industry_pe = financial_data.get('ind_pe', '')
        
        # Prepare research summary for validation (truncate if too long)
        research_summary = self._prepare_research_summary(research_data)
        if len(research_summary) > 50000:  # Limit to ~50k chars
            research_summary = research_summary[:50000] + "\n... (truncated for length)"
        
        # Truncate report if too long
        report_truncated = report[:20000] + "... (truncated)" if len(report) > 20000 else report
        
        validation_prompt = f"""You are a STRICT and CRITICAL equity research expert. Your job is to carefully evaluate companies for BUY or AVOID decisions with EXTREME SCRUTINY. You must be CONSERVATIVE and focus heavily on RISKS, FRAUD, MALPRACTICES, and PAST TRACK RECORDS. Default to AVOID unless there is OVERWHELMING evidence for BUY.

Company: {company_name}

Financial Metrics:
- Market Cap: {market_cap} Cr
- P/E Ratio: {pe_ratio}
- ROCE: {roce}%
- Current Price: {current_price}
- Promoter Holding: {promoter_hold}%
- Change in FII Holding: {chg_fii}%
- Change in DII Holding: {chg_dii}%
- Debt/Equity: {debt_eq}
- Free Cash Flow (3Y): {fcf_3y} Cr
- Working Capital Days: {wc_days}
- Cash Cycle: {cash_cycle}
- Industry P/E: {industry_pe}

Research Evidence:
{research_summary[:30000]}

Analyst Report:
{report_truncated}

CRITICAL ANALYSIS GUIDELINES:

1. Financials first: Review hard numbers – profitability, growth, leverage, cash flows, capital efficiency. RED FLAGS: Declining promoter holdings (<50%), FII/DII exits, high debt, negative cash flow, poor working capital management.

2. Risk and fraud analysis: PRIORITIZE - Scrutinize ALL fraud cases, investigations, regulatory actions, lawsuits, SEBI violations, governance issues, accounting irregularities, insider trading, market manipulation.

3. Past track record: Analyze 5-10 year history. Look for consistent poor performance, volatility, management failures, capital allocation mistakes.

4. Moat and growth drivers: Only BUY if there's STRONG evidence of sustainable competitive advantage AND clear growth pathway to 40%+ return in 3 years.

5. Upside potential: Estimate if at least 40% upside in 3 years is plausible. Be CONSERVATIVE. Default to AVOID if uncertain.

6. Final call: 
   - BUY ONLY if: financials are strong, no major red flags, clear moat, manageable risks, and 40%+ return is highly probable.
   - AVOID if: any material risks, fraud concerns, weak financials, no clear moat, or uncertain upside.
   - When in doubt, ALWAYS choose AVOID.

7. Extract specific red flags and financial concerns from the research evidence and analyst report.

Please provide your evaluation in the following JSON structure (use empty arrays if none found):
{{
    "recommendation": "BUY" or "AVOID",
    "confidence": "high" or "medium" or "low",
    "expected_return_3y": "percentage estimate (e.g., '45%' or 'N/A')",
    "probability_40pct_return": "high/medium/low",
    "key_drivers": ["driver1", "driver2", ...],
    "key_risks": ["risk1", "risk2", ...],
    "red_flags_found": ["flag1", "flag2", ...],
    "financial_concerns": ["concern1", "concern2", ...],
    "reasoning": "detailed explanation: summarize your reasoning—use both numbers and qualitative arguments"
}}"""


        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a STRICT quantitative analyst specializing in return projections and risk assessment. You are EXTREMELY CONSERVATIVE and default to AVOID unless there is OVERWHELMING evidence for BUY. You prioritize risk management over potential returns."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
                max_tokens=16384  # GPT-4o-mini max is 16384
            )
            
            validation_result = json.loads(response.choices[0].message.content)
            return validation_result
            
        except Exception as e:
            return {
                "recommendation": "ERROR",
                "error": str(e),
                "reasoning": "Failed to generate validation"
            }
    
    def _prepare_research_summary(self, research_data: Dict) -> str:
        """Prepare research summary from full research data."""
        summary_parts = []
        
        for category_name, category_data in research_data.items():
            category_display = category_name.replace('_', ' ').title()
            summary_parts.append(f"\n{'='*60}")
            summary_parts.append(f"{category_display}")
            summary_parts.append(f"{'='*60}")
            
            subtopics = category_data.get('subtopics', {})
            for subtopic, subtopic_data in subtopics.items():
                summary_parts.append(f"\nSubtopic: {subtopic}")
                summary_parts.append(f"Query: {subtopic_data.get('query', 'N/A')}")
                summary_parts.append(f"Results Found: {subtopic_data.get('results_count', 0)}")
                
                evidence_items = subtopic_data.get('evidence', [])
                if evidence_items:
                    summary_parts.append(f"\nEvidence ({len(evidence_items)} items):")
                    for i, item in enumerate(evidence_items[:10], 1):  # Limit to top 10 per subtopic
                        summary_parts.append(f"\n  {i}. {item.get('title', 'N/A')}")
                        summary_parts.append(f"     Source: {item.get('source_domain', 'N/A')}")
                        summary_parts.append(f"     URL: {item.get('url', 'N/A')}")
                        summary_parts.append(f"     Date: {item.get('retrieval_date', 'N/A')}")
                        summary_parts.append(f"     Confidence: {item.get('confidence', 'N/A')}")
                        excerpt = item.get('excerpt', 'N/A')
                        if excerpt and len(excerpt) > 200:
                            excerpt = excerpt[:200] + "..."
                        summary_parts.append(f"     Excerpt: {excerpt}")
        
        return "\n".join(summary_parts)
    
    def _prepare_financial_summary(self, financial_data: Dict) -> str:
        """Prepare financial data summary for prompt."""
        lines = []
        for key, value in financial_data.items():
            if value and str(value) != 'nan':
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")
        return "\n".join(lines)
    
    def generate_tldr_summary(self, company_name: str, validation: Dict, report: str) -> str:
        """
        Generate a TLDR executive summary paragraph based on validation and report.
        
        Args:
            company_name: Company name
            validation: Validation results dictionary
            report: Analyst report text
            
        Returns:
            TLDR summary paragraph
        """
        recommendation = validation.get('recommendation', 'N/A')
        confidence = validation.get('confidence', 'N/A')
        expected_return = validation.get('expected_return_3y', 'N/A')
        reasoning = validation.get('reasoning', '')
        
        # Truncate reasoning if too long
        reasoning_truncated = reasoning[:500] + "..." if len(reasoning) > 500 else reasoning
        
        tldr_prompt = f"""Generate a concise TLDR (Too Long; Didn't Read) executive summary paragraph for an investment recommendation. This should be a single, well-written paragraph (3-5 sentences) that captures the essence of the investment decision.

Company: {company_name}
Recommendation: {recommendation}
Confidence: {confidence}
Expected 3-Year Return: {expected_return}
Key Reasoning: {reasoning_truncated}

Write a clear, professional executive summary paragraph that:
1. States the recommendation (BUY/AVOID) upfront
2. Provides the key rationale in 2-3 sentences
3. Mentions the expected return and confidence level
4. Is suitable for busy executives who need a quick overview

Output ONLY the paragraph text, no markdown formatting, no headers, just the paragraph itself."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at writing concise executive summaries for investment reports. You write clear, professional, and informative summaries."},
                    {"role": "user", "content": tldr_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            tldr = response.choices[0].message.content.strip()
            return tldr
            
        except Exception as e:
            # Fallback to simple summary if generation fails
            return f"{company_name} receives a {recommendation} recommendation with {confidence} confidence. Expected 3-year return is {expected_return}. {reasoning_truncated[:200]}..."
    
    def save_report(self, company_name: str, report: str, validation: Dict, output_dir: str = "reports"):
        """
        Save analyst report and validation to markdown file.
        
        Args:
            company_name: Company name
            report: Analyst report text
            validation: Validation results dictionary
            output_dir: Output directory for reports
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        safe_company_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        filename = f"{safe_company_name}_Analyst_Report_{date_str}.md"
        filepath = output_path / filename
        
        # Generate TLDR summary
        print("\nGenerating TLDR executive summary...")
        tldr_summary = self.generate_tldr_summary(company_name, validation, report)
        
        # Create markdown content
        md_content = f"""# Analyst Report: {company_name}

**Date:** {date_str}

---

## Executive Summary

**Recommendation:** {validation.get('recommendation', 'N/A')}  
**Confidence:** {validation.get('confidence', 'N/A')}  
**Expected 3-Year Return:** {validation.get('expected_return_3y', 'N/A')}  
**Probability of 40%+ Return:** {validation.get('probability_40pct_return', 'N/A')}

### TLDR Summary

{tldr_summary}

---

## Detailed Analysis

{report}

---

## Validation & Recommendation

### Recommendation: {validation.get('recommendation', 'N/A')}

### Key Drivers:
{chr(10).join(f"- {driver}" for driver in validation.get('key_drivers', [])) if validation.get('key_drivers') else "- None identified"}

### Key Risks:
{chr(10).join(f"- {risk}" for risk in validation.get('key_risks', [])) if validation.get('key_risks') else "- None identified"}

### Red Flags Found:
{chr(10).join(f"- [WARNING] {flag}" for flag in validation.get('red_flags_found', [])) if validation.get('red_flags_found') else "- No major red flags identified"}

### Financial Concerns:
{chr(10).join(f"- [WARNING] {concern}" for concern in validation.get('financial_concerns', [])) if validation.get('financial_concerns') else "- No major financial concerns identified"}

### Reasoning:
{validation.get('reasoning', 'N/A')}

---

*Report generated by AI Research Agent*
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\n[OK] Report saved to: {filepath}")
        return str(filepath)
