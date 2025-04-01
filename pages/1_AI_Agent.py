import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import time
import os
from PIL import Image
from io import BytesIO
from langchain_openai import ChatOpenAI
from langchain.agents import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from langchain.tools import Tool
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
'''
# IMPORTANTE: Esta debe ser la primera llamada a Streamlit en el script
st.set_page_config(
    page_title="DeFi Portfolio AI Agent",
    page_icon="🧠",
    layout="wide"
)
'''
# Estilo de la página
PRIMARY_COLOR = "#A199DA"
SECONDARY_COLOR = "#403680"
BG_COLOR = "#000000"
ACCENT_COLOR = "#A199DA"
LOGO_URL = "https://corp.orwee.io/wp-content/uploads/2023/07/cropped-imageonline-co-transparentimage-23-e1689783905238.webp"
LOGO_USER = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRMM9iuYpLlg4Z4qGzMITpHX9PmdEERT-GHtv7RXnVa7SXaJ6-pdi48oj792H-zPNBpiG0&usqp=CAU"

# Cargar avatares
assistant_avatar = None #load_image(LOGO_URL)
user_avatar = None #load_image(LOGO_USER)

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

        /* Filter display */
        .filter-container {{
            background-color: rgba(43, 49, 78, 0.5);
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
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
    """,
    unsafe_allow_html=True
)

# Check if logged in from main app
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'user' not in st.session_state:
    st.session_state.user = None

# User authentication setup - Sample users for testing (same as in main app)
USERS = {
    "admin": "admin123",
    "user1": "password123",
    "demo": "demo2024"
}

# Login function
def login(username, password):
    if username in USERS and USERS[username] == password:
        st.session_state.logged_in = True
        st.session_state.user = username
        return True
    else:
        return False

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

# DeFi Llama API function como herramienta de LangChain
def get_defi_llama_yields():
    """Consulta pools de https://yields.llama.fi/pools y devuelve los datos como DataFrame."""
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

# Initialize LangChain components with tools
@st.cache_resource
def setup_langchain():
    api_key = st.secrets.get("OPENAI_API_KEY", None)

    if not api_key:
        st.warning("OpenAI API key not found. AI capabilities will be limited.")
        return None, None, None

    try:
        # Crear el LLM
        llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini", api_key=api_key)

        # Crear memoria
        memory = ConversationBufferMemory(return_messages=True)

        # Herramienta para consultar DeFi Llama
        def query_defi_llama():
            return get_defi_llama_yields()

        defi_llama_tool = Tool(
            name="DeFiLlamaAPI",
            func=query_defi_llama,
            description="Consulta oportunidades de inversión DeFi a través de la API de DeFi Llama"
        )

        return llm, memory, defi_llama_tool
    except Exception as e:
        st.error(f"Error configuring LangChain: {e}")
        return None, None, None

# Initialize chat state variables
def init_chat_state():
    if 'defi_messages' not in st.session_state:
        st.session_state.defi_messages = [
            {"role": "assistant", "content": "Hola! Soy tu DeFi Investment Assistant. Puedo ayudarte a encontrar oportunidades de inversión basadas en tus preferencias. ¿Qué tipo de oportunidades estás buscando?"}
        ]

    # Dataframe para resultados de DeFi Llama
    if 'defi_df' not in st.session_state:
        st.session_state.defi_df = None

    # Inicialización del agente de pandas
    if 'df_agent' not in st.session_state:
        st.session_state.df_agent = None

    # Última consulta
    if 'last_query_time' not in st.session_state:
        st.session_state.last_query_time = None

# Función para crear el agente de DataFrame
def create_dataframe_agent(llm, df):
    if df is not None and not df.empty:
        try:
            agent = create_pandas_dataframe_agent(
                llm,
                df,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                handle_parsing_errors=True
            )
            return agent
        except Exception as e:
            st.error(f"Error creating DataFrame agent: {e}")
            return None
    return None

# Función para procesar consultas del usuario
def process_query(llm, df_agent, query):
    if df_agent is None:
        # Si no hay agente disponible, realizamos una nueva consulta
        df = get_defi_llama_yields()
        if df is not None and not df.empty:
            st.session_state.defi_df = df
            df_agent = create_dataframe_agent(llm, df)
            st.session_state.df_agent = df_agent
        else:
            return "No se pudieron obtener datos de DeFi Llama. Intenta más tarde."

    try:
        # Prompt para extraer intención y parámetros
        extraction_prompt = """
        Analiza la consulta del usuario sobre inversiones DeFi y ayúdame a entender:

        1. Qué token está buscando (ETH, BTC, USDC, etc.) si lo menciona
        2. Qué blockchain le interesa (Ethereum, Polygon, etc.) si lo menciona
        3. Si menciona un APY mínimo
        4. Si menciona un TVL mínimo
        5. Qué tipo de análisis quiere hacer

        Consulta: {query}
        """

        prompt_template = PromptTemplate(template=extraction_prompt, input_variables=["query"])
        extraction_chain = LLMChain(llm=llm, prompt=prompt_template)

        # Extraer parámetros
        extraction_result = extraction_chain.run(query=query)

        # Ahora ejecutamos la consulta en el DataFrame
        if "token" in query.lower() or "chain" in query.lower() or "blockchain" in query.lower() or "apy" in query.lower() or "tvl" in query.lower() or "protocol" in query.lower():
            # Construir una consulta más específica para el agente de DataFrame
            df_query = f"""
            Basado en los datos de DeFi Llama, {query}.

            Analiza esto como un experto en finanzas DeFi. Si la consulta menciona un token, blockchain, protocolo, APY o TVL,
            filtra los datos según esos criterios. Si menciona 'top', 'mejores' o similar, ordena por APY descendente
            y muestra los mejores resultados.

            Formatea el resultado como una tabla con las columnas más relevantes y limitada a 5-10 filas.
            """
            result = df_agent.run(df_query)
        else:
            result = df_agent.run(query)

        return f"{extraction_result}\n\n{result}"
    except Exception as e:
        return f"Error al procesar tu consulta: {str(e)}. Intenta ser más específico o reformular tu pregunta."

# Check login status
if not st.session_state.logged_in:
    show_login_form()
else:
    # Show logout button in the sidebar
    st.sidebar.markdown(f"**Logged in as:** {st.session_state.user}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

    # Inicializar variables de estado para el chat
    init_chat_state()

    # Configurar LangChain
    llm, memory, defi_llama_tool = setup_langchain()

    # Main AI Agent content
    st.title("AI Portfolio Agent")

    # Crear pestañas
    tab1, tab2 = st.tabs(["Oportunidades de Inversión", "Segunda Pestaña"])

    # Pestaña 1: Oportunidades de Inversión
    with tab1:
        st.subheader("Asistente de Inversión DeFi")

        # Mostrar el estado actual de los filtros (opcional, podemos mantenerlo)
        st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
        if st.button("Actualizar datos de DeFi Llama"):
            with st.spinner("Actualizando datos..."):
                df = get_defi_llama_yields()
                if df is not None and not df.empty:
                    st.session_state.defi_df = df
                    st.session_state.df_agent = create_dataframe_agent(llm, df)
                    st.session_state.defi_messages.append({"role": "assistant", "content": f"Datos actualizados. Tengo información de {len(df)} oportunidades de inversión. ¿Qué te gustaría analizar?"})
                    st.rerun()
                else:
                    st.error("No se pudieron obtener datos de DeFi Llama")
        st.markdown("</div>", unsafe_allow_html=True)

        # Contenedor de mensajes (con estilo de ChatGPT)
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

        # Mostrar cada mensaje en el contenedor
        for message in st.session_state.defi_messages:
            with st.chat_message(message["role"], avatar=assistant_avatar if message["role"] == "assistant" else user_avatar):
                st.write(message["content"])

        st.markdown("</div>", unsafe_allow_html=True)

        # Contenedor de entrada fijo en la parte inferior
        st.markdown("<div class='input-container'>", unsafe_allow_html=True)
        # Crear un contenedor para el input que se mantendrá fijo en la parte inferior
        input_container = st.container()

        with input_container:
            # Input del usuario
            user_input = st.chat_input("Escribe tu mensaje aquí...", key="defi_chat_input")

            if user_input:
                # Agregar mensaje del usuario al historial
                st.session_state.defi_messages.append({"role": "user", "content": user_input})

                # Obtener datos si aún no los tenemos
                if st.session_state.defi_df is None or st.session_state.df_agent is None:
                    with st.spinner("Obteniendo datos iniciales de DeFi Llama..."):
                        df = get_defi_llama_yields()
                        if df is not None and not df.empty:
                            st.session_state.defi_df = df
                            st.session_state.df_agent = create_dataframe_agent(llm, df)

                # Procesar la consulta
                if llm and st.session_state.df_agent:
                    with st.spinner("Procesando tu consulta..."):
                        response = process_query(llm, st.session_state.df_agent, user_input)
                else:
                    response = "No puedo procesar tu consulta porque no se han cargado correctamente los datos o la API de OpenAI. Intenta actualizar los datos de DeFi Llama."

                # Agregar respuesta al historial
                st.session_state.defi_messages.append({"role": "assistant", "content": response})

                # Recargar para mostrar los nuevos mensajes
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # Pestaña 2: Por implementar
    with tab2:
        st.subheader("Segunda pestaña - Por implementar")
        st.write("Esta funcionalidad estará disponible próximamente")
