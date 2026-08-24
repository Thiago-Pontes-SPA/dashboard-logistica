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

  def get_by_index(row_idx, col_idx):
    try:
      val = raw_df.iloc[row_idx, col_idx]
      val_num = pd.to_numeric(val, errors="coerce")
      return val_num if pd.notna(val_num) else 0
    except:
      return 0

  col_idx = (
      unidades_map[unidade_sel]
      if unidade_sel != "Consolidado Geral"
      else unidades_map["SPA"]
  )

  # Métricas Principais
  vol_total = get_by_index(15, col_idx)
  ocup_cam = get_by_index(14, col_idx)
  tot_passivo = get_by_index(11, col_idx)
  ret_dia = get_by_index(12, col_idx)

  # 1. Leitura Direta do Fluxo de Cargas nas Linhas
  cargas_dia = get_by_index(5, col_idx)  # Cargas do dia
  cargas_d1 = get_by_index(18, col_idx)  # Transferência / D+1
  pend_saida = get_by_index(6, col_idx)  # Cargas pendentes de saída
  recargas_cam = get_by_index(7, col_idx)  # Recargas do dia (Caminhão)
  recargas_hr = get_by_index(4, col_idx)  # Recargas HR

  # 2. Passivos por Tipo
  pass_agend = get_by_index(8, col_idx)
  pass_rota = get_by_index(9, col_idx)
  pass_sms = get_by_index(10, col_idx)

  # Formatação KPIs
  vol_fmt = (
      f"{vol_total:,.0f} UC".replace(",", ".") if vol_total > 0 else "0 UC"
  )
  ocup_fmt = f"{ocup_cam * 100:.1f}%" if 0 < ocup_cam <= 1 else f"{ocup_cam}%"
  ret_fmt = f"{ret_dia * 100:.2f}%" if 0 < ret_dia <= 1 else f"{ret_dia}%"

  # Cards
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

  # Gráfico 1: 5 Colunas solicitadas na ordem
  with col_g1:
    st.subheader("📦 Visão Geral de Cargas")
    operacao_df = pd.DataFrame({
        "Indicador": [
            "Cargas do dia",
            "D+1",
            "Pendentes de saída",
            "Recargas de Caminhão",
            "Recargas HR",
        ],
        "Quantidade": [
            cargas_dia,
            cargas_d1,
            pend_saida,
            recargas_cam,
            recargas_hr,
        ],
    })
    fig1 = px.bar(
        operacao_df,
        x="Indicador",
        y="Quantidade",
        color="Indicador",
        text_auto=True,
        color_discrete_sequence=[
            "#2E86C1",
            "#28B463",
            "#F1C40F",
            "#E74C3C",
            "#8E44AD",
        ],
    )
    fig1.update_layout(showlegend=False, xaxis_title="", yaxis_title="Qtd. Cargas")
    st.plotly_chart(fig1, use_container_width=True)

  # Gráfico 2: Cargas no Passivo
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

except Exception as e:
  st.error(f"Aguardando leitura dos dados: {e}")
