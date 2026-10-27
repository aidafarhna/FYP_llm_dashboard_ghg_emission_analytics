import pandas as pd
import streamlit as st

def load_and_process_data(filepath):
    """
    Reads the raw Excel data, standardizes the column names, 
    extracts the monthly tCO2e emissions, and filters for Scope 1 & 2.
    """
    sheets_to_read = ['2022', '2023']
    all_data = []
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for sheet in sheets_to_read:
        
        df_temp = pd.read_excel(filepath, sheet_name=sheet, header=2)
        
        # Grab tCO2e monthly columns (Index 21-32) and rename to standard months
        tco2e_month_cols = df_temp.columns[21:33]
        rename_dict = {old_col: new_col for old_col, new_col in zip(tco2e_month_cols, months)}
        df_temp.rename(columns=rename_dict, inplace=True)
        
        all_data.append(df_temp)
        
    df = pd.concat(all_data, ignore_index=True)
    df.columns = [str(col).replace('\n', ' ') for col in df.columns]
    
    # Filter strictly for Scope 1 and Scope 2
    df_filtered = df[df['Scope'].isin(['Scope 1', 'Scope 2'])].copy()
    df_filtered['Reference Year'] = pd.to_datetime(df_filtered['Reference Year']).dt.year
    
    return df_filtered

def save_to_main_sheet(df, filepath):
    """
    Saves the processed dataframe to a new sheet named 'main' 
    in the original Excel file.
    """
    with pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name='main', index=False)

# ---------------------------------------------------------
# Application Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    excel_file = "data 2022-2023.xlsx"
    
    # 1. Process the data
    raw_processed_df = load_and_process_data(excel_file)
    
    # Define exactly which columns we want to keep
    clean_columns = [
        'Source ID', 'Reference Year', 'Scope', 'Source Description', 
        'Activity Data', 'Activity Data Description', 'Units', 
        'Emission Factor', 'Total', 'Total Emission (Annual)',
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    
    # 2. Subset the dataframe to ONLY include our clean columns
    final_df = raw_processed_df[clean_columns]
    
    # 3. Save ONLY the clean, subsetted data to the 'main' sheet
    save_to_main_sheet(final_df, excel_file)
    
    # 4. Streamlit Display
    st.set_page_config(layout="wide")
    st.title("Scope 1 & Scope 2 GHG Data Processing")
    
    st.success("Clean data successfully centralized into the 'main' sheet!")
    st.write("Preview of the centralized 'main' dataset:")
    st.dataframe(final_df)