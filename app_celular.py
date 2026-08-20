import streamlit as st
import sqlite3
import time

st.set_page_config(page_title="ViscoLab", page_icon="🧪", layout="centered")

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

st.title("🧪 ViscoLab Móvel")

# SEÇÃO 1: Capilares
st.subheader("1. Seleção / Cadastro do Capilar")

conn = sqlite3.connect("capilares.db")
cursor = conn.cursor()
cursor.execute("SELECT identificacao FROM capilares")
lista_capilares = [row[0] for row in cursor.fetchall()]
conn.close()

capilar_sel = st.selectbox("Escolha o Capilar:", ["-- Selecionar --"] + lista_capilares)

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

with st.expander("Cadastrar / Editar Capilar"):
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

# SEÇÃO 2: Medição
st.subheader("2. Medição de Tempo")
temp_escolhida = st.radio("Temperatura da Análise:", ["40°C", "100°C"], horizontal=True)

tempo_input = st.text_input("Tempo no Cronômetro (Ex: 0.55 para 55s ou 1.20 para 1m20s):", placeholder="0.55")

# SEÇÃO 3: Cálculo
if st.button("CALCULAR VISCOSIDADE", type="primary"):
    try:
        tempo_float = float(tempo_input.replace(",", "."))
        minutos = int(tempo_float)
        segundos = round((tempo_float - minutos) * 100)
        segundos_totais = (minutos * 60) + segundos

        constante = c40_val if temp_escolhida == "40°C" else c100_val

        if constante > 0:
            viscosidade = segundos_totais * constante
            st.success(f"**Viscosidade Resultante:** {viscosidade:.5f} cSt")
        else:
            st.error("Selecione um capilar válido com constante preenchida!")
    except ValueError:
        st.error("Digite um formato de tempo válido.")

