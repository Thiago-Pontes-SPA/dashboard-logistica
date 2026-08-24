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

  # Identificação dinâmica das colunas conforme o cabeçalho amarelo da foto
  header_row_idx = None
  for idx, r in raw_df.iterrows():
    row_vals = [str(v).strip().upper() for v in r.values]
    if "SPA" in row_vals and "BGU" in row_vals:
      header_row_idx = idx
      break

  # Dicionário de colunas (BGU, CJU, LST, NIG, FRIG, SPA, CD'S)
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

  col_idx = 7  # Padrão CD'S (Coluna 7)
  if header_row_idx is not None:
    headers = [
        str(v).strip().upper() for v in raw_df.iloc[header_row_idx].values
    ]
    alvo = unidades_map[unidade_sel].upper()
    for i, h in enumerate(headers):
      if alvo == h or (alvo in h and len(h) <= 5):
        col_idx = i
        break

  st.caption(
      f"📊 Exibindo dados da aba: **{data_selecionada}** | Unidade:"
      f" **{unidade_sel}**"
  )
  st.markdown("---")

  # Função de busca linha por linha
  def get_metric_val(termo_exato):
    for r_idx in range(len(raw_df)):
      rotulo = " ".join(raw_df.iloc[r_idx, :2].dropna().astype(str)).upper()
      if termo_exato.upper() in rotulo:
        val = raw_df.iloc[r_idx, col_idx]
        val_num = pd.to_numeric(val, errors="coerce")
        return val_num if pd.notna(val_num) else 0
    return 0

  # --- GRÁFICO 1: OPERAÇÃO DE CARGAS ---
  cargas_dia = get_metric_val("CARGAS DO DIA")
  cargas_d1 = get_metric_val("CARGAS EM D+1")
  pend_saida = get_metric_val("CARGAS PENDENTES DE SAÍDA")
  recargas_cam = get_metric_val("RECARGAS DE CAMINHÃO")
  recargas_hr = get_metric_val("RECARGAS DE HR")

  # --- GRÁFICO 2: DETALHAMENTO DE PASSIVOS ---
  tot_passivo = get_metric_val("TOTAL PASSIVO")
  pass_agend = get_metric_val("AGENDAMENTO")
  pass_rota = get_metric_val("ROTA")
  pass_sms = get_metric_val("SMS")

  # --- GRÁFICO 3: INDICADORES DE ATENDIMENTO E FROTA ---
  ocup_cam = get_metric_val("OCUPAÇÃO CAMINHÕES")
  vol_total = get_metric_val("VOLUME TOTAL")
  qtd_clientes = get_metric_val("QDT CLIENTES")

  # Ajuste do percentual de ocupação
  ocup_pct = ocup_cam * 100 if 0 < ocup_cam <= 1 else ocup_cam

  # --- LAYOUT DOS 3 GRÁFICOS ---
  col_g1, col_g2, col_g3 = st.columns(3)

  # GRÁFICO 1
  with col_g1:
    st.subheader("📦 Fluxo de Cargas")
    df_g1 = pd.DataFrame({
        "Indicador": [
            "Cargas do Dia",
            "Cargas em D+1",
            "Cargas pendentes de saída",
            "Recargas de Caminhão",
            "Recargas de HR",
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
        df_g1,
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
    fig1.update_layout(showlegend=False, xaxis_title="", yaxis_title="Qtd.")
    st.plotly_chart(fig1, use_container_width=True)

  # GRÁFICO 2
  with col_g2:
    st.subheader("🚨 Passivos Operacionais")
    df_g2 = pd.DataFrame({
        "Indicador": [
            "Total Passivo",
            "Passivo de Agendamento",
            "Passivo de Rota",
            "Passivo de SMS",
        ],
        "Quantidade": [tot_passivo, pass_agend, pass_rota, pass_sms],
    })
    fig2 = px.bar(
        df_g2,
        x="Indicador",
        y="Quantidade",
        color="Indicador",
        text_auto=True,
        color_discrete_sequence=["#D35400", "#F39C12", "#E74C3C", "#2980B9"],
    )
    fig2.update_layout(showlegend=False, xaxis_title="", yaxis_title="Qtd.")
    st.plotly_chart(fig2, use_container_width=True)

  # GRÁFICO 3
  with col_g3:
    st.subheader("📈 Atendimento & Frota")
    df_g3 = pd.DataFrame({
        "Indicador": [
            "Ocupação dos caminhões (%)",
            "Volume total (UC)",
            "Quantidade de clientes",
        ],
        "Valor": [ocup_pct, vol_total, qtd_clientes],
    })
    fig3 = px.bar(
        df_g3,
        x="Indicador",
        y="Valor",
        color="Indicador",
        text_auto=True,
        color_discrete_sequence=["#16A085", "#2980B9", "#8E44AD"],
    )
    fig3.update_layout(showlegend=False, xaxis_title="", yaxis_title="Valor")
    st.plotly_chart(fig3, use_container_width=True)

except Exception as e:
  st.error(f"Erro ao processar os dados da planilha: {e}")
