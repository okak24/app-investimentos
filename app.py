import streamlit as st
import pandas as pd
from datetime import date

# Configuração da página
st.set_page_config(page_title="Dashboard de Investimentos", layout="wide")

st.title("📊 Portefólio de Investimentos")

# Inicializar os dados em memória (pode ser ligado a um ficheiro CSV ou base de dados depois)
if 'operacoes' not in st.session_state:
    st.session_state.operacoes = pd.DataFrame(columns=["Data", "Ativo", "Tipo", "Preço (USD)", "Valor (USD)", "Quantidade"])

# Layout em colunas para a área de Input
st.subheader("Nova Operação")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    data_op = st.date_input("Data", date.today())
with col2:
    ativo = st.selectbox("Ativo", ["Bitcoin (BTC)", "S&P 500 (ETF)", "Outro"])
with col3:
    tipo = st.selectbox("Tipo", ["Compra", "Venda"])
with col4:
    preco = st.number_input("Preço de Mercado (USD)", min_value=0.0, format="%.2f")
with col5:
    valor = st.number_input("Valor da Operação (USD)", min_value=0.0, format="%.2f")

# Botão para registar a operação (Substitui a Macro do Excel)
if st.button("Executar Operação"):
    if preco > 0 and valor > 0:
        qtd = valor / preco
        nova_linha = pd.DataFrame([{
            "Data": data_op, "Ativo": ativo, "Tipo": tipo, 
            "Preço (USD)": preco, "Valor (USD)": valor, "Quantidade": qtd
        }])
        st.session_state.operacoes = pd.concat([st.session_state.operacoes, nova_linha], ignore_index=True)
        st.success("Operação registada com sucesso!")

st.divider()

# Dashboard de Métricas (A coluna direita da tua imagem)
st.subheader("Resumo Geral")
if not st.session_state.operacoes.empty:
    total_investido = st.session_state.operacoes[st.session_state.operacoes['Tipo'] == 'Compra']['Valor (USD)'].sum()
    qtd_total = st.session_state.operacoes[st.session_state.operacoes['Tipo'] == 'Compra']['Quantidade'].sum()
    preco_medio = total_investido / qtd_total if qtd_total > 0 else 0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Valor Total Investido", f"${total_investido:,.2f}")
    m2.metric("Saldo Atual (Qtd)", f"{qtd_total:.8f}")
    m3.metric("Preço Médio", f"${preco_medio:,.2f}")
    m4.metric("Preço Atual (Mercado)", f"${preco:,.2f}", delta=f"{((preco/preco_medio)-1)*100:.2f}%" if preco_medio > 0 else "0%")

# Tabela de Histórico
st.subheader("Operações Diárias")
st.dataframe(st.session_state.operacoes, use_container_width=True)
