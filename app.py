import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# Configuração da Página
st.set_page_config(page_title="Portefólio Global", layout="wide")

# 1. SISTEMA DE LOGIN
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔒 Acesso ao Portefólio")
    user_input = st.text_input("Utilizador").lower()
    pwd_input = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if user_input in st.secrets["senhas"] and st.secrets["senhas"][user_input] == pwd_input:
            st.session_state.logged_in = True
            st.session_state.username = user_input
            st.rerun()
        else:
            st.error("Utilizador ou senha incorretos.")
    st.stop()

# 2. LIGAÇÃO À GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

# Carregar dados
try:
    df_total = conn.read(worksheet="Página1")
    # Limpeza básica de espaços nas colunas
    df_total.columns = df_total.columns.str.strip()
    st.session_state.operacoes = df_total
except Exception as e:
    st.error(f"Erro na ligação à Google: {e}")
    if 'operacoes' not in st.session_state:
        st.session_state.operacoes = pd.DataFrame(columns=["Utilizador", "Data", "Categoria", "Ativo", "Tipo", "Moeda", "Preço", "Comissões", "Valor Movimentado", "Quantidade"])

# 3. MENU LATERAL (NOVA OPERAÇÃO)
with st.sidebar:
    st.header("➕ Nova Operação")
    with st.form("form_operacao"):
        data_negocio = st.date_input("Data do Negócio", date.today())
        categoria = st.selectbox("Categoria", ["Ações", "Cripto", "Depósito"])
        ativo = st.text_input("Ativo")
        natureza = st.radio("Natureza", ["Compra", "Venda", "Dividendo"], horizontal=True)
        preco = st.number_input("Preço Unitário", min_value=0.0, step=0.01)
        moeda = st.radio("Moeda", ["EUR (€)", "USD ($)"], horizontal=True)
        valor_bruto = st.number_input("Valor Bruto", min_value=0.0, step=1.0)
        comissoes = st.number_input("Comissões", min_value=0.0, step=0.1)
        
        btn_registar = st.form_submit_button("Registar Movimento")

    if btn_registar:
        # Lógica de cálculo da quantidade
        qtd = (valor_bruto / preco) if preco > 0 else 0
        
        nova_linha = pd.DataFrame([{
            "Utilizador": st.session_state.username,
            "Data": str(data_negocio),
            "Categoria": categoria,
            "Ativo": ativo,
            "Tipo": natureza,
            "Moeda": moeda,
            "Preço": preco,
            "Comissões": comissoes,
            "Valor Movimentado": valor_bruto,
            "Quantidade": qtd
        }])
        
        st.session_state.operacoes = pd.concat([st.session_state.operacoes, nova_linha], ignore_index=True)
        
        try:
            conn.update(worksheet="Página1", data=st.session_state.operacoes)
            st.success("Operação registada com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao guardar na Google: {e}")

# 4. PAINEL PRINCIPAL
st.title(f"💼 Portefólio Global - Olá, {st.session_state.username.capitalize()}!")

# Filtrar dados do utilizador
if 'operacoes' in st.session_state:
    df_user = st.session_state.operacoes[st.session_state.operacoes['Utilizador'] == st.session_state.username]
    
    st.subheader("Histórico de Movimentos")
    st.dataframe(df_user, use_container_width=True)

if st.button("Sair"):
    st.session_state.logged_in = False
    st.rerun()
