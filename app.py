import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import random
import matplotlib as mpl
from PIL import Image
from io import BytesIO
import requests
import datetime

# Page configuration - DEBE SER LA PRIMERA LLAMADA A STREAMLIT
st.set_page_config(
    page_title="DeFi Portfolio Intelligence",
    page_icon="🚀",
    layout="wide"
)

# Custom color palette
PRIMARY_COLOR = "#A199DA"
SECONDARY_COLOR = "#403680"
BG_COLOR = "#000000"
ACCENT_COLOR = "#A199DA"

# Apply custom branding
def apply_custom_branding():
    # Custom CSS with branding
    css = f"""
    <style>
        /* Main background and text */
        .stApp {{
            background-color: {BG_COLOR};
            color: white;
        }}

        /* Header styling */
        h1, h2, h3, h4, h5, h6 {{
            font-family: monospace !important;
            color: {PRIMARY_COLOR};
        }}

        /* Custom button styling */
        .stButton > button {{
            background-color: {PRIMARY_COLOR} !important;
            color: white !important;
            border: none !important;
            font-family: monospace !important;
            padding: 10px 15px !important;
            border-radius: 4px !important;
            text-align: left !important;
            font-size: 14px !important;
            margin-bottom: 8px !important;
        }}

        .stButton > button:hover {{
            background-color: {SECONDARY_COLOR} !important;
        }}

        /* Metrics and key figures */
        .metric-value {{
            color: {PRIMARY_COLOR};
            font-weight: bold;
        }}

        /* Custom chart background */
        .chart-container {{
            background-color: rgba(43, 49, 78, 0.7);
            padding: 15px;
            border-radius: 5px;
            border: 1px solid {PRIMARY_COLOR};
        }}

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background-color: {BG_COLOR};
            color: white;
            border-radius: 4px 4px 0 0;
            padding: 10px 16px;
            border: 1px solid {PRIMARY_COLOR};
            border-bottom: none;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {PRIMARY_COLOR};
            color: white;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Función para cargar imágenes desde URL
@st.cache_data
def load_image(url):
    try:
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        return img
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

# Create custom sequential color palette for charts
def create_custom_cmap():
    return mpl.colors.LinearSegmentedColormap.from_list("Rocky", [PRIMARY_COLOR, SECONDARY_COLOR])

# Load portfolio data
@st.cache_data
def load_portfolio_data():
    portfolio_data = [
        {
            "id": 1,
            "wallet": "Wallet #1",
            "chain": "base",
            "protocol": "Uniswap V3",
            "token": "ODOS",
            "usd": 21.91
        },
        {
            "id": 2,
            "wallet": "Wallet #1",
            "chain": "mantle",
            "protocol": "Pendle V2",
            "token": "ETH/cmETH",
            "usd": 554.81
        },
        {
            "id": 3,
            "wallet": "Wallet #2",
            "chain": "base",
            "protocol": "aave",
            "token": "USDT",
            "usd": 2191
        },
        {
            "id": 4,
            "wallet": "Wallet #3",
            "chain": "solana",
            "protocol": "meteora",
            "token": "JLP/SOL",
            "usd": 551
        },
        {
            "id": 5,
            "wallet": "Wallet #1",
            "chain": "ethereum",
            "protocol": "Aave V3",
            "token": "ETH",
            "usd": 3.50
        },
    ]
    return pd.DataFrame(portfolio_data)

# Apply CSS after configuración de página
apply_custom_branding()

# Load data
df = load_portfolio_data()

# Classify tokens
def classify_token(token):
    stablecoins = ['USDT', 'USDC', 'DAI', 'BUSD']
    bluechips = ['ETH', 'BTC', 'SOL']

    for stable in stablecoins:
        if stable in token:
            return 'Stablecoin'

    for blue in bluechips:
        if blue in token:
            return 'Bluechip'

    return 'Altcoin'

df['category'] = df['token'].apply(classify_token)

# Configure plot style for all visualizations
plt.style.use('dark_background')
custom_cmap = create_custom_cmap()

def style_plot(ax):
    """Apply branding style to matplotlib plots"""
    ax.set_facecolor(BG_COLOR)
    ax.figure.set_facecolor(BG_COLOR)
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color(PRIMARY_COLOR)
    for spine in ax.spines.values():
        spine.set_color(ACCENT_COLOR)
    return ax

# Initialize session states
if 'conversation_logs' not in st.session_state:
    st.session_state.conversation_logs = []

# Create tabs for navigation
tabs = st.tabs(["Positions", "Wallet", "Blockchain", "Categories", "Summary"])

# [EL RESTO DEL CÓDIGO DE TABS IGUAL A LO QUE TE PROPORCIONÉ ANTERIORMENTE]
