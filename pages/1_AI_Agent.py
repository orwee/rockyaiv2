import streamlit as st
import pandas as pd
import datetime
import time
import requests
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

# Custom color palette
PRIMARY_COLOR = "#A199DA"
SECONDARY_COLOR = "#403680"
BG_COLOR = "#000000"
ACCENT_COLOR = "#A199DA"
LOGO_URL = "https://corp.orwee.io/wp-content/uploads/2023/07/cropped-imageonline-co-transparentimage-23-e1689783905238.webp"

# Cargar avatares
assistant_avatar = None
user_avatar = None

# Función para guardar los logs de conversación en session_state
def save_conversation_log(user_message, assistant_response, visualization_type=None):
    """
    Guarda los mensajes de la conversación en session_state y proporciona descarga
    """
    # Inicializar el registro de conversaciones si no existe
    if 'conversation_logs' not in st.session_state:
        st.session_state.conversation_logs = []

    # Añadir la nueva entrada de log
    log_entry = {
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'user_message': user_message,
        'assistant_response': assistant_response,
        'visualization_type': visualization_type if visualization_type else 'none'
    }

    # Guardar en session_state
    st.session_state.conversation_logs.append(log_entry)
    return True

# Apply custom branding
def apply_custom_branding():
    # Custom CSS with Rocky branding
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
            width: 100% !important;
            text-align: left !important;
            font-size: 14px !important;
            margin-bottom: 8px !important;
        }}

        .stButton > button:hover {{
            background-color: {SECONDARY_COLOR} !important;
        }}

        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background-color: {BG_COLOR};
            border-right: 1px solid {PRIMARY_COLOR};
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

        /* Import IBM Plex Mono font */
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&display=swap');

        /* Metrics and key figures */
        .metric-value {{
            color: {PRIMARY_COLOR};
            font-weight: bold;
        }}

        /* Chat container */
        .chat-container {{
            border-radius: 10px;
            background-color: rgba(43, 49, 78, 0.7);
            border: 1px solid {PRIMARY_COLOR};
            padding: 15px;
            margin-bottom: 80px; /* Espacio para el input fijo */
            overflow-y: auto;
            max-height: 60vh;
            min-height: 60vh;
            display: flex;
            flex-direction: column-reverse; /* Mensajes más recientes abajo */
        }}

        /* Input container fijo */
        .input-container {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 10px;
            background-color: {BG_COLOR};
            border-top: 1px solid {PRIMARY_COLOR};
            z-index: 1000;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Rocky - DeFi Assistant",
    page_icon="🚀",
    layout="wide"
)

# Apply branding
apply_custom_branding()

# Initialize session states
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Rocky, your DeFi Assistant built with OI (Orwee Intelligence). How can I help you today?"}
    ]

if 'defi_df' not in st.session_state:
    st.session_state.defi_df = None

if 'df_agent' not in st.session_state:
    st.session_state.df_agent = None

if 'last_query_time' not in st.session_state:
    st.session_state.last_query_time = None

# DeFi Llama API function
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_defi_llama_yields():
    """Consulta pools de https://yields.llama.fi/pools."""
    url = "https://yields.llama.fi/pools"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json().get("data", [])
            df = pd.DataFrame(data)
            return df
        else:
            return pd.DataFrame({"error": [f"Error {response.status_code}: {response.text}"]})
    except Exception as e:
        return pd.DataFrame({"error": [f"Exception occurred: {str(e)}"]})

# Configure the LangChain agent for DeFi Llama data
@st.cache_resource
def setup_defillama_agent(_df):
    api_key = st.secrets.get("OPENAI_API_KEY", None)

    if not api_key:
        st.warning("OpenAI API key not found. Smart assistant functionality will be limited.")
        return None

    try:
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=api_key)
        agent = create_pandas_dataframe_agent(
            llm,
            _df,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            handle_parsing_errors=True,
            allow_dangerous_code=True
        )
        return agent
    except Exception as e:
        st.error(f"Error configuring the DeFi Llama agent: {e}")
        return None

# Function to process DeFi Llama queries
def process_defillama_query(query):
    # Refresh data if needed
    current_time = time.time()
    if st.session_state.defi_df is None or st.session_state.last_query_time is None or current_time - st.session_state.last_query_time > 300:
        with st.spinner("Fetching latest DeFi data..."):
            st.session_state.defi_df = get_defi_llama_yields()
            st.session_state.last_query_time = current_time
            # Setup agent with fresh data
            if st.session_state.defi_df is not None and not st.session_state.defi_df.empty:
                st.session_state.df_agent = setup_defillama_agent(st.session_state.defi_df)

    # Use agent to process query
    if st.session_state.df_agent:
        try:
            # Enhance the query for DeFi Llama context
            enhanced_query = f"""
            Based on the DeFi Llama yields data, {query}.

            When analyzing this data:
            1. If the query mentions a token, chain, protocol, APY or TVL, filter accordingly
            2. For 'best' or 'top' queries, sort by APY in descending order
            3. Always limit results to 5 entries unless otherwise specified
            4. Format amounts with $ and % signs appropriately
            5. Provide specific investment insights and strategies when possible
            """

            response = st.session_state.df_agent.run(enhanced_query)
            return response
        except Exception as e:
            return f"Error processing your query: {str(e)}"
    else:
        return "I couldn't access the DeFi Llama data. Please try again later."

# Sidebar for branding
with st.sidebar:
    # Logo and title in sidebar
    st.markdown(
        f"""
        <div class="logo-container">
            <img src="{LOGO_URL}" alt="Rocky Logo">
            <div class="app-title">Rocky - DeFi Assistant</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")  # Separador después del logo

    # Área para logs de conversación
    if 'conversation_logs' in st.session_state and st.session_state.conversation_logs:
        # Convertir logs a DataFrame
        logs_df = pd.DataFrame(st.session_state.conversation_logs)

        # Botón para descargar logs
        csv_data = logs_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar logs",
            data=csv_data,
            file_name=f"rocky_logs_{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        # Opción para ver logs
        if st.checkbox("Ver logs de esta sesión"):
            st.dataframe(
                logs_df[['timestamp', 'user_message']],
                use_container_width=True
            )

# Contenedor de mensajes (con estilo de ChatGPT)
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

# Mostrar cada mensaje en el contenedor
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=assistant_avatar if msg["role"] == "assistant" else user_avatar):
        st.write(msg["content"])

st.markdown("</div>", unsafe_allow_html=True)

# Contenedor de entrada fijo en la parte inferior
st.markdown("<div class='input-container'>", unsafe_allow_html=True)
input_container = st.container()

with input_container:
    # Input del usuario
    prompt = st.chat_input("Type your query...", key="chat_input")
st.markdown("</div>", unsafe_allow_html=True)

# Procesar entrada del usuario (aquí puedes integrar tu lógica de procesamiento)
if prompt:
    # Agregar mensaje del usuario a la conversación
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Aquí podrías agregar la lógica para que el asistente procese la consulta
    # Por ejemplo, usando el agent de DeFi Llama para procesar consultas relacionadas
    response = process_defillama_query(prompt)

    # Agregar respuesta del asistente
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Guardar en logs
    save_conversation_log(prompt, response)

    # Forzar recarga para mostrar nuevos mensajes
    st.rerun()
