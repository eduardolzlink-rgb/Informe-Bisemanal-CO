import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuración de la página web
st.set_page_config(
    page_title="Dashboard Master - Plan de Reprogramación",
    page_icon="📊",
    layout="wide",
)

# Inicializar el estado de la página si no existe
if "pagina" not in st.session_state:
  st.session_state.pagina = "dashboard_completo"

# Variable global para el límite de las líneas Real y Desviación
limit_real_desv = pd.to_datetime("2026-06-29")


@st.cache_data
def load_all_data():
  file_path = "Plan Master Reprogramación V2 - Fin Diciembre 2025.xlsx"
  df_dash = pd.read_excel(file_path, sheet_name="Dashboard Completo", header=None)
  df_py = pd.read_excel(file_path, sheet_name="Python", header=None)
  df_gen = pd.read_excel(
      file_path, sheet_name="Dashboard General", header=None
  )
  df_cal = pd.read_excel(file_path, sheet_name="Dashboard Caldera", header=None)
  df_turb = pd.read_excel(file_path, sheet_name="Dashboard Turbina", header=None)
  df_desv = pd.read_excel(
      file_path, sheet_name="Análisis de Desviación", header=None
  )
  return df_dash, df_py, df_gen, df_cal, df_turb, df_desv


df_dash, df_py, df_gen, df_cal, df_turb, df_desv = load_all_data()


def get_metric_value(df, row_idx, col_idx, default_val):
  try:
    val = df.iloc[row_idx, col_idx]
    return float(val) if pd.notna(val) else default_val
  except Exception:
    return default_val


def get_status_icon(desv_val):
  p = desv_val * 100 if abs(desv_val) <= 1 else desv_val
  if p >= -3.0:
    return "🟢"
  elif -10.0 <= p < -3.0:
    return "🟡"
  else:
    return "🔴"


def filter_repeated_100(vals, dates):
  text_list = []
  for v, d_str in zip(vals, dates):
    if v is not None and not pd.isna(v):
      p_val = round(v * 100, 1)
      if p_val >= 100.0:
        if d_str == dates[-1]:
          text_list.append(f"{v:.1%}")
        else:
          text_list.append("")
      else:
        text_list.append(f"{v:.1%}")
    else:
      text_list.append("")
  return text_list


def create_gauge(target_value, title_text):
  """Crea un gráfico indicador (gauge) estático y rápido"""
  fig = go.Figure(
      go.Indicator(
          mode="gauge+number",
          value=target_value,
          number={"suffix": "%", "font": {"size": 42, "color": "#2c3e50"}},
          title={"text": title_text, "font": {"size": 16}},
          gauge={
              "axis": {"range": [0, 100], "tickwidth": 1},
              "bar": {"color": "#2980b9"},
              "steps": [
                  {"range": [0, 70], "color": "#f2f4f4"},
                  {"range": [70, 90], "color": "#fcf3cf"},
                  {"range": [90, 100], "color": "#d4efdf"},
              ],
          },
      )
  )
  fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=10))
  return fig


# ==========================================
# PÁGINA 1: DASHBOARD COMPLETO (ORIGINAL)
# ==========================================
if st.session_state.pagina == "dashboard_completo":
  st.title("📊 Plan Master de Reprogramación - Dashboard Completo")
  st.markdown(
      "Visualización web interactiva basada en los datos de la hoja 'Python' del"
      " archivo Excel."
  )

  avance_real_val = get_metric_value(df_dash, 11, 14, 0.8635)
  desviacion_val = get_metric_value(df_dash, 13, 14, -0.1365)
  aporte_val = get_metric_value(df_dash, 14, 14, -0.1365)
  avance_periodo_val = get_metric_value(df_dash, 15, 14, 0.0013)

  raw_dates_vals = df_py.iloc[1, 1:].values
  plan_og_raw = df_py.iloc[2, 1:].values
  reprog_raw = df_py.iloc[3, 1:].values
  real_raw = df_py.iloc[4, 1:].values
  desv_raw = df_py.iloc[5, 1:].values

  fechas_all, plan_original, reprogramacion, real, desviacion = [], [], [], [], []

  for i, d_val in enumerate(raw_dates_vals):
    if pd.notna(d_val):
      d_str = (
          d_val.strftime("%d/%m/%Y")
          if hasattr(d_val, "strftime")
          else str(d_val).strip()
      )
      fechas_all.append(d_str)
      plan_original.append(plan_og_raw[i] if pd.notna(plan_og_raw[i]) else None)
      reprogramacion.append(reprog_raw[i] if pd.notna(reprog_raw[i]) else None)
      real.append(real_raw[i] if pd.notna(real_raw[i]) else None)
      desviacion.append(desv_raw[i] if pd.notna(desv_raw[i]) else None)

  fechas_real_desv, real_f, desv_f = [], [], []
  for d_str, r, dv in zip(fechas_all, real, desviacion):
    dt = pd.to_datetime(d_str, format="%d/%m/%Y", errors="coerce")
    if pd.notna(dt) and dt <= limit_real_desv:
      fechas_real_desv.append(d_str)
      real_f.append(r)
      desv_f.append(dv)

  plan_og_text = filter_repeated_100(plan_original, fechas_all)
  reprog_text = filter_repeated_100(reprogramacion, fechas_all)
  real_text = [
      f"{v:.1%}" if v is not None and not pd.isna(v) else "" for v in real_f
  ]
  desv_text = [
      f"{v:.1%}" if v is not None and not pd.isna(v) and round(v * 100, 1) != 0.0 else ""
      for v in desv_f
  ]

  st.subheader("📈 Avance Global: Plan Original vs Real vs Reprogramación")
  fig_lines = go.Figure()
  fig_lines.add_trace(
      go.Scatter(
          x=fechas_all,
          y=plan_original,
          mode="lines+markers+text",
          name="Plan Original",
          line=dict(color="#f1c40f", width=2, shape="spline"),
          text=plan_og_text,
          textposition="top center",
          textfont=dict(size=10, color="#f1c40f"),
      )
  )
  fig_lines.add_trace(
      go.Scatter(
          x=fechas_all,
          y=reprogramacion,
          mode="lines+markers+text",
          name="Reprogramación",
          line=dict(color="#7f8c8d", width=2, shape="spline"),
          text=reprog_text,
          textposition="top center",
          textfont=dict(size=10, color="#7f8c8d"),
      )
  )
  fig_lines.add_trace(
      go.Scatter(
          x=fechas_real_desv,
          y=real_f,
          mode="lines+markers+text",
          name="Real",
          line=dict(color="#2980b9", width=3, shape="spline"),
          text=real_text,
          textposition="top center",
          textfont=dict(size=10, color="#2980b9"),
      )
  )
  fig_lines.add_trace(
      go.Scatter(
          x=fechas_real_desv,
          y=desv_f,
          mode="lines+markers+text",
          name="Desviación",
          line=dict(color="#27ae60", width=2, shape="spline"),
          text=desv_text,
          textposition="bottom center",
          textfont=dict(size=10, color="#27ae60"),
      )
  )
  fig_lines.update_layout(
      xaxis=dict(
          showgrid=True,
          gridwidth=1,
          gridcolor="#bdc3c7",
          griddash="dot",
          tickangle=-45,
      ),
      yaxis=dict(showgrid=False, title="Porcentaje de Avance", tickformat=".0%"),
      legend=dict(
          orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
      ),
      margin=dict(l=20, r=20, t=30, b=20),
      height=520,
  )
  st.plotly_chart(fig_lines, use_container_width=True)
  st.divider()

  col_izq, col_der = st.columns([1.2, 1])
  with col_izq:
    st.subheader("🎯 Resumen de Desviación Global")
    fig_gauge = create_gauge(
        avance_real_val * 100, "Avance Real vs Meta (Reprogramación)"
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    icon_desv_global = get_status_icon(desviacion_val)
    st.markdown(
        f"""
        * **Desviación:** {icon_desv_global} <span style='color:red; font-weight:bold;'>{desviacion_val:.1%}</span>
        * **Aporte:** <span style='color:red; font-weight:bold;'>{aporte_val:.2%}</span>
        * **Avance Período:** **{avance_periodo_val:.2%}**
        """,
        unsafe_allow_html=True,
    )

  with col_der:
    st.subheader("⚙️ Desglose por Componente")
    caldera_plan_str = "100,00 %"
    caldera_real_str = "91,08 %"
    caldera_desv_val = -0.0892
    icon_caldera = get_status_icon(caldera_desv_val)

    turbina_plan_str = "100,00 %"
    turbina_real_str = "71,70 %"
    turbina_desv_val = -0.2830
    icon_turbina = get_status_icon(turbina_desv_val)

    st.markdown(
        f"""
        <div style="background-color: #d4ac0d; padding: 10px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center;">
            Mantenimiento del Generador de Vapor (Caldera) y Equipos Auxiliares
        </div>
        <div style="background-color: #f8f9f9; padding: 15px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px;">
            <b>Planificado:</b> {caldera_plan_str} <br>
            <b>Real:</b> {caldera_real_str} <br>
            <b>Desviación:</b> {icon_caldera} -8,92%
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="background-color: #d4ac0d; padding: 10px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center;">
            Mantenimiento del Turbo Generador y Equipos Auxiliares
        </div>
        <div style="background-color: #f8f9f9; padding: 15px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd;">
            <b>Planificado:</b> {turbina_plan_str} <br>
            <b>Real:</b> {turbina_real_str} <br>
            <b>Desviación:</b> {icon_turbina} -28,30%
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.divider()
  col_btn1, col_btn2 = st.columns([1, 5])
  with col_btn1:
    if st.button("Página Siguiente ➡️", type="primary"):
      st.session_state.pagina = "dashboard_general"
      st.rerun()


# ==========================================
# PÁGINA 2: DASHBOARD GENERAL
# ==========================================
elif st.session_state.pagina == "dashboard_general":
  st.title("📊 Dashboard General (Bisemanal)")
  st.markdown(
      "Visualización basada en los datos consolidados de la hoja 'Dashboard"
      " General'."
  )

  gen_avance_real = get_metric_value(df_gen, 3, 2, 0.7840)
  gen_desviacion = get_metric_value(df_gen, 13, 1, -0.2160)
  gen_aporte = get_metric_value(df_gen, 14, 1, -0.2160)
  gen_avance_periodo = get_metric_value(df_gen, 15, 1, 0.0029)

  raw_dates_gen_vals = df_py.iloc[8, 1:].values
  plan_gen_raw = df_py.iloc[9, 1:].values
  real_gen_raw = df_py.iloc[10, 1:].values
  desv_gen_raw = df_py.iloc[11, 1:].values

  gen_fechas_all, gen_plan, gen_real_all, gen_desv_all = [], [], [], []
  for i, d_val in enumerate(raw_dates_gen_vals):
    if pd.notna(d_val):
      d_str = (
          d_val.strftime("%d/%m/%Y")
          if hasattr(d_val, "strftime")
          else str(d_val).strip()
      )
      gen_fechas_all.append(d_str)
      gen_plan.append(
          plan_gen_raw[i] if i < len(plan_gen_raw) and pd.notna(plan_gen_raw[i]) else 0
      )
      gen_real_all.append(
          real_gen_raw[i] if i < len(real_gen_raw) and pd.notna(real_gen_raw[i]) else 0
      )
      gen_desv_all.append(
          desv_gen_raw[i] if i < len(desv_gen_raw) and pd.notna(desv_gen_raw[i]) else 0
      )

  gen_fechas_real_desv, gen_real_f, gen_desv_f = [], [], []
  for d_str, r, dv in zip(gen_fechas_all, gen_real_all, gen_desv_all):
    dt = pd.to_datetime(d_str, format="%d/%m/%Y", errors="coerce")
    if pd.notna(dt) and dt <= limit_real_desv:
      gen_fechas_real_desv.append(d_str)
      gen_real_f.append(r)
      gen_desv_f.append(dv)

  txt_plan_gen = filter_repeated_100(gen_plan, gen_fechas_all)
  txt_real_gen = [
      f"{v:.1%}" if v is not None and not pd.isna(v) else "" for v in gen_real_f
  ]
  txt_desv_gen = [
      f"{v:.1%}" if v is not None and not pd.isna(v) and round(v * 100, 1) != 0.0 else ""
      for v in gen_desv_f
  ]

  st.subheader("📈 Avance Bisemanal (Plan vs Real vs Desviación)")
  fig_lines_gen = go.Figure()
  fig_lines_gen.add_trace(
      go.Scatter(
          x=gen_fechas_all,
          y=gen_plan,
          mode="lines+markers+text",
          name="Plan",
          line=dict(color="#7f8c8d", width=2, shape="spline"),
          text=txt_plan_gen,
          textposition="top center",
          textfont=dict(size=10, color="#7f8c8d"),
      )
  )
  fig_lines_gen.add_trace(
      go.Scatter(
          x=gen_fechas_real_desv,
          y=gen_real_f,
          mode="lines+markers+text",
          name="Real",
          line=dict(color="#2980b9", width=3, shape="spline"),
          text=txt_real_gen,
          textposition="top center",
          textfont=dict(size=10, color="#2980b9"),
      )
  )
  fig_lines_gen.add_trace(
      go.Scatter(
          x=gen_fechas_real_desv,
          y=gen_desv_f,
          mode="lines+markers+text",
          name="Desviación",
          line=dict(color="#27ae60", width=2, shape="spline"),
          text=txt_desv_gen,
          textposition="bottom center",
          textfont=dict(size=10, color="#27ae60"),
      )
  )
  fig_lines_gen.update_layout(
      xaxis=dict(
          showgrid=True,
          gridwidth=1,
          gridcolor="#bdc3c7",
          griddash="dot",
          tickangle=-45,
      ),
      yaxis=dict(showgrid=False, title="Porcentaje de Avance", tickformat=".0%"),
      legend=dict(
          orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
      ),
      margin=dict(l=20, r=20, t=30, b=20),
      height=520,
  )
  st.plotly_chart(fig_lines_gen, use_container_width=True)
  st.divider()

  col_gen_left, col_gen_right = st.columns([1.2, 1])
  with col_gen_left:
    st.subheader("🎯 Resumen General de Avance")
    fig_gauge_gen = create_gauge(
        gen_avance_real * 100, "Avance Real vs Plan (Dashboard General)"
    )
    st.plotly_chart(fig_gauge_gen, use_container_width=True)

    icon_gen_desv = get_status_icon(gen_desviacion)
    st.markdown(
        f"""
        * **Desviación:** {icon_gen_desv} <span style='color:red; font-weight:bold;'>{gen_desviacion:.2%}</span>
        * **Aporte:** <span style='color:red; font-weight:bold;'>{gen_aporte:.2%}</span>
        * **Avance Período:** **{gen_avance_periodo:.2%}**
        """,
        unsafe_allow_html=True,
    )

  with col_gen_right:
    st.subheader("⚙️ Desglose por Componente (General)")
    caldera_plan_g = get_metric_value(df_gen, 21, 1, 1.0)
    caldera_real_g = get_metric_value(df_gen, 22, 1, 0.8379)
    caldera_desv_g = get_metric_value(df_gen, 23, 1, -0.1621)
    icon_caldera_g = get_status_icon(caldera_desv_g)

    turbina_plan_g = get_metric_value(df_gen, 21, 3, 1.0)
    turbina_real_g = get_metric_value(df_gen, 22, 3, 0.6006)
    turbina_desv_g = get_metric_value(df_gen, 23, 3, -0.3994)
    icon_turbina_g = get_status_icon(turbina_desv_g)

    st.markdown(
        f"""
        <div style="background-color: #d4ac0d; padding: 10px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center;">
            Mantenimiento del Generador de Vapor (Caldera) y Equipos Auxiliares
        </div>
        <div style="background-color: #f8f9f9; padding: 15px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px;">
            <b>Planificado:</b> {caldera_plan_g:.2%} <br>
            <b>Real:</b> {caldera_real_g:.2%} <br>
            <b>Desviación:</b> {icon_caldera_g} {caldera_desv_g:.2%}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="background-color: #d4ac0d; padding: 10px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center;">
            Mantenimiento del Turbo Generador y Equipos Auxiliares
        </div>
        <div style="background-color: #f8f9f9; padding: 15px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd;">
            <b>Planificado:</b> {turbina_plan_g:.2%} <br>
            <b>Real:</b> {turbina_real_g:.2%} <br>
            <b>Desviación:</b> {icon_turbina_g} {turbina_desv_g:.2%}
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.divider()
  col_btn1, col_btn2 = st.columns([1, 5])
  with col_btn1:
    if st.button("⬅️ Página Anterior", type="secondary"):
      st.session_state.pagina = "dashboard_completo"
      st.rerun()
  with col_btn2:
    if st.button("Página Siguiente ➡️", type="primary", key="btn_next_gen"):
      st.session_state.pagina = "dashboard_caldera"
      st.rerun()


# ==========================================
# PÁGINA 3: DASHBOARD CALDERA
# ==========================================
elif st.session_state.pagina == "dashboard_caldera":
  st.title("📊 Dashboard Caldera (Bisemanal)")
  st.markdown(
      "Visualización basada en los datos consolidados de la hoja 'Python'"
      " (Dashboard Caldera Bisemanal)."
  )

  caldera_avance_real = 0.838
  caldera_desviacion = -0.162
  caldera_aporte = -0.1253
  caldera_avance_periodo = 0.0030

  raw_dates_cal_vals = df_py.iloc[14, 1:].values
  plan_cal_raw = df_py.iloc[15, 1:].values
  real_cal_raw = df_py.iloc[16, 1:].values
  desv_cal_raw = df_py.iloc[17, 1:].values

  cal_fechas_all, cal_plan, cal_real_all, cal_desv_all = [], [], [], []
  for i, d_val in enumerate(raw_dates_cal_vals):
    if pd.notna(d_val):
      d_str = (
          d_val.strftime("%d/%m/%Y")
          if hasattr(d_val, "strftime")
          else str(d_val).strip()
      )
      cal_fechas_all.append(d_str)
      cal_plan.append(
          plan_cal_raw[i] if i < len(plan_cal_raw) and pd.notna(plan_cal_raw[i]) else 0
      )
      cal_real_all.append(
          real_cal_raw[i] if i < len(real_cal_raw) and pd.notna(real_cal_raw[i]) else 0
      )
      cal_desv_all.append(
          desv_cal_raw[i] if i < len(desv_cal_raw) and pd.notna(desv_cal_raw[i]) else 0
      )

  cal_fechas_real_desv, cal_real_f, cal_desv_f = [], [], []
  for d_str, r, dv in zip(cal_fechas_all, cal_real_all, cal_desv_all):
    dt = pd.to_datetime(d_str, format="%d/%m/%Y", errors="coerce")
    if pd.notna(dt) and dt <= limit_real_desv:
      cal_fechas_real_desv.append(d_str)
      cal_real_f.append(r)
      cal_desv_f.append(dv)

  txt_plan_cal = filter_repeated_100(cal_plan, cal_fechas_all)
  txt_real_cal = [
      f"{v:.1%}" if v is not None and not pd.isna(v) else "" for v in cal_real_f
  ]
  txt_desv_cal = [
      f"{v:.1%}" if v is not None and not pd.isna(v) and round(v * 100, 1) != 0.0 else ""
      for v in cal_desv_f
  ]

  st.subheader("📈 Avance Bisemanal (Plan vs Real vs Desviación - Caldera)")
  fig_lines_cal = go.Figure()
  fig_lines_cal.add_trace(
      go.Scatter(
          x=cal_fechas_all,
          y=cal_plan,
          mode="lines+markers+text",
          name="Plan",
          line=dict(color="#7f8c8d", width=2, shape="spline"),
          text=txt_plan_cal,
          textposition="top center",
          textfont=dict(size=10, color="#7f8c8d"),
      )
  )
  fig_lines_cal.add_trace(
      go.Scatter(
          x=cal_fechas_real_desv,
          y=cal_real_f,
          mode="lines+markers+text",
          name="Real",
          line=dict(color="#2980b9", width=3, shape="spline"),
          text=txt_real_cal,
          textposition="top center",
          textfont=dict(size=10, color="#2980b9"),
      )
  )
  fig_lines_cal.add_trace(
      go.Scatter(
          x=cal_fechas_real_desv,
          y=cal_desv_f,
          mode="lines+markers+text",
          name="Desviación",
          line=dict(color="#27ae60", width=2, shape="spline"),
          text=txt_desv_cal,
          textposition="bottom center",
          textfont=dict(size=10, color="#27ae60"),
      )
  )
  fig_lines_cal.update_layout(
      xaxis=dict(
          showgrid=True,
          gridwidth=1,
          gridcolor="#bdc3c7",
          griddash="dot",
          tickangle=-45,
      ),
      yaxis=dict(showgrid=False, title="Porcentaje de Avance", tickformat=".0%"),
      legend=dict(
          orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
      ),
      margin=dict(l=20, r=20, t=30, b=20),
      height=520,
  )
  st.plotly_chart(fig_lines_cal, use_container_width=True)
  st.divider()

  st.subheader("🎯 Resumen Caldera de Avance")
  fig_gauge_cal = create_gauge(
      caldera_avance_real * 100, "Avance Real vs Plan (Dashboard Caldera)"
  )
  st.plotly_chart(fig_gauge_cal, use_container_width=True)

  icon_cal_desv = get_status_icon(caldera_desviacion)
  st.markdown(
      f"""
      * **Desviación:** {icon_cal_desv} <span style='color:red; font-weight:bold;'>{caldera_desviacion:.1%}</span>
      * **Aporte:** <span style='color:red; font-weight:bold;'>{caldera_aporte:.2%}</span>
      * **Avance Período:** **{caldera_avance_periodo:.2%}**
      """,
      unsafe_allow_html=True,
  )
  st.divider()

  st.subheader("📋 Detalle de Subcomponentes de Caldera (1.1 - 1.10)")
  r1_c1, r1_c2, r1_c3 = st.columns(3)
  with r1_c1:
    st.markdown(
        """<div style="background-color: #d4ac0d; padding: 8px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 13px;">1.1 Reparación expansiones metálicas</div><div style="background-color: #f8f9f9; padding: 12px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 13px;"><b>Planificado:</b> 100,00%<br><b>Real:</b> 90,86%<br><b>Desviación:</b> 🟡 -9,14%<br><b>Aporte:</b> -1,60%</div>""",
        unsafe_allow_html=True,
    )
  with r1_c2:
    st.markdown(
        """<div style="background-color: #d4ac0d; padding: 8px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 13px;">1.2 Reemplazo de tubos de gas</div><div style="background-color: #f8f9f9; padding: 12px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 13px;"><b>Planificado:</b> 100,00%<br><b>Real:</b> 100,00%<br><b>Desviación:</b> 🟢 0,00%<br><b>Aporte:</b> 0,00%</div>""",
        unsafe_allow_html=True,
    )
  with r1_c3:
    st.markdown(
        """<div style="background-color: #d4ac0d; padding: 8px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 13px;">1.3 Reparación envoltura metálica</div><div style="background-color: #f8f9f9; padding: 12px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 13px;"><b>Planificado:</b> 100,00%<br><b>Real:</b> 84,00%<br><b>Desviación:</b> 🔴 -16,00%<br><b>Aporte:</b> -1,72%</div>""",
        unsafe_allow_html=True,
    )

  r2_c1, r2_c2, r2_c3 = st.columns(3)
  with r2_c1:
    st.markdown(
        """<div style="background-color: #d4ac0d; padding: 8px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 13px;">1.4 Reparación cámaras muertas</div><div style="background-color: #f8f9f9; padding: 12px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 13px;"><b>Planificado:</b> 100,00%<br><b>Real:</b> 90,80%<br><b>Desviación:</b> 🟡 -9,20%<br><b>Aporte:</b> -0,56%</div>""",
        unsafe_allow_html=True,
    )
  with r2_c2:
    st.markdown(
        """<div style="background-color: #d4ac0d; padding: 8px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 13px;">1.5 Reparación ductos aire/gas</div><div style="background-color: #f8f9f9; padding: 12px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 13px;"><b>Planificado:</b> 100,00%<br><b>Real:</b> 100,00%<br><b>Desviación:</b> 🟢 0,00%<br><b>Aporte:</b> 0,00%</div>""",
        unsafe_allow_html=True,
    )
  with r2_c3:
    st.markdown(
        """<div style="background-color: #d4ac0d; padding: 8px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 13px;">1.6 Reemplazo tuberías ácido/soda</div><div style="background-color: #f8f9f9; padding: 12px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 13px;"><b>Planificado:</b> 100,00%<br><b>Real:</b> 0,00%<br><b>Desviación:</b> 🔴 -100,00%<br><b>Aporte:</b> -4,39%</div>""",
        unsafe_allow_html=True,
    )

  r3_c1, r3_c2, r3_c3 = st.columns(3)
  with r3_c1:
    st.markdown(
        """<div style="background-color: #d4ac0d; padding: 8px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 13px;">1.7 Mantenimiento balance BOP</div><div style="background-color: #f8f9f9; padding: 12px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 13px;"><b>Planificado:</b> 100,00%<br><b>Real:</b> 4,99%<br><b>Desviación:</b> 🔴 -95,01%<br><b>Aporte:</b> -4,17%</div>""",
        unsafe_allow_html=True,
    )
  with r3_c2:
    st.markdown(
        """<div style="background-color: #d4ac0d; padding: 8px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 13px;">1.9 Mantenimiento instrumentación</div><div style="background-color: #f8f9f9; padding: 12px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 13px;"><b>Planificado:</b> 100,00%<br><b>Real:</b> 98,78%<br><b>Desviación:</b> 🟢 -1,22%<br><b>Aporte:</b> -0,10%</div>""",
        unsafe_allow_html=True,
    )
  with r3_c3:
    st.markdown(
        """<div style="background-color: #d4ac0d; padding: 8px; border-radius: 5px 5px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 13px;">1.10 Compresores de aire</div><div style="background-color: #f8f9f9; padding: 12px; border-radius: 0px 0px 5px 5px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 13px;"><b>Planificado:</b> 100,00%<br><b>Real:</b> 100,00%<br><b>Desviación:</b> 🟢 0,00%<br><b>Aporte:</b> 0,00%</div>""",
        unsafe_allow_html=True,
    )

  st.divider()
  col_b1, col_b2 = st.columns([1, 5])
  with col_b1:
    if st.button("⬅️ Página Anterior", type="secondary"):
      st.session_state.pagina = "dashboard_general"
      st.rerun()
  with col_b2:
    if st.button("Página Siguiente (Turbina) ➡️", type="primary"):
      st.session_state.pagina = "dashboard_turbina"
      st.rerun()


# ==========================================
# PÁGINA 4: DASHBOARD TURBINA
# ==========================================
elif st.session_state.pagina == "dashboard_turbina":
  st.title("📊 Dashboard Turbina (Bisemanal)")
  st.markdown(
      "Visualización basada en los datos consolidados de la hoja 'Python'"
      " (Dashboard Turbina Bisemanal)."
  )

  turbina_avance_real = 0.6006
  turbina_desviacion = -0.3994
  turbina_aporte = -0.0907
  turbina_avance_periodo = 0.0025

  raw_dates_turb_vals = df_py.iloc[20, 1:].values if df_py.shape[0] > 20 else []
  plan_turb_raw = df_py.iloc[21, 1:].values if df_py.shape[0] > 21 else []
  real_turb_raw = df_py.iloc[22, 1:].values if df_py.shape[0] > 22 else []
  desv_turb_raw = df_py.iloc[23, 1:].values if df_py.shape[0] > 23 else []

  turb_fechas_all, turb_plan, turb_real_all, turb_desv_all = [], [], [], []
  for i, d_val in enumerate(raw_dates_turb_vals):
    if pd.notna(d_val):
      d_str = (
          d_val.strftime("%d/%m/%Y")
          if hasattr(d_val, "strftime")
          else str(d_val).strip()
      )
      turb_fechas_all.append(d_str)
      turb_plan.append(
          plan_turb_raw[i]
          if i < len(plan_turb_raw) and pd.notna(plan_turb_raw[i])
          else 0
      )
      turb_real_all.append(
          real_turb_raw[i]
          if i < len(real_turb_raw) and pd.notna(real_turb_raw[i])
          else 0
      )
      turb_desv_all.append(
          desv_turb_raw[i]
          if i < len(desv_turb_raw) and pd.notna(desv_turb_raw[i])
          else 0
      )

  turb_fechas_real_desv, turb_real_f, turb_desv_f = [], [], []
  for d_str, r, dv in zip(turb_fechas_all, turb_real_all, turb_desv_all):
    dt = pd.to_datetime(d_str, format="%d/%m/%Y", errors="coerce")
    if pd.notna(dt) and dt <= limit_real_desv:
      turb_fechas_real_desv.append(d_str)
      turb_real_f.append(r)
      turb_desv_f.append(dv)

  txt_plan_turb = filter_repeated_100(turb_plan, turb_fechas_all)
  txt_real_turb = [
      f"{v:.1%}" if v is not None and not pd.isna(v) else "" for v in turb_real_f
  ]
  txt_desv_turb = [
      f"{v:.1%}" if v is not None and not pd.isna(v) and round(v * 100, 1) != 0.0 else ""
      for v in turb_desv_f
  ]

  st.subheader("📈 Avance Bisemanal (Plan vs Real vs Desviación - Turbina)")
  fig_lines_turb = go.Figure()
  fig_lines_turb.add_trace(
      go.Scatter(
          x=turb_fechas_all,
          y=turb_plan,
          mode="lines+markers+text",
          name="Plan",
          line=dict(color="#7f8c8d", width=2, shape="spline"),
          text=txt_plan_turb,
          textposition="top center",
          textfont=dict(size=10, color="#7f8c8d"),
      )
  )
  fig_lines_turb.add_trace(
      go.Scatter(
          x=turb_fechas_real_desv,
          y=turb_real_f,
          mode="lines+markers+text",
          name="Real",
          line=dict(color="#2980b9", width=3, shape="spline"),
          text=txt_real_turb,
          textposition="top center",
          textfont=dict(size=10, color="#2980b9"),
      )
  )
  fig_lines_turb.add_trace(
      go.Scatter(
          x=turb_fechas_real_desv,
          y=turb_desv_f,
          mode="lines+markers+text",
          name="Desviación",
          line=dict(color="#27ae60", width=2, shape="spline"),
          text=txt_desv_turb,
          textposition="bottom center",
          textfont=dict(size=10, color="#27ae60"),
      )
  )
  fig_lines_turb.update_layout(
      xaxis=dict(
          showgrid=True,
          gridwidth=1,
          gridcolor="#bdc3c7",
          griddash="dot",
          tickangle=-45,
      ),
      yaxis=dict(showgrid=False, title="Porcentaje de Avance", tickformat=".0%"),
      legend=dict(
          orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
      ),
      margin=dict(l=20, r=20, t=30, b=20),
      height=520,
  )
  st.plotly_chart(fig_lines_turb, use_container_width=True)
  st.divider()

  st.subheader("🎯 Resumen Turbina de Avance")
  fig_gauge_turb = create_gauge(
      turbina_avance_real * 100, "Avance Real vs Plan (Dashboard Turbina)"
  )
  st.plotly_chart(fig_gauge_turb, use_container_width=True)

  icon_turb_desv = get_status_icon(turbina_desviacion)
  st.markdown(
      f"""
      * **Desviación:** {icon_turb_desv} <span style='color:red; font-weight:bold;'>{turbina_desviacion:.2%}</span>
      * **Aporte:** <span style='color:red; font-weight:bold;'>{turbina_aporte:.2%}</span>
      * **Avance Período:** **{turbina_avance_periodo:.2%}**
      """,
      unsafe_allow_html=True,
  )
  st.divider()

  st.subheader("📋 Detalle de Subcomponentes de Turbina (0.0 - 2.16)")
  tarjetas_turbina = [
      (
          "0.0 Actividades preliminares",
          "100,00%",
          "60,06%",
          "🔴 -39,94%",
          "0,00%",
      ),
      (
          "2.4 Reparación de componentes",
          "100,00%",
          "91,46%",
          "🟡 -8,54%",
          "-0,35%",
      ),
      (
          "2.6 Pruebas ensayos no destructivos",
          "100,00%",
          "100,00%",
          "🟢 0,00%",
          "0,00%",
      ),
      (
          "2.7 Alineación de la turbina",
          "100,00%",
          "0,00%",
          "🔴 -100,00%",
          "-1,15%",
      ),
      (
          "2.9 Limpieza sistema lubricación",
          "100,00%",
          "100,00%",
          "🟢 0,00%",
          "0,00%",
      ),
      ("2.10 Aislamiento térmico", "100,00%", "100,00%", "🟢 0,00%", "0,00%"),
      (
          "2.11 Inspección eléctrica generador",
          "100,00%",
          "100,00%",
          "🟢 0,00%",
          "0,00%",
      ),
      (
          "2.12 Preparación superficie metálica",
          "100,00%",
          "0,00%",
          "🔴 -100,00%",
          "-1,33%",
      ),
      (
          "2.13 Mantenimiento válvulas principales",
          "100,00%",
          "100,00%",
          "🟢 0,00%",
          "0,00%",
      ),
      (
          "2.14 Mantenimiento equipos auxiliares",
          "100,00%",
          "100,00%",
          "🟢 0,00%",
          "0,00%",
      ),
      (
          "2.15 Desarmado de componentes",
          "100,00%",
          "100,00%",
          "🟢 0,00%",
          "0,00%",
      ),
      ("2.16 Armado y ajustes", "100,00%", "100,00%", "🟢 0,00%", "0,00%"),
  ]

  cols_f1 = st.columns(6)
  for idx in range(6):
    titulo, plan, real, desv, aporte = tarjetas_turbina[idx]
    with cols_f1[idx]:
      st.markdown(
          f"""
            <div style="background-color: #d4ac0d; padding: 6px; border-radius: 4px 4px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 11px; height: 35px; display: flex; align-items: center; justify-content: center;">
                {titulo}
            </div>
            <div style="background-color: #f8f9f9; padding: 10px; border-radius: 0px 0px 4px 4px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 11px;">
                <b>Plan:</b> {plan}<br>
                <b>Real:</b> {real}<br>
                <b>Desv:</b> {desv}<br>
                <b>Aporte:</b> {aporte}
            </div>
            """,
          unsafe_allow_html=True,
      )

  cols_f2 = st.columns(6)
  for idx in range(6, 12):
    titulo, plan, real, desv, aporte = tarjetas_turbina[idx]
    with cols_f2[idx - 6]:
      st.markdown(
          f"""
            <div style="background-color: #d4ac0d; padding: 6px; border-radius: 4px 4px 0px 0px; color: white; font-weight: bold; text-align: center; font-size: 11px; height: 35px; display: flex; align-items: center; justify-content: center;">
                {titulo}
            </div>
            <div style="background-color: #f8f9f9; padding: 10px; border-radius: 0px 0px 4px 4px; border: 1px solid #ddd; margin-bottom: 15px; font-size: 11px;">
                <b>Plan:</b> {plan}<br>
                <b>Real:</b> {real}<br>
                <b>Desv:</b> {desv}<br>
                <b>Aporte:</b> {aporte}
            </div>
            """,
          unsafe_allow_html=True,
      )

  st.divider()
  col_b1, col_b2 = st.columns([1, 5])
  with col_b1:
    if st.button("⬅️ Página Anterior (Caldera)", type="secondary"):
      st.session_state.pagina = "dashboard_caldera"
      st.rerun()
  with col_b2:
    if st.button("Página Siguiente (Análisis de Desviación) ➡️", type="primary"):
      st.session_state.pagina = "analisis_desviacion"
      st.rerun()


# ==========================================
# PÁGINA 5: ANÁLISIS DE DESVIACIÓN
# ==========================================
elif st.session_state.pagina == "analisis_desviacion":
  st.title("📊 Análisis de Desviación")
  st.markdown(
      "Distribución de aportes negativos por componente basada en la hoja"
      " 'Análisis de Desviación'."
  )

  colors_caldera = ["#95a5a6", "#b7950b", "#e67e22", "#8e44ad"]
  colors_turbina = [
      "#2980b9",
      "#e91e63",
      "#bdc3c7",
      "#6d4c41",
      "#e67e22",
      "#8e44ad",
      "#e74c3c",
  ]

  # SECCIÓN 1: Caldera
  st.subheader(
      "1️⃣ Distribución de Aportes Negativos - Caldera y Equipos Auxiliares"
  )
  st.markdown("Aportes a la Desviación - Caldera")

  labels_caldera = [
      "1.3 Reparación envoltura metálica",
      "1.4 Reparación de cámaras muertas",
      "1.6 Reemplazo de tuberías ácido y soda",
      "1.7 Mantenimiento en los equipos de balance BOP y equipos",
  ]
  values_caldera = [6.9, 4.0, 43.4, 41.2]

  df_pie_cal = pd.DataFrame(
      {"Subcomponente": labels_caldera, "Porcentaje": values_caldera}
  )

  col_c1, col_c2 = st.columns([1.3, 1])
  with col_c1:
    fig_pie1 = px.pie(
        df_pie_cal,
        names="Subcomponente",
        values="Porcentaje",
        hole=0.0,
        color_discrete_sequence=colors_caldera,
    )
    fig_pie1.update_traces(
        textposition="outside", textinfo="percent", showlegend=False
    )
    fig_pie1.update_layout(height=400, margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(fig_pie1, use_container_width=True)

  with col_c2:
    st.markdown("##### Leyenda - Caldera")
    for name, color in zip(labels_caldera, colors_caldera):
      st.markdown(
          f"<span style='color:{color}; font-size:18px;'>■</span>"
          f" <b>{name}</b>",
          unsafe_allow_html=True,
      )

  st.divider()

  # SECCIÓN 2: Turbina
  st.subheader(
      "2️⃣ Distribución de Aportes Negativos - Turbo Generador y Equipos"
      " Auxiliares"
  )
  st.markdown("Aportes a la Desviación - Turbina")

  labels_turbina = [
      "2.4 Reparación de componentes en talleres",
      "2.7 Alineación de la turbina",
      "2.10 Aislamiento térmico",
      "2.12 Preparación de superficie metálica y cubrimiento",
      "2.14 Mantenimiento de equipos auxiliares",
      "2.15 Desarmado de componentes y mantenimientos",
      "2.16 Armado y ajustes",
  ]
  values_turbina = [1.5, 17.8, 13.8, 17.8, 15.8, 14.6, 8.9]

  df_pie_turb = pd.DataFrame(
      {"Subcomponente": labels_turbina, "Porcentaje": values_turbina}
  )

  col_t1, col_t2 = st.columns([1.3, 1])
  with col_t1:
    fig_pie2 = px.pie(
        df_pie_turb,
        names="Subcomponente",
        values="Porcentaje",
        hole=0.0,
        color_discrete_sequence=colors_turbina,
    )
    fig_pie2.update_traces(
        textposition="outside", textinfo="percent", showlegend=False
    )
    fig_pie2.update_layout(height=420, margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(fig_pie2, use_container_width=True)

  with col_t2:
    st.markdown("##### Leyenda - Turbina")
    for name, color in zip(labels_turbina, colors_turbina):
      st.markdown(
          f"<span style='color:{color}; font-size:18px;'>■</span>"
          f" <b>{name}</b>",
          unsafe_allow_html=True,
      )

  st.divider()
  if st.button("⬅️ Página Anterior (Turbina)", type="secondary"):
    st.session_state.pagina = "dashboard_turbina"
    st.rerun()