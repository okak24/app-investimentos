#import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Portefólio Premium", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

# 1. SISTEMA DE AUTENTICAÇÃO SEGURO (Lê do cofre do Streamlit)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔒 Acesso ao Portefólio")
    st.write("Por favor, insira os seus dados para entrar na sua conta.")
    
    with st.form("login_form"):
        user_input = st.text_input("Utilizador").lower()
        pwd_input = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button("Entrar")
        
        if submit_button:
            # Vai buscar as senhas ao cofre configurado no site do Streamlit
            senhas_seguras = st.secrets["senhas"]
            
            if user_input in senhas_seguras and senhas_seguras[user_input] == pwd_input:
                st.session_state.logged_in = True
                st.session_state.username = user_input
                st.rerun()
            else:
                st.error("Utilizador ou senha incorretos.")
    st.stop() # Bloqueia o resto do código até a pessoa fazer login

# 2. BOTÃO DE SAÍDA E ESTILIZAÇÃO
col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title(f"💼 Portefólio Global - Olá, {st.session_state.username.capitalize()}!")
with col_logout:
    if st.button("Sair (Logout)"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetricValue"] { font-size: 26px; font-weight: bold; color: #0f172a; }
    div[data-testid="stMetricLabel"] { font-size: 13px; color: #64748b; font-weight: 500; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #0284c7; color: white; font-weight: bold; }
    .stButton>button:hover { background-color: #0369a1; color: white; }
    </style>
""", unsafe_allow_html=True)

# 3. BASE DE DADOS DE ATIVOS (Expandida)
ativos_dict = {
    "Depósito / Levantamento": [
        "Caixa / Saldo Disponível na Corretora"
    ],
    "Ações Americanas (Top 15)": [
        "Apple (AAPL)", "Microsoft (MSFT)", "NVIDIA (NVDA)", "Amazon (AMZN)", "Alphabet (GOOGL)", 
        "Meta (META)", "Tesla (TSLA)", "Berkshire Hathaway (BRK.B)", "Eli Lilly (LLY)", "Broadcom (AVGO)", 
        "JPMorgan Chase (JPM)", "UnitedHealth (UNH)", "Visa (V)", "ExxonMobil (XOM)", "Johnson & Johnson (JNJ)"
    ],
    "Ações Europeias (Principais)": [
        "ASML Holding (ASML)", "Novo Nordisk (NOVO B)", "LVMH (MC)", "SAP (SAP)", "Roche (ROG)", 
        "Shell (SHEL)", "L'Oréal (OR)", "AstraZeneca (AZN)", "Novartis (NVS)", "TotalEnergies (TTE)"
    ],
    "Ações Globais, IA e Semicondutores (Top 25)": [
        "TSMC (TSM)", "AMD (AMD)", "Intel (INTC)", "Qualcomm (QCOM)", "Texas Instruments (TXN)", 
        "Micron Technology (MU)", "ARM Holdings (ARM)", "Applied Materials (AMAT)", "Lam Research (LRCX)", 
        "Palantir (PLTR)", "Salesforce (CRM)", "Adobe (ADBE)", "Netflix (NFLX)", "Tencent (TCEHY)", 
        "Alibaba (BABA)", "Samsung (SMSN)", "Sony (SONY)", "ASML (ASML)", "NXP Semiconductors (NXPI)", 
        "Infineon (IFX)", "STMicroelectronics (STM)", "CrowdStrike (CRWD)", "Palo Alto (PANW)", "Snowflake (SNOW)", "Datadog (DDOG)"
    ],
    "ETFs Americanos (Top 20)": [
        "SPDR S&P 500 (SPY)", "iShares Core S&P 500 (IVV)", "Vanguard S&P 500 (VOO)", "Invesco QQQ (QQQ)", 
        "Vanguard Total Stock Market (VTI)", "Vanguard Growth (VUG)", "iShares Russell 2000 (IWM)", 
        "Vanguard Value (VTV)", "Vanguard FTSE Developed Markets (VEA)", "iShares Core MSCI EAFE (IEFA)", 
        "Vanguard Total Bond Market (BND)", "iShares Core US Aggregate Bond (AGG)", "SPDR Gold Shares (GLD)", 
        "Vanguard Dividend Appreciation (VIG)", "Vanguard Real Estate (VNQ)", "Vanguard High Dividend Yield (VYM)", 
        "iShares Core S&P Total U.S. Stock Market (ITOT)", "Financial Select Sector SPDR (XLF)", 
        "Health Care Select Sector SPDR (XLV)", "Technology Select Sector SPDR (XLK)"
    ],
    "ETFs Europeus / UCITS (Top 20)": [
        "Vanguard FTSE All-World (VWCE)", "iShares Core MSCI World (IWDA)", "Vanguard S&P 500 (VUAA)", 
        "iShares Core S&P 500 (SXR8)", "iShares NASDAQ 100 (SXRV)", "iShares S&P 500 Info Tech (QDVE)", 
        "Vanguard FTSE North America (VNRT)", "iShares Core MSCI EM IMI (EIMI)", "iShares MSCI ACWI (IS3N)", 
        "Amundi MSCI World (CW8)", "Xtrackers Euro Stoxx 50 (XD5E)", "iShares Core FTSE 100 (ISF)", 
        "iShares Global Clean Energy (INRG)", "Vanguard FTSE Emerging Markets (VFEM)", "iShares Physical Gold (IGLN)", 
        "Vanguard All-World High Dividend (VHYL)", "iShares STOXX Europe 600 (EXSA)", "SPDR S&P US Dividend Aristocrats (UDVD)", 
        "Xtrackers MSCI World (XDWD)", "Amundi S&P 500 (PE500)"
    ],
    "Criptomoedas (Top 20)": [
        "Bitcoin (BTC)", "Ethereum (ETH)", "Tether (USDT)", "BNB (BNB)", "Solana (SOL)", 
        "USDC (USDC)", "XRP (XRP)", "Dogecoin (DOGE)", "Toncoin (TON)", "Cardano (ADA)", 
        "Shiba Inu (SHIB)", "Avalanche (AVAX)", "Polkadot (DOT)", "Bitcoin Cash (BCH)", 
        "Chainlink (LINK)", "Tron (TRX)", "Polygon (MATIC / POL)", "NEAR Protocol (NEAR)", 
        "Litecoin (LTC)", "Uniswap (UNI)"
    ]
}

# 4. INICIALIZAÇÃO DO HISTÓRICO GERAL (Com coluna de Utilizador)
if 'operacoes' not in st.session_state:
    st.session_state.operacoes = pd.DataFrame(columns=[
        "Utilizador", "Data", "Categoria", "Ativo", "Tipo", "Moeda", "Preço", "Comissões", "Valor Movimentado", "Quantidade"
    ])

# 5. MENU LATERAL (Formulário)
with st.sidebar:
    st.header("➕ Nova Operação")
    
    data_op = st.date_input("Data do Negócio", date.today())
    categoria = st.selectbox("Categoria", list(ativos_dict.keys()))
    ativo = st.selectbox("Ativo", ativos_dict[categoria])
    
    if categoria == "Depósito / Levantamento":
        tipo = st.radio("Natureza", ["Depósito", "Levantamento"], horizontal=True)
        preco = 1.0  # Para depósitos o preço não importa
        qtd = 0.0
    else:
        tipo = st.radio("Natureza", ["Compra", "Venda", "Dividendo"], horizontal=True)
        preco = st.number_input("Preço Unitário", min_value=0.0, step=0.01, format="%.2f")
    
    moeda = st.radio("Moeda", ["EUR (€)", "USD ($)"], horizontal=True)
    valor = st.number_input("Valor Bruto (S/ Taxas)", min_value=0.0, step=10.0, format="%.2f")
    comissao = st.number_input("Comissões / Taxas", min_value=0.0, step=0.5, format="%.2f")
    
    if st.button("🚀 Confirmar Movimento"):
        if valor > 0 or tipo == "Dividendo":
            # Calcular quantidade: Vendas e Levantamentos reduzem saldo
            if tipo in ["Compra", "Venda"]:
                qtd = (valor / preco) if tipo == "Compra" else -(valor / preco)
            elif tipo == "Dividendo":
                qtd = 0.0 # Dividendos não afetam a quantidade de ações, só dão dinheiro
            
            nova_linha = pd.DataFrame([{
                "Utilizador": st.session_state.username, "Data": data_op, "Categoria": categoria, 
                "Ativo": ativo, "Tipo": tipo, "Moeda": moeda, "Preço": preco, 
                "Comissões": comissao, "Valor Movimentado": valor, "Quantidade": qtd
            }])
            
            st.session_state.operacoes = pd.concat([st.session_state.operacoes, nova_linha], ignore_index=True)
            st.success("Movimento registado com sucesso!")
        else:
            st.error("Insira um valor maior que zero.")

# 6. DADOS DO UTILIZADOR ATUAL
df_total = st.session_state.operacoes
df_user = df_total[df_total['Utilizador'] == st.session_state.username]

# 7. PAINEL DE MÉTRICAS (Filtrado por Utilizador)
st.subheader(f"📊 Resumo Financeiro")
col_eur, col_usd = st.columns(2)

with col_eur:
    st.markdown("<h4 style='color: #0284c7;'>🇪🇺 Conta Euros (€)</h4>", unsafe_allow_html=True)
    compras_eur = df_user[(df_user['Moeda'] == "EUR (€)") & (df_user['Tipo'] == "Compra")]['Valor Movimentado'].sum()
    vendas_eur = df_user[(df_user['Moeda'] == "EUR (€)") & (df_user['Tipo'] == "Venda")]['Valor Movimentado'].sum()
    dividendos_eur = df_user[(df_user['Moeda'] == "EUR (€)") & (df_user['Tipo'] == "Dividendo")]['Valor Movimentado'].sum()
    comissoes_eur = df_user[df_user['Moeda'] == "EUR (€)"]['Comissões'].sum()
    
    net_eur = compras_eur - vendas_eur + comissoes_eur
    st.metric("Total Alocado em Ativos (€)", f"{net_eur:,.2f} €")
    st.caption(f"Dividendos Recebidos: {dividendos_eur:,.2f} € | Total Comissões: {comissoes_eur:,.2f} €")

with col_usd:
    st.markdown("<h4 style='color: #0284c7;'>🇺🇸 Conta Dólares ($)</h4>", unsafe_allow_html=True)
    compras_usd = df_user[(df_user['Moeda'] == "USD ($)") & (df_user['Tipo'] == "Compra")]['Valor Movimentado'].sum()
    vendas_usd = df_user[(df_user['Moeda'] == "USD ($)") & (df_user['Tipo'] == "Venda")]['Valor Movimentado'].sum()
    dividendos_usd = df_user[(df_user['Moeda'] == "USD ($)") & (df_user['Tipo'] == "Dividendo")]['Valor Movimentado'].sum()
    comissoes_usd = df_user[df_user['Moeda'] == "USD ($)"]['Comissões'].sum()
    
    net_usd = compras_usd - vendas_usd + comissoes_usd
    st.metric("Total Alocado em Ativos ($)", f"$ {net_usd:,.2f}")
    st.caption(f"Dividendos Recebidos: $ {dividendos_usd:,.2f} | Total Comissões: $ {comissoes_usd:,.2f}")

st.divider()

# 8. TABELA DE HISTÓRICO
st.subheader("📜 Histórico de Movimentos")

filtro_cat = st.multiselect("Filtrar por Categoria:", list(ativos_dict.keys()), default=list(ativos_dict.keys())[:3])
df_filtrado = df_user[df_user['Categoria'].isin(filtro_cat)].sort_values(by="Data", ascending=False)

# Mostrar tabela sem a coluna "Utilizador" pois já sabemos de quem é
st.dataframe(
    df_filtrado.drop(columns=["Utilizador"]).style.format({
        "Preço": "{:,.2f}",
        "Comissões": "{:,.2f}",
        "Valor Movimentado": "{:,.2f}",
        "Quantidade": "{:,.6f}"
    }),
    use_container_width=True
)
