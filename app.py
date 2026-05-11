import streamlit as st
import plotly.express as px
from database import SessionLocal
from services import add_asset, delete_asset, get_portfolio_summary

# Configuração da Página - Must be first
st.set_page_config(
    page_title="B3 Tracker Premium",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Customizada (Premium UI)
st.markdown("""
<style>
    /* Fundo Escuro Moderno */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Estilo dos Cards de Métricas */
    div[data-testid="metric-container"] {
        background-color: #1E212B;
        border: 1px solid #2D313A;
        padding: 5% 5% 5% 10%;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.5);
    }
    
    /* Textos dos Cards */
    div[data-testid="metric-container"] label {
        color: #A0AEC0 !important;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Espaçamento do container principal */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Tipografia Clean */
    h1, h2, h3 {
        color: #E2E8F0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Tabela Premium */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #2D313A;
    }
</style>
""", unsafe_allow_html=True)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def main():
    db = get_db()
    
    # Cabeçalho
    st.title("💎 B3 Tracker Premium Dashboard")
    st.markdown("Acompanhamento em tempo real do seu portfólio de Renda Variável com dados do Yahoo Finance.")
    
    # --- Sidebar: Gerenciamento ---
    st.sidebar.title("Configurações")
    st.sidebar.markdown("---")
    
    st.sidebar.header("➕ Cadastrar Ativo")
    with st.sidebar.form("add_asset_form"):
        new_ticker = st.text_input("Ticker (Ex: PETR4, MXRF11)")
        new_quantity = st.number_input("Quantidade", min_value=0.01, step=1.0)
        submit_button = st.form_submit_button("Adicionar à Carteira", use_container_width=True)
        
        if submit_button and new_ticker:
            try:
                asset = add_asset(db, new_ticker, new_quantity)
                st.sidebar.success(f"{asset.ticker} adicionado com sucesso!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Erro: {e}")

    st.sidebar.markdown("---")
    st.sidebar.header("➖ Remover Ativo")
    with st.sidebar.form("remove_asset_form"):
        del_ticker = st.text_input("Ticker para remover (Ex: PETR4 ou PETR4.SA)")
        del_button = st.form_submit_button("Remover da Carteira", use_container_width=True)
        
        if del_button and del_ticker:
            try:
                delete_asset(db, del_ticker)
                st.sidebar.success(f"{del_ticker} removido!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Erro: {e}")

    # --- Área Principal ---
    df_portfolio, total_patrimony = get_portfolio_summary(db)
    
    if df_portfolio.empty:
        st.info("👋 Bem-vindo! Comece adicionando seus ativos na barra lateral para visualizar seu Dashboard.")
        return

    # 1. Row de Métricas (Premium UI)
    st.markdown("### 📊 Visão Geral")
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("Patrimônio Total", f"R$ {total_patrimony:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    
    with cols[1]:
        st.metric("Ativos na Carteira", len(df_portfolio))
        
    top_asset = df_portfolio.loc[df_portfolio['Valor Total (R$)'].idxmax()]
    with cols[2]:
        st.metric("Maior Posição", top_asset['Ticker'])
        
    with cols[3]:
        st.metric("Valor Maior Posição", f"R$ {top_asset['Valor Total (R$)']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.markdown("---")

    # 2. Row de Gráficos (Plotly)
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Gráfico de Rosca (Donut Chart) - Distribuição
        fig_donut = px.pie(
            df_portfolio, 
            values='Valor Total (R$)', 
            names='Ticker', 
            hole=0.65,
            title="Distribuição do Patrimônio",
            color_discrete_sequence=px.colors.sequential.Tealgrn_r
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#E2E8F0',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=50, b=0, l=0, r=0)
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent+value')
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_chart2:
        # Gráfico de Barras - Valor por Ativo
        df_sorted = df_portfolio.sort_values(by="Valor Total (R$)", ascending=True)
        fig_bar = px.bar(
            df_sorted, 
            x='Valor Total (R$)', 
            y='Ticker', 
            orientation='h',
            title="Valor Investido por Ativo",
            text='Valor Total (R$)',
            color='Valor Total (R$)',
            color_continuous_scale='Tealgrn'
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#E2E8F0',
            xaxis_title="Valor (R$)",
            yaxis_title="",
            coloraxis_showscale=False,
            margin=dict(t=50, b=0, l=0, r=0)
        )
        # Formatação do texto nas barras para Real Brasileiro
        fig_bar.update_traces(texttemplate='R$ %{text:,.2f}', textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)

    # 3. Tabela de Detalhamento
    st.markdown("### 📋 Detalhamento da Carteira")
    
    # Formatação elegante para o dataframe exibido
    df_display = df_portfolio.copy()
    df_display['Preço Atual (R$)'] = df_display['Preço Atual (R$)'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_display['Valor Total (R$)'] = df_display['Valor Total (R$)'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_display['Quantidade'] = df_display['Quantidade'].apply(lambda x: f"{x:g}") # Remove zeros desnecessários (ex: 100.0 vira 100)
    
    st.dataframe(
        df_display, 
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    main()
