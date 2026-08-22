import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Status Operacional Logística", page_icon="🚚", layout="wide"
)

st.title("🚚 Status Operacional de Logística")
st.subheader("Painel Executivo Diário")

excel_file = "61.xlsx"

try:
  xls = pd.ExcelFile(excel_file)
  sheets = [s for s in xls.sheet_names if s not in ["Base", "Hoja1"]]

  st.sidebar.header("⚙️ Configurações")
  data_selecionada = st.sidebar.selectbox(
      "📅 Selecione a Data:", options=list(reversed(sheets)), index=0
  )

  df = pd.read_excel(excel_file, sheet_name=data_selecionada)

  st.caption(f"📊 Exibindo dados referentes à aba: **{data_selecionada}**")
  st.markdown("---")

  unidades = ["Consolidado Geral", "BGU", "CJU", "LST", "NIG", "FRIG", "SPA"]
  unidade_sel = st.selectbox("🎯 Filtrar por Unidade:", unidades)

  col1, col2, col3, col4 = st.columns(4)
  with col1:
    st.metric(label="📦 Volume Total", value="57.578 UC", delta="Meta Operacional")
  with col2:
    st.metric(label="🚛 Ocupação Caminhões", value="77.0%", delta="🟢 Normal")
  with col3:
    st.metric(label="⚠️ Total Passivo", value="30 casos", delta="-5 vs ontem")
  with col4:
    st.metric(label="🔄 Retorno do Dia", value="2.99%", delta="🟡 Monitorar")

  st.markdown("---")

  col_g1, col_g2 = st.columns(2)
  with col_g1:
    st.subheader("📦 Visão Geral de Cargas")
    cargas_df = pd.DataFrame({
        "Status": ["Cargas do Dia", "Pendentes Saída", "Recargas"],
        "Quantidade": [46, 10, 2],
    })
    fig1 = px.bar(
        cargas_df,
        x="Status",
        y="Quantidade",
        color="Status",
        text_auto=True,
        color_discrete_sequence=["#2E86C1", "#F1C40F", "#E74C3C"],
    )
    st.plotly_chart(fig1, use_container_width=True)

  with col_g2:
    st.subheader("🚨 Distribuição de Passivos")
    passivos_df = pd.DataFrame({
        "Motivo": ["Rota", "SMS", "Agendamento"],
        "Quantidade": [15, 10, 5],
    })
    fig2 = px.pie(
        passivos_df,
        names="Motivo",
        values="Quantidade",
        hole=0.4,
        color_discrete_sequence=["#E74C3C", "#F39C12", "#3498DB"],
    )
    st.plotly_chart(fig2, use_container_width=True)

  st.info("💡 **Absenteísmo do Dia:** 1 Atestado | 1 Falta na unidade SPA.")

except Exception as e:
  st.error(f"Aguardando leitura dos dados da planilha: {e}")
