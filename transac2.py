import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from PIL import Image

CORES_STK = {
    'azul_escuro': '#102E46',
    'dourado': '#C9BC2E',
    'azul_claro': '#1090B2',
    'preto': '#0B1B24',
    'branco': '#FFFFFF'
}

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
            # Remover as colunas especificadas
            columns_to_remove = ["URL", "Transaction", "Ownership"]
            df = df.drop(columns=[col for col in columns_to_remove if col in df.columns])
            
            df['Value'] = df['Value'].apply(clean_value)
            
            df_venda = df[df["Text"].str.contains("Sale", na=False, case=False)].reset_index(drop=True)
            df_compra = df[df["Text"].str.contains("Purchase", na=False, case=False)].reset_index(drop=True)
            
            df_agrupado_venda = df_venda.groupby("Insider")["Value"].sum().sort_values(ascending=False).reset_index()
            df_agrupado_compra = df_compra.groupby("Insider")["Value"].sum().sort_values(ascending=False).reset_index()
            
            # Formatação de moeda após a agregação
            for df in [df_venda, df_compra, df_agrupado_venda, df_agrupado_compra]:
                df['Value'] = df['Value'].apply(format_currency)
            
            return df_venda, df_compra, df_agrupado_venda, df_agrupado_compra
        else:
            st.warning(f"Não foram encontrados dados de transações de insiders para o ticker {ticker}.")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def display_table(title, df):
    st.subheader(title)
    if df.empty:
        st.info(f"Não há dados disponíveis para {title}.")
    else:
        st.dataframe(
            df.style
            .set_properties(**{
                'color': CORES_STK['branco'],
                'background-color': CORES_STK['azul_escuro'],
                'font-size': '16px',
                'border': f'1px solid {CORES_STK["azul_claro"]}'
            })
            .set_table_styles([
                {'selector': 'th', 'props': [
                    ('color', CORES_STK['branco']),
                    ('background-color', CORES_STK['azul_claro']),
                    ('font-size', '18px'),
                    ('font-weight', 'bold'),
                    ('text-align', 'left')
                ]},
                {'selector': 'td', 'props': [
                    ('text-align', 'left')
                ]},
            ]),
            height=400,
            use_container_width=True
        )
    st.markdown(f"""
    <div style="font-size: 14px; color: {CORES_STK['branco']};">
    Fonte: Yahoo Finance (yfinance)
    <br>
    Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
    </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Análise de Transações de Insiders", layout="wide")
    
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {CORES_STK['azul_escuro']};
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: {CORES_STK['azul_claro']};
            color: {CORES_STK['branco']};
        }}
        h1, h2, h3 {{
            color: {CORES_STK['branco']};
        }}
        .stTextInput > div > div > input {{
            color: {CORES_STK['azul_escuro']};
            font-size: 20px;
        }}
        p {{
            color: {CORES_STK['branco']};
            font-size: 18px;
        }}
    </style>
    """, unsafe_allow_html=True)

    st.title("Insiders (Buy and Sell) Analysis")

    ticker = st.text_input("Digite o ticker da ação (ex: NVDA, AAPL, GOOGL)", "ECL")

    if st.button("Analisar"):
        with st.spinner('Carregando dados...'):
            df_venda, df_compra, df_agrupado_venda, df_agrupado_compra = load_data(ticker)

        display_table("Vendas", df_venda)
        display_table("Compras", df_compra)
        display_table("Agrupado por Venda", df_agrupado_venda)
        display_table("Agrupado por Compra", df_agrupado_compra)

    st.markdown(f"""
    <div style="font-size: 16px; color: {CORES_STK['branco']}; margin-top: 50px;">
    <strong>Sobre os dados:</strong>
    <br>
    Todos os dados apresentados nesta aplicação são obtidos através da API do Yahoo Finance (yfinance).
    <br>
    O Yahoo Finance coleta estas informações de várias fontes, incluindo relatórios da SEC (para empresas dos EUA) e outras fontes oficiais.
    <br>
    A precisão e atualidade dos dados dependem da fonte original e do processo de coleta do Yahoo Finance.
    <br>
    Para informações mais detalhadas ou verificação de dados específicos, recomenda-se consultar os relatórios oficiais da empresa ou fontes regulatórias.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()












