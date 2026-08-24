from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Status Operacional Logística", page_icon="🚚", layout="wide"
)

st.title("🚚 Status Operacional de Logística")
st.subheader("Painel Executivo Diário")

excel_file = "61.xlsx"


@st.cache_data(ttl=60)
def obter_lista_abas(file_path):
  xls = pd.ExcelFile(file_path)
  return [s for s in xls.sheet_names if s not in ["Base", "Hoja1"]]


try:
  todas_abas = obter_lista_abas(excel_file)

  # Padrão: Seleciona a última aba com dados preenchidos
  padrao_idx = len(todas_abas) - 1

  st.sidebar.header("⚙️ Configurações")
  data_selecionada = st.sidebar.selectbox(
      "📅 Selecione a Data:", options=todas_abas, index=padrao_idx
  )

  raw_df = pd.read_excel(excel_file, sheet_name=data_selecionada)

  # Mapeamento fixo das colunas conforme a estrutura física da foto da planilha:
  # Coluna 1: BGU | 2: CJU | 3: LST | 4: NIG | 5: FRIG | 6: SPA | 7: CD'S
  unidades_map = {
      "Consolidado Geral (CD'S)": 7,
      "BGU": 1,
      "CJU": 2,
      "LST": 3,
      "NIG": 4,
      "FRIG": 5,
      "SPA": 6,
  }

  unidade_sel = st.selectbox(
      "🎯 Filtrar por Unidade:",
      list(unidades_map.keys()),
      key="filtro_unidades_main",
  )
  col_idx = unidades_map[unidade_sel]

  st.caption(
      f"📊 Exibindo dados da aba: **{data_selecionada}** | Unidade:"
      f" **{unidade_sel}**"
  )
  st.markdown("---")

  # Busca ultra-precisa garantindo que encontra a linha exata independente do espaço/má-formatação
  def get_val_linha(termo_busca):
    for r_idx in range(len(raw_df)):
      linha_texto = (
          " ".join(raw_df.iloc[r_idx, :2].dropna().astype(str))
          .upper()
          .replace(" ", "")
      )
      termo_limpo = termo_busca.upper().replace(" ", "")
      if termo_limpo in linha_texto:
        val = raw_df.iloc[r_idx, col_idx]
        val_num = pd.to_numeric(val, errors="coerce")
        return val_num if pd.notna(val_num) else 0
    return 0

  # LEITURA FIEL DA PLANILHA
  # 1. Visão Geral de Cargas
  cargas_dia = get_val_linha("CARGAS DO DIA")
  cargas_d1 = get_val_linha("CARGAS EM D+1")
  pend_saida = get_val_linha("CARGAS PENDENTES DE SAÍDA")
  recargas_cam = get_val_linha("RECARGAS DE CAMINHÃO")
  recargas_hr = get_val_linha("RECARGAS DE HR")

  # 2. Passivos Operacionais
  pass_agend = get_val_linha("PASSIVO ( AGENDAMENTO )")
  pass_rota = get_val_linha("PASSIVO ( ROTA )")
  pass_sms = get_val_linha("PASSIVO ( SMS )")
  tot_passivo = (
      get_val_linha("TOTAL PASSIVO")
      if get_val_linha("TOTAL PASSIVO") > 0
      else (pass_agend + pass_rota + pass_sms)
  )

  # 3. Gestão de Equipes
  eq_ativa = get_val_linha("EQUIPE ATIVA")
  eq_ferias = get_val_linha("EQUIPE DE FÉRIAS")
  absenteismo = get_val_linha("ABSENTEÍSMO")
  cap_equipes = get_val_linha("CAPACIDADE DE EQUIPES")

  # 4. Composição da Frota
  baiado = get_val_linha("BAIADO")
  truck = get_val_linha("TRUCK")
  hr_frota = get_val_linha("HR")

  # 5. Atendimento
  vol_total = get_val_linha("VOLUME TOTAL")
  qtd_clientes = get_val_linha("QDT CLIENTES")

  # 6. Ocupação & Eficiência
  ocup_cam = get_val_linha("OCUPAÇÃO CAMINHÕES")
  ocup_cd = get_val_linha("OCUPAÇÃO CD")
  estudo_entrega = get_val_linha("ESTUDO DE ENTREGA")

  # 7. Retorno
  ret_dia = get_val_linha("RETORNO DO DIA")
  ret_mes = get_val_linha("RETORNO DO MÊS")

  # Formatação de %
  ocup_cam_pct = ocup_cam * 100 if 0 < ocup_cam <= 1 else ocup_cam
  ocup_cd_pct = ocup_cd * 100 if 0 < ocup_cd <= 1 else ocup_cd
  estudo_pct = (
      estudo_entrega * 100 if 0 < estudo_entrega <= 1 else estudo_entrega
  )

  ret_dia_pct = ret_dia * 100 if 0 < ret_dia <= 1 else ret_dia
  ret_mes_pct = ret_mes * 100 if 0 < ret_mes <= 1 else ret_mes

  def aplicar_estilo(fig, altura=300):
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

  plotly_config = {"staticPlot": True, "responsive": True}

  # ================= LINHA 1 =================
  col1, col2 = st.columns(2)

  with col1:
    st.subheader("📦 Visão Geral de Cargas")
    df1 = pd.DataFrame({
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
        df1,
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
    max_g1 = max(df1["Quantidade"].max(), 5) * 1.25
    fig1.update_layout(yaxis_range=[0, max_g1])
    st.plotly_chart(
        aplicar_estilo(fig1), use_container_width=True, config=plotly_config
    )

  with col2:
    st.subheader("🚨 Passivos Operacionais")
    df2 = pd.DataFrame({
        "Indicador": [
            "Total Passivo",
            "Agendamento",
            "Rota",
            "SMS",
        ],
        "Quantidade": [tot_passivo, pass_agend, pass_rota, pass_sms],
    })
    fig2 = px.bar(
        df2,
        x="Indicador",
        y="Quantidade",
        color="Indicador",
        text_auto=True,
        color_discrete_sequence=["#D35400", "#F39C12", "#E74C3C", "#2980B9"],
    )
    max_g2 = max(df2["Quantidade"].max(), 5) * 1.25
    fig2.update_layout(yaxis_range=[0, max_g2])
    st.plotly_chart(
        aplicar_estilo(fig2), use_container_width=True, config=plotly_config
    )

  st.markdown("---")

  # ================= LINHA 2 =================
  col3, col4 = st.columns(2)

  with col3:
    st.subheader("👥 Gestão de Equipes")
    df3 = pd.DataFrame({
        "Indicador": [
            "Equipes Ativas",
            "Equipes Férias",
            "Absenteísmo",
            "Capacidade Eq.",
        ],
        "Quantidade": [eq_ativa, eq_ferias, absenteismo, cap_equipes],
    })
    fig3 = px.bar(
        df3,
        x="Indicador",
        y="Quantidade",
        color="Indicador",
        text_auto=True,
        color_discrete_sequence=["#27AE60", "#F39C12", "#C0392B", "#2980B9"],
    )
    max_g3 = max(df3["Quantidade"].max(), 5) * 1.25
    fig3.update_layout(yaxis_range=[0, max_g3])
    st.plotly_chart(
        aplicar_estilo(fig3), use_container_width=True, config=plotly_config
    )

  with col4:
    st.subheader("🚛 Composição da Frota")
    df4 = pd.DataFrame({
        "Veículo": ["Baiado", "Truck", "HR"],
        "Quantidade": [baiado, truck, hr_frota],
    })
    fig4 = px.bar(
        df4,
        x="Veículo",
        y="Quantidade",
        color="Veículo",
        text_auto=True,
        color_discrete_sequence=["#16A085", "#2980B9", "#8E44AD"],
    )
    max_g4 = max(df4["Quantidade"].max(), 5) * 1.25
    fig4.update_layout(yaxis_range=[0, max_g4])
    st.plotly_chart(
        aplicar_estilo(fig4), use_container_width=True, config=plotly_config
    )

  st.markdown("---")

  # ================= LINHA 3 =================
  col5, col6, col7 = st.columns(3)

  with col5:
    st.subheader("🎯 Atendimento")
    df5 = pd.DataFrame({
        "Indicador": ["Volume (UC)", "Qtd. Clientes"],
        "Valor": [vol_total, qtd_clientes],
        "Texto": [f"{vol_total:,.0f}".replace(",", "."), f"{qtd_clientes:,.0f}"],
    })
    fig5 = px.bar(
        df5,
        x="Indicador",
        y="Valor",
        color="Indicador",
        text="Texto",
        color_discrete_sequence=["#2980B9", "#8E44AD"],
    )
    max_g5 = max(df5["Valor"].max(), 5) * 1.25
    fig5.update_layout(yaxis_range=[0, max_g5])
    st.plotly_chart(
        aplicar_estilo(fig5), use_container_width=True, config=plotly_config
    )

  with col6:
    st.subheader("📊 Ocupação (%)")
    df6 = pd.DataFrame({
        "Indicador": [
            "Ocup. Caminhões",
            "Ocup. CD",
            "Estudo Entregas",
        ],
        "Valor": [ocup_cam_pct, ocup_cd_pct, estudo_pct],
        "Texto": [
            f"{ocup_cam_pct:.1f}%",
            f"{ocup_cd_pct:.1f}%",
            f"{estudo_pct:.1f}%",
        ],
    })
    fig6 = px.bar(
        df6,
        x="Indicador",
        y="Valor",
        color="Indicador",
        text="Texto",
        color_discrete_sequence=["#16A085", "#27AE60", "#F39C12"],
    )
    fig6.update_layout(yaxis_range=[0, 115])
    st.plotly_chart(
        aplicar_estilo(fig6), use_container_width=True, config=plotly_config
    )

  with col7:
    st.subheader("🔄 Retorno (%)")
    df7 = pd.DataFrame({
        "Indicador": ["Retorno Dia", "Retorno Mês"],
        "Valor": [ret_dia_pct, ret_mes_pct],
        "Texto": [f"{ret_dia_pct:.2f}%", f"{ret_mes_pct:.2f}%"],
    })
    fig7 = px.bar(
        df7,
        x="Indicador",
        y="Valor",
        color="Indicador",
        text="Texto",
        color_discrete_sequence=["#E74C3C", "#C0392B"],
    )
    max_ret = max(df7["Valor"].max(), 1.0) * 1.3
    fig7.update_layout(yaxis_range=[0, max_ret])
    st.plotly_chart(
        aplicar_estilo(fig7), use_container_width=True, config=plotly_config
    )

except Exception as e:
  st.error(f"Erro ao processar os dados da planilha: {e}")
    
