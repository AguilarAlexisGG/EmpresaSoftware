"""
Balanced Scorecard & OKR Module
================================
Implements strategic framework with OKRs (Objectives and Key Results) aligned 
to the Balanced Scorecard perspectives.

Four Perspectives:
1. Financial - Revenue, profitability, cost management
2. Customer - Satisfaction, retention, market share
3. Internal Processes - Quality, efficiency, innovation
4. Learning & Growth - Skills, culture, knowledge

Author: DSS Team
Date: 2025-11-27
"""

import pandas as pd
from dataclasses import dataclass, field
from typing import List, Dict, Any, Tuple
import numpy as np


@dataclass
class KeyResult:
    """Represents a measurable Key Result for an Objective."""
    kr: str  # Key Result description
    target: float  # Target value to achieve
    current: float  # Current value
    unit: str = "%"  # Unit of measurement
    
    @property
    def progress(self) -> float:
        """Calculate progress percentage."""
        if self.target == 0:
            return 100.0 if self.current >= 0 else 0.0
        return min((self.current / self.target) * 100, 100.0)
    
    @property
    def status(self) -> str:
        """Determine status based on progress."""
        if self.progress >= 90:
            return "On Track"
        elif self.progress >= 70:
            return "At Risk"
        else:
            return "Off Track"


@dataclass
class OKR:
    """Represents an Objective with multiple Key Results."""
    objective: str  # Strategic objective statement
    key_results: List[KeyResult] = field(default_factory=list)
    owner: str = "CEO"  # Responsible executive
    quarter: str = "Q1 2025"
    perspective: str = "Financial"  # Balanced Scorecard perspective
    
    @property
    def overall_progress(self) -> float:
        """Calculate average progress across all key results."""
        if not self.key_results:
            return 0.0
        return sum(kr.progress for kr in self.key_results) / len(self.key_results)
    
    @property
    def status(self) -> str:
        """Overall OKR status."""
        progress = self.overall_progress
        if progress >= 90:
            return "On Track"
        elif progress >= 70:
            return "At Risk"
        else:
            return "Off Track"


def generate_financial_okrs(df_proy: pd.DataFrame, quarter: str = "Q1 2025") -> List[OKR]:
    """
    Generate OKRs for Financial perspective.
    
    Args:
        df_proy: Projects DataFrame
        quarter: Target quarter
        
    Returns:
        List of financial OKRs
    """
    # Calculate current financial metrics
    total_revenue = df_proy['ganancia_neta'].sum()
    total_cost = df_proy['costo_total_real'].sum()
    profit_margin = (total_revenue / total_cost * 100) if total_cost > 0 else 0
    
    # OKR 1: Increase Revenue
    okr1 = OKR(
        objective="Aumentar Ingresos por Proyectos de Software",
        key_results=[
            KeyResult(
                kr="Generar $50M en ganancia neta",
                target=50_000_000,
                current=total_revenue,
                unit="$"
            ),
            KeyResult(
                kr="Cerrar 10 proyectos de alto valor (>$500K ganancia)",
                target=10,
                current=len(df_proy[df_proy['ganancia_neta'] > 500_000]),
                unit=" proyectos"
            ),
            KeyResult(
                kr="Mantener margen de beneficio >35%",
                target=35,
                current=profit_margin,
                unit="%"
            )
        ],
        owner="CFO",
        quarter=quarter,
        perspective="Financial"
    )
    
    # OKR 2: Cost Optimization
    avg_cost = df_proy[df_proy['costo_total_real'] > 0]['costo_total_real'].mean()
    
    okr2 = OKR(
        objective="Optimizar Costos Operativos",
        key_results=[
            KeyResult(
                kr="Reducir costo promedio por proyecto a $400K",
                target=400_000,
                current=avg_cost,
                unit="$"
            ),
            KeyResult(
                kr="Mantener proyectos sin sobrecosto en 90%",
                target=90,
                current=85,  # Placeholder - would calculate from actual vs budget
                unit="%"
            )
        ],
        owner="CFO",
        quarter=quarter,
        perspective="Financial"
    )
    
    return [okr1, okr2]


def generate_customer_okrs(df_proy: pd.DataFrame, quarter: str = "Q1 2025") -> List[OKR]:
    """
    Generate OKRs for Customer perspective.
    
    Args:
        df_proy: Projects DataFrame
        quarter: Target quarter
        
    Returns:
        List of customer-focused OKRs
    """
    unique_clients = df_proy['nombre_cliente'].nunique()
    
    # Calculate repeat business rate
    client_project_counts = df_proy.groupby('nombre_cliente').size()
    repeat_clients = len(client_project_counts[client_project_counts > 1])
    repeat_rate = (repeat_clients / unique_clients * 100) if unique_clients > 0 else 0
    
    okr1 = OKR(
        objective="Expandir Base de Clientes y Fidelización",
        key_results=[
            KeyResult(
                kr="Alcanzar 50 clientes activos",
                target=50,
                current=unique_clients,
                unit=" clientes"
            ),
            KeyResult(
                kr="Lograr 70% de tasa de clientes recurrentes",
                target=70,
                current=repeat_rate,
                unit="%"
            ),
            KeyResult(
                kr="Penetrar 3 nuevos países/mercados",
                target=3,
                current=1,  # Placeholder
                unit=" países"
            )
        ],
        owner="CCO",
        quarter=quarter,
        perspective="Customer"
    )
    
    # OKR 2: Client Satisfaction
    # Calculate avg project value as proxy for client investment
    avg_project_value = df_proy[df_proy['ganancia_neta'] > 0]['ganancia_neta'].mean()
    
    okr2 = OKR(
        objective="Mejorar Satisfacción y Valor para el Cliente",
        key_results=[
            KeyResult(
                kr="Alcanzar NPS de 75+",
                target=75,
                current=68,  # Placeholder - would come from surveys
                unit=" puntos"
            ),
            KeyResult(
                kr="Aumentar valor promedio de proyecto a $250K",
                target=250_000,
                current=avg_project_value,
                unit="$"
            )
        ],
        owner="CCO",
        quarter=quarter,
        perspective="Customer"
    )
    
    return [okr1, okr2]


def generate_internal_okrs(df_proy: pd.DataFrame, df_cal: pd.DataFrame, 
                          quarter: str = "Q1 2025") -> List[OKR]:
    """
    Generate OKRs for Internal Processes perspective.
    
    Args:
        df_proy: Projects DataFrame
        df_cal: Quality DataFrame
        quarter: Target quarter
        
    Returns:
        List of internal process OKRs
    """
    # Quality metrics
    total_defects = df_cal['cantidad_defectos_encontrados'].sum()
    total_projects = df_proy['nombre_proyecto'].nunique()
    defect_density = total_defects / total_projects if total_projects > 0 else 0
    
    # Calculate critical defects percentage
    critical_defects = df_cal[df_cal['severidad'] == 'crítica']['cantidad_defectos_encontrados'].sum()
    critical_pct = (critical_defects / total_defects * 100) if total_defects > 0 else 0
    
    okr1 = OKR(
        objective="Alcanzar Excelencia en Calidad de Software",
        key_results=[
            KeyResult(
                kr="Reducir densidad de defectos a <8 por proyecto",
                target=8,
                current=defect_density,
                unit=" def/proy"
            ),
            KeyResult(
                kr="Mantener defectos críticos <5% del total",
                target=5,
                current=critical_pct,
                unit="%"
            ),
            KeyResult(
                kr="Alcanzar 95% de cobertura de pruebas automatizadas",
                target=95,
                current=78,  # Placeholder
                unit="%"
            )
        ],
        owner="CTO",
        quarter=quarter,
        perspective="Internal Processes"
    )
    
    # OKR 2: Delivery Efficiency
    completion_rate = len(df_proy[df_proy['ganancia_neta'] > 0]) / len(df_proy) * 100
    
    okr2 = OKR(
        objective="Optimizar Eficiencia de Entrega",
        key_results=[
            KeyResult(
                kr="Lograr 90% de proyectos completados exitosamente",
                target=90,
                current=completion_rate,
                unit="%"
            ),
            KeyResult(
                kr="Reducir tiempo promedio de entrega a 4 meses",
                target=4,
                current=5.2,  # Placeholder
                unit=" meses"
            )
        ],
        owner="CTO",
        quarter=quarter,
        perspective="Internal Processes"
    )
    
    return [okr1, okr2]


def generate_learning_okrs(df_proy: pd.DataFrame, quarter: str = "Q1 2025") -> List[OKR]:
    """
    Generate OKRs for Learning & Growth perspective.
    
    Args:
        df_proy: Projects DataFrame
        quarter: Target quarter
        
    Returns:
        List of learning & growth OKRs
    """
    # Analyze technology diversity
    project_names = df_proy['nombre_proyecto'].unique()
    # Extract tech keywords from project names (simplified)
    tech_diversity = len(set(name.split('-')[1] for name in project_names if '-' in name))
    
    okr1 = OKR(
        objective="Desarrollar Capacidades Técnicas Avanzadas",
        key_results=[
            KeyResult(
                kr="Certificar 80% del equipo en tecnologías cloud",
                target=80,
                current=45,  # Placeholder
                unit="%"
            ),
            KeyResult(
                kr="Dominar 10 stacks tecnológicos diferentes",
                target=10,
                current=tech_diversity,
                unit=" tecnologías"
            ),
            KeyResult(
                kr="Implementar IA/ML en 5 proyectos",
                target=5,
                current=2,  # Placeholder
                unit=" proyectos"
            )
        ],
        owner="CTO",
        quarter=quarter,
        perspective="Learning & Growth"
    )
    
    okr2 = OKR(
        objective="Fortalecer Cultura de Innovación",
        key_results=[
            KeyResult(
                kr="Alcanzar 85% en índice de satisfacción empleados",
                target=85,
                current=72,  # Placeholder
                unit="%"
            ),
            KeyResult(
                kr="Generar 20 propuestas de mejora interna",
                target=20,
                current=12,  # Placeholder
                unit=" propuestas"
            )
        ],
        owner="CHRO",
        quarter=quarter,
        perspective="Learning & Growth"
    )
    
    return [okr1, okr2]


def generate_okrs_from_data(df_proy: pd.DataFrame, df_cal: pd.DataFrame, 
                            quarter: str = "Q1 2025") -> List[OKR]:
    """
    Generate all OKRs from OLAP data across four perspectives.
    
    Args:
        df_proy: Projects DataFrame
        df_cal: Quality DataFrame
        quarter: Target quarter
        
    Returns:
        Complete list of OKRs for all perspectives
    """
    all_okrs = []
    all_okrs.extend(generate_financial_okrs(df_proy, quarter))
    all_okrs.extend(generate_customer_okrs(df_proy, quarter))
    all_okrs.extend(generate_internal_okrs(df_proy, df_cal, quarter))
    all_okrs.extend(generate_learning_okrs(df_proy, quarter))
    
    return all_okrs


def calculate_perspective_score(okrs: List[OKR], perspective: str) -> Tuple[float, Dict]:
    """
    Calculate aggregated score for a Balanced Scorecard perspective.
    
    Args:
        okrs: List of all OKRs
        perspective: Perspective name
        
    Returns:
        Tuple of (score, metadata)
    """
    perspective_okrs = [okr for okr in okrs if okr.perspective == perspective]
    
    if not perspective_okrs:
        return 0.0, {'okr_count': 0, 'kr_count': 0, 'status': 'No OKRs'}
    
    # Calculate average progress across all OKRs in this perspective
    total_progress = sum(okr.overall_progress for okr in perspective_okrs)
    avg_progress = total_progress / len(perspective_okrs)
    
    # Count key results
    total_krs = sum(len(okr.key_results) for okr in perspective_okrs)
    
    # Status determination
    if avg_progress >= 90:
        status = "On Track"
    elif avg_progress >= 70:
        status = "At Risk"
    else:
        status = "Off Track"
    
    metadata = {
        'okr_count': len(perspective_okrs),
        'kr_count': total_krs,
        'status': status,
        'objectives': [okr.objective for okr in perspective_okrs]
    }
    
    return round(avg_progress, 1), metadata


def create_okr_hierarchy(okrs: List[OKR]) -> Dict[str, Any]:
    """
    Create hierarchical structure for OKR visualization (sunburst/treemap).
    
    Args:
        okrs: List of OKRs
        
    Returns:
        Nested dictionary structure for Plotly
    """
    hierarchy = {
        'name': 'Strategic OKRs',
        'children': []
    }
    
    # Group by perspective
    perspectives = {}
    for okr in okrs:
        if okr.perspective not in perspectives:
            perspectives[okr.perspective] = []
        perspectives[okr.perspective].append(okr)
    
    # Build hierarchy
    for perspective, perspective_okrs in perspectives.items():
        perspective_node = {
            'name': perspective,
            'children': []
        }
        
        for okr in perspective_okrs:
            okr_node = {
                'name': okr.objective[:40] + '...' if len(okr.objective) > 40 else okr.objective,
                'value': okr.overall_progress,
                'children': [
                    {
                        'name': kr.kr[:30] + '...' if len(kr.kr) > 30 else kr.kr,
                        'value': kr.progress
                    }
                    for kr in okr.key_results
                ]
            }
            perspective_node['children'].append(okr_node)
        
        hierarchy['children'].append(perspective_node)
    
    return hierarchy


def create_strategy_map_data(okrs: List[OKR]) -> Dict[str, List]:
    """
    Create data for Strategy Map (Sankey diagram) showing cause-effect relationships.
    
    Args:
        okrs: List of OKRs
        
    Returns:
        Dictionary with nodes and links for Plotly Sankey
    """
    # Define perspective relationships (bottom-up causality)
    perspective_order = ["Learning & Growth", "Internal Processes", "Customer", "Financial"]
    
    # Create nodes
    nodes = []
    node_colors = []
    color_map = {
        "Learning & Growth": "#17becf",
        "Internal Processes": "#bcbd22",
        "Customer": "#ff7f0e",
        "Financial": "#2ca02c"
    }
    
    for perspective in perspective_order:
        nodes.append(perspective)
        node_colors.append(color_map.get(perspective, "#gray"))
    
    # Create links (causality flows)
    links = {
        'source': [],
        'target': [],
        'value': []
    }
    
    # Learning & Growth → Internal Processes
    links['source'].append(0)  # Learning & Growth
    links['target'].append(1)  # Internal Processes
    links['value'].append(30)
    
    # Internal Processes → Customer
    links['source'].append(1)
    links['target'].append(2)
    links['value'].append(25)
    
    # Customer → Financial
    links['source'].append(2)
    links['target'].append(3)
    links['value'].append(20)
    
    # Learning & Growth → Customer (direct impact)
    links['source'].append(0)
    links['target'].append(2)
    links['value'].append(10)
    
    return {
        'nodes': nodes,
        'node_colors': node_colors,
        'links': links
    }


def get_perspective_icon(perspective: str) -> str:
    """Get emoji icon for perspective."""
    icons = {
        "Financial": "💰",
        "Customer": "👥",
        "Internal Processes": "⚙️",
        "Learning & Growth": "📚"
    }
    return icons.get(perspective, "📊")


def format_okr_table(okrs: List[OKR]) -> pd.DataFrame:
    """
    Format OKRs as a DataFrame for table display.
    
    Args:
        okrs: List of OKRs
        
    Returns:
        DataFrame with OKR details
    """
    rows = []
    for okr in okrs:
        for kr in okr.key_results:
            rows.append({
                'Perspectiva': okr.perspective,
                'Objetivo': okr.objective,
                'Key Result': kr.kr,
                'Objetivo_Valor': kr.target,
                'Actual': kr.current,
                'Progreso': f"{kr.progress:.0f}%",
                'Estado': kr.status,
                'Responsable': okr.owner
            })
    
    return pd.DataFrame(rows)
