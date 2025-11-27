import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema de Soporte a Decisiones", layout="wide")

# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        df_p = pd.read_csv('OLAP_Proyectos.csv')
        df_c = pd.read_csv('OLAP_Calidad.csv')
        return df_p, df_c
    except FileNotFoundError:
        st.error("⚠️ No se encontraron los archivos OLAP_*.csv en el repositorio.")
        return None, None

df_proy, df_cal = load_data()

if df_proy is not None and df_cal is not None:
        
    # TÍTULO Y SIDEBAR
    st.title("📊 Sistema de Soporte a Decisiones (DSS)")
    st.sidebar.header("Filtros")
    
    # Filtro de Año (Extraído dinámicamente)
    if 'año' in df_proy.columns:
        años = sorted(df_proy['año'].unique(), reverse=True)
        anio_sel = st.sidebar.selectbox("Seleccionar Año Fiscal", años)
        
        # Filtrar Dataframes
        df_proy_f = df_proy[df_proy['año'] == anio_sel]
        df_cal_f = df_cal[df_cal['año'] == anio_sel]
    else:
        st.warning("No se encontró columna 'año'. Mostrando todos los datos.")
        df_proy_f = df_proy
        df_cal_f = df_cal

    # --- TABS DE NAVEGACIÓN ---
    tab1, tab2, tab3 = st.tabs(["📈 Balanced Scorecard", "🎲 Predicción Montecarlo", "🔎 Explorador de Datos"])

    # ==========================================================================
    # TAB 1: BALANCED SCORECARD
    # ==========================================================================
    with tab1:
        st.header(f"Tablero Estratégico - {anio_sel}")
        
        # 1. FINANCIERA
        st.subheader("1. Perspectiva Financiera")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        ganancia = df_proy_f['ganancia_neta'].sum()
        venta = df_proy_f.get('valor_venta', df_proy_f['costo_total_real'] + df_proy_f['ganancia_neta']).sum() # Calculo fallback
        margen = (ganancia / venta * 100) if venta > 0 else 0
        
        kpi1.metric("Ganancia Neta", f"${ganancia:,.0f}")
        kpi2.metric("Margen de Beneficio", f"{margen:.1f}%", delta="Meta: >20%")
        kpi3.metric("Costo Operativo", f"${df_proy_f['costo_total_real'].sum():,.0f}")
        kpi4.metric("Proyectos Cerrados", len(df_proy_f))
        
        # 2. CLIENTES
        st.subheader("2. Perspectiva del Cliente")
        c1, c2 = st.columns(2)
        
        # Top Clientes
        top_cli = df_proy_f.groupby('nombre_cliente')['ganancia_neta'].sum().nlargest(5).reset_index()
        fig_cli = px.bar(top_cli, x='ganancia_neta', y='nombre_cliente', orientation='h', title="Top 5 Clientes (Rentabilidad)")
        c1.plotly_chart(fig_cli, use_container_width=True)
        
        # Mapa de Calor (Países)
        paises = df_proy_f.groupby('nombre_pais')['ganancia_neta'].sum().reset_index()
        fig_map = px.choropleth(paises, locations='nombre_pais', locationmode='country names', color='ganancia_neta', title="Rentabilidad por País")
        c2.plotly_chart(fig_map, use_container_width=True)

        # 3. PROCESOS INTERNOS (CALIDAD)
        st.subheader("3. Perspectiva de Procesos (Calidad)")
        try:
            total_defectos = df_cal_f['cantidad_defectos_encontrados'].sum()
            defectos_criticos = df_cal_f[df_cal_f['severidad'] == 'crítica']['cantidad_defectos_encontrados'].sum()
            
            kp_q1, kp_q2, kp_q3 = st.columns(3)
            kp_q1.metric("Total Defectos Detectados", total_defectos)
            kp_q2.metric("Defectos Críticos", defectos_criticos, delta_color="inverse")
            
            # Gráfica de Severidad
            sev_data = df_cal_f.groupby('severidad')['cantidad_defectos_encontrados'].sum().reset_index()
            fig_sev = px.pie(sev_data, names='severidad', values='cantidad_defectos_encontrados', title="Distribución de Severidad", hole=0.4)
            kp_q3.plotly_chart(fig_sev, use_container_width=True)
        except Exception as e:
            st.info("No hay datos de calidad para este periodo.")

    # ==========================================================================
    # TAB 2: PREDICCIÓN MONTECARLO
    # ==========================================================================
    with tab2:
        st.header("🔮 Simulador de Riesgos de Calidad")
        st.markdown("Este modelo utiliza la historia de tus proyectos para predecir cuántos defectos tendrá el **próximo proyecto**.")
        
        col_params, col_sim = st.columns([1, 2])
        
        with col_params:
            st.subheader("Configuración")
            # 1. Entrenar con datos históricos
            historial_defectos = df_cal.groupby('nombre_proyecto')['cantidad_defectos_encontrados'].sum()
            mu = historial_defectos.mean()
            sigma = historial_defectos.std()
            
            st.info(f"📊 Datos Históricos:\n- Promedio: {mu:.1f} defectos/proy\n- Desviación: {sigma:.1f}")
            
            n_sims = st.slider("Simulaciones", 1000, 10000, 5000)
            confianza = st.slider("Certeza requerida", 0.80, 0.99, 0.95)
            
            btn_simular = st.button("Ejecutar Montecarlo", type="primary")
            
        with col_sim:
            if btn_simular:
                # SIMULACIÓN MONTECARLO
                # Asumimos distribución normal truncada (no hay defectos negativos)
                simulacion = np.random.normal(mu, sigma, n_sims)
                simulacion = np.maximum(simulacion, 0) # Truncar a 0
                
                # Resultados
                max_esperado = np.percentile(simulacion, confianza * 100)
                media_sim = np.mean(simulacion)
                
                # Gráfico
                fig_hist = px.histogram(simulacion, nbins=50, title="Probabilidad de Cantidad de Defectos", labels={'value': 'Defectos Totales'})
                fig_hist.add_vline(x=max_esperado, line_dash="dash", line_color="red", annotation_text=f"Límite {confianza*100:.0f}%")
                fig_hist.add_vline(x=media_sim, line_dash="dash", line_color="green", annotation_text="Promedio")
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # CURVA RAYLEIGH PROYECTADA
                st.subheader("Curva de Descubrimiento Esperada (Rayleigh)")
                
                # Parámetros Rayleigh
                K = media_sim # Area total bajo la curva
                duracion_promedio = 180 # Días (estimado o calculado si tienes fechas inicio/fin)
                tm = duracion_promedio * 0.4 # El pico suele ser al 40% del proyecto
                
                t = np.linspace(0, duracion_promedio, 100)
                # Formula Rayleigh PDF para Software
                defectos_t = (2 * K / tm) * (t / tm) * np.exp(-(t/tm)**2)
                
                fig_ray = go.Figure()
                fig_ray.add_trace(go.Scatter(x=t, y=defectos_t, mode='lines', fill='tozeroy', name='Tendencia Esperada'))
                fig_ray.update_layout(xaxis_title="Días de Proyecto", yaxis_title="Defectos Nuevos por Día")
                st.plotly_chart(fig_ray, use_container_width=True)
                
                st.success(f"CONCLUSIÓN: Deberías planificar recursos de QA para mitigar hasta **{int(max_esperado)}** defectos totales, esperando el pico de trabajo alrededor del día **{int(tm)}**.")

    # ==========================================================================
    # TAB 3: EXPLORADOR
    # ==========================================================================
    with tab3:
        st.subheader("Base de Datos OLAP")
        st.dataframe(df_proy_f, use_container_width=True)