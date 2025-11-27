"""
KPI Calculator Module
=====================
Calculates Key Performance Indicators (KPIs) for Decision Support System.

Implements six core operational KPIs:
1. Project Completion Rate
2. Budget Efficiency
3. Team Utilization
4. Defect Density
5. Average Resolution Time
6. Client Satisfaction Index

Author: DSS Team
Date: 2025-11-27
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
from olap_functions import slice_olap, dice, calculate_metric_trend


def calculate_completion_rate(df_proy: pd.DataFrame) -> Tuple[float, Dict]:
    """
    Calculate project completion rate based on profitability.
    
    Projects with ganancia_neta > 0 are considered completed/successful.
    
    Args:
        df_proy: Projects DataFrame with 'ganancia_neta' column
        
    Returns:
        Tuple of (completion_rate_percentage, metadata_dict)
        
    Example:
        >>> rate, meta = calculate_completion_rate(df_projects)
        >>> print(f"Completion: {rate:.1f}%")
    """
    if df_proy.empty:
        return 0.0, {'completed': 0, 'total': 0, 'status': 'No data'}
    
    total_projects = len(df_proy)
    completed_projects = len(df_proy[df_proy['ganancia_neta'] > 0])
    
    rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0.0
    
    metadata = {
        'completed': completed_projects,
        'total': total_projects,
        'in_progress': total_projects - completed_projects,
        'status': 'healthy' if rate >= 80 else ('warning' if rate >= 50 else 'critical')
    }
    
    return round(rate, 2), metadata


def calculate_budget_efficiency(df_proy: pd.DataFrame) -> Tuple[float, Dict]:
    """
    Calculate budget efficiency as ratio of profit to cost.
    
    Formula: AVG(ganancia_neta / costo_total_real) * 100
    Filters out projects with zero cost.
    
    Args:
        df_proy: Projects DataFrame with 'ganancia_neta' and 'costo_total_real'
        
    Returns:
        Tuple of (efficiency_percentage, metadata_dict)
        
    Example:
        >>> efficiency, meta = calculate_budget_efficiency(df_projects)
        >>> print(f"Budget Efficiency: {efficiency:.1f}%")
    """
    # Filter projects with valid costs
    df_valid = df_proy[(df_proy['costo_total_real'] > 0) & (df_proy['ganancia_neta'].notna())]
    
    if df_valid.empty:
        return 0.0, {'avg_roi': 0, 'projects_analyzed': 0, 'status': 'No data'}
    
    # Calculate ROI for each project
    df_valid = df_valid.copy()
    df_valid['roi'] = (df_valid['ganancia_neta'] / df_valid['costo_total_real']) * 100
    
    avg_efficiency = df_valid['roi'].mean()
    
    metadata = {
        'avg_roi': round(avg_efficiency, 2),
        'best_roi': round(df_valid['roi'].max(), 2),
        'worst_roi': round(df_valid['roi'].min(), 2),
        'projects_analyzed': len(df_valid),
        'status': 'healthy' if avg_efficiency >= 30 else ('warning' if avg_efficiency >= 15 else 'critical')
    }
    
    return round(avg_efficiency, 2), metadata


def calculate_team_utilization(df_proy: pd.DataFrame) -> Tuple[float, Dict]:
    """
    Calculate team utilization rate.
    
    Formula: (Active Projects / Total Projects) * 100
    Active projects are those with ganancia_neta > 0 or costo_total_real > 0
    
    Args:
        df_proy: Projects DataFrame
        
    Returns:
        Tuple of (utilization_percentage, metadata_dict)
        
    Example:
        >>> util, meta = calculate_team_utilization(df_projects)
        >>> print(f"Team Utilization: {util:.1f}%")
    """
    if df_proy.empty:
        return 0.0, {'active': 0, 'total': 0, 'status': 'No data'}
    
    total_projects = len(df_proy)
    # Active: either has profit or costs (work has been done)
    active_projects = len(df_proy[(df_proy['ganancia_neta'] > 0) | (df_proy['costo_total_real'] > 0)])
    
    utilization = (active_projects / total_projects * 100) if total_projects > 0 else 0.0
    
    # Count unique clients for additional insight
    unique_clients = df_proy['nombre_cliente'].nunique() if 'nombre_cliente' in df_proy.columns else 0
    
    metadata = {
        'active_projects': active_projects,
        'total_projects': total_projects,
        'idle_projects': total_projects - active_projects,
        'unique_clients': unique_clients,
        'status': 'healthy' if utilization >= 70 else ('warning' if utilization >= 50 else 'critical')
    }
    
    return round(utilization, 2), metadata


def calculate_defect_density(df_cal: pd.DataFrame, df_proy: pd.DataFrame) -> Tuple[float, Dict]:
    """
    Calculate defect density (defects per project).
    
    Formula: Total Defects / Total Projects
    
    Args:
        df_cal: Quality/defects DataFrame with 'cantidad_defectos_encontrados'
        df_proy: Projects DataFrame
        
    Returns:
        Tuple of (defects_per_project, metadata_dict)
        
    Example:
        >>> density, meta = calculate_defect_density(df_quality, df_projects)
        >>> print(f"Defect Density: {density:.2f} defects/project")
    """
    if df_cal.empty or df_proy.empty:
        return 0.0, {'total_defects': 0, 'projects': 0, 'status': 'No data'}
    
    total_defects = df_cal['cantidad_defectos_encontrados'].sum()
    total_projects = df_proy['nombre_proyecto'].nunique()
    
    density = total_defects / total_projects if total_projects > 0 else 0.0
    
    # Calculate severity breakdown
    severity_breakdown = {}
    if 'severidad' in df_cal.columns:
        severity_breakdown = df_cal.groupby('severidad')['cantidad_defectos_encontrados'].sum().to_dict()
    
    metadata = {
        'total_defects': int(total_defects),
        'total_projects': total_projects,
        'density': round(density, 2),
        'severity_breakdown': severity_breakdown,
        'status': 'healthy' if density <= 10 else ('warning' if density <= 25 else 'critical')
    }
    
    return round(density, 2), metadata


def calculate_avg_resolution_time(df_cal: pd.DataFrame) -> Tuple[float, Dict]:
    """
    Calculate average defect resolution time using severity as proxy.
    
    Severity-to-time mapping:
    - crítica: 7 days
    - alta: 4 days
    - media: 2 days
    - baja/nula: 1 day
    
    Args:
        df_cal: Quality DataFrame with 'severidad' and 'cantidad_defectos_encontrados'
        
    Returns:
        Tuple of (avg_days, metadata_dict)
        
    Example:
        >>> avg_time, meta = calculate_avg_resolution_time(df_quality)
        >>> print(f"Avg Resolution: {avg_time:.1f} days")
    """
    if df_cal.empty or 'severidad' not in df_cal.columns:
        return 0.0, {'avg_days': 0, 'defects': 0, 'status': 'No data'}
    
    # Severity to resolution time mapping
    severity_days = {
        'crítica': 7,
        'alta': 4,
        'media': 2,
        'baja': 1,
        'nula': 0.5  # Trivial issues
    }
    
    df_with_time = df_cal.copy()
    df_with_time['estimated_days'] = df_with_time['severidad'].map(severity_days).fillna(2)  # Default 2 days
    
    # Weighted average based on defect count
    total_defects = df_with_time['cantidad_defectos_encontrados'].sum()
    
    if total_defects == 0:
        return 0.0, {'avg_days': 0, 'defects': 0, 'status': 'No defects'}
    
    df_with_time['weighted_time'] = (
        df_with_time['estimated_days'] * df_with_time['cantidad_defectos_encontrados']
    )
    
    avg_resolution = df_with_time['weighted_time'].sum() / total_defects
    
    # Calculate by severity
    resolution_by_severity = {}
    for severity, days in severity_days.items():
        count = df_cal[df_cal['severidad'] == severity]['cantidad_defectos_encontrados'].sum()
        if count > 0:
            resolution_by_severity[severity] = {'days': days, 'count': int(count)}
    
    metadata = {
        'avg_days': round(avg_resolution, 1),
        'total_defects': int(total_defects),
        'resolution_by_severity': resolution_by_severity,
        'status': 'healthy' if avg_resolution <= 3 else ('warning' if avg_resolution <= 5 else 'critical')
    }
    
    return round(avg_resolution, 1), metadata


def calculate_client_satisfaction(df_proy: pd.DataFrame, df_cal: pd.DataFrame) -> Tuple[float, Dict]:
    """
    Calculate Client Satisfaction Index.
    
    Composite formula:
    - Budget Efficiency (40% weight)
    - Low Defect Rate (60% weight)
    
    Normalized to 0-100 scale.
    
    Args:
        df_proy: Projects DataFrame
        df_cal: Quality DataFrame
        
    Returns:
        Tuple of (satisfaction_index, metadata_dict)
        
    Example:
        >>> satisfaction, meta = calculate_client_satisfaction(df_projects, df_quality)
        >>> print(f"Client Satisfaction: {satisfaction:.1f}/100")
    """
    # Component 1: Budget Efficiency (normalized to 0-100)
    budget_eff, budget_meta = calculate_budget_efficiency(df_proy)
    # Normalize: ROI of 50% or more = 100 points
    budget_score = min(budget_eff * 2, 100)  # Cap at 100
    
    # Component 2: Quality Score (inverse of defect density)
    defect_density, defect_meta = calculate_defect_density(df_cal, df_proy)
    # Normalize: 0 defects = 100, 50+ defects/project = 0
    quality_score = max(100 - (defect_density * 2), 0)
    
    # Composite score
    satisfaction_index = (budget_score * 0.4) + (quality_score * 0.6)
    
    metadata = {
        'index': round(satisfaction_index, 1),
        'budget_component': round(budget_score, 1),
        'quality_component': round(quality_score, 1),
        'budget_efficiency': budget_eff,
        'defect_density': defect_density,
        'status': 'healthy' if satisfaction_index >= 70 else ('warning' if satisfaction_index >= 50 else 'critical')
    }
    
    return round(satisfaction_index, 1), metadata


def calculate_all_kpis(df_proy: pd.DataFrame, df_cal: pd.DataFrame) -> Dict[str, Dict]:
    """
    Calculate all six KPIs at once.
    
    Args:
        df_proy: Projects DataFrame
        df_cal: Quality DataFrame
        
    Returns:
        Dictionary with all KPI values and metadata
        
    Example:
        >>> kpis = calculate_all_kpis(df_projects, df_quality)
        >>> print(kpis['completion_rate']['value'])
    """
    completion_rate, completion_meta = calculate_completion_rate(df_proy)
    budget_eff, budget_meta = calculate_budget_efficiency(df_proy)
    team_util, team_meta = calculate_team_utilization(df_proy)
    defect_dens, defect_meta = calculate_defect_density(df_cal, df_proy)
    resolution_time, resolution_meta = calculate_avg_resolution_time(df_cal)
    satisfaction, satisfaction_meta = calculate_client_satisfaction(df_proy, df_cal)
    
    return {
        'completion_rate': {'value': completion_rate, 'metadata': completion_meta, 'unit': '%'},
        'budget_efficiency': {'value': budget_eff, 'metadata': budget_meta, 'unit': '%'},
        'team_utilization': {'value': team_util, 'metadata': team_meta, 'unit': '%'},
        'defect_density': {'value': defect_dens, 'metadata': defect_meta, 'unit': 'defects/project'},
        'avg_resolution_time': {'value': resolution_time, 'metadata': resolution_meta, 'unit': 'days'},
        'client_satisfaction': {'value': satisfaction, 'metadata': satisfaction_meta, 'unit': 'index'}
    }


def get_kpi_color(value: float, kpi_type: str) -> str:
    """
    Get color coding for KPI based on thresholds.
    
    Args:
        value: KPI value
        kpi_type: Type of KPI (determines thresholds)
        
    Returns:
        Color string: 'green', 'yellow', or 'red'
        
    Example:
        >>> color = get_kpi_color(85, 'completion_rate')
        >>> # Returns 'green'
    """
    thresholds = {
        'completion_rate': {'green': 80, 'yellow': 50},
        'budget_efficiency': {'green': 30, 'yellow': 15},
        'team_utilization': {'green': 70, 'yellow': 50},
        'defect_density': {'green': 10, 'yellow': 25, 'inverse': True},  # Lower is better
        'avg_resolution_time': {'green': 3, 'yellow': 5, 'inverse': True},
        'client_satisfaction': {'green': 70, 'yellow': 50}
    }
    
    if kpi_type not in thresholds:
        return 'gray'
    
    threshold = thresholds[kpi_type]
    is_inverse = threshold.get('inverse', False)
    
    if is_inverse:
        # Lower values are better (defects, resolution time)
        if value <= threshold['green']:
            return 'green'
        elif value <= threshold['yellow']:
            return 'yellow'
        else:
            return 'red'
    else:
        # Higher values are better
        if value >= threshold['green']:
            return 'green'
        elif value >= threshold['yellow']:
            return 'yellow'
        else:
            return 'red'


def format_kpi_display(kpi_name: str, value: float, unit: str, metadata: Dict) -> Dict:
    """
    Format KPI data for dashboard display.
    
    Args:
        kpi_name: Name of the KPI
        value: KPI value
        unit: Unit of measurement
        metadata: Additional metadata
        
    Returns:
        Formatted dictionary for UI rendering
    """
    color = get_kpi_color(value, kpi_name)
    status = metadata.get('status', 'unknown')
    
    return {
        'name': kpi_name.replace('_', ' ').title(),
        'value': value,
        'unit': unit,
        'color': color,
        'status': status,
        'metadata': metadata,
        'display_value': f"{value:.1f}{unit}" if unit == '%' else f"{value:.1f} {unit}"
    }
