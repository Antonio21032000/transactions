import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from io import BytesIO

# Updated Colors
BG_COLOR = '#102F46'  # Dark blue for background
TITLE_BG_COLOR = '#DAA657'  # Golden color for title background
TITLE_TEXT_COLOR = 'white'
TEXT_COLOR = '#333333'

def clean_value(value):
    if isinstance(value, str):
        return float(value.replace('$', '').replace(',', ''))
    return float(value) if pd.notnull(value) else 0.0

def format_currency(value):
    return f"${value:,.2f}" if pd.notnull(value) else "N/A"

@st.cache_data
def load_data(ticker):
    try:
        empresa = yf.Ticker(ticker)
        df = empresa.insider_transactions
        
        if df is not None and not df.empty:
            # Convert Start Date to datetime and ensure it's working with the right column
            if 'Start Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Start Date'])
            elif 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
            else:
                st.error("Date column not found in the data")
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
            # Filter for dates from 2019-01-01 onwards
            date_filter = pd.to_datetime('2019-01-01')
            df_filtered = df[df['Date'] >= date_filter].copy()
            
            if 'Text' in df_filtered.columns:
                df_venda = df_filtered[df_filtered['Text'].str.contains('Sale', na=False, case=False)].copy()
                df_compra = df_filtered[df_filtered['Text'].str.contains('Purchase|Buy', na=False, case=False)].copy()
            elif 'Type' in df_filtered.columns:
                df_venda = df_filtered[df_filtered['Type'].str.contains('Sale', na=False, case=False)].copy()
                df_compra = df_filtered[df_filtered['Type'].str.contains('Purchase|Buy', na=False, case=False)].copy()
            
            # Sort by date descending
            df_venda = df_venda.sort_values('Date', ascending=False).reset_index(drop=True)
            df_compra = df_compra.sort_values('Date', ascending=False).reset_index(drop=True)
            
            # Clean and format value column
            for df in [df_venda, df_compra]:
                if 'Value' in df.columns:
                    df['Value'] = df['Value'].apply(clean_value)
            
            # Create aggregated views
            df_agrupado_venda = df_venda.groupby("Insider")['Value'].sum().sort_values(ascending=False).reset_index()
            df_agrupado_compra = df_compra.groupby("Insider")['Value'].sum().sort_values(ascending=False).reset_index()
            
            # Format values for display
            for df in [df_venda, df_compra, df_agrupado_venda, df_agrupado_compra]:
                if 'Value' in df.columns:
                    df['Value'] = df['Value'].apply(format_currency)
            
            # Format dates for display
            if not df_venda.empty:
                df_venda['Date'] = df_venda['Date'].dt.strftime('%Y-%m-%d')
            if not df_compra.empty:
                df_compra['Date'] = df_compra['Date'].dt.strftime('%Y-%m-%d')
            
            return df_venda, df_compra, df_agrupado_venda, df_agrupado_compra
        else:
            st.warning(f"No insider transaction data found for ticker {ticker}.")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def display_table(title, df):
    st.markdown(f'<h2 style="color: white;">{title}</h2>', unsafe_allow_html=True)
    if df.empty:
        st.info(f"No data available for {title} from 2019-01-01 onwards.")
    else:
        st.dataframe(df, height=400, use_container_width=True)

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
        .stButton>button:hover {{
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
    st.markdown('<p style="color: white; text-align: center;">Showing transactions from January 1st, 2019 onwards</p>', unsafe_allow_html=True)

    # Input and button in the left side
    ticker = st.text_input("Enter stock ticker (e.g., NVDA, AAPL, GOOGL)", "")
    
    if st.button("Analyze"):
        if ticker:
            with st.spinner('Loading data...'):
                df_venda, df_compra, df_agrupado_venda, df_agrupado_compra = load_data(ticker.upper())

            display_table("Sales Transactions", df_venda)
            display_table("Purchase Transactions", df_compra)
            display_table("Aggregated Sales by Insider", df_agrupado_venda)
            display_table("Aggregated Purchases by Insider", df_agrupado_compra)
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
