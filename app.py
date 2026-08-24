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

  # Função flexível de busca por texto exato/parcial na 1ª ou 2ª coluna de rótulos
  def buscar_valor_rotulo(termo_busca, col_pos):
    try:
      # Procura na coluna B (índice 1) ou C (índice 2)
      for col_rotulo in [1, 2]:
        col_str = raw_df.iloc[:, col_rotulo].astype(str).str.strip().str.upper()
        row_match = raw_df[col_str.str.contains(termo_busca.upper(), na=False)]
        if not row_match.empty:
          val = row_match.iloc[0, col_pos]
          val_num = pd.to_numeric(val, errors="coerce")
          return val_num if pd.notna(val_num) else 0
      return 0
    except:
      return 0

  # Identifica os nomes das colunas de Unidades (BGU, CJU, LST, NIG, FRIG, SPA)
  header_row_idx = None
  for idx, r in raw_df.iterrows():
    row_vals = [str(v).strip().upper() for v in r.values]
    if "SPA" in row_vals and "BGU" in row_vals:
      header_row_idx = idx
      break

  if header_row_idx is not None:
    headers = [str(v).strip().upper() for v in raw_df.iloc[header_row_idx].values]
    unidades_disponiveis = ["SPA", "FRIG", "NIG", "LST", "CJU", "BGU"]
    
    # Mapeia dinamicamente o índice real de cada coluna
    cols_map = {}
    for u in unidades_disponiveis:
      if u in headers:
        cols_map[u] = headers.index(u)
      else:
        cols_map[u] = 8 # fallback
  else:
    cols_map = {"SPA": 8, "FRIG": 7, "NIG": 6, "LST": 5, "CJU": 4, "BGU": 3}

  unidade_sel = st.selectbox(
      "🎯 Filtrar por Unidade:", ["Consolidado Geral"] + list(cols_map.keys())
  )

  st.caption(f"📊 Exibindo dados em tempo real da aba: **{data_selecionada}**")
  st.markdown("---")

  col_idx = cols_map[unidade_sel] if unidade_sel != "Consolidado Geral" else cols_map["SPA"]

  # Extração de Métricas Principais (KPIs)
  vol_total = buscar_valor_rotulo("VOLUME TOTAL", col_idx)
  ocup_cam = buscar_valor_rotulo("OCUPAÇÃO CAMINHÕES", col_idx)
  tot_passivo = buscar_valor_rotulo("TOTAL PASSIVO", col_idx)
  ret_dia = buscar_valor_rotulo("RETORNO DO DIA", col_idx)

  # Extração da Ordem Exata Solicitada para o Gráfico 1:
  cargas_dia = buscar_valor_rotulo("CARGAS DO DIA", col_idx)
  cargas_d1 = buscar_valor_rotulo("D+1", col_idx)
  if cargas_d1 == 0:
    cargas_d1 = buscar_valor_rotulo("TRANSFERÊNCIA", col_idx)
    
  pend_saida = buscar_valor_rotulo("PENDENTES DE SAÍDA", col_idx)
  recargas_cam = buscar_valor_rotulo("RECARGAS DO DIA", col_idx)
  recargas_hr = buscar_valor_rotulo("HR", col_idx)

  # Passivos por Tipo
  pass_agend = buscar_valor_rotulo("AGENDAMENTO", col_idx)
  pass_rota = buscar_valor_rotulo("ROTA", col_idx)
  pass_sms = buscar_valor_rotulo("SMS", col_idx)

  # Formatação dos KPIs
  vol_fmt = f"{vol_total:,.0f} UC".replace(",", ".") if vol_total > 0 else "0 UC"
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

  # Gráfico 1: 5 colunas na ordem solicitada
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
  st.error(f"Erro ao ler os dados da planilha: {e}")
