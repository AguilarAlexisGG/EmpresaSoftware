# 📐 Metodología de Cálculo del DSS

## Introducción

Este documento explica detalladamente cómo se calculan todos los indicadores, métricas y predicciones mostrados en el Sistema de Soporte a Decisiones (DSS).

---

## 1. KPIs Dashboard - Indicadores Operacionales

### 1.1 Tasa de Completación

**Definición**: Porcentaje de proyectos completados exitosamente sobre el total de proyectos.

**Fórmula**:
```
Tasa de Completación (%) = (Proyectos Completados / Total de Proyectos) × 100
```

**Implementación** (`kpi_calculator.py`):
```python
completed = len(df_proy[df_proy['estado'] == 'Completado'])
total = len(df_proy)
completion_rate = (completed / total) * 100
```

**Interpretación de Colores**:
- 🟢 Verde: ≥ 80% (Excelente)
- 🟡 Amarillo: 50-79% (Aceptable)
- 🔴 Rojo: < 50% (Crítico)

**Ejemplo**:
- Proyectos completados: 412
- Total de proyectos: 475
- Tasa = (412/475) × 100 = **86.7%** 🟢

---

### 1.2 Eficiencia Presupuestaria

**Definición**: Retorno sobre la inversión (ROI) promedio de todos los proyectos.

**Fórmula**:
```
ROI (%) = ((Ganancia Neta - Costo Total) / Costo Total) × 100

Eficiencia Presupuestaria = Promedio(ROI de todos los proyectos)
```

**Implementación**:
```python
df_proy['roi'] = ((df_proy['ganancia_neta'] - df_proy['costo_total_real']) 
                  / df_proy['costo_total_real']) * 100
avg_roi = df_proy['roi'].mean()
```

**Interpretación**:
- 🟢 Verde: ROI ≥ 30%
- 🟡 Amarillo: ROI 15-29%
- 🔴 Rojo: ROI < 15%

**Ejemplo**:
- Proyecto A: Ganancia $100K, Costo $80K → ROI = 25%
- Proyecto B: Ganancia $150K, Costo $100K → ROI = 50%
- Promedio = **37.5%** 🟢

---

### 1.3 Utilización de Equipo

**Definición**: Porcentaje de clientes únicos atendidos sobre la capacidad total estimada.

**Fórmula**:
```
Utilización (%) = (Clientes Únicos Atendidos / Capacidad Total) × 100

Donde Capacidad Total es un parámetro estimado (ej. 50 clientes)
```

**Implementación**:
```python
unique_clients = df_proy['nombre_cliente'].nunique()
total_capacity = 50  # Estimado
utilization = (unique_clients / total_capacity) * 100
```

**Interpretación**:
- 🟢 Verde: ≥ 70% (Alta utilización)
- 🟡 Amarillo: 50-69% (Media)
- 🔴 Rojo: < 50% (Subutilización)

**Ejemplo**:
- Clientes atendidos: 38
- Capacidad: 50
- Utilización = (38/50) × 100 = **76%** 🟢

---

### 1.4 Densidad de Defectos

**Definición**: Número promedio de defectos por proyecto.

**Fórmula**:
```
Densidad = Total de Defectos / Número de Proyectos
```

**Implementación**:
```python
total_defects = df_calidad['cantidad_defectos'].sum()
num_projects = df_proy['nombre_proyecto'].nunique()
defect_density = total_defects / num_projects
```

**Drill-Down por Severidad**:
```python
severity_breakdown = df_calidad.groupby('severidad')['cantidad_defectos'].sum()
```

**Interpretación**:
- 🟢 Verde: < 5 defectos/proyecto
- 🟡 Amarillo: 5-10 defectos/proyecto
- 🔴 Rojo: > 10 defectos/proyecto

**Ejemplo**:
- Total defectos: 3,450
- Proyectos: 475
- Densidad = 3450/475 = **7.26 def/proy** 🟡

**Distribución por Severidad**:
- Crítica: 345 (10%)
- Alta: 1,035 (30%)
- Media: 1,380 (40%)
- Baja: 690 (20%)

---

### 1.5 Tiempo Promedio de Resolución

**Definición**: Días promedio que tarda resolverse un defecto desde su detección.

**Fórmula**:
```
Tiempo = Promedio(Fecha Resolución - Fecha Detección)
```

**Implementación**:
```python
df_calidad['fecha_resolucion'] = pd.to_datetime(df_calidad['fecha_resolucion'])
df_calidad['fecha_deteccion'] = pd.to_datetime(df_calidad['fecha_deteccion'])
df_calidad['dias_resolucion'] = (df_calidad['fecha_resolucion'] - 
                                   df_calidad['fecha_deteccion']).dt.days
avg_resolution_time = df_calidad['dias_resolucion'].mean()
```

**Análisis por Severidad**:
```python
resolution_by_severity = df_calidad.groupby('severidad')['dias_resolucion'].agg(['mean', 'count'])
```

**Interpretación**:
- 🟢 Verde: ≤ 2 días
- 🟡 Amarillo: 3-5 días
- 🔴 Rojo: > 5 días

**Ejemplo**:
- Promedio general: **3.2 días** 🟡
- Por severidad:
  - Crítica: 0.8 días
  - Alta: 2.1 días
  - Media: 4.5 días
  - Baja: 7.2 días

---

### 1.6 Índice de Satisfacción del Cliente

**Definición**: Métrica compuesta que combina calidad y cumplimiento presupuestario.

**Fórmula**:
```
Componente Calidad = 100 - (Densidad de Defectos × 10)
Componente Presupuesto = min(ROI Promedio, 100)

Satisfacción = (Componente Calidad × 0.6) + (Componente Presupuesto × 0.4)
```

**Implementación**:
```python
quality_component = max(0, 100 - (defect_density * 10))
budget_component = min(avg_roi, 100)
satisfaction = (quality_component * 0.6) + (budget_component * 0.4)
```

**Ponderaciones**:
- Calidad: 60% (más peso)
- Presupuesto: 40%

**Interpretación**:
- 🟢 Verde: ≥ 70 puntos
- 🟡 Amarillo: 50-69 puntos
- 🔴 Rojo: < 50 puntos

**Ejemplo**:
- Densidad defectos: 7.26 → Calidad = 100 - (7.26 × 10) = 27.4
- ROI promedio: 37.5 → Presupuesto = 37.5
- Satisfacción = (27.4 × 0.6) + (37.5 × 0.4) = **31.4 puntos** 🔴

---

## 2. Balanced Scorecard & OKRs

### 2.1 Generación de OKRs desde Datos

Los OKRs (Objectives and Key Results) se generan automáticamente desde las métricas de los proyectos.

**Estructura**:
- **4 Perspectivas**: Financial, Customer, Internal Processes, Learning & Growth
- **2 Objetivos por Perspectiva** = 8 objetivos totales
- **3-4 Key Results por Objetivo** = ~28 Key Results totales

### 2.2 Perspectiva Financial

**Objetivo 1**: Maximizar Rentabilidad

**Key Results**:
1. **ROI Promedio ≥ 35%**
   - Cálculo: `avg_roi = df_proy['roi'].mean()`
   - Progreso: `(avg_roi / 35) * 100`

2. **Ganancia Neta Total ≥ $5M**
   - Cálculo: `total_ganancia = df_proy['ganancia_neta'].sum()`
   - Progreso: `(total_ganancia / 5_000_000) * 100`

3. **Margen de Beneficio ≥ 25%**
   - Cálculo: `margen = ((ganancia - costo) / ganancia) * 100`
   - Progreso: `(margen / 25) * 100`

**Objetivo 2**: Optimizar Costos

**Key Results**:
1. **Reducir Sobrecostos a < 10%**
   - Cálculo: `sobrecosto = ((costo_real - costo_estimado) / costo_estimado) * 100`
   - Progreso: `100 - sobrecosto_prom` (inverso)

2. **Eficiencia Operativa ≥ 80%**
   - Métrica compuesta de tiempo y presupuesto

### 2.3 Perspectiva Customer

**Objetivo 1**: Aumentar Satisfacción

**Key Results**:
1. **Índice Satisfacción ≥ 85**
   - Cálculo: Ver sección 1.6
   - Progreso: `(satisfaccion / 85) * 100`

2. **Tasa Retención Clientes ≥ 90%**
   - Cálculo: `clientes_repetidos / total_clientes`

**Objetivo 2**: Expandir Cartera

**Key Results**:
1. **Nuevos Clientes ≥ 15**
   - Conteo directo
   - Progreso: `(nuevos / 15) * 100`

2. **Proyectos por Cliente ≥ 3**
   - Promedio de proyectos

### 2.4 Perspectiva Internal Processes

**Objetivo 1**: Mejorar Calidad

**Key Results**:
1. **Densidad Defectos < 5 def/proy**
   - Cálculo: Ver sección 1.4
   - Progreso: `(1 - (densidad / 10)) * 100` (inverso)

2. **Tiempo Resolución < 3 días**
   - Cálculo: Ver sección 1.5
   - Progreso: `(3 / tiempo_prom) * 100` (inverso)

**Objetivo 2**: Optimizar Entrega

**Key Results**:
1. **Tasa Completación ≥ 90%**
   - Cálculo: Ver sección 1.1
   - Progreso: `(tasa / 90) * 100`

2. **Tiempo Promedio Proyecto ≤ 6 meses**
   - Análisis de duración

### 2.5 Perspectiva Learning & Growth

**Objetivo 1**: Desarrollar Talento

**Key Results**:
1. **Capacitación ≥ 40 hrs/año por empleado**
   - Dato externo o estimado

2. **Certificaciones ≥ 3 por equipo**
   - Conteo

**Objetivo 2**: Mejorar Procesos

**Key Results**:
1. **Adopción Mejores Prácticas ≥ 85%**
   - Métrica de calidad

2. **Automatización ≥ 50% tareas repetitivas**
   - Análisis de procesos

### 2.6 Cálculo de Scores por Perspectiva

**Fórmula**:
```
Score Perspectiva = Promedio(Progreso de todos los KRs en la perspectiva)
```

**Implementación**:
```python
def calculate_perspective_score(okrs, perspective):
    perspective_okrs = [okr for okr in okrs if okr.perspective == perspective]
    all_kr_progress = []
    for okr in perspective_okrs:
        all_kr_progress.extend([kr.progress for kr in okr.key_results])
    return sum(all_kr_progress) / len(all_kr_progress)
```

**Status Asignado**:
- **On Track**: Score ≥ 90%
- **At Risk**: Score 70-89%
- **Off Track**: Score < 70%

### 2.7 Progreso Temporal de OKRs

Las gráficas temporales simulan el progreso de los últimos 6 meses.

**Simulación**:
```python
months = pd.date_range(end=datetime.now(), periods=6, freq='M')
for i, month in enumerate(months):
    simulated_progress = kr.progress * (i + 1) / 6
    # Progreso crece linealmente hasta valor actual
```

**Nota**: En implementación real, esto se alimentaría de datos históricos reales de seguimiento de OKRs.

---

## 3. Modelo Predictivo de Defectos (Rayleigh)

### 3.1 Fundamento Matemático

El modelo se basa en la **Distribución de Rayleigh**, que modela la tasa de descubrimiento de defectos en el tiempo.

**Función de Densidad de Probabilidad (PDF)**:
```
f(t) = (t / σ²) × e^(-(t²)/(2σ²))
```

Donde:
- `t` = tiempo (días del proyecto)
- `σ` = parámetro de escala (relacionado con la dispersión)

**Para defectos acumulados**:
```
D(t) = K × (1 - e^(-(t²)/(2σ²)))
```

Donde:
- `K` = total de defectos esperados
- `D(t)` = defectos acumulados hasta el día `t`

**Tasa de descubrimiento de defectos por día**:
```
dD/dt = (K × t / σ²) × e^(-(t²)/(2σ²))
```

### 3.2 Calibración del Parámetro σ

El parámetro σ se calibra desde datos históricos.

**Método**:
```python
def calibrate_rayleigh_sigma(df_calidad, df_proyectos):
    # Agrupar defectos por proyecto
    defects_per_project = df_calidad.groupby('nombre_proyecto')['cantidad_defectos'].sum()
    
    # Calcular σ para cada proyecto histórico
    sigmas = []
    for proyecto in defects_per_project.index:
        duracion = df_proyectos[df_proyectos['nombre_proyecto'] == proyecto]['duracion_dias'].values[0]
        # σ se estima como 40% de la duración (pico esperado)
        sigma = duracion * 0.4
        sigmas.append(sigma)
    
    return np.mean(sigmas)
```

**Ajustes por Factores**:
```python
# Multiplicadores según experiencia del equipo
experience_multiplier = {
    'Junior': 1.3,   # Más tiempo para encontrar defectos
    'Mid': 1.0,      # Base
    'Senior': 0.8    # Más rápido
}

# Multiplicadores según complejidad
complexity_multiplier = {
    'Baja': 0.7,
    'Media': 1.0,
    'Alta': 1.3,
    'Muy Alta': 1.6
}

sigma_adjusted = sigma_base * experience_mult * complexity_mult
```

### 3.3 Predicción de Defectos Totales (K)

El total de defectos se estima basado en tamaño del proyecto.

**Fórmula Empírica**:
```
K = (LOC / 1000) × Defectos_por_KLOC × Factor_Equipo × Factor_Complejidad
```

**Implementación**:
```python
def predict_defects_rayleigh(project_size, duration_months, team_size, 
                              experience_level, technology_complexity):
    # Convertir Story Points a LOC
    loc = project_size * 50  # 1 SP ≈ 50 LOC
    
    # Defectos por KLOC (de datos históricos)
    defects_per_kloc = 8.5  # Promedio calibrado
    
    # Factores de ajuste
    experience_factor = {'Junior': 1.4, 'Mid': 1.0, 'Senior': 0.7}[experience_level]
    complexity_factor = {'Baja': 0.6, 'Media': 1.0, 'Alta': 1.4, 'Muy Alta': 1.8}[technology_complexity]
    team_factor = 1 + ((team_size - 5) * 0.05)  # Más equipo, más coordinación
    
    # Cálculo final
    K = (loc / 1000) * defects_per_kloc * experience_factor * complexity_factor * team_factor
    
    return round(K)
```

**Ejemplo**:
- Story Points: 100
- LOC estimado: 100 × 50 = 5,000
- Defectos/KLOC: 8.5
- Experiencia: Mid (factor 1.0)
- Complejidad: Media (factor 1.0)
- Equipo: 8 personas (factor 1.15)

```
K = (5000 / 1000) × 8.5 × 1.0 × 1.0 × 1.15 = 48.9 ≈ 49 defectos
```

### 3.4 Generación de la Curva

**Puntos de la Curva**:
```python
def generate_rayleigh_curve(total_defects, duration_days, sigma, confidence_level=0.95):
    time = np.linspace(0, duration_days, duration_days)
    
    # Tasa de defectos por día (PDF escalado)
    defects_per_day = (time / sigma**2) * np.exp(-(time**2) / (2 * sigma**2)) * total_defects
    
    # Intervalos de confianza
    z_score = 1.96  # Para 95% de confianza
    std_dev = defects_per_day * 0.15  # Asumiendo 15% de variación
    upper_bound = defects_per_day + (z_score * std_dev)
    lower_bound = np.maximum(0, defects_per_day - (z_score * std_dev))
    
    # Día del pico
    peak_day = sigma  # El pico ocurre en t = σ
    peak_value = defects_per_day[int(peak_day)]
    
    return {
        'time': time,
        'defects_per_day': defects_per_day,
        'upper_bound': upper_bound,
        'lower_bound': lower_bound,
        'peak_day': peak_day,
        'peak_value': peak_value,
        'confidence_level': confidence_level
    }
```

**Interpretación del Pico**:
- El pico ocurre en `t = σ`
- Representa el momento de máxima tasa de descubrimiento
- Típicamente ocurre entre 35-45% de la duración del proyecto

**Ejemplo**:
- Duración: 180 días (6 meses)
- σ calibrado: 72 días
- Pico esperado: día 72 (40% del proyecto)
- Defectos en pico: ~1.2 defectos/día

### 3.5 Distribución por Severidad

**Fórmula basada en datos históricos**:
```python
def predict_severity_distribution(total_defects):
    # Proporciones de datos históricos
    severity_ratios = {
        'Crítica': 0.10,    # 10%
        'Alta': 0.30,       # 30%
        'Media': 0.40,      # 40%
        'Baja': 0.20        # 20%
    }
    
    distribution = {}
    for severity, ratio in severity_ratios.items():
        distribution[severity] = round(total_defects * ratio)
    
    return distribution
```

**Ejemplo** (49 defectos totales):
- Crítica: 49 × 0.10 = 5
- Alta: 49 × 0.30 = 15
- Media: 49 × 0.40 = 20
- Baja: 49 × 0.20 = 10

### 3.6 Recomendaciones de Recursos QA

**Fórmula**:
```
Horas QA por Defecto:
- Crítica: 8 horas
- Alta: 4 horas
- Media: 2 horas
- Baja: 1 hora

Horas Totales QA = Σ(Defectos_Severidad × Horas_Severidad)

Ingenieros QA = ceil(Horas Totales / (Duración_Meses × 160 hrs/mes))
```

**Implementación**:
```python
def recommend_qa_resources(total_defects, duration_months):
    # Distribución por severidad
    severity_dist = predict_severity_distribution(total_defects)
    
    # Horas por severidad
    hours_per_severity = {
        'Crítica': 8,
        'Alta': 4,
        'Media': 2,
        'Baja': 1
    }
    
    # Calcular horas totales
    total_qa_hours = sum(
        severity_dist[sev] * hours_per_severity[sev]
        for sev in severity_dist
    )
    
    # Horas disponibles por ingeniero
    hours_per_month = 160  # Jornada completa
    available_hours = duration_months * hours_per_month
    
    # Ingenieros necesarios
    qa_engineers = math.ceil(total_qa_hours / available_hours)
    
    # Nivel de riesgo
    defects_per_month = total_defects / duration_months
    if defects_per_month < 5:
        risk = ('green', 'Bajo')
    elif defects_per_month < 10:
        risk = ('yellow', 'Medio')
    else:
        risk = ('red', 'Alto')
    
    return {
        'qa_engineers': qa_engineers,
        'qa_hours_total': total_qa_hours,
        'risk_level': risk[1],
        'risk_color': risk[0],
        'recommendation': f"Asignar {qa_engineers} ingeniero(s) QA..."
    }
```

**Ejemplo** (49 defectos, 6 meses):
```
Horas totales = (5×8) + (15×4) + (20×2) + (10×1) = 40 + 60 + 40 + 10 = 150 hrs
Horas disponibles = 6 meses × 160 hrs = 960 hrs/ingeniero
Ingenieros = ceil(150 / 960) = 1 ingeniero

Defectos/mes = 49 / 6 = 8.2 → Riesgo Medio 🟡
```

### 3.7 Confianza del Modelo

**Cálculo**:
```python
def calculate_model_confidence(df_calidad, df_proyectos):
    num_projects = len(df_proyectos)
    num_records = len(df_calidad)
    
    # Factor de datos
    if num_projects >= 100 and num_records >= 1000:
        data_score = 1.0
    elif num_projects >= 50 and num_records >= 500:
        data_score = 0.8
    else:
        data_score = 0.6
    
    # Factor de varianza
    cv = df_calidad['cantidad_defectos'].std() / df_calidad['cantidad_defectos'].mean()
    variance_score = max(0, 1 - (cv * 0.5))
    
    # Score final
    confidence = (data_score + variance_score) / 2
    
    if confidence >= 0.8:
        label = 'Alta'
    elif confidence >= 0.6:
        label = 'Media'
    else:
        label = 'Baja'
    
    return {
        'score': confidence,
        'label': label,
        'num_projects': num_projects,
        'num_quality_records': num_records
    }
```

---

## 4. Notas Técnicas

### 4.1 Limitaciones

**KPIs**:
- Asumen datos completos y precisos
- No consideran factores externos (mercado, competencia)
- Índice de satisfacción es una aproximación

**OKRs**:
- Progreso temporal es simulado (en producción se necesitan snapshots históricos)
- Ponderaciones son configurables según estrategia

**Rayleigh**:
- Modelo simplificado (no considera todos los factores de riesgo)
- Asume distribución normal de defectos
- Calibración mejora con más datos históricos

### 4.2 Mejoras Futuras

1. **Machine Learning**: Usar regresión para predicción más precisa de defectos
2. **Datos Temporales Reales**: Capturar snapshots de OKRs semanalmente
3. **Análisis de Sentimiento**: Integrar feedback de clientes para satisfacción
4. **Simulación Monte Carlo**: Añadir variabilidad estocástica a predicciones

### 4.3 Referencias

- **Rayleigh Model**: Musa, J. D. (1975). "A theory of software reliability and its application"
- **Balanced Scorecard**: Kaplan & Norton (1996). "The Balanced Scorecard"
- **OKRs**: Doerr, J. (2018). "Measure What Matters"

---

## Conclusión

Este documento proporciona la base matemática y metodológica de todos los cálculos del DSS. Para implementación específica, consultar el código fuente en:
- `kpi_calculator.py` - KPIs
- `balanced_scorecard.py` - OKRs
- `rayleigh_model.py` - Modelo predictivo
