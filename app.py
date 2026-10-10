"""
Dashboard Financiero Ejecutivo - Distribuciones Andina Comercial S.A.S. (2021-2025)
Diseñado con estándares de alta dirección y visualización analítica avanzada.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Configuración de página
st.set_page_config(
    page_title="Andina Dashboard Financiero",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -2px rgba(0, 0, 0, 0.2);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .delta-positive { color: #10b981; }
    .delta-negative { color: #ef4444; }
    .delta-neutral { color: #64748b; }
    
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-success { background-color: #064e3b; color: #6ee7b7; border: 1px solid #059669; }
    .badge-info { background-color: #0c4a6e; color: #7dd3fc; border: 1px solid #0284c7; }
    .badge-warning { background-color: #451a03; color: #fcd34d; border: 1px solid #d97706; }
    
    .section-header {
        border-bottom: 2px solid #334155;
        padding-bottom: 8px;
        margin-top: 24px;
        margin-bottom: 18px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CARGA Y PROCESAMIENTO DE DATOS
# ---------------------------------------------------------
@st.cache_data
def load_and_process_data():
    base_dir = os.path.dirname(__file__)
    archivos_path = os.path.join(base_dir, "archivos")
    
    bg_raw = pd.read_excel(os.path.join(archivos_path, "balance_general.xlsx"))
    er_raw = pd.read_excel(os.path.join(archivos_path, "estado_de_resultados.xlsx"))
    fe_raw = pd.read_excel(os.path.join(archivos_path, "estado_flujo_efectivo.xlsx"))
    
    years = [2021, 2022, 2023, 2024, 2025]
    
    # Procesar Balance General
    bg = bg_raw.dropna(subset=['Cuenta']).copy()
    bg['Cuenta'] = bg['Cuenta'].str.strip()
    bg_dict = {row['Cuenta']: row[years].to_dict() for _, row in bg.iterrows()}
    
    # Procesar Estado de Resultados
    er = er_raw.dropna(subset=['Cuenta']).copy()
    er['Cuenta'] = er['Cuenta'].str.strip()
    er_dict = {row['Cuenta']: row[years].to_dict() for _, row in er.iterrows()}
    
    # Procesar Flujo de Efectivo
    fe = fe_raw.dropna(subset=['Concepto']).copy()
    fe['Concepto'] = fe['Concepto'].str.strip()
    # Limpiar valor inconsistente en CFF 2021 si viene como -1.472
    fe_dict = {}
    for _, row in fe.iterrows():
        concepto = row['Concepto']
        vals = {}
        for y in years:
            v = row[y]
            # Fix if parsed as float string or wrong unit
            if concepto == "Flujo neto de efectivo de financiación (CFF)" and y == 2021 and abs(v) < 10:
                v = -1472.0
            vals[y] = float(v) if pd.notnull(v) else 0.0
        fe_dict[concepto] = vals
        
    # Construcción de Dataframe Consolidado de Métricas
    data = []
    for y in years:
        ventas = er_dict['Ingresos operacionales (ventas netas)'][y]
        costos = er_dict['Costo de ventas (mercancía vendida)'][y]
        util_bruta = er_dict['Utilidad bruta'][y]
        gastos_adm = er_dict['Gastos de administración'][y]
        gastos_vta = er_dict['Gastos de ventas'][y]
        deprec = er_dict['Depreciaciones y amortizaciones'][y]
        ebit = er_dict['Utilidad operacional (EBIT)'][y]
        ebitda = ebit + deprec
        intereses = er_dict['Gastos financieros (intereses)'][y]
        ebt = er_dict['Utilidad antes de impuestos'][y]
        impuestos = er_dict['Impuesto de renta'][y]
        util_neta = er_dict['Utilidad neta del ejercicio'][y]
        
        caja = bg_dict['Efectivo y equivalentes'][y]
        cx_cobrar = bg_dict['Deudores (cuentas por cobrar clientes)'][y]
        inventarios = bg_dict['Inventarios'][y]
        otros_act_corr = bg_dict['Otros activos corrientes'][y]
        act_corriente = bg_dict['Total activo corriente'][y]
        ppe_neto = bg_dict['Propiedad, planta y equipo (neto)'][y]
        intangibles = bg_dict['Intangibles (neto)'][y]
        act_total = bg_dict['Total activos'][y]
        
        oblig_cp = bg_dict['Obligaciones financieras - corto plazo'][y]
        proveedores = bg_dict['Proveedores'][y]
        otros_pas_corr = bg_dict['Cuentas por pagar y otros pasivos'][y]
        imp_pagar = bg_dict['Impuestos por pagar'][y]
        pas_corriente = bg_dict['Total pasivo corriente'][y]
        oblig_lp = bg_dict['Obligaciones financieras - largo plazo'][y]
        pas_total = bg_dict['Total pasivos'][y]
        
        patrimonio = bg_dict['Total patrimonio'][y]
        deuda_financiera = oblig_cp + oblig_lp
        deuda_neta = deuda_financiera - caja
        
        # Flujos
        cfo = fe_dict['Flujo neto de efectivo de operación (CFO)'][y]
        capex = abs(fe_dict['(-) Compras de propiedad, planta y equipo (CAPEX)'][y])
        cfi = fe_dict['Flujo neto de efectivo de inversión (CFI)'][y]
        cff = fe_dict['Flujo neto de efectivo de financiación (CFF)'][y]
        fcf = cfo - capex
        dividendos = abs(fe_dict['(-) Dividendos pagados'][y])
        
        # Capital de Trabajo
        wk = act_corriente - pas_corriente # Fondo de maniobra
        noa_cp = (cx_cobrar + inventarios) - proveedores # KTNO operativo
        
        # Días de Ciclo Operativo y de Efectivo
        dso = (cx_cobrar / ventas) * 365
        dio = (inventarios / costos) * 365
        dpo = (proveedores / costos) * 365
        ccc = dso + dio - dpo
        
        # Ratios de Rentabilidad
        mg_bruto = (util_bruta / ventas) * 100
        mg_ebitda = (ebitda / ventas) * 100
        mg_ebit = (ebit / ventas) * 100
        mg_neto = (util_neta / ventas) * 100
        
        roa = (util_neta / act_total) * 100
        roe = (util_neta / patrimonio) * 100
        
        # Ratios de Liquidez
        razon_corriente = act_corriente / pas_corriente
        prueba_acida = (act_corriente - inventarios) / pas_corriente
        ratio_caja = caja / pas_corriente
        
        # Ratios de Endeudamiento & Cobertura
        endeudamiento = (pas_total / act_total) * 100
        leverage_financiero = pas_total / patrimonio
        deuda_ebitda = deuda_financiera / ebitda
        deuda_neta_ebitda = deuda_neta / ebitda
        cobertura_intereses = ebit / intereses if intereses > 0 else 0
        
        # DuPont Decomposition
        rotacion_activos = ventas / act_total
        multiplicador_apalancamiento = act_total / patrimonio
        # Margen Neto decimal * Rotación * Apalancamiento = ROE
        
        # Creación de Valor (EVA Simplificado: NOPAT - WACC*CI)
        tasa_impuesto = impuestos / ebt if ebt > 0 else 0.30
        nopat = ebit * (1 - tasa_impuesto)
        capital_invertido = patrimonio + deuda_financiera - caja
        # Asumiendo un costo de capital de referencia (ej. 12% representativo para distribución en Colombia)
        wacc_ref = 0.12
        eva = nopat - (capital_invertido * wacc_ref)
        roic = (nopat / capital_invertido) * 100 if capital_invertido > 0 else 0
        
        data.append({
            'Año': y,
            'Ventas': ventas,
            'Costos': costos,
            'Utilidad Bruta': util_bruta,
            'Gastos Adm': gastos_adm,
            'Gastos Vta': gastos_vta,
            'Depreciación': deprec,
            'EBIT': ebit,
            'EBITDA': ebitda,
            'Gastos Financieros': intereses,
            'Utilidad Neta': util_neta,
            'Caja': caja,
            'CxC': cx_cobrar,
            'Inventarios': inventarios,
            'Activo Corriente': act_corriente,
            'PPE Neto': ppe_neto,
            'Activo Total': act_total,
            'Proveedores': proveedores,
            'Pasivo Corriente': pas_corriente,
            'Deuda CP': oblig_cp,
            'Deuda LP': oblig_lp,
            'Deuda Financiera Total': deuda_financiera,
            'Deuda Neta': deuda_neta,
            'Pasivo Total': pas_total,
            'Patrimonio': patrimonio,
            'CFO': cfo,
            'CAPEX': capex,
            'FCF': fcf,
            'CFI': cfi,
            'CFF': cff,
            'Dividendos': dividendos,
            'KTNO': noa_cp,
            'Capital de Trabajo Neto': wk,
            'DSO': dso,
            'DIO': dio,
            'DPO': dpo,
            'CCC': ccc,
            'Margen Bruto (%)': mg_bruto,
            'Margen EBITDA (%)': mg_ebitda,
            'Margen EBIT (%)': mg_ebit,
            'Margen Neto (%)': mg_neto,
            'ROA (%)': roa,
            'ROE (%)': roe,
            'ROIC (%)': roic,
            'Razón Corriente': razon_corriente,
            'Prueba Ácida': prueba_acida,
            'Ratio Efectivo': ratio_caja,
            'Endeudamiento (%)': endeudamiento,
            'Leverage': leverage_financiero,
            'Deuda / EBITDA': deuda_ebitda,
            'Deuda Neta / EBITDA': deuda_neta_ebitda,
            'Cobertura Intereses': cobertura_intereses,
            'Rotación Activos': rotacion_activos,
            'Multiplicador Capital': multiplicador_apalancamiento,
            'NOPAT': nopat,
            'Capital Invertido': capital_invertido,
            'EVA': eva
        })
        
    df_metrics = pd.DataFrame(data)
    
    # Calcular crecimientos anuales (YoY)
    df_metrics['Crecimiento Ventas (%)'] = df_metrics['Ventas'].pct_change() * 100
    df_metrics['Crecimiento EBITDA (%)'] = df_metrics['EBITDA'].pct_change() * 100
    df_metrics['Crecimiento Utilidad Neta (%)'] = df_metrics['Utilidad Neta'].pct_change() * 100
    df_metrics['Crecimiento FCF (%)'] = df_metrics['FCF'].pct_change() * 100
    
    return df_metrics, bg_raw, er_raw, fe_raw

df_metrics, bg_raw, er_raw, fe_raw = load_and_process_data()

# ---------------------------------------------------------
# SIDEBAR DE CONTROL & FILTROS
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135679.png", width=64)
    st.title("Andina Comercial")
    st.caption("Distribuciones Andina Comercial S.A.S. | NIT 900.xxx.xxx")
    st.markdown("---")
    
    modulo = st.radio(
        "Navegación Estratégica:",
        [
            "📊 Resumen Ejecutivo (C-Suite)",
            "📈 Rentabilidad & DuPont",
            "💧 Liquidez & Ciclo de Conversión",
            "⚖️ Endeudamiento & Solvencia",
            "💵 Flujo de Caja & Creación de Valor",
            "📑 Estados Financieros Detallados",
            "🎯 Simulador de Sensibilidad (What-If)"
        ]
    )
    
    st.markdown("---")
    selected_year = st.selectbox(
        "Año de Referencia para Diagnóstico:",
        [2025, 2024, 2023, 2022, 2021],
        index=0
    )
    
    st.markdown("---")
    st.info(
        "💡 **Contexto del Caso:**\n"
        "Distribuidora B2B colombiana de equipos de seguridad electrónica y redes. "
        "En 2021 sufrió tensión de caja por rápida expansión sin disciplina operativa. "
        "Desde 2022 implementó riguroso control de cartera, proveedores y plataforma B2B digital."
    )

# Obtener datos del año seleccionado y año anterior
curr_row = df_metrics[df_metrics['Año'] == selected_year].iloc[0]
prev_row = df_metrics[df_metrics['Año'] == (selected_year - 1)].iloc[0] if selected_year > 2021 else None

def format_curr(val):
    return f"${val:,.0f} M"

def get_delta_str(curr, prev, is_pct=False, invert_color=False):
    if prev is None:
        return ""
    diff = curr - prev
    pct_diff = ((curr - prev) / abs(prev) * 100) if prev != 0 else 0
    sign = "+" if diff > 0 else ""
    
    is_good = diff > 0 if not invert_color else diff < 0
    color_class = "delta-positive" if is_good else ("delta-negative" if diff != 0 else "delta-neutral")
    arrow = "▲" if diff > 0 else ("▼" if diff < 0 else "■")
    
    if is_pct:
        text = f"{arrow} {sign}{diff:.2f} pp ({sign}{pct_diff:.1f}%)"
    else:
        text = f"{arrow} {sign}{diff:,.0f} M ({sign}{pct_diff:.1f}%)"
    return f'<div class="metric-delta {color_class}">{text} vs {selected_year-1}</div>'

# ---------------------------------------------------------
# MÓDULO 1: RESUMEN EJECUTIVO (C-SUITE)
# ---------------------------------------------------------
if modulo == "📊 Resumen Ejecutivo (C-Suite)":
    st.title("📊 Tablero de Control Directivo (C-Suite)")
    st.caption(f"Visión integral del desempeño económico y financiero - Ejercicio Fiscal {selected_year}")
    
    # KPIs Clave en Cards
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        delta_html = get_delta_str(curr_row['Ventas'], prev_row['Ventas'] if prev_row is not None else None)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Ingresos Operacionales</div>
            <div class="metric-value">{format_curr(curr_row['Ventas'])}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    with c2:
        delta_html = get_delta_str(curr_row['EBITDA'], prev_row['EBITDA'] if prev_row is not None else None)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">EBITDA Operativo</div>
            <div class="metric-value">{format_curr(curr_row['EBITDA'])}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    with c3:
        delta_html = get_delta_str(curr_row['Margen EBITDA (%)'], prev_row['Margen EBITDA (%)'] if prev_row is not None else None, is_pct=True)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Margen EBITDA</div>
            <div class="metric-value">{curr_row['Margen EBITDA (%)']:.2f}%</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    with c4:
        delta_html = get_delta_str(curr_row['Utilidad Neta'], prev_row['Utilidad Neta'] if prev_row is not None else None)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Utilidad Neta</div>
            <div class="metric-value">{format_curr(curr_row['Utilidad Neta'])}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    with c5:
        delta_html = get_delta_str(curr_row['FCF'], prev_row['FCF'] if prev_row is not None else None)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Flujo Caja Libre (FCF)</div>
            <div class="metric-value">{format_curr(curr_row['FCF'])}</div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # Fila de Gráficos Principales: Evolución de Ingresos y Márgenes vs Ciclo de Efectivo
    col_left, col_right = st.columns([1.2, 1])
    
    with col_left:
        st.subheader("📈 Trayectoria de Crecimiento & Rentabilidad (2021-2025)")
        fig_evol = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_evol.add_trace(
            go.Bar(
                x=df_metrics['Año'],
                y=df_metrics['Ventas'],
                name="Ventas Netas",
                marker_color='#2563eb',
                opacity=0.85
            ),
            secondary_y=False
        )
        fig_evol.add_trace(
            go.Bar(
                x=df_metrics['Año'],
                y=df_metrics['Utilidad Bruta'],
                name="Utilidad Bruta",
                marker_color='#38bdf8',
                opacity=0.85
            ),
            secondary_y=False
        )
        fig_evol.add_trace(
            go.Scatter(
                x=df_metrics['Año'],
                y=df_metrics['Margen EBITDA (%)'],
                name="Margen EBITDA (%)",
                line=dict(color='#10b981', width=3),
                mode='lines+markers'
            ),
            secondary_y=True
        )
        fig_evol.add_trace(
            go.Scatter(
                x=df_metrics['Año'],
                y=df_metrics['Margen Neto (%)'],
                name="Margen Neto (%)",
                line=dict(color='#f59e0b', width=3, dash='dot'),
                mode='lines+markers'
            ),
            secondary_y=True
        )
        fig_evol.update_layout(
            barmode='group',
            height=380,
            template='plotly_dark',
            margin=dict(l=40, r=40, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_evol.update_xaxes(title_text="Año")
        fig_evol.update_yaxes(title_text="Millones COP ($)", secondary_y=False)
        fig_evol.update_yaxes(title_text="Margen (%)", secondary_y=True)
        st.plotly_chart(fig_evol, use_container_width=True)
        
    with col_right:
        st.subheader("⏱️ Ciclo de Conversión de Efectivo (CCC)")
        fig_ccc = go.Figure()
        fig_ccc.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['DSO'], name='Días Cartera (DSO)', line=dict(color='#f59e0b', width=2), mode='lines+markers'))
        fig_ccc.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['DIO'], name='Días Inventario (DIO)', line=dict(color='#06b6d4', width=2), mode='lines+markers'))
        fig_ccc.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['DPO'], name='Días Proveedores (DPO)', line=dict(color='#a855f7', width=2), mode='lines+markers'))
        fig_ccc.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['CCC'], name='Ciclo Neto (CCC)', line=dict(color='#10b981', width=4), mode='lines+markers+text', text=[f"{val:.0f}d" for val in df_metrics['CCC']], textposition="top center"))
        fig_ccc.update_layout(
            height=380,
            template='plotly_dark',
            margin=dict(l=40, r=40, t=30, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_ccc.update_yaxes(title_text="Días")
        st.plotly_chart(fig_ccc, use_container_width=True)
        
    # Fila Inferior: Estructura Financiera y Diagnóstico Cualitativo
    col_diag1, col_diag2 = st.columns([1, 1])
    
    with col_diag1:
        st.subheader(f"🧱 Estructura de Financiación ({selected_year})")
        deuda_bancaria = curr_row['Deuda Financiera Total']
        proveedores_val = curr_row['Proveedores']
        otros_pasivos = curr_row['Pasivo Total'] - deuda_bancaria - proveedores_val
        patrimonio_val = curr_row['Patrimonio']
        
        labels_fin = ['Deuda Bancaria (CP+LP)', 'Proveedores Comerciales', 'Otros Pasivos', 'Patrimonio Neto']
        values_fin = [deuda_bancaria, proveedores_val, otros_pasivos, patrimonio_val]
        colors_fin = ['#ef4444', '#f59e0b', '#64748b', '#10b981']
        
        fig_donut = go.Figure(data=[go.Pie(labels=labels_fin, values=values_fin, hole=.5, marker_colors=colors_fin)])
        fig_donut.update_layout(
            height=300,
            template='plotly_dark',
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_diag2:
        st.subheader("📋 Diagnóstico Estratégico del Analista")
        st.markdown(f"""
        > **Evaluación del Desempeño ({selected_year}):**
        > - **Expansión Sostenible:** Los ingresos crecieron a **{format_curr(curr_row['Ventas'])}** con un Margen Bruto sostenido del **{curr_row['Margen Bruto (%)']:.1f}%**, confirmando que la propuesta de valor basada en soporte técnico e inventario inmediato permite pricing power.
        > - **Eficiencia en Apalancamiento Operativo:** Los gastos operativos crecieron a un ritmo menor que las ventas gracias a la digitalización y sinergias comerciales, impulsando el margen EBITDA a **{curr_row['Margen EBITDA (%)']:.2f}%**.
        > - **Conversión de Caja:** La compañía superó el bache de 2021 (donde crecía absorbiendo caja). En {selected_year}, el Ciclo de Conversión de Efectivo es de **{curr_row['CCC']:.1f} días**, generando un Flujo de Caja Libre positivo de **{format_curr(curr_row['FCF'])}**.
        > - **Salud del Pasivo:** La Deuda Neta / EBITDA se ubica en **{curr_row['Deuda Neta / EBITDA']:.2f}x**, demostrando una posición de desapalancamiento saludable y alta solvencia.
        """)

# ---------------------------------------------------------
# MÓDULO 2: RENTABILIDAD & DUPONT
# ---------------------------------------------------------
elif modulo == "📈 Rentabilidad & DuPont":
    st.title("📈 Análisis Profundo de Rentabilidad & Modelo DuPont")
    st.caption("Descomposición piramidal de los retornos sobre activos (ROA), patrimonio (ROE) y capital invertido (ROIC)")
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Margen Neto", f"{curr_row['Margen Neto (%)']:.2f}%", f"{curr_row['Margen Neto (%)'] - prev_row['Margen Neto (%)']:.2f} pp" if prev_row is not None else None)
    with k2:
        st.metric("ROA (Retorno Activos)", f"{curr_row['ROA (%)']:.2f}%", f"{curr_row['ROA (%)'] - prev_row['ROA (%)']:.2f} pp" if prev_row is not None else None)
    with k3:
        st.metric("ROE (Retorno Patrimonio)", f"{curr_row['ROE (%)']:.2f}%", f"{curr_row['ROE (%)'] - prev_row['ROE (%)']:.2f} pp" if prev_row is not None else None)
    with k4:
        st.metric("ROIC (Retorno Capital)", f"{curr_row['ROIC (%)']:.2f}%", f"{curr_row['ROIC (%)'] - prev_row['ROIC (%)']:.2f} pp" if prev_row is not None else None)
        
    st.write("")
    
    # Visualización Modelo DuPont
    st.subheader(f"🧩 Descomposición DuPont de 3 Factores para el ROE ({selected_year})")
    st.markdown(
        r"$$\text{ROE} = \underbrace{\frac{\text{Utilidad Neta}}{\text{Ventas}}}_{\text{Margen Neto}} \times \underbrace{\frac{\text{Ventas}}{\text{Activo Total}}}_{\text{Rotación de Activos}} \times \underbrace{\frac{\text{Activo Total}}{\text{Patrimonio}}}_{\text{Apalancamiento Financiero}}$$"
    )
    
    dp_col1, dp_col2, dp_col3, dp_col4 = st.columns([1, 1, 1, 1.2])
    with dp_col1:
        st.info(f"**1. Eficiencia Operativa**\n\nMargen Neto: **{curr_row['Margen Neto (%)']:.2f}%**\n\nCapacidad de convertir cada $100 de ventas en utilidad final.")
    with dp_col2:
        st.info(f"**2. Eficiencia de Activos**\n\nRotación: **{curr_row['Rotación Activos']:.2f}x**\n\nGeneración de ventas por cada peso invertido en activos totales.")
    with dp_col3:
        st.info(f"**3. Estructura de Capital**\n\nMultiplicador: **{curr_row['Multiplicador Capital']:.2f}x**\n\nGrado de apalancamiento sobre los recursos de los accionistas.")
    with dp_col4:
        calc_roe = (curr_row['Margen Neto (%)']/100) * curr_row['Rotación Activos'] * curr_row['Multiplicador Capital'] * 100
        st.success(f"**🎯 ROE Resultante**\n\n**{curr_row['ROE (%)']:.2f}%** (Verificación: {calc_roe:.2f}%)\n\nRetorno final generado para los socios de Andina.")
        
    st.write("")
    st.subheader("📊 Evolución Histórica de Retornos (2021-2025)")
    fig_ret = go.Figure()
    fig_ret.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['ROE (%)'], name='ROE (%)', line=dict(color='#10b981', width=3), mode='lines+markers'))
    fig_ret.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['ROIC (%)'], name='ROIC (%)', line=dict(color='#38bdf8', width=3), mode='lines+markers'))
    fig_ret.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['ROA (%)'], name='ROA (%)', line=dict(color='#f59e0b', width=2), mode='lines+markers'))
    fig_ret.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['Margen Neto (%)'], name='Margen Neto (%)', line=dict(color='#ec4899', width=2, dash='dash'), mode='lines+markers'))
    fig_ret.update_layout(height=360, template='plotly_dark', margin=dict(l=30, r=30, t=30, b=30), yaxis_title="Porcentaje (%)")
    st.plotly_chart(fig_ret, use_container_width=True)
    
    # Análisis de Cascada (Waterfall) del P&L
    st.subheader(f"🌊 Cascada de Pérdidas y Ganancias (P&L Waterfall - {selected_year})")
    wf_fig = go.Figure(go.Waterfall(
        name="P&L",
        orientation="v",
        measure=["relative", "relative", "total", "relative", "relative", "relative", "total", "relative", "total"],
        x=["Ventas", "Costo Ventas", "Utilidad Bruta", "Gastos Adm", "Gastos Vta", "Depreciación", "EBIT", "Financieros + Imp", "Utilidad Neta"],
        textposition="outside",
        text=[f"+{curr_row['Ventas']:,.0f}", f"-{curr_row['Costos']:,.0f}", f"{curr_row['Utilidad Bruta']:,.0f}", f"-{curr_row['Gastos Adm']:,.0f}", f"-{curr_row['Gastos Vta']:,.0f}", f"-{curr_row['Depreciación']:,.0f}", f"{curr_row['EBIT']:,.0f}", f"-{(curr_row['Gastos Financieros'] + er_raw.loc[er_raw['Cuenta'].str.contains('Impuesto', na=False), selected_year].values[0]):,.0f}", f"{curr_row['Utilidad Neta']:,.0f}"],
        y=[curr_row['Ventas'], -curr_row['Costos'], 0, -curr_row['Gastos Adm'], -curr_row['Gastos Vta'], -curr_row['Depreciación'], 0, -(curr_row['Gastos Financieros'] + er_raw.loc[er_raw['Cuenta'].str.contains('Impuesto', na=False), selected_year].values[0]), 0],
        connector={"line": {"color": "#64748b"}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#2563eb"}}
    ))
    wf_fig.update_layout(height=400, template='plotly_dark', margin=dict(l=30, r=30, t=30, b=30))
    st.plotly_chart(wf_fig, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 3: LIQUIDEZ & CICLO DE EFECTIVO
# ---------------------------------------------------------
elif modulo == "💧 Liquidez & Ciclo de Conversión":
    st.title("💧 Diagnóstico de Liquidez y Gestión de Capital de Trabajo")
    st.caption("Control de solvencia a corto plazo, días de calle y evolución del KTNO")
    
    l1, l2, l3, l4 = st.columns(4)
    with l1:
        st.metric("Razón Corriente", f"{curr_row['Razón Corriente']:.2f}x", f"{curr_row['Razón Corriente'] - prev_row['Razón Corriente']:.2f}" if prev_row is not None else None)
    with l2:
        st.metric("Prueba Ácida", f"{curr_row['Prueba Ácida']:.2f}x", f"{curr_row['Prueba Ácida'] - prev_row['Prueba Ácida']:.2f}" if prev_row is not None else None)
    with l3:
        st.metric("Ciclo Efectivo (CCC)", f"{curr_row['CCC']:.1f} días", f"{curr_row['CCC'] - prev_row['CCC']:.1f} d" if prev_row is not None else None, delta_color="inverse")
    with l4:
        st.metric("KTNO Operativo", format_curr(curr_row['KTNO']), f"{curr_row['KTNO'] - prev_row['KTNO']:,.0f} M" if prev_row is not None else None)
        
    st.write("")
    
    c_liq_left, c_liq_right = st.columns(2)
    with c_liq_left:
        st.subheader("📐 Ratios de Cobertura de Corto Plazo")
        fig_ratios = go.Figure()
        fig_ratios.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['Razón Corriente'], name='Razón Corriente', marker_color='#3b82f6'))
        fig_ratios.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['Prueba Ácida'], name='Prueba Ácida', marker_color='#06b6d4'))
        fig_ratios.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['Ratio Efectivo'], name='Ratio Caja / Pasivo CP', marker_color='#10b981'))
        fig_ratios.add_hline(y=1.0, line_dash="dash", line_color="#ef4444", annotation_text="Límite Cobertura 1.0x")
        fig_ratios.update_layout(barmode='group', height=360, template='plotly_dark', margin=dict(l=30, r=30, t=30, b=30), yaxis_title="Veces (x)")
        st.plotly_chart(fig_ratios, use_container_width=True)
        
    with c_liq_right:
        st.subheader("📦 Composición del Capital de Trabajo Neto Operativo (KTNO)")
        fig_ktno = go.Figure()
        fig_ktno.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['CxC'], name='(+) Cuentas por Cobrar', marker_color='#f59e0b'))
        fig_ktno.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['Inventarios'], name='(+) Inventarios', marker_color='#8b5cf6'))
        fig_ktno.add_trace(go.Bar(x=df_metrics['Año'], y=-df_metrics['Proveedores'], name='(-) Proveedores', marker_color='#ef4444'))
        fig_ktno.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['KTNO'], name='(=) KTNO Neto', line=dict(color='#10b981', width=3), mode='lines+markers'))
        fig_ktno.update_layout(barmode='relative', height=360, template='plotly_dark', margin=dict(l=30, r=30, t=30, b=30), yaxis_title="Millones COP ($)")
        st.plotly_chart(fig_ktno, use_container_width=True)
        
    st.subheader("💡 Análisis de Sensibilidad Operativa del Ciclo de Efectivo")
    st.markdown(f"""
    En **{selected_year}**, Distribuciones Andina tarda:
    - **{curr_row['DSO']:.1f} días** en cobrar su cartera de clientes B2B.
    - **{curr_row['DIO']:.1f} días** en rotar sus existencias en bodega.
    - **Financiación de Proveedores:** La compañía paga a sus proveedores cada **{curr_row['DPO']:.1f} días**.
    - **Resultado:** El Ciclo de Conversión de Efectivo neto se sitúa en **{curr_row['CCC']:.1f} días**. Comparado con 2021 (donde el ciclo neto exigía mayor fondeo), la empresa ha logrado estabilizar la cartera y apalancarse más inteligentemente con aliados estratégicos, liberando recursos para reinversión en tecnología y distribución de dividendos.
    """)

# ---------------------------------------------------------
# MÓDULO 4: ENDEUDAMIENTO & SOLVENCIA
# ---------------------------------------------------------
elif modulo == "⚖️ Endeudamiento & Solvencia":
    st.title("⚖️ Estructura de Capital, Deuda y Cobertura Financiera")
    st.caption("Perfil de pasivos, leverage bancario y capacidad de servicio de la deuda")
    
    e1, e2, e3, e4 = st.columns(4)
    with e1:
        st.metric("Endeudamiento Total", f"{curr_row['Endeudamiento (%)']:.2f}%", f"{curr_row['Endeudamiento (%)'] - prev_row['Endeudamiento (%)']:.2f} pp" if prev_row is not None else None, delta_color="inverse")
    with e2:
        st.metric("Deuda Financiera Total", format_curr(curr_row['Deuda Financiera Total']), f"{curr_row['Deuda Financiera Total'] - prev_row['Deuda Financiera Total']:,.0f} M" if prev_row is not None else None)
    with e3:
        st.metric("Deuda / EBITDA", f"{curr_row['Deuda / EBITDA']:.2f}x", f"{curr_row['Deuda / EBITDA'] - prev_row['Deuda / EBITDA']:.2f}x" if prev_row is not None else None, delta_color="inverse")
    with e4:
        st.metric("Cobertura de Intereses", f"{curr_row['Cobertura Intereses']:.2f}x", f"{curr_row['Cobertura Intereses'] - prev_row['Cobertura Intereses']:.2f}x" if prev_row is not None else None)
        
    st.write("")
    
    col_deuda1, col_deuda2 = st.columns(2)
    with col_deuda1:
        st.subheader("🏦 Estructura Temporal de la Deuda Bancaria")
        fig_db = go.Figure()
        fig_db.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['Deuda CP'], name='Deuda Corto Plazo', marker_color='#f87171'))
        fig_db.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['Deuda LP'], name='Deuda Largo Plazo', marker_color='#dc2626'))
        fig_db.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['Deuda Neta'], name='Deuda Neta (D - Caja)', line=dict(color='#facc15', width=3), mode='lines+markers'))
        fig_db.update_layout(barmode='stack', height=360, template='plotly_dark', margin=dict(l=30, r=30, t=30, b=30), yaxis_title="Millones COP ($)")
        st.plotly_chart(fig_db, use_container_width=True)
        
    with col_deuda2:
        st.subheader("🛡️ Ratios de Solvencia: Deuda / EBITDA vs Cobertura")
        fig_solv = make_subplots(specs=[[{"secondary_y": True}]])
        fig_solv.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['Deuda / EBITDA'], name='Deuda Bruta / EBITDA (x)', line=dict(color='#fb923c', width=3), mode='lines+markers'), secondary_y=False)
        fig_solv.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['Deuda Neta / EBITDA'], name='Deuda Neta / EBITDA (x)', line=dict(color='#34d399', width=3), mode='lines+markers'), secondary_y=False)
        fig_solv.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['Cobertura Intereses'], name='Cobertura Intereses (EBIT/Int)', marker_color='#60a5fa', opacity=0.4), secondary_y=True)
        fig_solv.update_layout(height=360, template='plotly_dark', margin=dict(l=30, r=30, t=30, b=30), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_solv.update_yaxes(title_text="Deuda / EBITDA (x)", secondary_y=False)
        fig_solv.update_yaxes(title_text="Cobertura Intereses (x)", secondary_y=True)
        st.plotly_chart(fig_solv, use_container_width=True)
        
    st.info(
        f"📌 **Conclusión de Solvencia ({selected_year}):** La empresa cuenta con una sólida cobertura de intereses de **{curr_row['Cobertura Intereses']:.2f} veces**, "
        f"lo que significa que su utilidad operacional cubre holgadamente sus obligaciones financieras con bancos. "
        f"Además, la acumulación de efectivo ha reducido significativamente la Deuda Neta / EBITDA a **{curr_row['Deuda Neta / EBITDA']:.2f}x**, "
        "brindando un amplio margen de maniobra para futuros planes de expansión o financiamiento de CAPEX."
    )

# ---------------------------------------------------------
# MÓDULO 5: FLUJO DE CAJA & CREACIÓN DE VALOR
# ---------------------------------------------------------
elif modulo == "💵 Flujo de Caja & Creación de Valor":
    st.title("💵 Dinámica de Flujo de Efectivo & Generación de Valor (EVA)")
    st.caption("Conversión de resultados contables a liquidez real, autofinanciamiento y creación de valor económico")
    
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.metric("Flujo Operativo (CFO)", format_curr(curr_row['CFO']), f"{curr_row['CFO'] - prev_row['CFO']:,.0f} M" if prev_row is not None else None)
    with f2:
        st.metric("Inversión CAPEX", format_curr(curr_row['CAPEX']), f"{curr_row['CAPEX'] - prev_row['CAPEX']:,.0f} M" if prev_row is not None else None)
    with f3:
        st.metric("Flujo de Caja Libre (FCF)", format_curr(curr_row['FCF']), f"{curr_row['FCF'] - prev_row['FCF']:,.0f} M" if prev_row is not None else None)
    with f4:
        st.metric("EVA Estimado", format_curr(curr_row['EVA']), f"{curr_row['EVA'] - prev_row['EVA']:,.0f} M" if prev_row is not None else None)
        
    st.write("")
    
    col_fc1, col_fc2 = st.columns(2)
    with col_fc1:
        st.subheader("🌊 Flujos de Caja por Actividad (Operación, Inversión, Financiación)")
        fig_cf_act = go.Figure()
        fig_cf_act.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['CFO'], name='Flujo Operación (CFO)', marker_color='#10b981'))
        fig_cf_act.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['CFI'], name='Flujo Inversión (CFI)', marker_color='#ef4444'))
        fig_cf_act.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['CFF'], name='Flujo Financiación (CFF)', marker_color='#3b82f6'))
        fig_cf_act.update_layout(barmode='group', height=360, template='plotly_dark', margin=dict(l=30, r=30, t=30, b=30), yaxis_title="Millones COP ($)")
        st.plotly_chart(fig_cf_act, use_container_width=True)
        
    with col_fc2:
        st.subheader("💰 Generación de Caja Libre vs Dividendos Pagados")
        fig_fcf_div = go.Figure()
        fig_fcf_div.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['FCF'], name='Flujo de Caja Libre (FCF)', marker_color='#06b6d4'))
        fig_fcf_div.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['Dividendos'], name='Dividendos Distribuidos', marker_color='#f59e0b'))
        fig_fcf_div.add_trace(go.Scatter(x=df_metrics['Año'], y=df_metrics['Caja'], name='Saldo Caja Final', line=dict(color='#a855f7', width=3), mode='lines+markers'))
        fig_fcf_div.update_layout(barmode='group', height=360, template='plotly_dark', margin=dict(l=30, r=30, t=30, b=30), yaxis_title="Millones COP ($)")
        st.plotly_chart(fig_fcf_div, use_container_width=True)
        
    st.write("")
    st.subheader("💎 Análisis de Creación de Valor Económico Agregado (EVA)")
    st.markdown(r"$$\text{EVA} = \text{NOPAT} - (\text{Capital Invertido} \times \text{WACC})$$")
    eva_c1, eva_c2, eva_c3 = st.columns(3)
    with eva_c1:
        st.metric("NOPAT (Utilidad Operativa post-impuestos)", format_curr(curr_row['NOPAT']))
    with eva_c2:
        st.metric("Capital Invertido Operativo", format_curr(curr_row['Capital Invertido']))
    with eva_c3:
        st.metric("Costo del Capital (WACC ref. 12%)", format_curr(curr_row['Capital Invertido'] * 0.12))
        
    fig_eva = go.Figure()
    fig_eva.add_trace(go.Bar(x=df_metrics['Año'], y=df_metrics['EVA'], name='EVA Generado ($ M)', marker_color=np.where(df_metrics['EVA'] >= 0, '#10b981', '#ef4444')))
    fig_eva.update_layout(height=280, template='plotly_dark', margin=dict(l=30, r=30, t=30, b=30), yaxis_title="Millones COP ($)")
    st.plotly_chart(fig_eva, use_container_width=True)

# ---------------------------------------------------------
# MÓDULO 6: ESTADOS FINANCIEROS DETALLADOS
# ---------------------------------------------------------
elif modulo == "📑 Estados Financieros Detallados":
    st.title("📑 Estados Financieros Completos (2021 - 2025)")
    st.caption("Cifras auditadas en millones de pesos colombianos (COP)")
    
    tab_bg, tab_er, tab_fe, tab_metricas = st.tabs([
        "Balance General", "Estado de Resultados", "Flujo de Efectivo", "Matriz Consolidada de Ratios"
    ])
    
    with tab_bg:
        st.subheader("Balance General")
        bg_disp = bg_raw.copy()
        bg_disp.columns = [str(c) for c in bg_disp.columns]
        for y in [2021, 2022, 2023, 2024, 2025]:
            bg_disp[str(y)] = bg_disp[str(y)].map(lambda x: f"${x:,.0f}" if pd.notnull(x) else "")
        st.dataframe(bg_disp.fillna(""), use_container_width=True, hide_index=True)
        
    with tab_er:
        st.subheader("Estado de Resultados (P&L)")
        er_disp = er_raw.copy()
        er_disp.columns = [str(c) for c in er_disp.columns]
        for y in [2021, 2022, 2023, 2024, 2025]:
            er_disp[str(y)] = er_disp[str(y)].map(lambda x: f"${x:,.0f}" if pd.notnull(x) else "")
        st.dataframe(er_disp.fillna(""), use_container_width=True, hide_index=True)
        
    with tab_fe:
        st.subheader("Estado de Flujo de Efectivo (Método Indirecto)")
        fe_disp = fe_raw.copy()
        fe_disp.columns = [str(c) for c in fe_disp.columns]
        for y in [2021, 2022, 2023, 2024, 2025]:
            fe_disp[str(y)] = fe_disp[str(y)].map(lambda x: f"${x:,.0f}" if pd.notnull(x) else "")
        st.dataframe(fe_disp.fillna(""), use_container_width=True, hide_index=True)
        
    with tab_metricas:
        st.subheader("Histórico Completo de Indicadores Financieros")
        ratios_cols = [
            'Año', 'Margen Bruto (%)', 'Margen EBITDA (%)', 'Margen EBIT (%)', 'Margen Neto (%)',
            'ROA (%)', 'ROE (%)', 'ROIC (%)', 'Razón Corriente', 'Prueba Ácida',
            'DSO', 'DIO', 'DPO', 'CCC', 'Endeudamiento (%)', 'Deuda / EBITDA', 'Cobertura Intereses'
        ]
        ratios_df = df_metrics[ratios_cols].round(2)
        st.dataframe(ratios_df, use_container_width=True, hide_index=True)
        
        # Botón de Descarga
        csv = df_metrics.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Base de Indicadores (CSV)",
            data=csv,
            file_name="indicadores_financieros_andina.csv",
            mime="text/csv"
        )

# ---------------------------------------------------------
# MÓDULO 7: SIMULADOR DE SENSIBILIDAD (WHAT-IF)
# ---------------------------------------------------------
elif modulo == "🎯 Simulador de Sensibilidad (What-If)":
    st.title("🎯 Simulador Estratégico de Sensibilidad (What-If)")
    st.caption(f"Evalúa el impacto de variaciones en ventas, costos y días de cobro tomando como base el año {selected_year}")
    
    st.markdown("""
    Este simulador permite a la junta directiva y al equipo financiero proyectar cómo cambios en variables críticas 
    afectarían la **Utilidad Neta**, el **EBITDA**, la **Caja Operativa** y el **ROE**.
    """)
    
    sc_col1, sc_col2, sc_col3 = st.columns(3)
    with sc_col1:
        delta_vta = st.slider("Variación en Ventas (%)", min_value=-25.0, max_value=25.0, value=0.0, step=1.0)
    with sc_col2:
        delta_mg_bruto = st.slider("Cambio en Margen Bruto (puntos porcentuales)", min_value=-5.0, max_value=5.0, value=0.0, step=0.5)
    with sc_col3:
        delta_dso = st.slider("Variación en Días Cartera (DSO)", min_value=-20, max_value=20, value=0, step=1)
        
    # Cálculos proyectados
    base_vta = curr_row['Ventas']
    sim_vta = base_vta * (1 + delta_vta / 100)
    
    base_mg_bruto = curr_row['Margen Bruto (%)']
    sim_mg_bruto = (base_mg_bruto + delta_mg_bruto) / 100
    
    sim_util_bruta = sim_vta * sim_mg_bruto
    sim_costos = sim_vta - sim_util_bruta
    
    # Supuesto: Gastos operativos fijos al 70%, variables al 30%
    base_ga = curr_row['Gastos Adm']
    base_gv = curr_row['Gastos Vta']
    sim_ga = base_ga * (0.7 + 0.3 * (sim_vta / base_vta))
    sim_gv = base_gv * (0.5 + 0.5 * (sim_vta / base_vta))
    sim_deprec = curr_row['Depreciación']
    
    sim_ebit = sim_util_bruta - sim_ga - sim_gv - sim_deprec
    sim_ebitda = sim_ebit + sim_deprec
    sim_intereses = curr_row['Gastos Financieros']
    sim_ebt = sim_ebit - sim_intereses
    sim_imp = max(0, sim_ebt * 0.30)
    sim_util_neta = sim_ebt - sim_imp
    
    # Impacto en cartera
    sim_dso = curr_row['DSO'] + delta_dso
    sim_cxc = (sim_dso / 365) * sim_vta
    delta_cxc_caja = curr_row['CxC'] - sim_cxc
    sim_cfo = curr_row['CFO'] + (sim_util_neta - curr_row['Utilidad Neta']) + delta_cxc_caja
    
    sim_roe = (sim_util_neta / curr_row['Patrimonio']) * 100
    
    st.write("")
    st.subheader("📊 Comparación Escenario Base vs. Simulado")
    
    sim_m1, sim_m2, sim_m3, sim_m4 = st.columns(4)
    with sim_m1:
        st.metric("Ventas Proyectadas", format_curr(sim_vta), f"{sim_vta - base_vta:+,.0f} M")
    with sim_m2:
        st.metric("EBITDA Proyectado", format_curr(sim_ebitda), f"{sim_ebitda - curr_row['EBITDA']:+,.0f} M")
    with sim_m3:
        st.metric("Utilidad Neta", format_curr(sim_util_neta), f"{sim_util_neta - curr_row['Utilidad Neta']:+,.0f} M")
    with sim_m4:
        st.metric("ROE Proyectado", f"{sim_roe:.2f}%", f"{sim_roe - curr_row['ROE (%)']:+.2f} pp")
        
    st.write("")
    # Gráfica de barras comparativa
    categories = ['Ventas', 'Utilidad Bruta', 'EBITDA', 'Utilidad Neta', 'Flujo Operativo (CFO)']
    val_base = [base_vta, curr_row['Utilidad Bruta'], curr_row['EBITDA'], curr_row['Utilidad Neta'], curr_row['CFO']]
    val_sim = [sim_vta, sim_util_bruta, sim_ebitda, sim_util_neta, sim_cfo]
    
    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(name='Escenario Base', x=categories, y=val_base, marker_color='#64748b'))
    fig_comp.add_trace(go.Bar(name='Escenario Simulado', x=categories, y=val_sim, marker_color='#10b981'))
    fig_comp.update_layout(barmode='group', height=360, template='plotly_dark', yaxis_title="Millones COP ($)")
    st.plotly_chart(fig_comp, use_container_width=True)
    
    st.markdown(f"""
    > **Conclusión del Escenario:**
    > - Si las ventas varían en **{delta_vta:+.1f}%** y el margen bruto se ajusta en **{delta_mg_bruto:+.1f} pp**, la Utilidad Neta pasa a **{format_curr(sim_util_neta)}**.
    > - La alteración de cartera ({delta_dso:+d} días en DSO) genera un impacto directo en liquidez de **{delta_cxc_caja:+,.0f} M**, dejando el Flujo Operativo en **{format_curr(sim_cfo)}**.
    """)

# Footer común
st.markdown("---")
st.caption("Distribuciones Andina Comercial S.A.S. | Dashboard Financiero Analítico | Desarrollado con Streamlit & Plotly")
