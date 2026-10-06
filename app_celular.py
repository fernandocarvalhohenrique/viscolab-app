import streamlit as st
import sqlite3

# Configuração da página e PWA
st.set_page_config(
    page_title="ViscoLab Móvel", 
    page_icon="🧪", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS para transformar a interface numa App Nativa (PWA / Mobile UI)
st.markdown("""
    <head>
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="theme-color" content="#0e1117">
    </head>
    <style>
        /* Ocultar elementos padrão do Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        
        /* Ajustar espaçamento do topo no telemóvel */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 500px !important;
        }

        /* Estilização do Título e Cabeçalho */
        .app-title {
            text-align: center;
            font-size: 1.8rem;
            font-weight: 700;
            color: #1E293B;
            margin-bottom: 0.2rem;
        }
        .app-subtitle {
            text-align: center;
            font-size: 0.85rem;
            color: #64748B;
            margin-bottom: 1.5rem;
        }

        /* Estilização dos Botões Principais */
        div.stButton > button:first-child {
            width: 100% !important;
            height: 3rem !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            background-color: #2563EB !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3) !important;
            transition: all 0.2s ease !important;
        }
        div.stButton > button:first-child:active {
            transform: scale(0.98) !important;
        }

        /* Cartões de Alerta/Resultado */
        .result-card {
            background-color: #F0FDF4;
            border: 1px solid #BBF7D0;
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            margin-top: 1rem;
        }
        .result-value {
            font-size: 1.6rem;
            font-weight: 700;
            color: #166534;
        }
    </style>
""", unsafe_allow_html=True)

# --- BANCO DE DADOS ---
def iniciar_banco():
    conn = sqlite3.connect("capilares.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS capilares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identificacao TEXT UNIQUE NOT NULL,
            constante_40 REAL,
            constante_100 REAL
        )
    """)
    conn.commit()
    conn.close()

iniciar_banco()

# --- INTERFACE PRINCIPAL ---
st.markdown('<div class="app-title">🧪 ViscoLab Móvel</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Cálculo de Viscosidade Cinemática de Laboratório</div>', unsafe_allow_html=True)

# SEÇÃO 1: Capilares
st.markdown("### 1. Seleção do Capilar")

conn = sqlite3.connect("capilares.db")
cursor = conn.cursor()
cursor.execute("SELECT identificacao FROM capilares")
lista_capilares = [row[0] for row in cursor.fetchall()]
conn.close()

capilar_sel = st.selectbox("Escolha o Capilar:", ["-- Selecionar --"] + lista_capilares, label_visibility="collapsed")

c40_val, c100_val = 0.0, 0.0
if capilar_sel != "-- Selecionar --":
    conn = sqlite3.connect("capilares.db")
    cursor = conn.cursor()
    cursor.execute("SELECT constante_40, constante_100 FROM capilares WHERE identificacao = ?", (capilar_sel,))
    dados = cursor.fetchone()
    conn.close()
    if dados:
        c40_val = dados[0] or 0.0
        c100_val = dados[1] or 0.0

with st.expander("➕ Cadastrar / Editar Capilar"):
    novo_nome = st.text_input("Identificação do Capilar (Ex: 1B 75)")
    nova_c40 = st.number_input("Constante 40°C", value=0.0, format="%.5f")
    nova_c100 = st.number_input("Constante 100°C", value=0.0, format="%.5f")
    if st.button("Salvar Capilar"):
        if novo_nome:
            conn = sqlite3.connect("capilares.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO capilares (identificacao, constante_40, constante_100)
                VALUES (?, ?, ?)
                ON CONFLICT(identificacao) DO UPDATE SET
                    constante_40=excluded.constante_40,
                    constante_100=excluded.constante_100
            """, (novo_nome, nova_c40, nova_c100))
            conn.commit()
            conn.close()
            st.success("Capilar salvo com sucesso!")
            st.rerun()

st.divider()

# SEÇÃO 2: Medição
st.markdown("### 2. Medição de Tempo")
temp_escolhida = st.radio("Temperatura da Análise:", ["40°C", "100°C"], horizontal=True)

tempo_input = st.text_input(
    "Tempo no Cronômetro:", 
    placeholder="Ex: 0.55 (55s) ou 1.20 (1m 20s)"
)

# SEÇÃO 3: Cálculo
if st.button("CALCULAR VISCOSIDADE"):
    try:
        tempo_float = float(tempo_input.replace(",", "."))
        minutos = int(tempo_float)
        segundos = round((tempo_float - minutos) * 100)
        segundos_totais = (minutos * 60) + segundos

        constante = c40_val if temp_escolhida == "40°C" else c100_val

        if constante > 0:
            viscosidade = segundos_totais * constante
            st.markdown(f"""
                <div class="result-card">
                    <div style="color: #15803D; font-size: 0.9rem; font-weight: 600;">VISCOSIDADE RESULTANTE</div>
                    <div class="result-value">{viscosidade:.5f} cSt</div>
                    <div style="color: #64748B; font-size: 0.8rem; margin-top: 4px;">Tempo total: {segundos_totais}s | Temp: {temp_escolhida}</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Selecione um capilar válido com constante preenchida!")
    except ValueError:
        st.error("Digite um formato de tempo válido.")
