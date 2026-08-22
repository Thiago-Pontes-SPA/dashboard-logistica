import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Status Operacional Logística", page_icon="🚚", layout="wide"
)

# 1. Carregar planilha e pegar a aba mais recente
excel_path = "61.xlsx"
xls = pd.ExcelFile(excel_path)
# Pega a última aba da lista (a mais recente preenchida)
aba_atual = xls.sheet_names[-1]

df = pd.read_excel(excel_path, sheet_name=aba_atual)

# Tratamento básico dos dados da aba
st.title("🚚 Status Operacional de Logística")
st.caption(f"📅 Dados referentes ao dia: **{aba_atual}**")

# Selector de Unidade
unidades = ["Consolidado Geral", "BGU", "CJU", "LST", "NIG", "FRIG", "SPA"]
unidade_sel = st.selectbox("📍 Filtrar por Unidade:", unidades)

# Exibição dos KPIs dinâmicos conforme a unidade selecionada...
