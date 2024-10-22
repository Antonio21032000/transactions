import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import numpy as np
from io import BytesIO

# Updated Colors
BG_COLOR = '#102F46'
TITLE_BG_COLOR = '#DAA657'
TITLE_TEXT_COLOR = 'white'
TEXT_COLOR = '#333333'

def clean_value(value):
    try:
        if isinstance(value, str):
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
            use_container_width=True
        )
        
        # Add download button
        excel_data = convert_df_to_excel(display_df)
        st.download_button(
            label=f"Download {download_text}",
            data=excel_data,
            file_name=f'{download_text.lower().replace(" ", "_")}.xlsx',
            mime='application/vnd.ms-excel'
        )

def main():
    st.set_page_config(page_title="US Insider Analysis", layout="wide")
    
    # Apply custom CSS styles
    st.markdown(f"""
        <style>
        .reportview-container .main .block-container{{
            max-width: 1200px;
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }}
        .stApp {{
            background-color: {BG_COLOR};
        }}
        .stButton>button {{
            color: white;
            background-color: {TITLE_BG_COLOR};
            border-radius: 5px;
            font-weight: bold;
            border: none;
            padding: 0.75rem 2rem;
            transition: background-color 0.3s;
            width: 200px;
            margin-top: 5px;
        }}
        .stDownloadButton>button {{
            color: white;
            background-color: {TITLE_BG_COLOR};
            border-radius: 5px;
            font-weight: bold;
            border: none;
            padding: 0.5rem 1rem;
            transition: background-color 0.3s;
            margin-top: 10px;
        }}
        .stButton>button:hover, .stDownloadButton>button:hover {{
            background-color: #b8952d;
        }}
        .title-container {{
            background-color: {TITLE_BG_COLOR};
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }}
        .title-container h1 {{
            color: {TITLE_TEXT_COLOR};
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin: 0;
        }}
        .stTextInput>div>div>input {{
            color: {TEXT_COLOR};
            background-color: white;
            border-radius: 5px;
            font-size: 16px;
            padding: 0.75rem;
            width: 300px;
        }}
        .stTextInput>label {{
            color: white !important;
            font-size: 16px !important;
        }}
        .stDataFrame {{
            background-color: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .stDataFrame table {{
            color: {TEXT_COLOR} !important;
        }}
        .stDataFrame th {{
            background-color: {TITLE_BG_COLOR} !important;
            color: {TITLE_TEXT_COLOR} !important;
            padding: 0.5rem !important;
        }}
        .stDataFrame td {{
            background-color: white !important;
            padding: 0.5rem !important;
        }}
        .stDataFrame tr:nth-of-type(even) {{
            background-color: #f8f8f8 !important;
        }}
        h1, h2, h3, h4, h5, h6, .stMarkdown {{
            color: white !important;
        }}
        p {{
            color: white !important;
        }}
        .stAlert {{
            background-color: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
        }}
        div[data-testid="stToolbar"] {{
            display: none;
        }}
        </style>
    """, unsafe_allow_html=True)

    # Title with new styling
    st.markdown('<div class="title-container"><h1>US Insider Analysis</h1></div>', unsafe_allow_html=True)

    # Add date filter information
    st.markdown('<p style="color: white; text-align: center;">Showing transactions from January 1st, 2023 onwards</p>', unsafe_allow_html=True)

    # Input and button in the left side
    ticker = st.text_input("Enter stock ticker (e.g., NVDA, AAPL, GOOGL)", "")
    
    if st.button("Analyze"):
        if ticker:
            with st.spinner('Loading data...'):
                df_venda, df_compra, df_agrupado_venda, df_agrupado_compra = load_data(ticker.upper())

            display_table("Sales Transactions", df_venda, "Sales Data")
            display_table("Purchase Transactions", df_compra, "Purchase Data")
            display_table("Aggregated Sales by Insider", df_agrupado_venda, "Aggregated Sales Data")
            display_table("Aggregated Purchases by Insider", df_agrupado_compra, "Aggregated Purchase Data")
        else:
            st.warning("Please enter a ticker symbol")

    # Footer with just the regulatory note
    st.markdown("""
        <div style="position: fixed; bottom: 0; width: 100%; background-color: rgba(16, 47, 70, 0.9); padding: 10px; text-align: center; font-size: 12px; color: #999999;">
        For more detailed information or verification of specific data, please consult official company reports or regulatory sources.
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
