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

  # Mapeamento manual exato das colunas de Unidades (Aba padrão)
  # Coluna 3 = BGU | 4 = CJU | 5 = LST | 6 = NIG | 7 = FRIG | 8 = SPA
  unidades_map = {
      "Consolidado Geral (SPA)": 8,
      "SPA": 8,
      "FRIG": 7,
      "NIG": 6,
      "LST": 5,
      "CJU": 4,
      "BGU": 3,
  }

  unidade_sel = st.selectbox(
      "🎯 Filtrar por Unidade:", list(unidades_map.keys())
  )
  col_idx = unidades_map[unidade_sel]

  st.caption(f"📊 Exibindo dados da aba: **{data_selecionada}** | Coluna lida: **{unidade_sel}**")
  st.markdown("---")

  def extrair_valor_linha(termo_chave, col_pos):
    for r_idx in range(len(raw_df)):
      linha_texto = " ".join(raw_df.iloc[r_idx, :3].dropna().astype(str)).upper()
      if termo_chave.upper() in linha_texto:
        val = raw_df.iloc[r_idx, col_pos]
        val_num = pd.to_numeric(val, errors="coerce")
        return val_num if pd.notna(val_num) else 0
    return 0

  # Leitura das Métricas Principais (KPIs)
  vol_total = extrair_valor_linha("VOLUME TOTAL", col_idx)
  ocup_cam = extrair_valor_linha("OCUPAÇÃO CAMINHÕES", col_idx)
  tot_passivo = extrair_valor_linha("TOTAL PASSIVO", col_idx)
  ret_dia = extrair_valor_linha("RETORNO DO DIA", col_idx)

  # Leitura dos Indicadores das Barras
  cargas_dia = extrair_valor_linha("CARGAS DO DIA", col_idx)
  cargas_d1 = extrair_valor_linha("TRANSFERÊNCIA", col_idx)
  if cargas_d1 == 0:
    cargas_d1 = extrair_valor_linha("D+1", col_idx)

  pend_saida = extrair_valor_linha("PENDENTES DE SAÍDA", col_idx)
  recargas_cam = extrair_valor_linha("RECARGAS DO DIA", col_idx)
  recargas_hr = extrair_valor_linha("TRUCK", col_idx)
  if recargas_hr == 0:
    recargas_hr = extrair_valor_linha("HR", col_idx)

  # Leitura dos Passivos
  pass_agend = extrair_valor_linha("AGENDAMENTO", col_idx)
  pass_rota = extrair_valor_linha("ROTA", col_idx)
  pass_sms = extrair_valor_linha("SMS", col_idx)

  # Formatação dos KPIs
  vol_fmt = f"{vol_total:,.0f} UC".replace(",", ".") if vol_total > 0 else f"{vol_total}"
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

  # Gráfico 1
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

  # Gráfico 2
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

  # Diagnóstico dos Dados
  with st.expander("🔍 Clique aqui para conferir a tabela de dados extraída da planilha"):
    st.dataframe(raw_df.dropna(how="all"))

except Exception as e:
  st.error(f"Erro ao processar a planilha: {e}")
