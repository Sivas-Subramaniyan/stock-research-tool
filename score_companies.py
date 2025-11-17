#%%
# score_companies.py

import pandas as pd
import numpy as np
#%%
# ---------- CONFIG ----------
INPUT_FILE = "screener_results_cleaned.xlsx"   # change if needed
SHEET = 0                               # sheet name or index
OUTPUT_FILE = "ranked_companies.csv"

# Column names (as per your list). Edit strings if your excel has different names.
COLS = {
    "name": "Name",
    "marcap": "Mar Cap Rs.Cr.",
    "pe": "P/E",
    "ind_pe": "Ind PE",
    "roce": "ROCE %",
    "sales": "Sales Rs.Cr.",
    "opm": "OPM %",
    "debt_eq": "Debt / Eq",
    "eps_12m": "EPS 12M Rs.",
    "prom_hold": "Prom. Hold. %",
    "fcf_3y": "Free Cash Flow 3Yrs Rs.Cr.",
    "cf_op_3y": "CF Opr 3Yrs Rs.Cr.",
    "chg_fii": "Chg in FII Hold %",
    "chg_dii": "Chg in DII Hold %",
    "wc_days": "WC Days",
    "cash_cycle": "Cash Cycle",
    #"sales_growth_3y": "Sales growth 3Years",
    #"eps_growth_3y": "EPS growth 3Years",
}

# ---------- WEIGHTS (tweakable) ----------
WEIGHTS = {
    "roce": 0.20,
    "fcf_3y": 0.20,
    #"sales_growth_3y": 0.12,
    #"eps_growth_3y": 0.12,
    "debt_eq": 0.10,
    "valuation": 0.10,       # P/E vs Ind PE
    "cf_op_3y": 0.10,
    "opm": 0.10,
    "prom_hold": 0.05,
    "wc_efficiency": 0.15,  # combines WC Days and Cash Cycle
}

# ---------- HELPER FUNCTIONS ----------
def winsorize_series(s, lower_q=0.05, upper_q=0.95):
    """Clip values at given quantiles, handling NaNs."""
    if s.dropna().empty:
        return s
    lo = s.quantile(lower_q)
    hi = s.quantile(upper_q)
    return s.clip(lower=lo, upper=hi)

def minmax_scale(s):
    mn = s.min()
    mx = s.max()
    if pd.isna(mn) or pd.isna(mx) or mx == mn:
        return pd.Series(0.5, index=s.index)  # fallback
    return (s - mn) / (mx - mn)

# ---------- MAIN ----------
def compute_scores(df):
    df = df.copy()

    # Safely parse numeric columns: remove commas and percent signs if present
    def to_numeric(col):
        return pd.to_numeric(df[col].astype(str).str.replace(',', '').str.replace('%',''), errors='coerce')

    # Extract / normalize columns
    for k, col in COLS.items():
            # 🚫 Skip non-numeric columns (like company Name)
        if k == "name":
            continue
        
        if col in df.columns:
            df[col + "_num"] = pd.to_numeric(
                df[col].astype(str).str.replace(',', '').str.replace('%',''),
                errors='coerce'
            )
            print ("Yes", col)
        else:
            df[col + "_num"] = np.nan
            print ("No",col)

    # Create features used
    roce = winsorize_series(df[COLS["roce"] + "_num"])
    fcf3 = winsorize_series(df[COLS["fcf_3y"] + "_num"])
    cfop3 = winsorize_series(df[COLS["cf_op_3y"] + "_num"])
    #sales_g3 = winsorize_series(df[COLS["sales_growth_3y"] + "_num"])
    #eps_g3 = winsorize_series(df[COLS["eps_growth_3y"] + "_num"])
    debt_eq = winsorize_series(df[COLS["debt_eq"] + "_num"])
    prom = winsorize_series(df[COLS["prom_hold"] + "_num"])
    opm = winsorize_series(df[COLS["opm"] + "_num"])
    wc_days = winsorize_series(df[COLS["wc_days"] + "_num"])
    cash_cycle = winsorize_series(df[COLS["cash_cycle"] + "_num"])
    pe = winsorize_series(df[COLS["pe"] + "_num"])
    ind_pe = winsorize_series(df[COLS["ind_pe"] + "_num"])
    marcap = winsorize_series(df[COLS["marcap"] + "_num"])

    # normalize each to 0-1
    roce_s = minmax_scale(roce)
    fcf3_s = minmax_scale(fcf3)
    cfop3_s = minmax_scale(cfop3)
    #sales_g3_s = minmax_scale(sales_g3)
    #eps_g3_s = minmax_scale(eps_g3)
    debt_eq_s = minmax_scale(debt_eq)            # lower better -> invert later
    prom_s = minmax_scale(prom)
    opm_s = minmax_scale(opm)
    wc_days_s = minmax_scale(wc_days)            # lower better -> invert later
    cash_cycle_s = minmax_scale(cash_cycle)      # lower better -> invert later
    marcap_s = minmax_scale(np.log1p(marcap.fillna(0)))  # use log(marketcap) to compress
    # valuation: compute pe/ind_pe ratio (lower = cheaper)
    pe_ind_ratio = pe / ind_pe.replace({0: np.nan})
    pe_ind_ratio = winsorize_series(pe_ind_ratio)
    pe_ind_s = minmax_scale(pe_ind_ratio)

    # For "lower is better" features invert: new = 1 - normalized
    debt_eq_inv = 1 - debt_eq_s.fillna(0.5)
    wc_eff_inv = 1 - ((wc_days_s.fillna(0.5) + cash_cycle_s.fillna(0.5)) / 2)

    # Compose final score
    df["sc_roce"] = roce_s
    df["sc_fcf3"] = fcf3_s
    #df["sc_salesg3"] = sales_g3_s
    #df["sc_epsg3"] = eps_g3_s
    df["sc_debteq"] = debt_eq_inv
    df["sc_valuation"] = 1 - pe_ind_s.fillna(0.5)     # invert ratio: lower ratio -> higher score
    df["sc_cfop3"] = cfop3_s
    df["sc_opm"] = opm_s
    df["sc_prom"] = prom_s
    df["sc_wceff"] = wc_eff_inv

    # Weighted sum
    df["investment_score"] = (
        WEIGHTS["roce"] * df["sc_roce"].fillna(0.5) +
        WEIGHTS["fcf_3y"] * df["sc_fcf3"].fillna(0.5) +
        #WEIGHTS["sales_growth_3y"] * df["sc_salesg3"].fillna(0.5) +
        #WEIGHTS["eps_growth_3y"] * df["sc_epsg3"].fillna(0.5) +
        WEIGHTS["debt_eq"] * df["sc_debteq"].fillna(0.5) +
        WEIGHTS["valuation"] * df["sc_valuation"].fillna(0.5) +
        WEIGHTS["cf_op_3y"] * df["sc_cfop3"].fillna(0.5) +
        WEIGHTS["opm"] * df["sc_opm"].fillna(0.5) +
        WEIGHTS["prom_hold"] * df["sc_prom"].fillna(0.5) +
        WEIGHTS["wc_efficiency"] * df["sc_wceff"].fillna(0.5)
    )

    # add rank
    df["rank"] = df["investment_score"].rank(method="min", ascending=False).astype(int)
# ✅ Sort by rank (ascending = best ranks first)
    df = df.sort_values(by="rank", ascending=True).reset_index(drop=True)

    return df

if __name__ == "__main__":
    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET)
    scored = compute_scores(df)
    # Select output columns
    out_cols = ["rank", COLS["name"], COLS["marcap"], COLS["pe"], COLS["roce"], COLS["fcf_3y"], COLS["debt_eq"], COLS["prom_hold"], "investment_score"]
    # keep only columns present
    out_cols = [c for c in out_cols if c in scored.columns or c in scored.columns]  # safe
    scored.to_csv(OUTPUT_FILE, index=False)
    print(f"Wrote ranked results to {OUTPUT_FILE}")

# %%
