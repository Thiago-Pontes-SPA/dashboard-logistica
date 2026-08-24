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
  todas_abas = [s for s in xls.sheet_names if s not in ["Base", "Hoja1"]]

  padrao_idx = (
      todas_abas.index("31.10")
      if "31.10" in todas_abas
      else len(todas_abas) - 1
  )

  st.sidebar.header("⚙️ Configurações")
  data_selecionada = st.sidebar.selectbox(
      "📅 Selecione a Data:", options=todas_abas, index=padrao_idx
  )

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
          raw_df.iloc[:, 1]
          .astype(str)
          .str.upper()
          .str.contains(metric_name.upper(), na=False)
      ]
      if not row.empty:
        val = row.iloc[0, col_idx]
        val_num = pd.to_numeric(val, errors="coerce")
        return val_num if pd.notna(val_num) else 0
      return 0
    except:
      return 0

  col_idx = (
      unidades_map[unidade_sel]
      if unidade_sel != "Consolidado Geral"
      else unidades_map["SPA"]
  )

  # Métricas Principais (KPIs)
  vol_total = get_metric("Volume total", col_idx)
  ocup_cam = get_metric("Ocupação caminhões", col_idx)
  tot_passivo = get_metric("Total passivo", col_idx)
  ret_dia = get_metric("Retorno do dia", col_idx)

  # Dados do Novo Gráfico Unificado (Pendentes, D+1, Recargas)
  cargas_pend = get_metric("pendentes de saída", col_idx)
  cargas_d1 = get_metric("D+1", col_idx)
  recargas = get_metric("Recargas do dia", col_idx)

  # Dados do Gráfico de Passivos por Tipo
  pass_agend = get_metric("Agendamento", col_idx)
  pass_rota = get_metric("Rota", col_idx)
  pass_sms = get_metric("SMS", col_idx)

  # Absenteísmo
  absenteismo_row = raw_df[
      raw_df.iloc[:, 1].astype(str).str.contains("Absenteísmo", na=False)
  ]
  absenteismo = (
      absenteismo_row.iloc[0, col_idx] if not absenteismo_row.empty else 0
  )

  # Formatação KPIs
  vol_fmt = (
      f"{vol_total:,.0f} UC".replace(",", ".") if vol_total > 0 else "0 UC"
  )
  ocup_fmt = f"{ocup_cam * 100:.1f}%" if 0 < ocup_cam <= 1 else f"{ocup_cam}%"
  ret_fmt = f"{ret_dia * 100:.2f}%" if 0 < ret_dia <= 1 else f"{ret_dia}%"

  # Cards Superiores
  col1, col2, col3, col4 = st.columns(4)
  with col1:
    st.metric(label="📦 Volume Total", value=vol_fmt)
  with col2:
    st.metric(label="🚛 Ocupação Caminhões", value=ocup_fmt)
  with col3:
    st.metric(label="⚠️ Total Passivo", value=f"{int(tot_passivo)} cargas")
  with col4:
    st.metric(label="🔄 Retorno do Dia", value=ret_fmt)

  st.markdown("---")

  col_g1, col_g2 = st.columns(2)

  # Gráfico 1: Pendentes, D+1 e Recargas
  with col_g1:
    st.subheader("📋 Pendentes, D+1 e Recargas")
    operacao_df = pd.DataFrame({
        "Indicador": ["Pendentes de Saída", "Cargas D+1", "Recargas do Dia"],
        "Quantidade": [cargas_pend, cargas_d1, recargas],
    })
    fig1 = px.bar(
        operacao_df,
        x="Indicador",
        y="Quantidade",
        color="Indicador",
        text_auto=True,
        color_discrete_sequence=["#F1C40F", "#3498DB", "#E74C3C"],
    )
    fig1.update_layout(showlegend=False, xaxis_title="", yaxis_title="Qtd. Cargas")
    st.plotly_chart(fig1, use_container_width=True)

  # Gráfico 2: Cargas no Passivo por Motivo
  with col_g2:
    st.subheader("🚨 Cargas no Passivo por Motivo")
    passivos_df = pd.DataFrame({
        "Tipo de Passivo": ["Agendamento", "Rota", "SMS"],
        "Quantidade de Cargas": [pass_agend, pass_rota, pass_sms],
    })
    fig2 = px.bar(
        passivos_df,
        x="Tipo de Passivo",
        y="Quantidade de Cargas",
        color="Tipo de Passivo",
        text_auto=True,
        color_discrete_sequence=["#F39C12", "#E74C3C", "#2980B9"],
    )
    fig2.update_layout(
        showlegend=False, xaxis_title="", yaxis_title="Qtd. Cargas"
    )
    st.plotly_chart(fig2, use_container_width=True)

  # Informação de Absenteísmo
  if pd.notna(absenteismo) and str(absenteismo) != "0":
    st.info(f"💡 **Absenteísmo do Dia ({unidade_sel}):** {absenteismo}")

except Exception as e:
  st.error(f"Aguardando sincronização de dados: {e}")
