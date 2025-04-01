import streamlit as st

# IMPORTANTE: Esta debe ser la primera llamada a Streamlit en el script
st.set_page_config(
    page_title="DeFi Portfolio AI Agent",
    page_icon="🧠",
    layout="wide"
)

# Estilo de la página
PRIMARY_COLOR = "#A199DA"
SECONDARY_COLOR = "#403680"
BG_COLOR = "#000000"
ACCENT_COLOR = "#A199DA"

# Apply custom CSS
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {BG_COLOR};
            color: white;
        }}
        h1, h2, h3, h4, h5, h6 {{
            font-family: monospace !important;
            color: {PRIMARY_COLOR};
        }}

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
    </style>
    """,
    unsafe_allow_html=True
)


# Main AI Agent content
st.title("AI Portfolio Agent")
st.write("This is where the AI agent will be implemented")
