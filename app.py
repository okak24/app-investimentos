import streamlit as st
import pandas as pd
from datetime import date
import time
from streamlit_gsheets import GSheetsConnection

# Configuração da página
st.set_page_config(page_title="Portefólio Premium", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

# 1. SISTEMA DE AUTENTICAÇÃO
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.login_time = 0

if st.session_state.logged_in:
    if time.time() - st.session_state.login_time > 3600:
        st.session_state.logged_in = False
        st.warning("Sessão expirada. Faça login novamente.")

if not st.session_state.logged_in:
    st.title("🔒 Acesso ao Portefólio")
    with st.form("login_form"):
        user_input = st.text_input("Utilizador").lower()
        pwd_input = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            try:
                if user_input in st.secrets["senhas"] and st.secrets["senhas"][user_input] == pwd_input:
                    st.session_state.logged_in = True
                    st.session_state.username = user_input
                    st.session_state.login_time = time.time()
                    st.rerun()
                else:
                    st.error("Utilizador ou senha incorretos.")
            except Exception:
                st.error("Erro na configuração dos Secrets.")
    st.stop()

# Logout
if st.sidebar.button("Sair"):
    st.session_state.logged_in = False
    st.rerun()

# 2. DEFINIÇÃO DA ESTRUTURA
colunas_base = ["Utilizador", "Data", "Categoria", "Ativo", "Tipo", "Moeda", "Preço", "Comissões", "Valor Movimentado", "Quantidade"]
ativos_dict = {
    "Depósito / Levantamento": ["Caixa / Saldo Disponível na Corretora"],
    "Ações Americanas": ["Apple (AAPL)", "Microsoft (MSFT)", "NVIDIA (NVDA)", "Amazon (AMZN)", "Tesla (TSLA)"],
    "Criptomoedas": ["Bitcoin (BTC)", "Ethereum (ETH)", "Solana (SOL)"]
}

# 3. LIGAÇÃO AO GOOGLE SHEETS
gsheets_active = False
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_sheet = conn.read(worksheet="Página1", usecols=list(range(10)))
    if 'operacoes' not in st.session_state:
        st.session_state.operacoes = df_sheet
    gsheets_active = True
except Exception as e:
    st.warning(f"Modo Offline: {e}")
    if 'operacoes' not in st.session_state:
        st.session_state.operacoes = pd.DataFrame(columns=colunas_base)

# 4. MENU LATERAL
with st.sidebar:
    st.header("➕ Nova Operação")
    data_op = st.date_input("Data", date.today())
    categoria = st.selectbox("Categoria", list(ativos_dict.keys()))
    ativo = st.selectbox("Ativo", ativos_dict[categoria])
    tipo = st.radio("Natureza", ["Compra", "Venda", "Dividendo"], horizontal=True)
    preco = st.number_input("Preço Unitário", min_value=0.0, step=0.01)
    moeda = st.radio("Moeda", ["EUR (€)", "USD ($)"], horizontal=True)
    valor = st.number_input("Valor Bruto", min_value=0.0, step=10.0)
    comissao = st.number_input("Comissões", min_value=0.0, step=0.5)
    
    if st.button("🚀 Registar Movimento"):
        qtd = (valor / preco) if tipo in ["Compra", "Venda"] else 0.0
        if tipo == "Venda": qtd = -abs(qtd)
        
        nova_linha = pd.DataFrame([{
            "Utilizador": st.session_state.username, "Data": str(data_op), "Categoria": categoria, 
            "Ativo": ativo, "Tipo": tipo, "Moeda": moeda, "Preço": preco, 
            "Comissões": comissao, "Valor Movimentado": valor, "Quantidade": qtd
        }])
        
        st.session_state.operacoes = pd.concat([st.session_state.operacoes, nova_linha], ignore_index=True)
        
        if gsheets_active:
            conn.update(worksheet="Página1", data=st.session_state.operacoes)
        st.success("Registado!")
        st.rerun()

# 5. PAINEL E TABELA
st.title(f"💼 Portefólio - {st.session_state.username.capitalize()}")
df_user = st.session_state.operacoes[st.session_state.operacoes['Utilizador'] == st.session_state.username]

st.subheader("📜 Histórico")
df_editado = st.data_editor(df_user.drop(columns=["Utilizador"]), num_rows="dynamic", use_container_width=True)

if st.button("💾 Guardar Alterações"):
    df_editado["Utilizador"] = st.session_state.username
    outros = st.session_state.operacoes[st.session_state.operacoes['Utilizador'] != st.session_state.username]
    st.session_state.operacoes = pd.concat([outros, df_editado], ignore_index=True)
    if gsheets_active:
        conn.update(worksheet="Página1", data=st.session_state.operacoes)
    st.success("Alterações guardadas!")
    st.rerun()
