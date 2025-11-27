"""
OLAP Functions Module
=====================
Provides core OLAP (Online Analytical Processing) operations for multidimensional data analysis.

This module implements standard OLAP operations:
- Slice: Filter by single dimension
- Dice: Filter by multiple dimensions
- Drill Down: Increase granularity
- Roll Up: Decrease granularity (aggregate)
- Pivot: Reshape data for analysis

Author: DSS Team
Date: 2025-11-27
"""

import pandas as pd
from typing import Dict, List, Any, Optional, Union
import numpy as np


def slice_olap(df: pd.DataFrame, dimension: str, value: Any) -> pd.DataFrame:
    """
    Filter DataFrame by a single dimension value (SLICE operation).
    
    Args:
        df: Input DataFrame
        dimension: Column name to filter on
        value: Value to filter for
        
    Returns:
        Filtered DataFrame
        
    Raises:
        ValueError: If dimension doesn't exist in DataFrame
        
    Example:
        >>> df_china = slice_olap(df_projects, 'nombre_pais', 'China')
        >>> # Returns only projects in China
    """
    if dimension not in df.columns:
        raise ValueError(f"Dimension '{dimension}' not found in DataFrame. Available: {df.columns.tolist()}")
    
    return df[df[dimension] == value].copy()


def dice(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Filter DataFrame by multiple dimensions (DICE operation).
    
    Args:
        df: Input DataFrame
        filters: Dictionary of {column_name: value} pairs
        
    Returns:
        Filtered DataFrame
        
    Raises:
        ValueError: If any dimension doesn't exist in DataFrame
        
    Example:
        >>> df_filtered = dice(df_projects, {
        ...     'nombre_pais': 'China',
        ...     'ganancia_neta': lambda x: x > 100000
        ... })
        >>> # Returns projects in China with profit > 100K
    """
    result = df.copy()
    
    for dimension, value in filters.items():
        if dimension not in df.columns:
            raise ValueError(f"Dimension '{dimension}' not found. Available: {df.columns.tolist()}")
        
        # Support callable filters (lambda functions)
        if callable(value):
            result = result[result[dimension].apply(value)]
        else:
            result = result[result[dimension] == value]
    
    return result


def drill_down(df: pd.DataFrame, dimension: str, hierarchy: List[str], 
               target_level: str) -> pd.DataFrame:
    """
    Increase granularity by drilling down a hierarchy.
    
    Args:
        df: Input DataFrame
        dimension: Base dimension to drill down
        hierarchy: List of columns representing hierarchy levels (broader to finer)
        target_level: Target column in hierarchy to group by
        
    Returns:
        DataFrame grouped at target level
        
    Example:
        >>> # Drill from year to month level
        >>> df_monthly = drill_down(df, 'tiempo', ['año', 'mes', 'dia'], 'mes')
    """
    if target_level not in hierarchy:
        raise ValueError(f"Target level '{target_level}' not in hierarchy: {hierarchy}")
    
    # Find the position of target level
    target_idx = hierarchy.index(target_level)
    
    # Group by all levels up to and including target
    group_cols = [col for col in hierarchy[:target_idx + 1] if col in df.columns]
    
    if not group_cols:
        raise ValueError(f"None of the hierarchy columns found in DataFrame")
    
    return df.groupby(group_cols, as_index=False).agg({
        col: 'sum' if pd.api.types.is_numeric_dtype(df[col]) else 'first'
        for col in df.columns if col not in group_cols
    })


def roll_up(df: pd.DataFrame, dimension: str, hierarchy: List[str], 
            target_level: str) -> pd.DataFrame:
    """
    Decrease granularity by rolling up a hierarchy (aggregation).
    
    Args:
        df: Input DataFrame
        dimension: Base dimension to roll up
        hierarchy: List of columns representing hierarchy levels (broader to finer)
        target_level: Target column in hierarchy to aggregate to
        
    Returns:
        DataFrame aggregated at target level
        
    Example:
        >>> # Roll up from daily to yearly level
        >>> df_yearly = roll_up(df, 'tiempo', ['año', 'mes', 'dia'], 'año')
    """
    if target_level not in hierarchy:
        raise ValueError(f"Target level '{target_level}' not in hierarchy: {hierarchy}")
    
    # Find position of target level (should be earlier in hierarchy for roll-up)
    target_idx = hierarchy.index(target_level)
    
    # Group by target level only
    group_cols = [col for col in hierarchy[:target_idx + 1] if col in df.columns]
    
    if not group_cols:
        raise ValueError(f"Target level '{target_level}' not found in DataFrame")
    
    # Aggregate numeric columns
    agg_dict = {}
    for col in df.columns:
        if col not in group_cols:
            if pd.api.types.is_numeric_dtype(df[col]):
                agg_dict[col] = 'sum'
            else:
                agg_dict[col] = 'first'  # Take first value for non-numeric
    
    return df.groupby(group_cols, as_index=False).agg(agg_dict)


def pivot_olap(df: pd.DataFrame, rows: Union[str, List[str]], 
               columns: str, values: str, 
               aggfunc: str = 'sum') -> pd.DataFrame:
    """
    Reshape DataFrame for multidimensional analysis (PIVOT operation).
    
    Args:
        df: Input DataFrame
        rows: Column(s) to use for row index
        columns: Column to use for column headers
        values: Column to aggregate
        aggfunc: Aggregation function ('sum', 'mean', 'count', etc.)
        
    Returns:
        Pivoted DataFrame
        
    Example:
        >>> # Create matrix of profits by country and year
        >>> pivot_df = pivot_olap(df_projects, 
        ...                       rows='nombre_pais', 
        ...                       columns='año', 
        ...                       values='ganancia_neta',
        ...                       aggfunc='sum')
    """
    required_cols = [rows] if isinstance(rows, str) else rows
    required_cols.extend([columns, values])
    
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Columns not found: {missing}. Available: {df.columns.tolist()}")
    
    try:
        pivot_table = pd.pivot_table(
            df,
            index=rows,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        )
        return pivot_table.reset_index()
    except Exception as e:
        raise ValueError(f"Pivot operation failed: {str(e)}")


def calculate_metric_trend(df: pd.DataFrame, time_column: str, 
                           metric_column: str, periods: int = 6) -> Dict[str, Any]:
    """
    Calculate trend for a metric over time (for sparklines).
    
    Args:
        df: Input DataFrame
        time_column: Column representing time dimension
        metric_column: Column to calculate trend for
        periods: Number of recent periods to analyze
        
    Returns:
        Dictionary with trend data and statistics
        
    Example:
        >>> trend = calculate_metric_trend(df, 'mes', 'ganancia_neta', periods=6)
        >>> # Returns {'values': [...], 'direction': 'up', 'change_pct': 15.5}
    """
    if time_column not in df.columns or metric_column not in df.columns:
        return {'values': [], 'direction': 'flat', 'change_pct': 0}
    
    # Sort by time and aggregate
    df_sorted = df.sort_values(time_column)
    trend_data = df_sorted.groupby(time_column)[metric_column].sum().tail(periods)
    
    values = trend_data.values.tolist()
    
    if len(values) < 2:
        return {'values': values, 'direction': 'flat', 'change_pct': 0}
    
    # Calculate direction and change
    first_val = values[0] if values[0] != 0 else 0.01  # Avoid division by zero
    last_val = values[-1]
    change_pct = ((last_val - first_val) / abs(first_val)) * 100
    
    direction = 'up' if change_pct > 5 else ('down' if change_pct < -5 else 'flat')
    
    return {
        'values': values,
        'direction': direction,
        'change_pct': round(change_pct, 1),
        'min': min(values),
        'max': max(values),
        'avg': round(np.mean(values), 2)
    }


def apply_olap_filters(df: pd.DataFrame, 
                       date_range: Optional[tuple] = None,
                       dimensions: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Apply multiple OLAP filters to a DataFrame (convenience function).
    
    Args:
        df: Input DataFrame
        date_range: Optional tuple of (start_date, end_date)
        dimensions: Optional dictionary of dimension filters
        
    Returns:
        Filtered DataFrame
        
    Example:
        >>> filtered = apply_olap_filters(
        ...     df,
        ...     date_range=('2024-01-01', '2024-12-31'),
        ...     dimensions={'nombre_pais': 'China', 'status': 'completed'}
        ... )
    """
    result = df.copy()
    
    # Apply date range filter if provided
    if date_range and 'fecha' in df.columns:
        start, end = date_range
        result = result[(result['fecha'] >= start) & (result['fecha'] <= end)]
    
    # Apply dimension filters
    if dimensions:
        result = dice(result, dimensions)
    
    return result


# Utility function for data quality
def validate_olap_cube(df: pd.DataFrame, required_dimensions: List[str], 
                       required_measures: List[str]) -> Dict[str, Any]:
    """
    Validate that a DataFrame has required OLAP dimensions and measures.
    
    Args:
        df: DataFrame to validate
        required_dimensions: List of required dimension columns
        required_measures: List of required measure columns
        
    Returns:
        Dictionary with validation results
        
    Example:
        >>> validation = validate_olap_cube(
        ...     df, 
        ...     required_dimensions=['nombre_proyecto', 'nombre_cliente'],
        ...     required_measures=['ganancia_neta', 'costo_total_real']
        ... )
    """
    missing_dims = [dim for dim in required_dimensions if dim not in df.columns]
    missing_measures = [measure for measure in required_measures if measure not in df.columns]
    
    # Check for null values in measures
    null_counts = {}
    for measure in required_measures:
        if measure in df.columns:
            null_counts[measure] = df[measure].isnull().sum()
    
    return {
        'valid': len(missing_dims) == 0 and len(missing_measures) == 0,
        'missing_dimensions': missing_dims,
        'missing_measures': missing_measures,
        'null_counts': null_counts,
        'row_count': len(df),
        'column_count': len(df.columns)
    }
