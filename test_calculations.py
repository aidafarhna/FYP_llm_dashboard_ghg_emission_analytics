import pandas as pd
import pytest

# Import the specific calculation functions directly from your dashboard code
from app import compute_kpis, to_number

def test_to_number_conversion():
    # Provide dirty data (strings, blanks, nulls)
    raw_data = pd.Series(["100", "", "50.5", None])
    
    # Run your cleaning function
    cleaned_result = to_number(raw_data)
    
    # The sum should perfectly equal 150.5, ignoring blanks and nulls
    assert cleaned_result.sum() == 150.5

def test_compute_kpis_math():
    # 1. Create a dummy dataframe for the current year
    df_current = pd.DataFrame({
        "Reference Year": [2024, 2024],
        "Source ID": ["Plant A", "Plant B"],
        "Scope": ["Scope 1", "Scope 2"],
        "Total Emission (Annual)": [1000, 500]
    })
    
    # 2. Create a dummy dataframe for the previous year to test YoY logic
    df_prev = pd.DataFrame({
        "Reference Year": [2023, 2023],
        "Source ID": ["Plant A", "Plant B"],
        "Scope": ["Scope 1", "Scope 2"],
        "Total Emission (Annual)": [900, 500]
    })
    
    # 3. Process the dummy data through your function
    kpis = compute_kpis(df_current, df_prev)
    
    # 4. Verify the exact expected outputs
    assert kpis["scope1"] == 1000
    assert kpis["scope2"] == 500
    assert kpis["combined"] == 1500
    assert kpis["prev_total"] == 1400
    
    # Verify Year-over-Year (YoY) percentage: (1500 - 1400) / 1400 * 100 = 7.1428%
    assert round(kpis["yoy"], 2) == 7.14