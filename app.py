import streamlit as st
import pandas as pd
from datetime import date

# 1. Configuração profissional da página (Otimizada para Mobile e Desktop)
st.set_page_config(
    page_title="Portefólio Premium",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed" # Começa fechado no telemóvel para dar espaço ao dashboard
)

# Estilização visual personalizada para um acabamento "Premium App"
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    div[data-testid="stMetricValue"] { font-size: 26px; font-weight: bold; color: #0f172a; }
    div[data-testid="stMetricLabel"] { font-size: 13px; color: #64748b; font-weight: 500; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #0284c7; color: white; font-weight: bold; }
    .stButton>button:hover { background-color: #0369a1; color: white; }
    </style>
""", unsafe_allow_html=True)

# Título Principal do Dashboard
st.title("💼 Gestão de Portefólio Global")
st.caption("Controlo profissional de Ações, ETFs e Criptomoedas")

# 2. Base de Dados de Ativos de Referência (Sugestões Solicitadas)
ativos_dict = {
    "Ações Americanas (EUA)": [
        "NVIDIA (NVDA)", 
        "Apple (AAPL)", 
        "Microsoft (MSFT)", 
        "Tesla (TSLA)", 
        "Amazon (AMZN)", 
        "Alphabet / Google (GOOGL)", 
        "Meta / Facebook (META)"
    ],
    "ETFs (Globais e Europeus)": [
        "S&P 500 UCITS ETF (VUAA / VUSA)", 
        "MSCI World Core UCITS ETF (IWDA)", 
        "Nasdaq 100 UCITS ETF (SXRV)", 
        "Euro Stoxx 50 (SX5E)", 
        "FTSE All-World Vanguard (VWCE)"
    ],
    "Criptomoedas de Referência": [
        "Bitcoin (BTC)", 
        "Ethereum (ETH)", 
        "Solana (SOL)", 
        "Cardano (ADA)", 
        "Ripple (XRP)"
    ]
}

# 3. Inicialização do Histórico de Dados em Memória
if 'operacoes' not in st.session_state:
    # Iniciamos com alguns registos reais simulados para o ecrã não aparecer vazio e sem graça
    st.session_state.operacoes = pd.DataFrame([
        {"Data": date(2026, 6, 11), "Categoria": "Criptomoedas de Referência", "Ativo": "Bitcoin (BTC)", "Tipo": "Compra", "Moeda": "USD ($)", "Preço": 63597.00, "Valor Movimentado": 500.00, "Quantidade": 0.007862},
        {"Data": date(2026, 6, 15), "Categoria": "ETFs (Globais e Europeus)", "Ativo": "S&P 500 UCITS ETF (VUAA / VUSA)", "Tipo": "Compra", "Moeda": "EUR (€)", "Preço": 92.50, "Valor Movimentado": 200.00, "Quantidade": 2.162162},
        {"Data": date(2026, 6, 20), "Categoria": "Ações Americanas (EUA)", "Ativo": "NVIDIA (NVDA)", "Tipo": "Compra", "Moeda": "USD ($)", "Preço": 127.40, "Valor Movimentado": 150.00, "Quantidade": 1.177394}
    ])

# 4. MENU LATERAL (Formulário de Entrada - No Telemóvel fica escondido num botão no topo esquerdo)
with st.sidebar:
    st.header("➕ Nova Operação")
    st.write("Insira os detalhes do investimento abaixo:")
    
    data_op = st.date_input("Data do Negócio", date.today())
    categoria = st.selectbox("Categoria do Ativo", list(ativos_dict.keys()))
    ativo = st.selectbox("Ativo Comercializado", ativos_dict[categoria])
    
    tipo = st.radio("Natureza da Operação", ["Compra", "Venda"], horizontal=True)
    moeda = st.radio("Moeda Utilizada", ["EUR (€)", "USD ($)"], horizontal=True)
    
    sinal_moeda = "€" if "EUR" in moeda else "$"
    preco = st.number_input(f"Preço Unitário do Ativo ({sinal_moeda})", min_value=0.0, step=0.01, format="%.2f")
    valor = st.number_input(f"Valor Total Investido ({sinal_moeda})", min_value=0.0, step=10.0, format="%.2f")
    
    # Execução do Botão de Registo
    if st.button("🚀 Confirmar e Registar"):
        if preco > 0 and valor > 0:
            # Se for venda, a quantidade entra como negativa para abater no saldo total
            qtd = (valor / preco) if tipo == "Compra" else -(valor / preco)
            
            nova_linha = pd.DataFrame([{
                "Data": data_op, "Categoria": categoria, "Ativo": ativo, "Tipo": tipo,
                "Moeda": moeda, "Preço": preco, "Valor Movimentado": valor, "Quantidade": qtd
            }])
            
            st.session_state.operacoes = pd.concat([st.session_state.operacoes, nova_linha], ignore_index=True)
            st.success(f"{ativo} adicionado com sucesso!")
        else:
            st.error("Por favor, preencha valores válidos maiores que zero.")

# 5. PAINEL DE MÉTRICAS (Zebra-Striping de Moedas)
df_atual = st.session_state.operacoes

st.subheader("📊 Resumo Atual do Portefólio")
col_eur, col_usd = st.columns(2)

with col_eur:
    st.markdown("<h4 style='color: #0284c7;'>🇪🇺 Total em Euros (€)</h4>", unsafe_allow_html=True)
    compras_eur = df_atual[(df_atual['Moeda'] == "EUR (€)") & (df_atual['Tipo'] == "Compra")]['Valor Movimentado'].sum()
    vendas_eur = df_atual[(df_atual['Moeda'] == "EUR (€)") & (df_atual['Tipo'] == "Venda")]['Valor Movimentado'].sum()
    net_eur = compras_eur - vendas_eur
    st.metric("Capital Alocado (€)", f"{net_eur:,.2f} €")

with col_usd:
    st.markdown("<h4 style='color: #0284c7;'>🇺🇸 Total em Dólares ($)</h4>", unsafe_allow_html=True)
    compras_usd = df_atual[(df_atual['Moeda'] == "USD ($)") & (df_atual['Tipo'] == "Compra")]['Valor Movimentado'].sum()
    vendas_usd = df_atual[(df_atual['Moeda'] == "USD ($)") & (df_atual['Tipo'] == "Venda")]['Valor Movimentado'].sum()
    net_usd = compras_usd - vendas_usd
    st.metric("Capital Alocado ($)", f"$ {net_usd:,.2f}")

st.divider()

# 6. TABELA DE HISTÓRICO COM FILTROS AVANÇADOS
st.subheader("📜 Histórico Analítico de Operações")

# Filtros rápidos para facilitar a pesquisa no ecrã do telemóvel
filtro_moeda = st.multiselect("Filtrar por Moeda:", ["EUR (€)", "USD ($)"], default=["EUR (€)", "USD ($)"])
df_filtrado = df_atual[df_atual['Moeda'].isin(filtro_moeda)].sort_values(by="Data", ascending=False)

# Renderização da Tabela Formatada Profissionalmente
st.dataframe(
    df_filtrado.style.format({
        "Preço": "{:,.2f}",
        "Valor Movimentado": "{:,.2f}",
        "Quantidade": "{:,.6f}"
    }),
    use_container_width=True
)

st.caption("💡 No telemóvel: Toque no ícone de três linhas no canto superior esquerdo para abrir o formulário e registar novos investimentos.")
