import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import numpy as np
from io import BytesIO

# Updated Colors
BG_COLOR = '#102F46'  # Dark blue for background
TITLE_BG_COLOR = '#DAA657'  # Golden color for title background
TITLE_TEXT_COLOR = 'white'
TEXT_COLOR = '#333333'

def clean_value(value):
    try:
        if isinstance(value, str):
            # Remove '$' and ',' from string and convert to float
            return float(value.replace('$', '').replace(',', ''))
        elif isinstance(value, (int, float)):
            return float(value)
        else:
            return 0.0
    except:
        return 0.0

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    processed_data = output.getvalue()
    return processed_data

@st.cache_data
def load_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.insider_transactions
        
        if df is not None and not df.empty:
            # Ensure we have the correct date column
            date_col = 'Start Date' if 'Start Date' in df.columns else 'Date'
            df['Date'] = pd.to_datetime(df[date_col])
            
            # Filter for dates from 2023-01-01 onwards
            date_filter = pd.to_datetime('2023-01-01')
            df = df[df['Date'] >= date_filter].copy()
            
            # Split into sales and purchases
            sales_df = df[df['Type'].str.contains('Sale', case=False, na=False)].copy()
            purchase_df = df[df['Type'].str.contains('Purchase|Buy', case=False, na=False)].copy()
            
            # Process sales dataframe
            if not sales_df.empty:
                sales_df['Value_Float'] = sales_df['Value'].apply(clean_value)
                sales_df['Value_Display'] = sales_df['Value']
                sales_df = sales_df.sort_values('Date', ascending=False)
                sales_df['Date'] = sales_df['Date'].dt.strftime('%Y-%m-%d')
                
                # Create aggregated sales
                sales_agg = sales_df.groupby('Insider')['Value_Float'].sum().reset_index()
                sales_agg = sales_agg.sort_values('Value_Float', ascending=False)
                sales_agg['Value'] = sales_agg['Value_Float'].apply(lambda x: f"${x:,.2f}")
            else:
                sales_agg = pd.DataFrame()
            
            # Process purchase dataframe
            if not purchase_df.empty:
                purchase_df['Value_Float'] = purchase_df['Value'].apply(clean_value)
                purchase_df['Value_Display'] = purchase_df['Value']
                purchase_df = purchase_df.sort_values('Date', ascending=False)
                purchase_df['Date'] = purchase_df['Date'].dt.strftime('%Y-%m-%d')
                
                # Create aggregated purchases
                purchase_agg = purchase_df.groupby('Insider')['Value_Float'].sum().reset_index()
                purchase_agg = purchase_agg.sort_values('Value_Float', ascending=False)
                purchase_agg['Value'] = purchase_agg['Value_Float'].apply(lambda x: f"${x:,.2f}")
            else:
                purchase_agg = pd.DataFrame()
            
            # Select and rename columns for display
            columns = ['Date', 'Insider', 'Value_Display', 'Value_Float']
            sales_df = sales_df[columns].rename(columns={'Value_Display': 'Value'})
            purchase_df = purchase_df[columns].rename(columns={'Value_Display': 'Value'})
            
            return sales_df, purchase_df, sales_agg, purchase_agg
            
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def display_table(title, df, download_text):
    st.markdown(f'<h2 style="color: white;">{title}</h2>', unsafe_allow_html=True)
    
    if df.empty:
        st.info(f"No data available for {title} from January 1st, 2023 onwards.")
    else:
        # Drop Value_Float column for display but keep it for sorting
        display_df = df.copy()
        if 'Value_Float' in display_df.columns:
            display_df = display_df.drop('Value_Float', axis=1)
        
        st.dataframe(
            display_df,
            height=400,
            use_container_width=True,
            column_config={
                "Value": st.column_config.TextColumn(
                    "Value",
                    help="Transaction value",
                    default="0",
                    max_chars=50
                )
            }
        )
        
        # Add download button
        excel_data = convert_df_to_excel(display_df)
        st.download_button(
            label=f"Download {download_text}",
            data=excel_data,
            file_name=f'{download_text.lower().replace(" ", "_")}.xlsx',
            mime='application/vnd.ms-excel'
        )

[Resto do código do main() é exatamente igual ao anterior]

if __name__ == "__main__":
    main()
