# Sistema de Soporte a Decisiones (DSS)

Este proyecto implementa un Sistema de Soporte a Decisiones (DSS) para una empresa de desarrollo de software, diseñado para optimizar la gestión de proyectos y la calidad del software.

## 📋 Características Principales

### 1. KPIs Dashboard - Indicadores Operacionales
- **6 Métricas Clave**: Tasa de Completación, Eficiencia Presupuestaria, Utilización de Equipo, Densidad de Defectos, Tiempo de Resolución e Índice de Satisfacción.
- **Visualizaciones Interactivas**: Gauge charts, pie charts y métricas con drill-down por severidad.
- **Actualización en Tiempo Real**: Botón de refrescar datos desde OLAP cubes.

### 2. OKRs & Balanced Scorecard
- **4 Perspectivas Estratégicas**: Financial, Customer, Internal Processes, Learning & Growth.
- **Gráficas de Progreso Temporal**: Visualización de avance de OKRs en los últimos 6 meses.
- **Jerarquía Interactiva**: Sunburst chart que muestra objetivos, Key Results y su interrelación.
- **Automático desde Datos**: OKRs generados dinámicamente desde métricas de proyectos.

### 3. Modelo Predictivo de Defectos (Rayleigh)
- **Input en Story Points**: Estimación ágil (1 SP ≈ 50 LOC) para proyectos nuevos.
- **Curva de Rayleigh**: Distribución temporal de defectos con intervalos de confianza 95%.
- **Recomendaciones QA**: Cálculo automático de recursos de Quality Assurance necesarios.
- **Análisis de Riesgo**: Clasificación de proyectos según densidad de defectos esperada.

### 3. Arquitectura de Datos
- **ETL Automatizado**: Scripts en Python para la generación y transformación de datos.
- **Almacenamiento ROLAP**: Estructura optimizada en archivos CSV (`OLAP_*.csv`).

## 🚀 Instalación y Ejecución

### Prerrequisitos
- Python 3.8 o superior.
- Pip (Gestor de paquetes de Python).

### Pasos
1.  **Clonar el repositorio**:
    ```bash
    git clone <url-del-repositorio>
    cd EmpresaSoftware
    ```

2.  **Crear un entorno virtual** (Recomendado):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # En Windows
    # source venv/bin/activate  # En Linux/Mac
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación**:
    ```bash
    streamlit run app.py
    ```

## 🔐 Credenciales de Acceso

El sistema cuenta con un control de acceso basado en roles (RBAC).

| Rol | Usuario | Contraseña | Permisos |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | Acceso Total (Dashboard + Predicción) |
| **Project Manager** | `pm` | `pm123` | Acceso Total (Dashboard + Predicción) |
| **Invitado** | `invitado` | `guest` | Solo Visualización (Dashboard) |

> **Nota**: Las credenciales se gestionan a través de `st.secrets` o el archivo `.streamlit/secrets.toml`.

## 📂 Estructura del Proyecto

```text
EmpresaSoftware/
├── app.py                    # Aplicación principal (Streamlit)
├── olap_functions.py         # Operaciones OLAP (slice, dice, drill-down, roll-up)
├── kpi_calculator.py         # Cálculo de 6 KPIs operacionales
├── balanced_scorecard.py     # Generación de OKRs y Balanced Scorecard
├── rayleigh_model.py         # Modelo predictivo de defectos (Rayleigh)
├── etl/                      # Scripts de procesamiento de datos
│   ├── ETL.py                # Lógica de transformación y carga
│   └── datosSinteticos.py    # Generador de datos de prueba
├── OLAP_Proyectos.csv        # Cubo OLAP de proyectos
├── OLAP_Calidad.csv          # Cubo OLAP de calidad y defectos
├── requirements.txt          # Dependencias del proyecto
├── README.md                 # Este archivo
└── DOCUMENTACION.md          # Documentación técnica detallada
```

## 🛠️ Tecnologías Utilizadas
- **Python**: Lenguaje principal.
- **Streamlit**: Framework para la interfaz de usuario.
- **Pandas/NumPy**: Procesamiento y análisis de datos.
- **Plotly**: Visualizaciones interactivas (gauges, sunburst, line charts).
- **SciPy**: Distribuciones estadísticas para modelo Rayleigh.

## 📊 Funcionalidades por Sección

### KPIs Dashboard
- Tasa de Completación con gauge chart
- Eficiencia Presupuestaria (ROI)
- Utilización de Equipo
- Densidad de Defectos con pie chart de severidad
- Tiempo Promedio de Resolución
- Índice de Satisfacción del Cliente

### OKRs & Balanced Scorecard
- Vista general con 4 perspectivas y progress bars
- Gráficas de líneas temporales (progreso últimos 6 meses)
- Sunburst chart de jerarquía de objetivos (3 niveles)

### Predicción Rayleigh  
- Input: Story Points, Duración, Tamaño Equipo, Experiencia, Complejidad
- Output: Curva de defectos, Pico de defectos, Recursos QA, Nivel de riesgo
- Restricción RBAC: Solo admin y pm
