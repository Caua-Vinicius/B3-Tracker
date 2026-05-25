import streamlit as st
import plotly.express as px
import pandas as pd
from database import SessionLocal
from services import add_asset, delete_asset, get_portfolio_summary, fetch_asset_details

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

    /* Painel de Detalhe do Ativo */
    .detail-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #1A1D2E 0%, #252836 100%);
        border: 1px solid #2D313A;
        border-left: 4px solid #00D4AA;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    .detail-ticker {
        font-size: 1.5rem;
        font-weight: 800;
        color: #00D4AA;
        letter-spacing: 0.05em;
    }
    .detail-name {
        font-size: 1rem;
        color: #CBD5E0;
        flex: 1;
    }
    .detail-sector {
        font-size: 0.8rem;
        color: #A0AEC0;
        background: #2D313A;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
    }
    .metric-caption {
        font-size: 0.75rem;
        color: #718096;
        margin-top: -0.8rem;
        margin-bottom: 0.5rem;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

def render_asset_detail(ticker: str):
    """Renderiza o painel de análise fundamentalista de um ativo."""
    with st.spinner(f"Carregando análise de {ticker}..."):
        details = fetch_asset_details(ticker)

    info = details.get("info", {})
    history = details.get("history", pd.DataFrame())

    if not info:
        st.warning(f"Não foi possível carregar os dados de {ticker}. Tente novamente.")
        return

    # --- Helpers de formatação centralizados ---
    def fmt_brl(val):
        """Formata valor monetário em Real Brasileiro com separadores PT-BR."""
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return "—"
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def fmt_mktcap(val):
        """Formata Patrimônio de Mercado em bi/mi com separador PT-BR."""
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return "—"
        if val >= 1e9:
            return f"R$ {val / 1e9:.1f} bi".replace(".", ",")
        return f"R$ {val / 1e6:.0f} mi"

    def fmt_pct(val):
        """Formata variação percentual com sinal e separador PT-BR (entrada: decimal, ex: 0.03)."""
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        return f"{val * 100:+.2f}%".replace(".", ",")

    def fmt_dy(val):
        """
        Formata Dividend Yield com guard contra dupla multiplicação.
        O yfinance retorna `dividendYield` de forma inconsistente:
          - Às vezes em decimal puro: 0.1211  → precisa multiplicar por 100
          - Às vezes já em percentagem: 12.11  → NÃO deve multiplicar por 100
        Guard: se val > 1, já está em %, usamos direto.
        """
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return "—"
        dy_pct = val if val > 1 else val * 100
        return f"{dy_pct:.2f}% a.a.".replace(".", ",")

    # --- Cabeçalho do ativo ---
    name = info.get("longName") or ticker
    sector = info.get("sector") or info.get("industry") or "Não informado"
    st.markdown(
        f'<div class="detail-header">'
        f'<span class="detail-ticker">{ticker}</span>'
        f'<span class="detail-name">{name}</span>'
        f'<span class="detail-sector">🏷️ {sector}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    price   = info.get("currentPrice") or info.get("regularMarketPrice") or 0
    dy      = info.get("dividendYield")
    ptb     = info.get("priceToBook")
    mktcap  = info.get("marketCap")
    vol     = info.get("volume") or info.get("regularMarketVolume")
    avg_vol = info.get("averageVolume") or info.get("averageDailyVolume10Day")
    high52  = info.get("fiftyTwoWeekHigh")
    low52   = info.get("fiftyTwoWeekLow")
    chg52   = info.get("52WeekChange")

    # --- Linha 1: métricas de valor ---
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("💰 Preço Atual", fmt_brl(price) if price else "—")
        st.markdown('<p class="metric-caption">Última cotação negociada no mercado.</p>', unsafe_allow_html=True)

    with c2:
        st.metric("📊 DY 12 meses", fmt_dy(dy))
        st.markdown('<p class="metric-caption">% do preço pago em dividendos nos últimos 12 meses. Quanto maior, mais renda passiva o ativo distribui.</p>', unsafe_allow_html=True)

    with c3:
        st.metric("📐 P/VP", f"{ptb:.2f}".replace(".", ",") if ptb else "—")
        if ptb:
            _TOLERANCE = 0.005  # ±0,5% — trata P/VP ≈ 1 como valor justo
            if ptb < (1 - _TOLERANCE):
                caption = f"Comprando {(1 - ptb) * 100:.0f}% abaixo do patrimônio. P/VP &lt; 1 indica desconto real."
            elif ptb > (1 + _TOLERANCE):
                caption = f"Comprando {(ptb - 1) * 100:.0f}% acima do patrimônio. Avalie se o prêmio é justificado."
            else:
                caption = "Negociado ao valor patrimonial justo (P/VP ≈ 1)."
        else:
            caption = "Preço ÷ Valor Patrimonial por cota. Referência de desconto/prêmio do fundo."
        st.markdown(f'<p class="metric-caption">{caption}</p>', unsafe_allow_html=True)

    with c4:
        st.metric("🏦 Patrimônio de Mercado", fmt_mktcap(mktcap))
        st.markdown('<p class="metric-caption">Total de cotas × preço atual. Fundos maiores tendem a ter mais liquidez e diversificação interna.</p>', unsafe_allow_html=True)

    st.markdown("<div style='margin:0.5rem 0'></div>", unsafe_allow_html=True)

    # --- Linha 2: métricas de liquidez e range ---
    c5, c6, c7, c8 = st.columns(4)

    with c5:
        vol_str = f"{vol:,.0f}".replace(",", ".") if vol else "—"
        st.metric("📦 Volume do Dia", vol_str)
        st.markdown('<p class="metric-caption">Cotas negociadas hoje. Volume alto = mais fácil executar ordens sem deslocar o preço.</p>', unsafe_allow_html=True)

    with c6:
        avg_str = f"{avg_vol:,.0f}".replace(",", ".") if avg_vol else "—"
        st.metric("📉 Volume Médio (3m)", avg_str)
        st.markdown('<p class="metric-caption">Média diária dos últimos 3 meses. Indica a liquidez histórica — importante para comparar com o volume de hoje.</p>', unsafe_allow_html=True)

    with c7:
        st.metric("📈 Máx 52 Semanas", fmt_brl(high52) if high52 else "—")
        low_str = fmt_brl(low52) if low52 else "—"
        st.markdown(f'<p class="metric-caption">Maior preço negociado nos últimos 12 meses. Mínima do período foi {low_str}.</p>', unsafe_allow_html=True)

    with c8:
        chg_str = fmt_pct(chg52) or "—"
        st.metric("🔄 Variação 12 meses", chg_str, delta=fmt_pct(chg52))
        st.markdown('<p class="metric-caption">Variação de preço no último ano, sem contar dividendos. Combine com o DY para ter a rentabilidade total.</p>', unsafe_allow_html=True)

    # --- Barra visual de posição no range 52 semanas ---
    if high52 and low52 and price and high52 != low52:
        position = min(max((price - low52) / (high52 - low52), 0.0), 1.0)
        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns([1.8, 6, 1.8])
        with r1:
            st.caption(f"🔻 Mín {fmt_brl(low52)}")
        with r2:
            st.caption("**Posição no range de 52 semanas**")
            st.progress(position)
        with r3:
            st.caption(f"🔺 Máx {fmt_brl(high52)}")

    # --- Gráfico histórico de preços ---
    if not history.empty:
        st.markdown("---")
        st.markdown("##### 📈 Histórico de Preços — Últimos 6 Meses")
        hist_df = history.reset_index()[["Date", "Close"]].dropna()
        fig = px.area(
            hist_df,
            x="Date",
            y="Close",
            labels={"Date": "Data", "Close": "Preço (R$)"},
        )
        fig.update_traces(
            line=dict(color="#00D4AA", width=2),
            fillcolor="rgba(0, 212, 170, 0.10)",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#E2E8F0",
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(showgrid=True, gridcolor="#2D313A", title="Preço (R$)"),
            margin=dict(t=10, b=10, l=0, r=0),
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)


def main():
    
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
                with SessionLocal() as db:
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
                with SessionLocal() as db:
                    delete_asset(db, del_ticker)
                st.sidebar.success(f"{del_ticker} removido!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Erro: {e}")

    # --- Área Principal ---
    with SessionLocal() as db:
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
        hide_index=True,
    )

    # 4. Painel de Análise Detalhada
    st.markdown("---")
    st.markdown("### 🔍 Análise Detalhada por Ativo")
    st.caption("Selecione um ativo abaixo para ver seus indicadores fundamentalistas com explicações.")

    ticker_options = df_portfolio["Ticker"].tolist()
    selected = st.selectbox(
        "Ativo:",
        options=ticker_options,
        index=0,
        key="detail_selectbox",
        label_visibility="collapsed",
    )

    if selected:
        render_asset_detail(selected)

if __name__ == "__main__":
    main()
