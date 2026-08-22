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
  # Seleciona abas ignorando bases
  todas_abas = [s for s in xls.sheet_names if s not in ["Base", "Hoja1"]]

  # Define por padrão a aba de dados reais ('31.10') se existir, senão a primeira da lista
  padrao_idx = (
      todas_abas.index("31.10")
      if "31.10" in todas_abas
      else len(todas_abas) - 1
  )

  st.sidebar.header("⚙️ Configurações")
  # O Streamlit guarda a escolha do usuário na variável data_selecionada
  data_selecionada = st.sidebar.selectbox(
      "📅 Selecione a Data:", options=todas_abas, index=padrao_idx
  )

  # Carrega estritamente a aba selecionada no menu
  raw_df = pd.read_excel(excel_file, sheet_name=data_selecionada)

  unidades_map = {
      "SPA": 8,
      "FRIG": 7,
      "NIG": 6,
      "LST": 5,
      "CJU": 4,
      "BGU": 3,
  }

  unidade_sel = st.selectbox(
      "🎯 Filtrar por Unidade:", ["Consolidado Geral"] + list(unidades_map.keys())
  )

  st.caption(f"📊 Exibindo dados em tempo real da aba: **{data_selecionada}**")
  st.markdown("---")

  def get_metric(metric_name, col_idx):
    try:
      row = raw_df[
          raw_df.iloc[:, 1].astype(str).str.contains(metric_name, na=False)
      ]
      if not row.empty:
        val = row.iloc[0, col_idx]
        return val if pd.notna(val) else 0
      return 0
    except:
      return 0

  col_idx = (
      unidades_map[unidade_sel]
      if unidade_sel != "Consolidado Geral"
      else unidades_map["SPA"]
  )

  vol_total = get_metric("Volume total", col_idx)
  ocup_cam = get_metric("Ocupação caminhões", col_idx)
  tot_passivo = get_metric("Total passivo", col_idx)
  ret_dia = get_metric("Retorno do dia", col_idx)

  cargas_dia = get_metric("Cargas do dia", col_idx)
  cargas_pend = get_metric("Cargas pendentes", col_idx)
  recargas = get_metric("Recargas do dia", col_idx)

  pass_rota = get_metric("Passivo ( Rota )", col_idx)
  pass_sms = get_metric("Passivo ( SMS", col_idx)
  pass_agend = get_metric("Passivo ( Agendamento", col_idx)

  absenteismo = get_metric("Absenteísmo", col_idx)

  vol_fmt = (
      f"{vol_total:,.0f} UC".replace(",", ".")
      if isinstance(vol_total, (int, float)) and vol_total > 0
      else str(vol_total)
  )
  ocup_fmt = (
      f"{ocup_cam * 100:.1f}%"
      if isinstance(ocup_cam, (int, float)) and 0 < ocup_cam <= 1
      else f"{ocup_cam}%"
  )
  ret_fmt = (
      f"{ret_dia * 100:.2f}%"
      if isinstance(ret_dia, (int, float)) and 0 < ret_dia <= 1
      else f"{ret_dia}%"
  )

  col1, col2, col3, col4 = st.columns(4)
  with col1:
    st.metric(label="📦 Volume Total", value=vol_fmt)
  with col2:
    st.metric(label="🚛 Ocupação Caminhões", value=ocup_fmt)
  with col3:
    st.metric(label="⚠️ Total Passivo", value=f"{tot_passivo} casos")
  with col4:
    st.metric(label="🔄 Retorno do Dia", value=ret_fmt)

  st.markdown("---")

  col_g1, col_g2 = st.columns(2)
  with col_g1:
    st.subheader("📦 Visão Geral de Cargas")
    cargas_df = pd.DataFrame({
        "Status": ["Cargas do Dia", "Pendentes Saída", "Recargas"],
        "Quantidade": [cargas_dia, cargas_pend, recargas],
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
        "Quantidade": [pass_rota, pass_sms, pass_agend],
    })
    fig2 = px.pie(
        passivos_df,
        names="Motivo",
        values="Quantidade",
        hole=0.4,
        color_discrete_sequence=["#E74C3C", "#F39C12", "#3498DB"],
    )
    st.plotly_chart(fig2, use_container_width=True)

  if absenteismo and str(absenteismo) != "0":
    st.info(f"💡 **Absenteísmo do Dia ({unidade_sel}):** {absenteismo}")

except Exception as e:
  st.error(f"Aguardando sincronização de dados: {e}")
