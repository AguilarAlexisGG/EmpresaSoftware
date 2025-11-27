# Documentación Técnica del Sistema DSS

## 1. Arquitectura del Sistema

El sistema sigue una arquitectura de **Aplicación de Datos Monolítica** basada en Streamlit, con un desacoplamiento lógico entre la capa de presentación, la lógica de negocio y la capa de datos.

### Diagrama de Flujo
1.  **Fuentes de Datos**: Scripts de generación sintética (`etl/datosSinteticos.py`).
2.  **ETL**: Procesamiento batch (`etl/ETL.py`) que genera cubos OLAP planos.
3.  **Data Warehouse**: Archivos CSV (`OLAP_Proyectos.csv`, `OLAP_Calidad.csv`).
4.  **Frontend**: Aplicación interactiva (`app.py`) que consume los CSV en memoria.

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
-   **Librerías**: `numpy` para la generación de números aleatorios y cálculo vectorial.
-   **Visualización**: `plotly.graph_objects` para graficar la curva de densidad de probabilidad.

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
1.  Modificar `etl/ETL.py` para calcular la nueva métrica y guardarla en el CSV.
2.  Editar `app.py` para leer la nueva columna y agregar un componente `st.metric`.
