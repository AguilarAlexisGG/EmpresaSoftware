# Documentación Técnica del Sistema DSS

## 1. Arquitectura del Sistema

El sistema sigue una arquitectura de **Aplicación de Datos Monolítica** basada en Streamlit, con un desacoplamiento lógico entre la capa de presentación, la lógica de negocio y la capa de datos.

### Diagrama de Flujo
1. **Fuentes de Datos**: Scripts de generación sintética (`etl/datosSinteticos.py`).
2. **ETL**: Procesamiento batch (`etl/ETL.py`) que genera cubos OLAP planos.
3. **Data Warehouse**: Archivos CSV (`OLAP_Proyectos.csv`, `OLAP_Calidad.csv`).
4. **Módulos DSS**: Cuatro módulos especializados:
   - `olap_functions.py`: Operaciones OLAP (slice, dice, drill-down, roll-up, pivot)
   - `kpi_calculator.py`: Cálculo de 6 KPIs con metadata y colores
   - `balanced_scorecard.py`: Generación de OKRs desde datos
   - `rayleigh_model.py`: Predicción de defectos con Rayleigh
5. **Frontend**: Aplicación interactiva (`app.py`) con navegación sidebar y visualizaciones Plotly.

## 2. Procesos ETL (Extracción, Transformación y Carga)

### Generación de Datos
El script `etl/datosSinteticos.py` simula la operación de una empresa de software, creando:
-   **Proyectos**: Con fechas, presupuestos y estados.
-   **Transacciones**: Ingresos y gastos asociados a proyectos.
-   **Calidad**: Reportes de defectos con severidad y estado.

### Transformación (ETL.py)
El script principal de ETL realiza las siguientes tareas:
-   **Limpieza**: Manejo de nulos y formatos de fecha.
-   **Agregación**: Cálculo de `ganancia_neta`, `costo_total_real` y `margen`.
-   **Desnormalización**: Cruce de tablas para crear vistas planas optimizadas para lectura (OLAP).

## 3. Modelo Predictivo (Rayleigh)

El módulo de predicción (`app.py` -> Tab 2) implementa un modelo estocástico para la gestión de calidad.

### Fundamento Matemático
Se basa en la **Curva de Rayleigh**, que modela la tasa de descubrimiento de defectos en el ciclo de vida del software:

$$ f(t) = \frac{2K}{t_m} \frac{t}{t_m} e^{-(t/t_m)^2} $$

-   **$K$ (Volumen de Defectos)**: Estimado mediante **Simulación de Montecarlo** (10,000 iteraciones) usando la media y desviación estándar histórica de la empresa.
-   **$t_m$ (Tiempo Pico)**: Estimado como el 40% de la duración promedio del proyecto.

### Implementación
-   **Input**: Story Points (convertidos a LOC internamente: 1 SP = 50 LOC)
-   **Cálculo de $K$**: Basado en defectos históricos por tamaño de proyecto
-   **Ajuste $t_m$**: Calibrado según duración del proyecto y experiencia del equipo
-   **Librerías**: `scipy.stats` para distribución Rayleigh y cálculos estadísticos
-   **Visualización**: `plotly.graph_objects` para curva con intervalos de confianza (95%)
-   **Salida**: Defectos totales, día de pico, recursos QA recomendados, nivel de riesgo

### Mejoras Recientes (UX)
-   **Gráficas Temporales OKR**: Progreso de Key Results en últimos 6 meses (line charts)
-   **Visualizaciones Aumentadas**: Pie charts (350px) y Sunburst (700px) para mejor legibilidad
-   **Story Points**: Métrica ágil para estimación de proyectos

## 4. Seguridad

### Autenticación y Autorización
-   **Mecanismo**: Validación contra credenciales almacenadas en `st.secrets`.
-   **Persistencia**: Uso de `st.session_state` para mantener la sesión del usuario activa entre recargas.
-   **RBAC**:
    -   `admin` / `pm`: Acceso completo.
    -   `invitado`: Acceso restringido (sin predicción).

## 5. Guía de Mantenimiento

### Actualización de Datos
Para refrescar los datos del dashboard con nueva información:
1.  Ejecutar `python etl/datosSinteticos.py` (Opcional, para nuevos datos random).
2.  Ejecutar `python etl/ETL.py`.
3.  Recargar la página web (F5) o reiniciar el servidor Streamlit.

### Agregar Nuevos KPIs
1.  Crear función de cálculo en `kpi_calculator.py` siguiendo el patrón existente.
2.  Agregar metada de colores y umbrales.
3.  Integrar en `app.py` sección KPIs con gauge chart o métrica.

### Modificar OKRs
1.  Editar `balanced_scorecard.py` en función `generate_okrs_from_data()`.
2.  Ajustar perspectivas, objetivos o Key Results según necesidades estratégicas.
3.  Las gráficas se generan automáticamente desde los datos de OKR.

## 6. Módulos Implementados

### olap_functions.py
Operaciones OLAP sobre DataFrames de Pandas:
- `slice_olap()`: Filtrado por dimensión específica
- `dice()`: Filtrado múltiple por varias dimensiones  
- `drill_down()`: Desagregación de datos
- `roll_up()`: Agregación de datos
- `pivot()`: Tabla pivote multidimensional

### kpi_calculator.py  
6 KPIs operacionales:
1. Tasa de Completación (proyectos terminados/total)
2. Eficiencia Presupuestaria (ROI promedio)
3. Utilización de Equipo (% proyectos activos)
4. Densidad de Defectos (defectos/proyecto)
5. Tiempo Promedio de Resolución (días)
6. Índice de Satisfacción Cliente (métrica compuesta)

### balanced_scorecard.py
Generación automática de OKRs:
- 4 perspectivas del Balanced Scorecard
- 2 objetivos por perspectiva (8 total)
- 3-4 Key Results por objetivo
- Cálculo de scores y jerarquías

### rayleigh_model.py
Predicción de defectos:
- Calibración de parámetro sigma desde datos históricos
- Predicción de defectos totales
- Generación de curva con intervalos de confianza
- Recomendación de recursos QA
- Cálculo de nivel de riesgo del proyecto
