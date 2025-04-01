import streamlit as st
import pandas as pd
from PIL import Image
from io import BytesIO
import requests

# Custom color palette
PRIMARY_COLOR = "#A199DA"
SECONDARY_COLOR = "#403680"
BG_COLOR = "#000000"
ACCENT_COLOR = "#A199DA"
LOGO_URL = "https://corp.orwee.io/wp-content/uploads/2023/07/cropped-imageonline-co-transparentimage-23-e1689783905238.webp"

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
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="DeFi Portfolio AI Agent",
    page_icon="🧠",
    layout="wide"
)

# Apply branding
apply_custom_branding()

# Logo and title
st.markdown(
    f"""
    <div class="logo-container">
        <img src="{LOGO_URL}" alt="Rocky Logo">
        <div class="app-title">Rocky - DeFi AI Assistant</div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("AI Portfolio Agent")

# Solo añadir el título como se pidió
st.write("This is where the AI agent will be implemented")
