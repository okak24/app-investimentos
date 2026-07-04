import streamlit as st
import pandas as pd
from datetime import date
import time
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portefólio Investimentos", page_icon="📈", layout="wide")

# 2. SISTEMA DE AUTENTICAÇÃO
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title("🔒 Login")
    user_input = st.text_input("Utilizador").lower()
    pwd_input = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        # Verifica se o utilizador existe nos secrets
        if user_input in st.secrets.get("senhas", {}) and st.secrets["senhas"][user_input] == pwd_input:
            st.session_state.logged_in = True
            st.session_state.username = user_input
            st.rerun()
        else:
            st.error("Credenciais inválidas.")
    st.stop()

# Logout no sidebar
if st.sidebar.button("Sair"):
    st.session_state.logged_in = False
    st.rerun()

# 3. CONEXÃO GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def carregar_dados():
    try:
        # Lê os dados da folha
        df = conn.read(worksheet="Página1", usecols=list(range(10)))
        # Garante que as colunas são strings e limpa espaços vazios
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao ler Google Sheets: {e}")
        return pd.DataFrame(columns=["Utilizador", "Data", "Categoria", "Ativo", "Tipo", "Moeda", "Preço", "Comissões", "Valor Movimentado", "Quantidade"])

# Carrega ou inicializa dados
if 'operacoes' not in st.session_state:
    st.session_state.operacoes = carregar_dados()

# 4. DASHBOARD E LÓGICA DE NEGÓCIO
st.title(f"📈 Dashboard de {st.session_state.username.capitalize()}")

# Filtra dados do user
df_user = st.session_state.operacoes[st.session_state.operacoes['Utilizador'] == st.session_state.username]

# Métricas (Cálculos)
total_investido = df_user[df_user['Tipo'] == 'Compra']['Valor Movimentado'].sum()
total_vendas = df_user[df_user['Tipo'] == 'Venda']['Valor Movimentado'].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Investido", f"{total_investido:.2f} €")
col2.metric("Total Realizado", f"{total_vendas:.2f} €")
col3.metric("Saldo Líquido", f"{(total_vendas - total_investido):.2f} €")

# 5. MENU LATERAL (REGISTO)
with st.sidebar:
    st.header("➕ Nova Operação")
    with st.form("form_operacao", clear_on_submit=True):
        data_op = st.date_input("Data", date.today())
        cat = st.selectbox("Categoria", ["Ações", "Cripto", "Depósito"])
        ativo = st.text_input("Ativo (ex: AAPL)")
        tipo = st.radio("Natureza", ["Compra", "Venda"], horizontal=True)
        preco = st.number_input("Preço Unitário", min_value=0.0, step=0.01)
        valor = st.number_input("Valor Bruto", min_value=0.0, step=1.0)
        
        if st.form_submit_button("Registar"):
            nova_linha = pd.DataFrame([{
                "Utilizador": st.session_state.username, 
                "Data": str(data_op), 
                "Categoria": cat, 
                "Ativo": ativo, 
                "Tipo": tipo, 
                "Moeda": "EUR", 
                "Preço": preco, 
                "Comissões": 0, 
                "Valor Movimentado": valor, 
                "Quantidade": (valor/preco) if preco > 0 else 0
            }])
            
            # Atualiza estado local
            st.session_state.operacoes = pd.concat([st.session_state.operacoes, nova_linha], ignore_index=True)
            
            # Escreve na Google Sheet
            try:
                conn.update(worksheet="Página1", data=st.session_state.operacoes)
                st.success("Guardado na Cloud!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gravar: {e}")

# 6. TABELA EDITÁVEL
st.subheader("📜 Histórico Detalhado")
df_editado = st.data_editor(df_user, use_container_width=True)

if st.button("💾 Guardar Alterações na Tabela"):
    # Atualiza o dataframe principal
    outros = st.session_state.operacoes[st.session_state.operacoes['Utilizador'] != st.session_state.username]
    st.session_state.operacoes = pd.concat([outros, df_editado], ignore_index=True)
    
    try:
        conn.update(worksheet="Página1", data=st.session_state.operacoes)
        st.success("Tabela atualizada!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao gravar: {e}")
