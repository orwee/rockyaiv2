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

# Custom color palette
PRIMARY_COLOR = "#A199DA"
SECONDARY_COLOR = "#403680"
BG_COLOR = "#000000"
ACCENT_COLOR = "#A199DA"
LOGO_URL = "https://corp.orwee.io/wp-content/uploads/2023/07/cropped-imageonline-co-transparentimage-23-e1689783905238.webp"
LOGO_USER = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRMM9iuYpLlg4Z4qGzMITpHX9PmdEERT-GHtv7RXnVa7SXaJ6-pdi48oj792H-zPNBpiG0&usqp=CAU"

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

# Cargar avatares
assistant_avatar = load_image(LOGO_URL)
user_avatar = load_image(LOGO_USER)

# Create custom sequential color palette for charts
def create_custom_cmap():
    return mpl.colors.LinearSegmentedColormap.from_list("Rocky", [PRIMARY_COLOR, SECONDARY_COLOR])

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

        /* Add your logo */
        .logo-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 10px;
            text-align: center;
        }}

        .logo-container img {{
            width: 30%;
            margin-bottom: 10px;
        }}

        .app-title {{
            font-family: monospace;
            font-weight: bold;
            font-size: 1.5em;
            color: {PRIMARY_COLOR};
            font-size: 14px !important;
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
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="DeFi Portfolio Intelligence",
    page_icon="🚀",
    layout="wide"
)

# Apply branding
apply_custom_branding()

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

# Conversational responses for each query type
def get_conversational_response(query_type):
    responses = {
        'wallet': [
            "Here's the distribution of your funds by wallet. There's an interesting concentration pattern:",
            "Analyzing your wallets... This is interesting. Here's how your funds are distributed across different wallets:",
            "I've reviewed your data and here's the wallet distribution. There are clear concentration patterns."
        ],
        'chain': [
            "I've analyzed your exposure to different blockchains. Here's a breakdown of how your funds are distributed:",
            "Blockchain diversification analysis: This data shows which chains you're currently invested in and how value is distributed:",
            "Here's the blockchain analysis. It's interesting to see the distribution across different ecosystems:"
        ],
        'category': [
            "I've categorized your tokens and here's the distribution. This shows your balance between stablecoins, bluechips, and altcoins:",
            "Let's look at the distribution by token category... This is interesting. The proportion between different asset types is notable:",
            "Here's the category analysis. The distribution reflects certain investment patterns:"
        ],
        'dashboard': [
            "Here's a dashboard with the main metrics and visualizations of your portfolio:",
            "An overview is always useful. I've generated this dashboard with different perspectives of your portfolio to visualize the distributions:",
            "Presenting a complete summary of your portfolio with different visualizations to better understand the current position:"
        ],
        'total': [
            "I've calculated the total value of your portfolio. You currently have invested:",
            "According to my calculations, the total value of your portfolio at this moment is:",
            "Reviewing your positions, the total value of your portfolio is:"
        ],
        'positions': [
            "Here are the details of all your positions. You can filter by any criteria and by value range. Percentages are calculated based on the current selection:",
            "I've prepared an interactive table with all your positions. Use the filters to find exactly what you're looking for and the value range that interests you:",
            "These are all your current positions. The filters allow you to analyze specific segments of your portfolio. The percentage column shows the proportion within your selection:"
        ]
    }

    return random.choice(responses.get(query_type, ["Here's what you asked for:"]))

# Initialize session states
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Rocky, your DeFi Portfolio Assistant. How can I help you today?"}
    ]

if 'show_visualization' not in st.session_state:
    st.session_state.show_visualization = {
        'show': False,
        'type': None,      # can be 'dashboard', 'specific', 'positions'
        'group_by': None   # wallet, chain, etc. (None for dashboard)
    }

if 'conversation_logs' not in st.session_state:
    st.session_state.conversation_logs = []

# BILINGUAL KEYWORDS MAP
BILINGUAL_KEYWORDS = {
    'wallet': ['wallet', 'billetera', 'cartera', 'wallets'],
    'chain': ['chain', 'blockchain', 'cadena', 'blockchains', 'chains'],
    'category': ['category', 'categoría', 'categoria', 'tipo', 'categories'],
    'protocol': ['protocol', 'protocolo', 'protocols'],
    'dashboard': ['dashboard', 'tablero', 'completo', 'general', 'overview', 'summary'],
    'positions': ['positions', 'posiciones', 'activos', 'assets', 'holdings'],
    'total': ['total', 'valor', 'value', 'balance', 'worth']
}

# Logo and title
st.markdown(
    f"""
    <div class="logo-container">
        <img src="{LOGO_URL}" alt="Rocky Logo">
        <div class="app-title">Rocky - DeFi Portfolio Assistant</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Portfolio Analysis")

# Quick function buttons row at the top instead of sidebar
st.subheader("Quick Functions")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Wallet Distribution", key="wallet_dist", use_container_width=True):
        response = get_conversational_response('wallet')
        st.session_state.messages.append({"role": "user", "content": "Show wallet distribution"})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.show_visualization = {
            'show': True,
            'type': 'specific',
            'group_by': 'wallet'
        }

    if st.button("Blockchain Analysis", key="blockchain_analysis", use_container_width=True):
        response = get_conversational_response('chain')
        st.session_state.messages.append({"role": "user", "content": "Visualize my blockchain exposure"})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.show_visualization = {
            'show': True,
            'type': 'specific',
            'group_by': 'chain'
        }

with col2:
    if st.button("Token Categories", key="token_categories", use_container_width=True):
        response = get_conversational_response('category')
        st.session_state.messages.append({"role": "user", "content": "Distribution by token categories"})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.show_visualization = {
            'show': True,
            'type': 'specific',
            'group_by': 'category'
        }

    if st.button("Complete Dashboard", key="complete_dashboard", use_container_width=True):
        response = get_conversational_response('dashboard')
        st.session_state.messages.append({"role": "user", "content": "Show a complete dashboard"})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.show_visualization = {
            'show': True,
            'type': 'dashboard',
            'group_by': None
        }

with col3:
    if st.button("Show Positions", key="show_positions", use_container_width=True):
        response = get_conversational_response('positions')
        st.session_state.messages.append({"role": "user", "content": "Show all my positions"})
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.show_visualization = {
            'show': True,
            'type': 'positions',
            'group_by': None
        }

    if st.button("Total Value", key="total_value", use_container_width=True):
        response = get_conversational_response('total')
        total_value = df['usd'].sum()
        st.session_state.messages.append({"role": "user", "content": "What's the total value of my portfolio?"})
        st.session_state.messages.append({"role": "assistant", "content": f"{response} ${total_value:.2f} USD"})
        st.session_state.show_visualization = {
            'show': False,
            'type': None,
            'group_by': None
        }

# Visualization area (if activated)
if st.session_state.show_visualization['show']:
    viz_type = st.session_state.show_visualization['type']
    group_by = st.session_state.show_visualization.get('group_by', None)

    viz_container = st.container()

    # [Mantener el resto del código de visualización igual que en el original]
    # (Este es el código largo de visualización que incluye todas las funciones de gráficos)

    with viz_container:
        if viz_type == 'specific' and group_by:
            # Código de visualización específica
            # [Mantener igual que en el original]
            pass
        elif viz_type == 'dashboard':
            # Código del dashboard
            # [Mantener igual que en el original]
            pass
        elif viz_type == 'positions':
            # Código de posiciones
            # [Mantener igual que en el original]
            pass
