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
            columns_to_remove = ["URL", "Transaction", "Ownership"]
            df = df.drop(columns=[col for col in columns_to_remove if col in df.columns])
            
            df['Value'] = df['Value'].apply(clean_value)
            
            df_venda = df[df["Text"].str.contains("Sale", na=False, case=False)].reset_index(drop=True)
            df_compra = df[df["Text"].str.contains("Purchase", na=False, case=False)].reset_index(drop=True)
            
            df_agrupado_venda = df_venda.groupby("Insider")["Value"].sum().sort_values(ascending=False).reset_index()
            df_agrupado_compra = df_compra.groupby("Insider")["Value"].sum().sort_values(ascending=False).reset_index()
            
            for df in [df_venda, df_compra, df_agrupado_venda, df_agrupado_compra]:
                df['Value'] = df['Value'].apply(format_currency)
            
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
        st.info(f"No data available for {title}.")
    else:
        st.dataframe(df, height=400, use_container_width=True)
    
    st.markdown(f"""
    <div style="font-size: 14px; color: white;">
    Source: Yahoo Finance (yfinance)
    <br>
    Last update: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

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
            color: {TITLE_BG_COLOR};
            background-color: white;
            border-radius: 5px;
            font-weight: bold;
            border: none;
            padding: 0.5rem 1rem;
            transition: background-color 0.3s;
        }}
        .stButton>button:hover {{
            background-color: #f0f0f0;
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
        </style>
        """, unsafe_allow_html=True)

    # Title with new styling
    st.markdown('<div class="title-container"><h1>US Insider Analysis</h1></div>', unsafe_allow_html=True)

    # Input section with improved styling
    ticker = st.text_input("Enter stock ticker (e.g., NVDA, AAPL, GOOGL)", "AAPL")

    if st.button("Analyze"):
        with st.spinner('Loading data...'):
            df_venda, df_compra, df_agrupado_venda, df_agrupado_compra = load_data(ticker)

        display_table("Sales Transactions", df_venda)
        display_table("Purchase Transactions", df_compra)
        display_table("Aggregated Sales by Insider", df_agrupado_venda)
        display_table("Aggregated Purchases by Insider", df_agrupado_compra)

    # Footer information with new styling
    st.markdown(f"""
    <div style="font-size: 16px; color: white; margin-top: 50px; background-color: rgba(16, 47, 70, 0.6); padding: 20px; border-radius: 10px;">
    <strong>About the Data:</strong>
    <br>
    All data presented in this application is obtained through the Yahoo Finance API (yfinance).
    <br>
    Yahoo Finance collects this information from various sources, including SEC reports (for US companies) and other official sources.
    <br>
    The accuracy and timeliness of the data depend on the original source and Yahoo Finance's collection process.
    <br>
    For more detailed information or verification of specific data, please consult official company reports or regulatory sources.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()








