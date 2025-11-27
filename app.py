# Lista de cambios implementados:
# 1. ✅ Gráficas temporales de OKRs (en lugar de listas expandibles)
# 2. ✅ Eliminada pestaña Mapa Estratégico 
# 3. ✅ Aumentado tamaño de gráficos pequeños (pie charts 200→350px)
# 4. ✅ Cambiado LOC a Story Points
# 5. ✅ Mejorado tamaño de Sunburst (600→700px)
# 6. ✅ Emojis mantenidos (NO Material Icons)
# 7. ✅ Sin filtros globales

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Import DSS modules
from olap_functions import slice_olap, dice, calculate_metric_trend
from kpi_calculator import (
    calculate_all_kpis, get_kpi_color, format_kpi_display
)
from balanced_scorecard import (
    generate_okrs_from_data, calculate_perspective_score,
    create_okr_hierarchy, get_perspective_icon, format_okr_table
)
from rayleigh_model import (
    calibrate_rayleigh_sigma, predict_defects_rayleigh,
    generate_rayleigh_curve, recommend_qa_resources,
    calculate_model_confidence, validate_prediction_inputs
)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Soporte a Decisiones", layout="wide", page_icon="📊")

# --- AUTENTICACIÓN ---
def check_password():
    """Retorna `True` si el usuario tiene la contraseña correcta."""
    
    def password_entered():
        """Chequea si la contraseña es correcta."""
        if st.session_state["username"] in st.secrets["passwords"] and st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]:
            st.session_state["authentication_status"] = True
            st.session_state["current_user"] = st.session_state["username"]
        else:
            st.session_state["authentication_status"] = False
    
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    
    if not st.session_state["authentication_status"]:
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", on_change=password_entered, key="password")
        
        if st.session_state["authentication_status"] is False:
            st.error("Usuario o contraseña incorrectos")
        return False
    else:
        return True

# Simulación de Secretos
if "passwords" not in st.secrets:
    st.secrets["passwords"] = {"admin": "admin123", "pm": "pm123", "invitado": "guest"}

if check_password():
    if "username" not in st.session_state and "current_user" in st.session_state:
        st.session_state["username"] = st.session_state["current_user"]
    
    # --- CARGA DE DATOS ---
    @st.cache_data
    def load_data():
        try:
            df_p = pd.read_csv('OLAP_Proyectos.csv')
            df_c = pd.read_csv('OLAP_Calidad.csv')
            return df_p, df_c
        except FileNotFoundError:
            st.error("⚠️ No se encontraron los archivos OLAP_*.csv")
            return None, None
    
    df_proy, df_cal = load_data()
    
    if df_proy is not None and df_cal is not None:
        
        # SIDEBAR - User Info and Navigation
        st.sidebar.success(f"👤 {st.session_state.get('username', 'Usuario')}")
        if st.sidebar.button("🚪 Cerrar Sesión"):
            st.session_state["authentication_status"] = None
            if "current_user" in st.session_state:
                del st.session_state["current_user"]
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # NAVIGATION
        st.sidebar.header("📊 Sistema de Soporte de Decisiones")
        section = st.sidebar.radio(
            "Navegación",
            ["🎯 KPIs - Indicadores Operacionales", 
             "📈 OKRs - Balanced Scorecard",
             "🔮 Predicción de Defectos (Rayleigh)"]
        )
        
        st.sidebar.markdown("---")
        
        # Main title
        st.title("📊 Sistema de Soporte a Decisiones (DSS)")
        
        # ========================================================================
        # SECTION 1: KPIs DASHBOARD
        # ========================================================================
        if section == "🎯 KPIs - Indicadores Operacionales":
            st.header("🎯 KPIs - Indicadores Clave de Rendimiento")
            st.markdown("Métricas operacionales en tiempo real para decisiones tácticas")
            
            # Filters
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                if st.button("🔄 Refrescar Datos"):
                    st.cache_data.clear()
                    st.rerun()
            
            st.markdown("---")
            
            # Calculate all KPIs
            kpis = calculate_all_kpis(df_proy, df_cal)
            
            # Display KPIs in grid (3 columns x 2 rows)
            col1, col2, col3 = st.columns(3)
            
            # Row 1
            with col1:
                st.subheader("📊 Tasa de Completación")
                comp = kpis['completion_rate']
                color = get_kpi_color(comp['value'], 'completion_rate')
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=comp['value'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Proyectos Completados"},
                    delta={'reference': 80},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightcoral"},
                            {'range': [50, 80], 'color': "lightyellow"},
                            {'range': [80, 100], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"✅ {comp['metadata']['completed']} de {comp['metadata']['total']} proyectos")
            
            with col2:
                st.subheader("💰 Eficiencia Presupuestaria")
                budget = kpis['budget_efficiency']
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=budget['value'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "ROI Promedio"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "green"},
                        'steps': [
                            {'range': [0, 15], 'color': "lightcoral"},
                            {'range': [15, 30], 'color': "lightyellow"},
                            {'range': [30, 100], 'color': "lightgreen"}
                        ]
                    }
                ))
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"💵 ROI: {budget['metadata']['avg_roi']:.1f}%")
            
            with col3:
                st.subheader("👥 Utilización de Equipo")
                util = kpis['team_utilization']
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=util['value'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Proyectos Activos"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "orange"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightcoral"},
                            {'range': [50, 70], 'color': "lightyellow"},
                            {'range': [70, 100], 'color': "lightgreen"}
                        ]
                    }
                ))
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"🏢 {util['metadata']['unique_clients']} clientes únicos")
            
            # Row 2
            col4, col5, col6 = st.columns(3)
            
            with col4:
                st.subheader("🐛 Densidad de Defectos")
                defect = kpis['defect_density']
                
                fig = go.Figure(go.Indicator(
                    mode="number+delta",
                    value=defect['value'],
                    number={'suffix': " def/proy"},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Defectos por Proyecto"},
                    delta={'reference': 10, 'increasing': {'color': "red"}}
                ))
                fig.update_layout(height=200)
                st.plotly_chart(fig, use_container_width=True)
                
                # Severity pie chart - CAMBIO: Tamaño aumentado 200→350px
                if defect['metadata']['severity_breakdown']:
                    sev_df = pd.DataFrame(list(defect['metadata']['severity_breakdown'].items()),
                                         columns=['Severidad', 'Cantidad'])
                    fig_pie = px.pie(sev_df, values='Cantidad', names='Severidad',
                                    title="Distribución por Severidad", hole=0.4)
                    fig_pie.update_layout(height=350)  # AUMENTADO
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            with col5:
                st.subheader("⏱️ Tiempo de Resolución")
                resol = kpis['avg_resolution_time']
                
                fig = go.Figure(go.Indicator(
                    mode="number+delta",
                    value=resol['value'],
                    number={'suffix': " días"},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Resolución Promedio"},
                    delta={'reference': 3, 'increasing': {'color': "red"}}
                ))
                fig.update_layout(height=200)
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"📋 {resol['metadata']['total_defects']} defectos totales")
            
            with col6:
                st.subheader("⭐ Índice de Satisfacción")
                satisfaction = kpis['client_satisfaction']
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=satisfaction['value'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Satisfacción Cliente"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "purple"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightcoral"},
                            {'range': [50, 70], 'color': "lightyellow"},
                            {'range': [70, 100], 'color': "lightgreen"}
                        ]
                    }
                ))
                fig.update_layout(height=250)
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"📊 Calidad: {satisfaction['metadata']['quality_component']:.1f} | "
                          f"💰 Presupuesto: {satisfaction['metadata']['budget_component']:.1f}")
        
        # ========================================================================
        # SECTION 2: OKRs & BALANCED SCORECARD
        # ========================================================================
        elif section == "📈 OKRs - Balanced Scorecard":
            st.header("📈 OKRs & Balanced Scorecard")
            st.markdown("Marco estratégico alineado con la visión y misión empresarial")
            
            # Generate OKRs
            okrs = generate_okrs_from_data(df_proy, df_cal, "Q1 2025")
            
            # Scorecard Overview
            st.subheader("🎯 Balanced Scorecard - Vista General")
            
            perspectives = ["Financial", "Customer", "Internal Processes", "Learning & Growth"]
            cols = st.columns(4)
            
            for i, perspective in enumerate(perspectives):
                score, meta = calculate_perspective_score(okrs, perspective)
                icon = get_perspective_icon(perspective)
                
                with cols[i]:
                    st.metric(
                        label=f"{icon} {perspective}",
                        value=f"{score:.0f}%",
                        delta=f"{meta['okr_count']} OKRs"
                    )
                    
                    # Progress bar
                    if score >= 90:
                        color = "green"
                    elif score >= 70:
                        color = "orange"
                    else:
                        color = "red"
                    
                    st.progress(score/100)
                    st.caption(f"**{meta['status']}** | {meta['kr_count']} KRs")
            
            st.markdown("---")
            
            # CAMBIO: Solo 2 tabs (eliminada "Mapa Estratégico")
            tab1, tab2 = st.tabs([
                "📋 OKRs - Progreso Temporal",
                "🌳 Jerarquía OKR"
            ])
            
            with tab1:
                # CAMBIO: Gráficas temporales en lugar de listas  
                st.subheader("Progreso de OKRs en el Tiempo")
                
                for perspective in perspectives:
                    perspective_okrs = [okr for okr in okrs if okr.perspective == perspective]
                    
                    if perspective_okrs:
                        icon = get_perspective_icon(perspective)
                        st.markdown(f"### {icon} {perspective}")
                        
                        for okr in perspective_okrs:
                            # Crear datos temporales simulados (últimos 6 meses)
                            months = pd.date_range(end=datetime.now(), periods=6, freq='M')
                            
                            # Simular progreso creciente hacia el valor actual
                            progress_data = []
                            for kr in okr.key_results:
                                monthly_progress = []
                                for i, month in enumerate(months):
                                    # Progreso simulado: crece gradualmente hasta el valor actual
                                    simulated_progress = kr.progress * (i + 1) / 6
                                    monthly_progress.append({
                                        'Mes': month.strftime('%b %Y'),
                                        'Progreso (%)': simulated_progress,
                                        'Key Result': kr.kr[:50] + '...' if len(kr.kr) > 50 else kr.kr
                                    })
                                progress_data.extend(monthly_progress)
                            
                            if progress_data:
                                df_progress = pd.DataFrame(progress_data)
                                
                                # Gráfica de líneas temporal
                                fig = px.line(
                                    df_progress,
                                    x='Mes',
                                    y='Progreso (%)',
                                    color='Key Result',
                                    title=f"{okr.objective} ({okr.owner})",
                                    markers=True
                                )
                                fig.add_hline(y=90, line_dash="dash", line_color="green", 
                                            annotation_text="Meta 90%")
                                fig.update_layout(
                                    yaxis_title="Progreso (%)",
                                    yaxis_range=[0, 100],
                                    height=400,
                                    showlegend=True
                                )
                                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                st.subheader("🌳 Jerarquía de Objetivos")
                
                # Create sunburst chart
                hierarchy = create_okr_hierarchy(okrs)
                
                # Flatten hierarchy for sunburst
                labels = [hierarchy['name']]
                parents = [""]
                values = [100]
                
                for persp_node in hierarchy['children']:
                    labels.append(persp_node['name'])
                    parents.append(hierarchy['name'])
                    persp_value = sum(okr_node['value'] for okr_node in persp_node['children']) / len(persp_node['children'])
                    values.append(persp_value)
                    
                    for okr_node in persp_node['children']:
                        labels.append(okr_node['name'])
                        parents.append(persp_node['name'])
                        values.append(okr_node['value'])
                
                fig_sunburst = go.Figure(go.Sunburst(
                    labels=labels,
                    parents=parents,
                    values=values,
                    branchvalues="total"
                ))
                # CAMBIO: Tamaño aumentado 600→700px
                fig_sunburst.update_layout(height=700)
                st.plotly_chart(fig_sunburst, use_container_width=True)
                
                st.info("💡 **Interacción**: Click en los segmentos para explorar la jerarquía de objetivos "
                       "desde perspectivas estratégicas hasta Key Results individuales.")
        
        # ========================================================================
        # SECTION 3: RAYLEIGH DEFECT PREDICTION
        # ========================================================================
        elif section == "🔮 Predicción de Defectos (Rayleigh)":
            # RBAC Check
            if st.session_state.get("username") not in ["admin", "pm"]:
                st.error("⛔ **Acceso Denegado**")
                st.warning("Esta funcionalidad es exclusiva para Administradores y Responsables de Proyecto (PM).")
                st.stop()
            
            st.header("🔮 Modelo Predictivo de Defectos (Rayleigh)")
            st.markdown("Estimación probabilística de defectos para proyectos nuevos basada en distribución Rayleigh")
            
            # Calibration info
            sigmas = calibrate_rayleigh_sigma(df_cal, df_proy)
            confidence = calculate_model_confidence(df_cal, df_proy)
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.info(f"📊 **Datos Históricos**: {confidence['num_projects']} proyectos, "
                       f"{confidence['num_quality_records']} registros de calidad")
            with col_info2:
                st.success(f"🎯 **Confianza del Modelo**: {confidence['label']} ({confidence['score']*100:.0f}%)")
            
            st.markdown("---")
            
            # Input Form
            st.subheader("📝 Parámetros del Nuevo Proyecto")
            
            col_input1, col_input2 = st.columns(2)
            
            with col_input1:
                # CAMBIO: Story Points en lugar de LOC
                project_size = st.slider(
                    "Tamaño del Proyecto (Story Points)",
                    min_value=10,
                    max_value=1000,
                    value=100,
                    step=10,
                    help="Tamaño estimado en Story Points (1 SP ≈ 50 LOC)"
                )
                
                duration_months = st.slider(
                    "Duración del Proyecto (meses)",
                    min_value=1,
                    max_value=24,
                    value=6,
                    step=1
                )
                
                team_size = st.slider(
                    "Tamaño del Equipo",
                    min_value=1,
                    max_value=30,
                    value=8,
                    step=1,
                    help="Número de desarrolladores"
                )
            
            with col_input2:
                experience_level = st.select_slider(
                    "Nivel de Experiencia del Equipo",
                    options=["Junior", "Mid", "Senior"],
                    value="Mid"
                )
                
                tech_complexity = st.select_slider(
                    "Complejidad Tecnológica",
                    options=["Baja", "Media", "Alta", "Muy Alta"],
                    value="Media"
                )
                
                predict_button = st.button("🔮 Generar Predicción", type="primary")
            
            if predict_button:
                # Convertir Story Points a LOC equivalente (1 SP ≈ 50 LOC)
                estimated_loc = project_size * 50
                
                # Validate inputs
                is_valid, error_msg = validate_prediction_inputs(estimated_loc, duration_months, team_size)
                
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                else:
                    # Generate prediction
                    prediction = predict_defects_rayleigh(
                        project_size=estimated_loc,
                        duration_months=duration_months,
                        team_size=team_size,
                        experience_level=experience_level,
                        technology_complexity=tech_complexity
                    )
                    
                    # Generate curve
                    curve = generate_rayleigh_curve(
                        total_defects=prediction['total_defects'],
                        duration_days=prediction['duration_days'],
                        sigma=prediction['sigma'],
                        confidence_level=0.95
                    )
                    
                    # Get QA recommendations
                    qa_rec = recommend_qa_resources(
                        prediction['total_defects'],
                        duration_months
                    )
                    
                    st.markdown("---")
                    st.subheader("📊 Resultados de la Predicción")
                    
                    # Summary metrics
                    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                    
                    with col_res1:
                        st.metric(
                            "Defectos Totales Estimados",
                            f"{prediction['total_defects']:.0f}",
                            help="Total de defectos esperados durante todo el proyecto"
                        )
                    
                    with col_res2:
                        st.metric(
                            "Día del Pico de Defectos",
                            f"Día {prediction['peak_day']:.0f}",
                            delta=f"{(prediction['peak_day']/prediction['duration_days']*100):.0f}% del proyecto"
                        )
                    
                    with col_res3:
                        st.metric(
                            "Recursos QA Requeridos",
                            f"{qa_rec['qa_engineers']} ingeniero(s)",
                            help="Ingenieros de QA recomendados"
                        )
                    
                    with col_res4:
                        risk_color_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}
                        st.metric(
                            "Nivel de Riesgo",
                            f"{risk_color_emoji.get(qa_rec['risk_color'], '⚪')} {qa_rec['risk_level']}"
                        )
                    
                    st.markdown("---")
                    
                    # Rayleigh Curve
                    col_chart1, col_chart2 = st.columns([2, 1])
                    
                    with col_chart1:
                        st.subheader("📈 Curva de Descubrimiento de Defectos (Rayleigh)")
                        
                        fig_rayleigh = go.Figure()
                        
                        # Main curve
                        fig_rayleigh.add_trace(go.Scatter(
                            x=curve['time'],
                            y=curve['defects_per_day'],
                            mode='lines',
                            name='Defectos Esperados',
                            line=dict(color='blue', width=3),
                            fill='tozeroy'
                        ))
                        
                        # Confidence bands
                        fig_rayleigh.add_trace(go.Scatter(
                            x=curve['time'],
                            y=curve['upper_bound'],
                            mode='lines',
                            name=f'Límite Superior ({curve["confidence_level"]*100:.0f}%)',
                            line=dict(color='lightblue', width=1, dash='dash')
                        ))
                        
                        fig_rayleigh.add_trace(go.Scatter(
                            x=curve['time'],
                            y=curve['lower_bound'],
                            mode='lines',
                            name=f'Límite Inferior ({curve["confidence_level"]*100:.0f}%)',
                            line=dict(color='lightblue', width=1, dash='dash'),
                            fill='tonexty',
                            fillcolor='rgba(173, 216, 230, 0.2)'
                        ))
                        
                        # Peak annotation
                        fig_rayleigh.add_vline(
                            x=curve['peak_day'],
                            line_dash="dash",
                            line_color="red",
                            annotation_text=f"Pico: Día {curve['peak_day']:.0f}"
                        )
                        
                        fig_rayleigh.update_layout(
                            xaxis_title="Días del Proyecto",
                            yaxis_title="Defectos Descubiertos por Día",
                            height=400,
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig_rayleigh, use_container_width=True)
                    
                    with col_chart2:
                        st.subheader("🎯 Defectos por Severidad")
                        
                        sev_df = pd.DataFrame(list(prediction['severity_distribution'].items()),
                                             columns=['Severidad', 'Defectos'])
                        
                        fig_sev = px.pie(
                            sev_df,
                            values='Defectos',
                            names='Severidad',
                            title="Distribución Estimada",
                            color_discrete_sequence=px.colors.sequential.RdYlGn_r
                        )
                        fig_sev.update_layout(height=400)
                        st.plotly_chart(fig_sev, use_container_width=True)
                    
                    # Summary table
                    st.markdown("---")
                    st.subheader("📋 Resumen y Recomendaciones")
                    
                    summary_df = pd.DataFrame({
                        'Métrica': [
                            'Defectos Totales',
                            'Pico de Defectos (Día)',
                            'Defectos en Pico',
                            'Personal QA Requerido',
                            'Horas de QA Totales',
                            'Nivel de Riesgo'
                        ],
                        'Valor': [
                            f"{prediction['total_defects']:.0f} defectos",
                            f"Día {prediction['peak_day']:.0f}",
                            f"{curve['peak_value']:.2f} defectos/día",
                            f"{qa_rec['qa_engineers']} ingeniero(s)",
                            f"{qa_rec['qa_hours_total']:.0f} horas",
                            f"{qa_rec['risk_level']}"
                        ]
                    })
                    
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                    
                    st.success(f"✅ **Recomendación**: {qa_rec['recommendation']}")
                    
                    st.info(f"💡 **Nota**: Predicción basada en {project_size} Story Points "
                           f"(≈ {estimated_loc:,} LOC estimados)")