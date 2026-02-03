import sqlite3
import pandas as pd
import statsmodels.api as sm

# --- CONFIGURATION ---
DB_NAME = 'garmin_data.db'

def run_analysis(data_subset, label):
    print(f"\n{'='*20} ANALYSIS FOR: {label} {'='*20}")
    
    # Check data sufficiency
    num_rows = len(data_subset)
    print(f"Number of rows considered: {num_rows}")
    if num_rows < 10:
        print("Not enough data to run reliable statistics.")
        return

    # Variables for analysis
    # Y = Pace (seconds/km)
    Y = data_subset['Pace_sec_km']
    
    # --- 1. Correlation Matrix ---
    print("\n--- Correlation Matrix ---")
    corr_matrix = data_subset[['Pace_sec_km', 'Heart_Rate', 'Cadence']].corr()
    print(corr_matrix)

    # --- 2. Linear Regression: Pace ~ Heart Rate ---
    X_hr = data_subset['Heart_Rate']
    X_hr_const = sm.add_constant(X_hr)
    
    try:
        model_hr = sm.OLS(Y, X_hr_const).fit()
        print(f"\n--- Linear Regression (Pace ~ Heart Rate) ---")
        print(f"Coefficient: {model_hr.params['Heart_Rate']:.4f}")
        print(f"P-value:     {model_hr.pvalues['Heart_Rate']:.4f}  (Significant if < 0.05)")
        conf = model_hr.conf_int().loc['Heart_Rate']
        print(f"95% Conf. Int: [{conf[0]:.4f}, {conf[1]:.4f}]")
    except Exception as e:
        print(f"Could not run HR regression: {e}")

    # --- 3. Linear Regression: Pace ~ Cadence ---
    X_cad = data_subset['Cadence']
    X_cad_const = sm.add_constant(X_cad)
    
    try:
        model_cad = sm.OLS(Y, X_cad_const).fit()
        print(f"\n--- Linear Regression (Pace ~ Cadence) ---")
        print(f"Coefficient: {model_cad.params['Cadence']:.4f}")
        print(f"P-value:     {model_cad.pvalues['Cadence']:.4f}  (Significant if < 0.05)")
        conf = model_cad.conf_int().loc['Cadence']
        print(f"95% Conf. Int: [{conf[0]:.4f}, {conf[1]:.4f}]")
    except Exception as e:
        print(f"Could not run Cadence regression: {e}")

    # --- 4. Multilinear Regression: Pace ~ HR + Cadence ---
    X_multi = data_subset[['Heart_Rate', 'Cadence']]
    X_multi = sm.add_constant(X_multi)
    
    try:
        model_multi = sm.OLS(Y, X_multi).fit()
        print(f"\n--- Multilinear Regression (Pace ~ HR + Cadence) ---")
        print(f"R-squared: {model_multi.rsquared:.4f}")
        
        # Create a nice summary table for the multilinear results
        print("\nVariable      Coef     P-value    [0.025   0.975]")
        print("-" * 50)
        for var in ['Heart_Rate', 'Cadence']:
            coef = model_multi.params[var]
            pval = model_multi.pvalues[var]
            conf = model_multi.conf_int().loc[var]
            print(f"{var:<12} {coef:>7.4f}  {pval:>7.4f}    [{conf[0]:.4f}, {conf[1]:.4f}]")
            
    except Exception as e:
        print(f"Could not run Multilinear regression: {e}")

# --- MAIN EXECUTION ---
try:
    conn = sqlite3.connect(DB_NAME)
    query = "SELECT * FROM running_data"
    df = pd.read_sql_query(query, conn)
    conn.close()

    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year

    run_analysis(df, "ALL DATA")

    years = [2021, 2022, 2023, 2024, 2025]
    for year in years:
        df_year = df[df['Year'] == year]
        run_analysis(df_year, f"YEAR {year}")

except Exception as e:
    print(f"An error occurred: {e}")