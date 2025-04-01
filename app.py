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
import hashlib

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

        /* Login form styling */
        .login-container {{
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 10px;
            background-color: rgba(43, 49, 78, 0.7);
            border: 1px solid {PRIMARY_COLOR};
        }}

        .login-title {{
            text-align: center;
            margin-bottom: 20px;
            color: {PRIMARY_COLOR};
            font-family: monospace;
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

# Apply CSS
apply_custom_branding()

# User authentication setup - Sample users for testing
USERS = {
    "admin": "admin123",
    "user1": "password123",
    "demo": "demo2024"
}

# Initialize session states
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user' not in st.session_state:
    st.session_state.user = None

# Login function
def login(username, password):
    if username in USERS and USERS[username] == password:
        st.session_state.logged_in = True
        st.session_state.user = username
        return True
    else:
        return False

# Logout function
def logout():
    st.session_state.logged_in = False
    st.session_state.user = None

# Login form
def show_login_form():
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>DeFi Portfolio Login</h2>", unsafe_allow_html=True)

    # Login inputs
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([1, 1])

    with col1:
        login_button = st.button("Login")

    with col2:
        st.markdown("""
        <div style="font-size: 0.8em; margin-top: 8px;">
        Test users:<br>
        - admin/admin123<br>
        - user1/password123<br>
        - demo/demo2024
        </div>
        """, unsafe_allow_html=True)

    if login_button:
        if login(username, password):
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown("</div>", unsafe_allow_html=True)

# Check login status
if not st.session_state.logged_in:
    show_login_form()
else:
    # Show logout button in the sidebar
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.user}")
    if st.sidebar.button("Logout"):
        logout()
        st.rerun()

    # Here starts the main application code
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

    # POSITIONS TAB
    with tabs[0]:
        st.subheader("All Positions")

        # Enrich DataFrame with data to display
        df_display = df.copy()

        # Create filters
        st.write("#### Filters")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # Wallet filter
            wallet_options = ['All'] + sorted(df_display['wallet'].unique().tolist())
            wallet_filter = st.selectbox('Wallet', wallet_options)

        with col2:
            # Blockchain filter
            chain_options = ['All'] + sorted(df_display['chain'].unique().tolist())
            chain_filter = st.selectbox('Blockchain', chain_options)

        with col3:
            # Category filter
            category_options = ['All'] + sorted(df_display['category'].unique().tolist())
            category_filter = st.selectbox('Category', category_options)

        with col4:
            # Protocol filter
            protocol_options = ['All'] + sorted(df_display['protocol'].unique().tolist())
            protocol_filter = st.selectbox('Protocol', protocol_options)

        # Apply filters
        if wallet_filter != 'All':
            df_display = df_display[df_display['wallet'] == wallet_filter]

        if chain_filter != 'All':
            df_display = df_display[df_display['chain'] == chain_filter]

        if category_filter != 'All':
            df_display = df_display[df_display['category'] == category_filter]

        if protocol_filter != 'All':
            df_display = df_display[df_display['protocol'] == protocol_filter]

        # Range to filter by USD value (minimum and maximum)
        min_usd = float(df['usd'].min())
        max_usd = float(df['usd'].max())

        usd_range = st.slider(
            "Value Range (USD)",
            min_value=min_usd,
            max_value=max_usd,
            value=(min_usd, max_usd),  # Default value: full range
            step=1.0
        )

        # Apply USD range filter
        df_display = df_display[(df_display['usd'] >= usd_range[0]) & (df_display['usd'] <= usd_range[1])]

        # Show number of results
        st.write(f"Showing {len(df_display)} of {len(df)} positions")

        # Calculate percentages AFTER all filters, based on the filtered table
        if not df_display.empty:
            filtered_total = df_display['usd'].sum()
            df_display['% of Total'] = (df_display['usd'] / filtered_total * 100).round(2)
        else:
            df_display['% of Total'] = 0  # Handle empty case

        # Reorganize columns for better display
        df_display = df_display[['wallet', 'chain', 'protocol', 'token', 'category', 'usd', '% of Total']]

        # Rename columns for better presentation
        df_display.columns = ['Wallet', 'Blockchain', 'Protocol', 'Token', 'Category', 'USD', '% of Selection']

        # Interactive table with filtering and sorting
        st.dataframe(
            df_display,
            column_config={
                "USD": st.column_config.NumberColumn(
                    format="$%.2f",
                ),
                "% of Selection": st.column_config.ProgressColumn(
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=True,
            use_container_width=True
        )

        # Add useful metrics
        if len(df_display) > 0:  # Only if there are results after filtering
            filtered_total = df_display['USD'].sum()
            total_portfolio = df['usd'].sum()
            filtered_percent = (filtered_total / total_portfolio) * 100

            st.subheader("Selection Metrics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Positions", f"{len(df_display)}")
            with col2:
                st.metric("Total Value", f"${filtered_total:.2f}")
            with col3:
                st.metric("% of Portfolio", f"{filtered_percent:.1f}%")
            with col4:
                if len(df_display) > 0:
                    st.metric("Average", f"${df_display['USD'].mean():.2f}")

    # WALLET TAB
    with tabs[1]:
        st.subheader("Wallet Analysis")

        # Aggregate data
        wallet_data = df.groupby('wallet')['usd'].sum().sort_values(ascending=False)
        total = wallet_data.sum()

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(8, 5))
            wallet_data.plot(kind='bar', ax=ax, color=PRIMARY_COLOR)
            style_plot(ax)
            ax.set_title(f"USD by Wallet")
            ax.set_xlabel("Wallet")
            ax.set_ylabel("USD")
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots(figsize=(8, 5))
            colors = plt.cm.get_cmap(custom_cmap)(np.linspace(0, 1, len(wallet_data)))
            wallet_data.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=colors)
            style_plot(ax)
            ax.set_title(f"Distribution by Wallet")
            ax.axis('equal')
            st.pyplot(fig)

        # Data table
        data_df = pd.DataFrame({
            "Wallet": wallet_data.index,
            "USD": wallet_data.values.round(2),
            "Percentage (%)": [(v/total*100).round(2) for v in wallet_data.values]
        })
        st.dataframe(data_df, hide_index=True)

        # Prepare information for the summary
        top_item = wallet_data.idxmax()
        top_value = wallet_data.max()
        top_percent = (top_value/total*100).round(2)

        # Calculate concentration index (simplified Herfindahl-Hirschman)
        hhi = ((wallet_data / total) ** 2).sum() * 100

        # Formatted text
        st.markdown(f"""
        ### Distribution Analysis by Wallet

        - **Total value:** ${total:.2f} USD
        - **Number of wallets:** {len(wallet_data)}
        - **Highest concentration:** {top_item} with ${top_value:.2f} ({top_percent}% of total)
        - **Average value per wallet:** ${(total/len(wallet_data)).round(2)} USD
        - **Concentration index:** {hhi:.1f}/100 (higher values indicate greater concentration)
        """)

    # BLOCKCHAIN TAB
    with tabs[2]:
        st.subheader("Blockchain Analysis")

        # Aggregate data
        chain_data = df.groupby('chain')['usd'].sum().sort_values(ascending=False)
        total = chain_data.sum()

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(8, 5))
            chain_data.plot(kind='bar', ax=ax, color=PRIMARY_COLOR)
            style_plot(ax)
            ax.set_title(f"USD by Blockchain")
            ax.set_xlabel("Blockchain")
            ax.set_ylabel("USD")
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots(figsize=(8, 5))
            colors = plt.cm.get_cmap(custom_cmap)(np.linspace(0, 1, len(chain_data)))
            chain_data.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=colors)
            style_plot(ax)
            ax.set_title(f"Distribution by Blockchain")
            ax.axis('equal')
            st.pyplot(fig)

        # Data table
        data_df = pd.DataFrame({
            "Blockchain": chain_data.index,
            "USD": chain_data.values.round(2),
            "Percentage (%)": [(v/total*100).round(2) for v in chain_data.values]
        })
        st.dataframe(data_df, hide_index=True)

        # Prepare information for the summary
        top_item = chain_data.idxmax()
        top_value = chain_data.max()
        top_percent = (top_value/total*100).round(2)

        # Calculate concentration index (simplified Herfindahl-Hirschman)
        hhi = ((chain_data / total) ** 2).sum() * 100

        # Formatted text
        st.markdown(f"""
        ### Distribution Analysis by Blockchain

        - **Total value:** ${total:.2f} USD
        - **Number of blockchains:** {len(chain_data)}
        - **Highest concentration:** {top_item} with ${top_value:.2f} ({top_percent}% of total)
        - **Average value per blockchain:** ${(total/len(chain_data)).round(2)} USD
        - **Concentration index:** {hhi:.1f}/100 (higher values indicate greater concentration)
        """)

    # CATEGORIES TAB
    with tabs[3]:
        st.subheader("Categories Analysis")

        # Aggregate data
        cat_data = df.groupby('category')['usd'].sum().sort_values(ascending=False)
        total = cat_data.sum()

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            fig, ax = plt.subplots(figsize=(8, 5))
            cat_data.plot(kind='bar', ax=ax, color=PRIMARY_COLOR)
            style_plot(ax)
            ax.set_title(f"USD by Category")
            ax.set_xlabel("Category")
            ax.set_ylabel("USD")
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots(figsize=(8, 5))
            colors = plt.cm.get_cmap(custom_cmap)(np.linspace(0, 1, len(cat_data)))
            cat_data.plot(kind='pie', autopct='%1.1f%%', ax=ax, colors=colors)
            style_plot(ax)
            ax.set_title(f"Distribution by Category")
            ax.axis('equal')
            st.pyplot(fig)

        # Data table
        data_df = pd.DataFrame({
            "Category": cat_data.index,
            "USD": cat_data.values.round(2),
            "Percentage (%)": [(v/total*100).round(2) for v in cat_data.values]
        })
        st.dataframe(data_df, hide_index=True)

        # Prepare information for the summary
        top_item = cat_data.idxmax()
        top_value = cat_data.max()
        top_percent = (top_value/total*100).round(2)

        # Calculate concentration index (simplified Herfindahl-Hirschman)
        hhi = ((cat_data / total) ** 2).sum() * 100

        # Risk assessment
        risk_level = "High Risk" if cat_data.get('Altcoin', 0)/total > 0.5 else "Medium Risk" if cat_data.get('Altcoin', 0)/total > 0.25 else "Conservative"

        # Formatted text
        st.markdown(f"""
        ### Distribution Analysis by Category

        - **Total value:** ${total:.2f} USD
        - **Number of categories:** {len(cat_data)}
        - **Highest concentration:** {top_item} with ${top_value:.2f} ({top_percent}% of total)
        - **Risk Assessment:** {risk_level}
        - **Concentration index:** {hhi:.1f}/100 (higher values indicate greater concentration)
        """)

    # SUMMARY TAB
    with tabs[4]:
        st.subheader("Portfolio Summary")

        # First row: general metrics
        total_value = df['usd'].sum()
        avg_value = df['usd'].mean()
        unique_chains = df['chain'].nunique()

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Value", f"${total_value:.2f}")
        col2.metric("Average per Position", f"${avg_value:.2f}")
        col3.metric("Blockchains", f"{unique_chains}")

        # Main distribution metrics
        st.subheader("Key Metrics")

        # Prepare data
        wallet_data = df.groupby('wallet')['usd'].sum().sort_values(ascending=False)
        chain_data = df.groupby('chain')['usd'].sum().sort_values(ascending=False)
        cat_data = df.groupby('category')['usd'].sum().sort_values(ascending=False)

        # Calculate summaries
        top_wallet = wallet_data.idxmax()
        top_wallet_value = wallet_data.max()
        top_wallet_percent = (top_wallet_value/total_value*100).round(2)

        top_chain = chain_data.idxmax()
        top_chain_value = chain_data.max()
        top_chain_percent = (top_chain_value/total_value*100).round(2)

        top_category = cat_data.idxmax()
        top_category_value = cat_data.max()
        top_category_percent = (top_category_value/total_value*100).round(2)

        # Display metrics in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Top Wallet", f"{top_wallet}")
            st.metric("Amount", f"${top_wallet_value:.2f}")
            st.metric("Percentage", f"{top_wallet_percent}%")

        with col2:
            st.metric("Top Blockchain", f"{top_chain}")
            st.metric("Amount", f"${top_chain_value:.2f}")
            st.metric("Percentage", f"{top_chain_percent}%")

        with col3:
            st.metric("Top Category", f"{top_category}")
            st.metric("Amount", f"${top_category_value:.2f}")
            st.metric("Percentage", f"{top_category_percent}%")

        # Position Ranking
        st.subheader("Top Positions")
        positions_df = df.copy()
        positions_df['position_name'] = positions_df['token'] + ' (' + positions_df['protocol'] + ')'

        # Sort by USD in descending order
        top_positions = positions_df.sort_values('usd', ascending=False)

        if len(top_positions) > 5:
            top_positions = top_positions.head(5)

        # Position chart (horizontal bars)
        fig, ax = plt.subplots(figsize=(10, max(4, len(top_positions) * 0.4)))
        positions_plot = top_positions.set_index('position_name')['usd']
        colors = plt.cm.get_cmap(custom_cmap)(np.linspace(0, 1, len(positions_plot)))
        positions_plot.plot(kind='barh', ax=ax, color=colors)
        style_plot(ax)
        ax.invert_yaxis()  # Make it display in descending order visually
        ax.set_title("Top Positions by USD")
        ax.set_xlabel("USD")
        ax.set_ylabel("Position")
        st.pyplot(fig)

        # Portfolio strategy summary
        st.subheader("Strategy Assessment")

        # Calculate diversification metrics
        wallet_hhi = ((wallet_data / total_value) ** 2).sum() * 100
        chain_hhi = ((chain_data / total_value) ** 2).sum() * 100
        category_hhi = ((cat_data / total_value) ** 2).sum() * 100

        # Coefficient of variation (higher means more spread out values)
        coef_var = (df['usd'].std() / df['usd'].mean() * 100)

        # Wallet concentration level
        wallet_concentration = "High" if wallet_hhi > 50 else "Medium" if wallet_hhi > 25 else "Low"

        # Blockchain concentration level
        chain_concentration = "High" if chain_hhi > 50 else "Medium" if chain_hhi > 25 else "Low"

        # Category concentration level
        category_concentration = "High" if category_hhi > 50 else "Medium" if category_hhi > 25 else "Low"

        # Position size variation
        pos_variation = "High" if coef_var > 100 else "Medium" if coef_var > 50 else "Low"

        # Strategy assessment
        st.markdown(f"""
        ### Portfolio Characteristics

        The portfolio consists of **{len(df)} positions** with a total value of **${total_value:.2f}**
        spread across **{unique_chains} blockchains** and **{len(wallet_data)} wallets**.

        #### Diversification Assessment:
        - **Wallet concentration:** {wallet_concentration} ({wallet_hhi:.1f}/100)
        - **Blockchain concentration:** {chain_concentration} ({chain_hhi:.1f}/100)
        - **Category concentration:** {category_concentration} ({category_hhi:.1f}/100)
        - **Position size variation:** {pos_variation} ({coef_var:.1f}%)

        #### Key Distribution Stats:
        - **Main blockchain exposure:** {', '.join([f"**{chain}**: **{(value/total_value*100).round(1)}%**" for chain, value in chain_data.items()][:3])}
        - **Main category exposure:** {', '.join([f"**{cat}**: **{(value/total_value*100).round(1)}%**" for cat, value in cat_data.items()])}
        """)
