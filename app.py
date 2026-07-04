import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Portefólio Premium", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

# 1. SISTEMA DE AUTENTICAÇÃO SEGURO
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
            try:
                senhas_seguras = st.secrets["senhas"]
                if user_input in senhas_seguras and senhas_seguras[user_input] == pwd_input:
                    st.session_state.logged_in = True
                    st.session_state.username = user_input
                    st.rerun()
                else:
                    st.error("Utilizador ou senha incorretos.")
            except FileNotFoundError:
                st.error("Erro: O cofre de senhas (Secrets) ainda não foi configurado no Streamlit.")
    st.stop()

col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title(f"💼 Portefólio Global - Olá, {st.session_state.username.capitalize()}!")
with col_logout:
    if st.button("Sair"):
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

# 2. DEFINIÇÃO DA ESTRUTURA BASE E ATIVOS
colunas_base = ["Utilizador", "Data", "Categoria", "Ativo", "Tipo", "Moeda", "Preço", "Comissões", "Valor Movimentado", "Quantidade"]

ativos_dict = {
    "Depósito / Levantamento": ["Caixa / Saldo Disponível na Corretora"],
    "Ações Americanas (Top 15)": ["Apple (AAPL)", "Microsoft (MSFT)", "NVIDIA (NVDA)", "Amazon (AMZN)", "Alphabet (GOOGL)", "Meta (META)", "Tesla (TSLA)", "Berkshire Hathaway (BRK.B)", "Eli Lilly (LLY)", "Broadcom (AVGO)", "JPMorgan Chase (JPM)", "UnitedHealth (UNH)", "Visa (V)", "ExxonMobil (XOM)", "Johnson & Johnson (JNJ)"],
    "Ações Europeias (Principais)": ["ASML Holding (ASML)", "Novo Nordisk (NOVO B)", "LVMH (MC)", "SAP (SAP)", "Roche (ROG)", "Shell (SHEL)", "L'Oréal (OR)", "AstraZeneca (AZN)", "Novartis (NVS)", "TotalEnergies (TTE)"],
    "Ações Globais, IA e Semicondutores": ["TSMC (TSM)", "AMD (AMD)", "Intel (INTC)", "Qualcomm (QCOM)", "Texas Instruments (TXN)", "Micron Technology (MU)", "ARM Holdings (ARM)", "Applied Materials (AMAT)", "Lam Research (LRCX)", "Palantir (PLTR)", "Salesforce (CRM)", "Adobe (ADBE)", "Netflix (NFLX)", "ASML (ASML)", "NXP Semiconductors (NXPI)"],
    "ETFs Americanos (Top 20)": ["SPDR S&P 500 (SPY)", "iShares Core S&P 500 (IVV)", "Vanguard S&P 500 (VOO)", "Invesco QQQ (QQQ)", "Vanguard Total Stock Market (VTI)", "Vanguard Growth (VUG)"],
    "ETFs Europeus / UCITS": ["Vanguard FTSE All-World (VWCE)", "iShares Core MSCI World (IWDA)", "Vanguard S&P 500 (VUAA)", "iShares Core S&P 500 (SXR8)", "iShares NASDAQ 100 (SXRV)", "iShares S&P 500 Info Tech (QDVE)"],
    "Criptomoedas (Top 20)": ["Bitcoin (BTC)", "Ethereum (ETH)", "Tether (USDT)", "BNB (BNB)", "Solana (SOL)", "XRP (XRP)", "Dogecoin (DOGE)", "Cardano (ADA)", "Bitcoin Cash (BCH)", "Chainlink (LINK)"]
}

# 3. LIGAÇÃO INTELIGENTE (GOOGLE SHEETS OU LOCAL)
gsheets_active = False
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_sheet = conn.read(worksheet="Página1", usecols=list(range(10)))
    if 'operacoes' not in st.session_state:
        st.session_state.operacoes = df_sheet
    gsheets_active = True
except Exception:
    if 'operacoes' not in st.session_state:
        st.session_state.operacoes = pd.DataFrame(columns=colunas_base)

if not gsheets_active:
    st.warning("⚠️ Ligação ao Google Sheets não detetada. A app está a usar o modo de Backup Local. Guarde o seu ficheiro CSV antes de sair!")

# 4. MENU LATERAL
with st.sidebar:
    st.header("➕ Nova Operação")
    data_op = st.date_input("Data do Negócio", date.today())
    categoria = st.selectbox("Categoria", list(ativos_dict.keys()))
    ativo = st.selectbox("Ativo", ativos_dict[categoria])
    
    if categoria == "Depósito / Levantamento":
        tipo = st.radio("Natureza", ["Depósito", "Levantamento"], horizontal=True)
        preco, qtd = 1.0, 0.0
    else:
        tipo = st.radio("Natureza", ["Compra", "Venda", "Dividendo"], horizontal=True)
        preco = st.number_input("Preço Unitário", min_value=0.0, step=0.01, format="%.2f")
    
    moeda = st.radio("Moeda", ["EUR (€)", "USD ($)"], horizontal=True)
    valor = st.number_input("Valor Bruto", min_value=0.0, step=10.0, format="%.2f")
    comissao = st.number_input("Comissões", min_value=0.0, step=0.5, format="%.2f")
    
    if st.button("🚀 Registar Movimento"):
        if valor > 0 or tipo == "Dividendo":
            if tipo in ["Compra", "Venda"]:
                qtd = (valor / preco) if tipo == "Compra" else -(valor / preco)
            elif tipo == "Dividendo":
                qtd = 0.0
            
            nova_linha = pd.DataFrame([{
                "Utilizador": st.session_state.username, "Data": data_op, "Categoria": categoria, 
                "Ativo": ativo, "Tipo": tipo, "Moeda": moeda, "Preço": preco, 
                "Comissões": comissao, "Valor Movimentado": valor, "Quantidade": qtd
            }])
            
            st.session_state.operacoes = pd.concat([st.session_state.operacoes, nova_linha], ignore_index=True)
            
            if gsheets_active:
                conn.update(worksheet="Página1", data=st.session_state.operacoes)
                
            st.success("Registado com sucesso!")
            st.rerun() # Esta linha resolve o problema, forçando a app a mostrar o botão de backup imediatamente
        else:
            st.error("Insira um valor válido.")

    st.divider()
    
    # 5. ZONA DE BACKUPS REPOSICIONADA
    st.header("📁 Backups Locais")
    
    ficheiro_carregado = st.file_uploader("1. Carregar Backup (.csv)", type="csv")
    if ficheiro_carregado is not None:
        novo_df = pd.read_csv(ficheiro_carregado)
        novo_df['Data'] = pd.to_datetime(novo_df['Data']).dt.date
        st.session_state.operacoes = novo_df
        if gsheets_active:
            conn.update(worksheet="Página1", data=st.session_state.operacoes)
        st.success("✅ Backup carregado!")
        st.rerun()

    # O botão agora vai aparecer sempre que existirem registos
    if not st.session_state.operacoes.empty:
        csv = st.session_state.operacoes.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 2. Descarregar Backup Atual", 
            data=csv, 
            file_name="backup_investimentos.csv", 
            mime="text/csv", 
            use_container_width=True
        )

# 6. PAINEL PRINCIPAL (DASHBOARD)
df_total = st.session_state.operacoes
df_user = df_total[df_total['Utilizador'] == st.session_state.username]

st.subheader("📊 Resumo Financeiro")
col_eur, col_usd = st.columns(2)

with col_eur:
    st.markdown("<h4 style='color: #0284c7;'>🇪🇺 Euros (€)</h4>", unsafe_allow_html=True)
    compras_eur = pd.to_numeric(df_user[(df_user['Moeda'] == "EUR (€)") & (df_user['Tipo'] == "Compra")]['Valor Movimentado']).sum()
    vendas_eur = pd.to_numeric(df_user[(df_user['Moeda'] == "EUR (€)") & (df_user['Tipo'] == "Venda")]['Valor Movimentado']).sum()
    comissoes_eur = pd.to_numeric(df_user[df_user['Moeda'] == "EUR (€)"]['Comissões']).sum()
    net_eur = compras_eur - vendas_eur + comissoes_eur
    st.metric("Total Alocado (€)", f"{net_eur:,.2f} €")

with col_usd:
    st.markdown("<h4 style='color: #0284c7;'>🇺🇸 Dólares ($)</h4>", unsafe_allow_html=True)
    compras_usd = pd.to_numeric(df_user[(df_user['Moeda'] == "USD ($)") & (df_user['Tipo'] == "Compra")]['Valor Movimentado']).sum()
    vendas_usd = pd.to_numeric(df_user[(df_user['Moeda'] == "USD ($)") & (df_user['Tipo'] == "Venda")]['Valor Movimentado']).sum()
    comissoes_usd = pd.to_numeric(df_user[df_user['Moeda'] == "USD ($)"]['Comissões']).sum()
    net_usd = compras_usd - vendas_usd + comissoes_usd
    st.metric("Total Alocado ($)", f"$ {net_usd:,.2f}")

st.divider()
st.subheader("📜 Histórico de Movimentos")
st.dataframe(df_user.drop(columns=["Utilizador"]), use_container_width=True)
