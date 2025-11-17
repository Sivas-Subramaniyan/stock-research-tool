"""
Company Selector - Reads and allows selection from ranked_companies.csv
"""

import pandas as pd
from typing import Dict, Optional, List
from pathlib import Path


class CompanySelector:
    """Handles company selection from ranked_companies.csv"""
    
    def __init__(self, csv_path: str = "ranked_companies.csv"):
        """
        Initialize company selector.
        
        Args:
            csv_path: Path to ranked_companies.csv
        """
        self.csv_path = Path(csv_path)
        self.df = None
        self.load_companies()
    
    def load_companies(self):
        """Load companies from CSV file."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        self.df = pd.read_csv(self.csv_path)
        print(f"Loaded {len(self.df)} companies from {self.csv_path}")
    
    def list_companies(self, top_n: Optional[int] = None) -> pd.DataFrame:
        """
        List companies, optionally limited to top N.
        
        Args:
            top_n: Number of top companies to return (by rank)
            
        Returns:
            DataFrame with company information
        """
        if top_n:
            return self.df.head(top_n)[['rank', 'Name', 'Mar Cap Rs.Cr.', 'P/E', 'ROCE %', 'investment_score']]
        return self.df[['rank', 'Name', 'Mar Cap Rs.Cr.', 'P/E', 'ROCE %', 'investment_score']]
    
    def get_company_by_name(self, company_name: str) -> Optional[Dict]:
        """
        Get company data by name (case-insensitive partial match).
        
        Args:
            company_name: Company name to search for
            
        Returns:
            Dictionary with company data or None if not found
        """
        # Try exact match first
        match = self.df[self.df['Name'].str.lower() == company_name.lower()]
        
        # If no exact match, try partial match
        if match.empty:
            match = self.df[self.df['Name'].str.lower().str.contains(company_name.lower(), na=False)]
        
        if match.empty:
            return None
        
        # Get first match
        row = match.iloc[0]
        
        # Extract financial data (handle NaN values)
        def safe_str(value):
            if pd.isna(value) or value == '':
                return ''
            return str(value)
        
        financial_data = {
            "CMP Rs.": safe_str(row.get('CMP Rs.', '')),
            "market_cap": safe_str(row.get('Mar Cap Rs.Cr.', '')),
            "pe_ratio": safe_str(row.get('P/E', '')),
            "roce": safe_str(row.get('ROCE %', '')),
            "sales": safe_str(row.get('Sales Rs.Cr.', '')),
            "opm": safe_str(row.get('OPM %', '')),
            "debt_eq": safe_str(row.get('Debt / Eq', '')),
            "eps_12m": safe_str(row.get('EPS 12M Rs.', '')),
            "prom_hold": safe_str(row.get('Prom. Hold. %', '')),
            "fcf_3y": safe_str(row.get('Free Cash Flow 3Yrs Rs.Cr.', '')),
            "cf_op_3y": safe_str(row.get('CF Opr 3Yrs Rs.Cr.', '')),
            "ind_pe": safe_str(row.get('Ind PE', '')),
            "chg_fii": safe_str(row.get('Chg in FII Hold %', '')),
            "chg_dii": safe_str(row.get('Chg in DII Hold %', '')),
            "wc_days": safe_str(row.get('WC Days', '')),
            "cash_cycle": safe_str(row.get('Cash Cycle', '')),
            "investment_score": safe_str(row.get('investment_score', '')),
            "rank": safe_str(row.get('rank', ''))
        }
        
        return {
            "company_name": row['Name'],
            "financial_data": financial_data
        }
    
    def get_company_by_rank(self, rank: int) -> Optional[Dict]:
        """
        Get company data by rank.
        
        Args:
            rank: Rank of the company (1 = best)
            
        Returns:
            Dictionary with company data or None if not found
        """
        match = self.df[self.df['rank'] == rank]
        
        if match.empty:
            return None
        
        row = match.iloc[0]
        
        # Extract financial data (handle NaN values)
        def safe_str(value):
            if pd.isna(value) or value == '':
                return ''
            return str(value)
        
        financial_data = {
            "CMP Rs.": safe_str(row.get('CMP Rs.', '')),
            "market_cap": safe_str(row.get('Mar Cap Rs.Cr.', '')),
            "pe_ratio": safe_str(row.get('P/E', '')),
            "roce": safe_str(row.get('ROCE %', '')),
            "sales": safe_str(row.get('Sales Rs.Cr.', '')),
            "opm": safe_str(row.get('OPM %', '')),
            "debt_eq": safe_str(row.get('Debt / Eq', '')),
            "eps_12m": safe_str(row.get('EPS 12M Rs.', '')),
            "prom_hold": safe_str(row.get('Prom. Hold. %', '')),
            "fcf_3y": safe_str(row.get('Free Cash Flow 3Yrs Rs.Cr.', '')),
            "cf_op_3y": safe_str(row.get('CF Opr 3Yrs Rs.Cr.', '')),
            "ind_pe": safe_str(row.get('Ind PE', '')),
            "chg_fii": safe_str(row.get('Chg in FII Hold %', '')),
            "chg_dii": safe_str(row.get('Chg in DII Hold %', '')),
            "wc_days": safe_str(row.get('WC Days', '')),
            "cash_cycle": safe_str(row.get('Cash Cycle', '')),
            "investment_score": safe_str(row.get('investment_score', '')),
            "rank": safe_str(row.get('rank', ''))
        }
        
        return {
            "company_name": row['Name'],
            "financial_data": financial_data
        }
    
    def interactive_select(self) -> Optional[Dict]:
        """
        Interactive company selection.
        
        Returns:
            Dictionary with company data or None if cancelled
        """
        print("\n" + "="*60)
        print("Company Selector")
        print("="*60)
        print("\nTop 20 Companies by Investment Score:\n")
        
        top_companies = self.list_companies(top_n=20)
        for idx, row in top_companies.iterrows():
            print(f"Rank {row['rank']:3d}: {row['Name']:40s} | Score: {row['investment_score']:.4f}")
        
        print("\nOptions:")
        print("1. Enter company name (partial match supported)")
        print("2. Enter rank number")
        print("3. Cancel")
        
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        if choice == "1":
            company_name = input("Enter company name: ").strip()
            return self.get_company_by_name(company_name)
        elif choice == "2":
            try:
                rank = int(input("Enter rank number: ").strip())
                return self.get_company_by_rank(rank)
            except ValueError:
                print("Invalid rank number")
                return None
        else:
            return None

