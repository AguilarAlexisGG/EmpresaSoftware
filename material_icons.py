"""
Material Icons Helper for Streamlit
====================================
Provides functions to render Google Material Icons in Streamlit using HTML/CSS.

Icons from: https://fonts.google.com/icons
"""

import streamlit as st


def load_material_icons():
    """Load Material Icons stylesheet in the Streamlit app."""
    st.markdown("""
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
    .material-icons {
        vertical-align: middle;
        font-size: 24px;
    }
    .material-icons.small { font-size: 18px; }
    .material-icons.medium { font-size: 24px; }
    .material-icons.large { font-size: 36px; }
    </style>
    """, unsafe_allow_html=True)


def icon(name: str, size: str = "medium", color: str = None) -> str:
    """
    Return HTML for a Material Icon.
    
    Args:
        name: Icon name from Material Icons (e.g., 'dashboard', 'analytics')
        size: 'small', 'medium', or 'large'
        color: Optional color in hex or CSS color name
        
    Returns:
        HTML string for the icon
        
    Example:
        >>> st.markdown(icon('dashboard') + " Dashboard", unsafe_allow_html=True)
    """
    color_style = f"color: {color};" if color else ""
    return f'<span class="material-icons {size}" style="{color_style}">{name}</span>'


# Common icons mapping
ICONS = {
    # Navigation
    'dashboard': 'dashboard',
    'analytics': 'analytics',
    'insights': 'insights',
    'targets': 'track_changes',
    'predictions': 'psychology',
    
    # KPIs
    'completion': 'task_alt',
    'budget': 'account_balance_wallet',
    'team': 'groups',
    'bugs': 'bug_report',
    'time': 'schedule',
    'satisfaction': 'sentiment_satisfied',
    
    # OKRs
    'financial': 'paid',
    'customer': 'people',
    'processes': 'settings',
    'learning': 'school',
    
    # Actions
    'refresh': 'refresh',
    'logout': 'logout',
    'login': 'login',
    'close': 'close',
    'filter': 'filter_list',
    
    # Status
    'success': 'check_circle',
    'warning': 'warning',
    'error': 'error',
    'info': 'info',
    
    # Metrics
    'trending_up': 'trending_up',
    'trending_down': 'trending_down',
    'trending_flat': 'trending_flat',
}


def get_icon(key: str, size: str = "medium", color: str = None) -> str:
    """Get icon HTML by key from ICONS mapping."""
    icon_name = ICONS.get(key, 'circle')
    return icon(icon_name, size, color)
