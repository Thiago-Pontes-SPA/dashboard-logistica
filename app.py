from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Status Operacional Logística", page_icon="🚚", layout="wide"
)

# Título do Painel
st.title("🚚 Status Operacional de Logística - Gestão BCFNS")
st.subheader("Painel Executivo Diário")

excel_file = "61.xlsx"


@st.cache_data(ttl=300)
def obter_lista_abas(file_path):
  xls = pd.ExcelFile(file_path)
  return [s for s in xls.sheet_names if s not in ["Base", "Hoja1"]]


try:
  todas_abas = obter_lista_abas(excel_file)

  hoje_str = datetime.now().strftime("%d.%m.%2y")

  padrao_idx = len(todas_abas) - 1
  if hoje_str in todas_abas:
    padrao_idx = todas_abas.index(hoje_str)
  else:
    for idx, aba in enumerate(todas_abas):
      if aba <= hoje_str:
        padrao_idx = idx

  # Mapeamento das unidades
  unidades_map = {
      "Consolidado Geral (CD'S)": "CD'S",
      "BGU": "BGU",
      "CJU": "CJU",
      "LST": "LST",
      "NIG": "NIG",
      "FRIG": "FRIG",
      "SPA": "SPA",
  }

  # ================= CAIXAS DE FILTRO NO CORPO PRINCIPAL =================
  unidade_sel = st.selectbox(
      "🎯 Filtrar por Unidade:", list(unidades_map.keys())
  )

  data_selecionada = st.selectbox(
      "📅 Selecione a Data:", options=todas_abas, index=padrao_idx
  )
  # =======================================================================

  raw_df = pd.read_excel(excel_file, sheet_name=data_selecionada)

  header_row_idx = None
  for idx, r in raw_df.iterrows():
    row_vals = [str(v).strip().upper() for v in r.values]
    if "SPA" in row_vals and "BGU" in row_vals:
      header_row_idx = idx
      break

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

  def get_metric_val(termo_exato):
    for r_idx in range(len(raw_df)):
      rotulo = " ".join(raw_df.iloc[r_idx, :2].dropna().astype(str)).upper()
      if termo_exato.upper() in rotulo:
        val = raw_df.iloc[r_idx, col_idx]
        val_num = pd.to_numeric(val, errors="coerce")
        return val_num if pd.notna(val_num) else 0
    return 0

  # LEITURA DOS DADOS
  # 1. Fluxo de Cargas
  cargas_dia = get_metric_val("CARGAS DO DIA")
  cargas_d1 = get_metric_val("CARGAS EM D+1")
  pend_saida = get_metric_val("CARGAS PENDENTES DE SAÍDA")
  recargas_cam = get_metric_val("RECARGAS DE CAMINHÃO")
  recargas_hr = get_metric_val("RECARGAS DE HR")

  # 2. Passivos
  tot_passivo = get_metric_val("TOTAL PASSIVO")
  pass_agend = get_metric_val("AGENDAMENTO")
  pass_rota = get_metric_val("ROTA")
  pass_sms = get_metric_val("SMS")

  # 3. Gestão de Equipes
  eq_ativa = get_metric_val("EQUIPE ATIVA")
  eq_ferias = get_metric_val("EQUIPE DE FÉRIAS")
  absenteismo = get_metric_val("ABSENTEÍSMO")
  cap_equipes = get_metric_val("CAPACIDADE DE EQUIPES")

  # 4. Composição da Frota
  baiado = get_metric_val("BAIADO")
  truck = get_metric_val("TRUCK")
  hr_frota = get_metric_val("HR")

  # 5. Atendimento
  vol_total = get_metric_val("VOLUME TOTAL")
  qtd_clientes = get_metric_val("QDT CLIENTES")

  # 6. Ocupação & Eficiência
  ocup_cam = get_metric_val("OCUPAÇÃO CAMINHÕES")
  ocup_cd = get_metric_val("OCUPAÇÃO CD")
  estudo_entrega = get_metric_val("ESTUDO DE ENTREGA")

  # 7. Retorno
  ret_dia = get_metric_val("RETORNO DO DIA")
  ret_mes = get_metric_val("RETORNO DO MÊS")

  # Tratamento de Porcentagens
  ocup_cam_pct = ocup_cam * 100 if 0 < ocup_cam <= 1 else ocup_cam
  ocup_cd_pct = ocup_cd * 100 if 0 < ocup_cd <= 1 else ocup_cd
  estudo_pct = (
      estudo_entrega * 100 if 0 < estudo_entrega <= 1 else estudo_entrega
  )

  ret_dia_pct = ret_dia * 100 if 0 < ret_dia <= 1 else ret_dia
  ret_mes_pct = ret_mes * 100 if 0 < ret_mes <= 1 else ret_mes

  def aplicar_estilo_grafico(fig, altura=300):
    fig.update_layout(
        height=altura,
        showlegend=False,
        margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(fixedrange=True, title=""),
        yaxis=dict(fixedrange=True, title=""),
        dragmode=False,
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    return fig

  plotly_config = {
      "staticPlot": True,
      "responsive": True,
  }

  # ================= LINHA 1: OPERAÇÃO E PASSIVOS =================
  col_l1_1, col_l1_2 = st.columns(2)

  with col_l1_1:
    st.subheader("📦 Visão Geral de Cargas")
    df_g1 = pd.DataFrame({
        "Indicador": [
            "Cargas do Dia",
            "Cargas em D+1",
            "Pendentes saída",
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
    st.plotly_chart(
        aplicar_estilo_grafico(fig1),
        use_container_width=True,
        config=plotly_config,
    )

  with col_l1_2:
    st.subheader("🚨 Passivos Operacionais")
    df_g2 = pd.DataFrame({
        "Indicador": [
            "Total Passivo",
            "Agendamento",
            "Rota",
            "SMS",
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
    max_passivo = max(tot_passivo, pass_agend, pass_rota, pass_sms, 5) * 1.3
    fig2.update_layout(yaxis_range=[0, max_passivo])

    st.plotly_chart(
        aplicar_estilo_grafico(fig2),
        use_container_width=True,
        config=plotly_config,
    )

  st.markdown("---")

  # ================= LINHA 2: EQUIPES E FROTA =================
  col_l2_1, col_l2_2 = st.columns(2)

  with col_l2_1:
    st.subheader("👥 Gestão de Equipes")
    df_g3 = pd.DataFrame({
        "Indicador": [
            "Equipes Ativas",
            "Equipes Férias",
            "Absenteísmo",
            "Capacidade Eq.",
        ],
        "Quantidade": [eq_ativa, eq_ferias, absenteismo, cap_equipes],
    })
    fig3 = px.bar(
        df_g3,
        x="Indicador",
        y="Quantidade",
        color="Indicador",
        text_auto=True,
        color_discrete_sequence=["#27AE60", "#F39C12", "#C0392B", "#2980B9"],
    )
    st.plotly_chart(
        aplicar_estilo_grafico(fig3),
        use_container_width=True,
        config=plotly_config,
    )

  with col_l2_2:
    st.subheader("🚛 Composição da Frota")
    df_g4 = pd.DataFrame({
        "Veículo": ["Baiado", "Truck", "HR"],
        "Quantidade": [baiado, truck, hr_frota],
    })
    fig4 = px.bar(
        df_g4,
        x="Veículo",
        y="Quantidade",
        color="Veículo",
        text_auto=True,
        color_discrete_sequence=["#16A085", "#2980B9", "#8E44AD"],
    )
    st.plotly_chart(
        aplicar_estilo_grafico(fig4),
        use_container_width=True,
        config=plotly_config,
    )

  st.markdown("---")

  # ================= LINHA 3: ATENDIMENTO, OCUPAÇÃO E RETORNO =================
  col_l3_1, col_l3_2, col_l3_3 = st.columns(3)

  with col_l3_1:
    st.subheader("🎯 Atendimento")
    df_g5 = pd.DataFrame({
        "Indicador": ["Volume (UC)", "Qtd. Clientes"],
        "Valor": [vol_total, qtd_clientes],
        "Texto": [
            f"{vol_total:,.0f}".replace(",", "."),
            f"{qtd_clientes:,.0f}".replace(",", "."),
        ],
    })
    fig5 = px.bar(
        df_g5,
        x="Indicador",
        y="Valor",
        color="Indicador",
        text="Texto",
        color_discrete_sequence=["#2980B9", "#8E44AD"],
    )
    st.plotly_chart(
        aplicar_estilo_grafico(fig5),
        use_container_width=True,
        config=plotly_config,
    )

  with col_l3_2:
    st.subheader("📊 Ocupação (%)")
    df_g6 = pd.DataFrame({
        "Indicador": [
            "Ocup. Caminhões",
            "Ocup. CD",
            "Estudo Entregas",
        ],
        "Valor": [ocup_cam_pct, ocup_cd_pct, estudo_pct],
        "Texto": [
            f"{ocup_cam_pct:.1f}%".replace(".", ","),
            f"{ocup_cd_pct:.1f}%".replace(".", ","),
            f"{estudo_pct:.1f}%".replace(".", ","),
        ],
    })
    fig6 = px.bar(
        df_g6,
        x="Indicador",
        y="Valor",
        color="Indicador",
        text="Texto",
        color_discrete_sequence=["#16A085", "#27AE60", "#F39C12"],
    )
    fig6.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(
        aplicar_estilo_grafico(fig6),
        use_container_width=True,
        config=plotly_config,
    )

  with col_l3_3:
    st.subheader("🔄 Retorno (%)")
    df_g7 = pd.DataFrame({
        "Indicador": ["Retorno Dia", "Retorno Mês"],
        "Valor": [ret_dia_pct, ret_mes_pct],
        "Texto": [
            f"{ret_dia_pct:.2f}%".replace(".", ","),
            f"{ret_mes_pct:.2f}%".replace(".", ","),
        ],
    })
    fig7 = px.bar(
        df_g7,
        x="Indicador",
        y="Valor",
        color="Indicador",
        text="Texto",
        color_discrete_sequence=["#E74C3C", "#C0392B"],
    )
    st.plotly_chart(
        aplicar_estilo_grafico(fig7),
        use_container_width=True,
        config=plotly_config,
    )

except Exception as e:
  st.error(f"Erro ao processar os dados da planilha: {e}")
