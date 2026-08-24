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
      todas_abas.index("22.08.26")
      if "22.08.26" in todas_abas
      else len(todas_abas) - 1
  )

  st.sidebar.header("⚙️ Configurações")
  data_selecionada = st.sidebar.selectbox(
      "📅 Selecione a Data:", options=todas_abas, index=padrao_idx
  )

  raw_df = pd.read_excel(excel_file, sheet_name=data_selecionada)

  # Mapeamento exato das colunas conforme a foto da planilha:
  # BGU=1 | CJU=2 | LST=3 | NIG=4 | FRIG=5 | SPA=6 | CD'S (Consolidado)=7
  unidades_map = {
      "Consolidado Geral (CD'S)": "CD'S",
      "BGU": "BGU",
      "CJU": "CJU",
      "LST": "LST",
      "NIG": "NIG",
      "FRIG": "FRIG",
      "SPA": "SPA",
  }

  unidade_sel = st.selectbox(
      "🎯 Filtrar por Unidade:", list(unidades_map.keys())
  )

  # Encontra a linha de cabeçalho onde estão as siglas das unidades
  header_row_idx = None
  for idx, r in raw_df.iterrows():
    row_vals = [str(v).strip().upper() for v in r.values]
    if "SPA" in row_vals and "BGU" in row_vals:
      header_row_idx = idx
      break

  # Descobre o índice numérico real da coluna selecionada
  col_idx = 7  # Padrão CD'S
  if header_row_idx is not None:
    headers = [
        str(v).strip().upper() for v in raw_df.iloc[header_row_idx].values
    ]
    alvo = unidades_map[unidade_sel].upper()
    for i, h in enumerate(headers):
      if alvo in h or h in alvo:
        col_idx = i
        break

  st.caption(
      f"📊 Exibindo dados da aba: **{data_selecionada}** | Unidade:"
      f" **{unidade_sel}**"
  )
  st.markdown("---")

  def buscar_valor_exato(nome_linha):
    for r_idx in range(len(raw_df)):
      rotulo = str(raw_df.iloc[r_idx, 0]).strip().upper()
      if rotulo == "":
        rotulo = str(raw_df.iloc[r_idx, 1]).strip().upper()
      if nome_linha.upper() in rotulo:
        val = raw_df.iloc[r_idx, col_idx]
        val_num = pd.to_numeric(val, errors="coerce")
        return val_num if pd.notna(val_num) else 0
    return 0

  # Extração dos KPIs
  vol_total = buscar_valor_exato("VOLUME TOTAL")
  ocup_cam = buscar_valor_exato("OCUPAÇÃO CAMINHÕES")
  tot_passivo = buscar_valor_exato("TOTAL PASSIVO")
  ret_dia = buscar_valor_exato("RETORNO DO DIA")

  # Extração dos 5 Indicadores das Barras
  cargas_dia = buscar_valor_exato("CARGAS DO DIA")
  cargas_d1 = buscar_valor_exato("CARGAS EM D+1")
  pend_saida = buscar_valor_exato("CARGAS PENDENTES DE SAÍDA")
  recargas_cam = buscar_valor_exato("RECARGAS DE CAMINHÃO")
  recargas_hr = buscar_valor_exato("RECARGAS DE HR")

  # Extração dos Passivos
  pass_agend = buscar_valor_exato("PASSIVO ( AGENDAMENTO )")
  pass_rota = buscar_valor_exato("PASSIVO ( ROTA )")
  pass_sms = buscar_valor_exato("PASSIVO ( SMS )")

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

  # Gráfico 1: 5 Colunas
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

  # Gráfico 2: Passivos
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
  st.error(f"Erro ao processar a planilha: {e}")
