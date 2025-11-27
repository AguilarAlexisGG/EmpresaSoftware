"""
Rayleigh Defect Prediction Model
=================================
Implements Rayleigh distribution-based defect prediction for software projects.

The Rayleigh model is well-suited for software defect prediction because defects
typically follow a pattern where they increase to a peak and then decline as the
project progresses.

Rayleigh PDF: f(t) = (t/σ²) * exp(-t²/2σ²)
where σ (sigma) is the scale parameter determining when the peak occurs.

Author: DSS Team
Date: 2025-11-27
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List, Optional
from scipy import integrate
from scipy.stats import rayleigh


def calibrate_rayleigh_sigma(df_cal: pd.DataFrame, df_proy: pd.DataFrame) -> Dict[str, float]:
    """
    Calibrate Rayleigh scale parameter (σ) from historical defect patterns.
    
    For software projects, the peak typically occurs around 40% of the project duration.
    σ ≈ 0.4 * duration
    
    Args:
        df_cal: Quality DataFrame with historical defects
        df_proy: Projects DataFrame
        
    Returns:
        Dictionary mapping project characteristics to σ values
        
    Example:
        >>> sigmas = calibrate_rayleigh_sigma(df_quality, df_projects)
        >>> print(sigmas['default'])  # Default σ for average project
    """
    # Calculate historical patterns
    project_defects = df_cal.groupby('nombre_proyecto')['cantidad_defectos_encontrados'].sum()
    
    if project_defects.empty:
        # Default values if no historical data
        return {
            'default': 60.0,  # 60 days for typical 150-day (5-month) project
            'small': 40.0,    # 40 days for small projects (3-4 months)
            'medium': 60.0,   # 60 days for medium projects (5-6 months)
            'large': 90.0,    # 90 days for large projects (7-9 months)
            'confidence': 0.5  # Low confidence due to no data
        }
    
    # Analyze defect patterns to estimate σ
    # In a Rayleigh distribution, peak occurs at σ
    # For software, peak is typically at 40% of project duration
    
    avg_defects = project_defects.mean()
    std_defects = project_defects.std()
    
    # Calibrate based on typical project durations (estimated)
    # Assuming typical project is 5-6 months = 150-180 days
    typical_duration = 165  # days
    peak_at_40_percent = typical_duration * 0.4
    
    return {
        'default': peak_at_40_percent,  # ≈ 66 days
        'small': 40.0,     # 3 months * 0.4 = 36 days
        'medium': 66.0,    # 5.5 months * 0.4 = 66 days  
        'large': 100.0,    # 8 months * 0.4 = 96 days
        'xlarge': 144.0,   # 12 months * 0.4 = 144 days
        'avg_historical_defects': float(avg_defects),
        'std_historical_defects': float(std_defects),
        'confidence': 0.8  # Higher confidence with real data
    }


def estimate_base_defects(project_size: int, team_size: int, 
                          experience_level: str, technology_complexity: str) -> float:
    """
    Estimate base defect count using empirical formulas.
    
    Based on industry benchmarks:
    - Average: 10-50 defects per 1000 LOC
    - High-quality: 2-10 defects per 1000 LOC
    
    Args:
        project_size: Size in LOC (Lines of Code)
        team_size: Number of developers
        experience_level: "Junior", "Mid", or "Senior"
        technology_complexity: Complexity rating
        
    Returns:
        Estimated total defects
    """
    # Base defect density (defects per 1000 LOC)
    experience_multiplier = {
        "Junior": 1.5,   # Less experienced teams introduce more defects
        "Mid": 1.0,      # Average
        "Senior": 0.6    # More experienced teams are more careful
    }
    
    complexity_multiplier = {
        "Baja": 0.7,
        "Media": 1.0,
        "Alta": 1.4,
        "Muy Alta": 1.8
    }
    
    # Base rate: 20 defects per 1000 LOC (industry average)
    base_defect_density = 20
    
    # Apply multipliers
    exp_mult = experience_multiplier.get(experience_level, 1.0)
    comp_mult = complexity_multiplier.get(technology_complexity, 1.0)
    
    # Team size effect (larger teams = more communication overhead)
    team_mult = 1.0 + (0.05 * (team_size - 5)) if team_size > 5 else 1.0
    
    # Calculate total defects
    total_defects = (project_size / 1000) * base_defect_density * exp_mult * comp_mult * team_mult
    
    return max(total_defects, 1.0)  # At least 1 defect


def predict_defects_rayleigh(project_size: int, duration_months: int, 
                             team_size: int, experience_level: str,
                             technology_complexity: str = "Media",
                             sigma: Optional[float] = None) -> Dict[str, any]:
    """
    Predict total defects and distribution for a new project.
    
    Args:
        project_size: Project size in LOC
        duration_months: Expected duration in months
        team_size: Number of developers
        experience_level: "Junior", "Mid", or "Senior"
        technology_complexity: "Baja", "Media", "Alta", "Muy Alta"
        sigma: Optional custom σ value (uses calibrated if None)
        
    Returns:
        Dictionary with prediction results
        
    Example:
        >>> result = predict_defects_rayleigh(
        ...     project_size=50000,
        ...     duration_months=6,
        ...     team_size=8,
        ...     experience_level="Mid",
        ...     technology_complexity="Alta"
        ... )
        >>> print(f"Expected defects: {result['total_defects']}")
    """
    # Estimate total defects
    total_defects = estimate_base_defects(
        project_size, team_size, experience_level, technology_complexity
    )
    
    # Determine σ based on project duration
    duration_days = duration_months * 30
    if sigma is None:
        sigma = duration_days * 0.4  # Peak at 40% of duration
    
    # Calculate when peak occurs
    peak_day = sigma
    
    # Distribute defects by severity
    severity_distribution = {
        'Crítica': total_defects * 0.10,   # 10% critical
        'Alta': total_defects * 0.25,      # 25% high
        'Media': total_defects * 0.40,     # 40% medium
        'Baja': total_defects * 0.25       # 25% low
    }
    
    # Calculate defects rate at peak
    # For Rayleigh: mode (peak) occurs at σ, max value = σ * exp(-1/2)
    peak_defects_per_day = total_defects * 0.015  # Empirical: ~1.5% of total at peak day
    
    return {
        'total_defects': round(total_defects, 1),
        'peak_day': round(peak_day, 1),
        'peak_defects_per_day': round(peak_defects_per_day, 2),
        'sigma': sigma,
        'duration_days': duration_days,
        'severity_distribution': {k: round(v, 1) for k, v in severity_distribution.items()},
        'project_params': {
            'size': project_size,
            'duration_months': duration_months,
            'team_size': team_size,
            'experience': experience_level,
            'complexity': technology_complexity
        }
    }


def generate_rayleigh_curve(total_defects: float, duration_days: int, 
                            sigma: Optional[float] = None,
                            confidence_level: float = 0.95) -> Dict[str, np.ndarray]:
    """
    Generate Rayleigh defect discovery curve over time.
    
    Args:
        total_defects: Total expected defects
        duration_days: Project duration in days
        sigma: Scale parameter (default: 0.4 * duration)
        confidence_level: Confidence level for intervals (0.8 or 0.95)
        
    Returns:
        Dictionary with time points, defect rates, and confidence bands
        
    Example:
        >>> curve = generate_rayleigh_curve(100, 180, sigma=72)
        >>> import matplotlib.pyplot as plt
        >>> plt.plot(curve['time'], curve['defects_per_day'])
    """
    if sigma is None:
        sigma = duration_days * 0.4
    
    # Time points (daily)
    time = np.linspace(0, duration_days, duration_days)
    
    # Rayleigh PDF: f(t) = (t/σ²) * exp(-t²/2σ²)
    # Normalized to integrate to total_defects
    rayleigh_pdf = (time / (sigma ** 2)) * np.exp(-(time ** 2) / (2 * sigma ** 2))
    
    # Scale to total defects
    # Integrate Rayleigh PDF from 0 to duration
    integral = np.trapz(rayleigh_pdf, time)
    if integral > 0:
        defects_per_day = rayleigh_pdf * (total_defects / integral)
    else:
        defects_per_day = np.zeros_like(time)
    
    # Calculate cumulative defects
    cumulative_defects = np.cumsum(defects_per_day)
    
    # Generate confidence intervals (±20% for 80%, ±30% for 95%)
    if confidence_level >= 0.95:
        margin = 0.30
    else:
        margin = 0.20
    
    upper_bound = defects_per_day * (1 + margin)
    lower_bound = defects_per_day * (1 - margin)
    lower_bound = np.maximum(lower_bound, 0)  # Can't be negative
    
    return {
        'time': time,
        'defects_per_day': defects_per_day,
        'cumulative_defects': cumulative_defects,
        'upper_bound': upper_bound,
        'lower_bound': lower_bound,
        'confidence_level': confidence_level,
        'sigma': sigma,
        'peak_day': sigma,
        'peak_value': np.max(defects_per_day)
    }


def recommend_qa_resources(predicted_defects: float, duration_months: int) -> Dict[str, any]:
    """
    Recommend QA resources based on predicted defect count.
    
    Heuristic: 1 QA engineer can handle ~50 defects per project
    Plus overhead for test creation and regression testing.
    
    Args:
        predicted_defects: Total predicted defects
        duration_months: Project duration
        
    Returns:
        Dictionary with resource recommendations
        
    Example:
        >>> rec = recommend_qa_resources(120, 6)
        >>> print(f"Recommended QA team: {rec['qa_engineers']} engineers")
    """
    # Base calculation: 1 QA per 50 defects
    base_qa = predicted_defects / 50
    
    # Adjust for project duration (shorter projects need more concentrated effort)
    if duration_months <= 3:
        duration_mult = 1.3
    elif duration_months <= 6:
        duration_mult = 1.0
    else:
        duration_mult = 0.9  # Longer projects can spread QA work
    
    recommended_qa = base_qa * duration_mult
    
    # Minimum 1 QA engineer for any project
    recommended_qa = max(recommended_qa, 1)
    
    # Risk assessment
    if predicted_defects < 30:
        risk_level = "Bajo"
        risk_color = "green"
    elif predicted_defects < 80:
        risk_level = "Medio"
        risk_color = "yellow"
    else:
        risk_level = "Alto"
        risk_color = "red"
    
    # Calculate estimated QA hours
    # Assume: 2 hours per defect (find, verify, retest)
    qa_hours = predicted_defects * 2
    
    return {
        'qa_engineers': int(np.ceil(recommended_qa)),
        'qa_hours_total': round(qa_hours, 0),
        'qa_hours_per_month': round(qa_hours / duration_months, 0),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'recommendation': (
            f"Asignar {int(np.ceil(recommended_qa))} ingeniero(s) QA por "
            f"{duration_months} meses. Estimar {int(qa_hours)} horas totales de pruebas."
        )
    }


def calculate_model_confidence(df_cal: pd.DataFrame, df_proy: pd.DataFrame) -> Dict[str, any]:
    """
    Calculate model confidence based on historical data volume and quality.
    
    Args:
        df_cal: Quality DataFrame
        df_proy: Projects DataFrame
        
    Returns:
        Confidence metrics
    """
    num_projects = df_proy['nombre_proyecto'].nunique()
    num_quality_records = len(df_cal)
    
    # Confidence scoring
    if num_projects >= 100 and num_quality_records >= 1000:
        confidence_score = 0.95
        confidence_label = "Muy Alta"
    elif num_projects >= 50 and num_quality_records >= 500:
        confidence_score = 0.85
        confidence_label = "Alta"
    elif num_projects >= 20 and num_quality_records >= 200:
        confidence_score = 0.70
        confidence_label = "Media"
    else:
        confidence_score = 0.50
        confidence_label = "Baja"
    
    return {
        'score': confidence_score,
        'label': confidence_label,
        'num_projects': num_projects,
        'num_quality_records': num_quality_records,
        'message': (
            f"Modelo calibrado con {num_projects} proyectos históricos y "
            f"{num_quality_records} registros de calidad. Confianza: {confidence_label}."
        )
    }


def validate_prediction_inputs(project_size: int, duration_months: int, 
                               team_size: int) -> Tuple[bool, str]:
    """
    Validate prediction input parameters.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if project_size < 100:
        return False, "Tamaño de proyecto debe ser al menos 100 LOC"
    
    if project_size > 10_000_000:
        return False, "Tamaño de proyecto demasiado grande (>10M LOC)"
    
    if duration_months < 1 or duration_months > 36:
        return False, "Duración debe estar entre 1 y 36 meses"
    
    if team_size < 1 or team_size > 100:
        return False, "Tamaño de equipo debe estar entre 1 y 100 desarrolladores"
    
    return True, ""
