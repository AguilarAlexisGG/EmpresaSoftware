# Sistema de Soporte a Decisiones (DSS)

Este proyecto implementa un Sistema de Soporte a Decisiones (DSS) para una empresa de desarrollo de software, diseñado para optimizar la gestión de proyectos y la calidad del software.

## 📋 Características Principales

### 1. Dashboard Estratégico (Balanced Scorecard)
- **Perspectiva Financiera**: Monitoreo de Ganancia Neta, Margen de Beneficio y Costos.
- **Perspectiva del Cliente**: Análisis de rentabilidad por cliente y geolocalización.
- **Perspectiva de Procesos**: Seguimiento de defectos y métricas de calidad.

### 2. Modelo Predictivo (Montecarlo + Rayleigh)
- **Simulación Estocástica**: Proyección de defectos futuros basada en datos históricos.
- **Curva de Rayleigh**: Estimación de la distribución temporal de hallazgos de defectos.
- **Herramienta de Planificación**: Permite a los Project Managers estimar recursos de QA necesarios.

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
├── app.py                  # Aplicación principal (Streamlit)
├── etl/                    # Scripts de procesamiento de datos
│   ├── ETL.py              # Lógica de transformación y carga
│   └── datosSinteticos.py  # Generador de datos de prueba
├── OLAP_Proyectos.csv      # Datos procesados de proyectos
├── OLAP_Calidad.csv        # Datos procesados de calidad
├── requirements.txt        # Dependencias del proyecto
├── DOCUMENTACION.md        # Documentación técnica detallada
└── reporte_proyecto.tex    # Reporte académico en LaTeX
```

## 🛠️ Tecnologías Utilizadas
- **Python**: Lenguaje principal.
- **Streamlit**: Framework para la interfaz de usuario.
- **Pandas/NumPy**: Procesamiento y análisis de datos.
- **Plotly**: Visualizaciones interactivas.
