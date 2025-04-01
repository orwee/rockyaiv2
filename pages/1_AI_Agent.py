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
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory

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
            margin-bottom: 15px;
            overflow-y: auto;
            max-height: 400px;
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

# DeFi Llama API function
def get_defi_llama_yields():
    """Consulta pools de https://yields.llama.fi/pools."""
    url = "https://yields.llama.fi/pools"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Exception occurred: {str(e)}"}

# Initialize LangChain components
@st.cache_resource
def setup_langchain():
    try:
        # Try to read from secrets.toml first
        api_key = st.secrets.get("OPENAI_API_KEY", None)
    except:
        # If not in secrets, read from environment variables
        api_key = os.environ.get("OPENAI_API_KEY", None)

    if not api_key:
        st.warning("OpenAI API key not found. AI capabilities will be limited.")
        return None

    try:
        llm = ChatOpenAI(temperature=0.7, model="gpt-4o-mini", api_key=api_key)
        memory = ConversationBufferMemory(return_messages=True)
        return llm, memory
    except Exception as e:
        st.error(f"Error configuring LangChain: {e}")
        return None, None

# Initialize chat state variables
def init_chat_state():
    if 'defi_messages' not in st.session_state:
        st.session_state.defi_messages = [
            {"role": "assistant", "content": "Hola! Soy tu DeFi Investment Assistant. Puedo ayudarte a encontrar oportunidades de inversión basadas en tus preferencias. ¿Qué tipo de oportunidades estás buscando?"}
        ]

    # Filtros para DeFi Llama
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'blockchain' not in st.session_state:
        st.session_state.blockchain = None
    if 'protocol' not in st.session_state:
        st.session_state.protocol = None
    if 'min_apy' not in st.session_state:
        st.session_state.min_apy = 0.0
    if 'min_tvl' not in st.session_state:
        st.session_state.min_tvl = 0.0
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'last_query_time' not in st.session_state:
        st.session_state.last_query_time = None

# Integración de LangChain con DeFi Llama
def process_message_with_langchain(llm, message):
    # Contexto del sistema para LangChain
    system_prompt = """
    Eres un asistente especializado en DeFi que ayuda a los usuarios a encontrar oportunidades de inversión.
    Tu tarea es extraer los siguientes parámetros del mensaje del usuario:
    - Token (ej. ETH, BTC, USDC)
    - Blockchain (ej. Ethereum, Polygon, Solana)
    - Protocolo (ej. Aave, Curve, Uniswap)
    - APY mínimo (un porcentaje)
    - TVL mínimo (un valor en USD)
    
    Responde de manera conversacional y solicita cualquier información faltante.
    """
    
    # Crear contexto para LangChain
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""
        Analiza este mensaje del usuario y extrae los parámetros para buscar oportunidades DeFi:
        "{message}"
        
        Información actual:
        - Token: {st.session_state.token if st.session_state.token else 'No especificado'}
        - Blockchain: {st.session_state.blockchain if st.session_state.blockchain else 'No especificado'}
        - Protocolo: {st.session_state.protocol if st.session_state.protocol else 'No especificado'}
        - APY mínimo: {st.session_state.min_apy}%
        - TVL mínimo: ${st.session_state.min_tvl:,.2f}
        
        Responde de manera conversacional y actualiza los parámetros según corresponda.
        """)
    ]
    
    # Obtener respuesta del modelo
    response = llm.invoke(messages)
    
    # Analizar la respuesta para extraer parámetros
    response_text = response.content
    
    # Extraer token (símbolos comunes en cripto)
    token_keywords = ["token", "moneda", "cripto"]
    for keyword in token_keywords:
        if keyword.lower() in message.lower():
            # Buscar palabras en mayúsculas que podrían ser tokens
            words = message.split()
            for word in words:
                if word.isupper() and len(word) >= 2 and len(word) <= 5:
                    st.session_state.token = word

    # Extraer blockchain
    blockchain_keywords = {
        "ethereum": "Ethereum",
        "polygon": "Polygon",
        "arbitrum": "Arbitrum",
        "optimism": "Optimism",
        "solana": "Solana",
        "avalanche": "Avalanche",
        "base": "Base",
        "bnb": "BSC",
        "binance": "BSC"
    }

    for keyword, value in blockchain_keywords.items():
        if keyword.lower() in message.lower():
            st.session_state.blockchain = value

    # Extraer protocolo
    protocol_keywords = {
        "aave": "Aave",
        "curve": "Curve",
        "uniswap": "Uniswap",
        "compound": "Compound",
        "sushi": "SushiSwap",
        "convex": "Convex"
    }

    for keyword, value in protocol_keywords.items():
        if keyword.lower() in message.lower():
            st.session_state.protocol = value

    # Extraer APY mínimo
    apy_keywords = ["apy", "rendimiento", "interés", "ganancia", "%"]
    for keyword in apy_keywords:
        if keyword.lower() in message.lower():
            # Buscar números cerca de las palabras clave
            parts = message.lower().split()
            for i, part in enumerate(parts):
                if keyword in part and i > 0:
                    try:
                        possible_number = parts[i-1].replace('%', '').replace(',', '.')
                        apy = float(possible_number)
                        st.session_state.min_apy = apy
                    except:
                        pass

    # Extraer TVL mínimo
    tvl_keywords = ["tvl", "locked", "bloqueado"]
    for keyword in tvl_keywords:
        if keyword.lower() in message.lower():
            # Buscar números cerca de las palabras clave
            parts = message.lower().split()
            for i, part in enumerate(parts):
                if keyword in part and i > 0:
                    try:
                        possible_number = parts[i-1].replace('$', '').replace('k', '000').replace('m', '000000').replace(',', '')
                        tvl = float(possible_number)
                        st.session_state.min_tvl = tvl
                    except:
                        pass

    # Verificar si el usuario quiere buscar
    search_keywords = ["buscar", "mostrar", "ver", "encontrar", "resultados", "oportunidades"]
    for keyword in search_keywords:
        if keyword.lower() in message.lower():
            result = search_defi_opportunities()
            if "encontrado" in result:
                return f"{response_text}\n\n{result}"

    return response_text

# Función para buscar oportunidades basadas en los filtros
def search_defi_opportunities():
    # Para evitar demasiadas llamadas a la API, limitamos a una vez por minuto
    current_time = time.time()
    if st.session_state.last_query_time is not None and current_time - st.session_state.last_query_time < 60:
        # Si hay resultados previos, los usamos
        if st.session_state.search_results is not None:
            return "Aquí tienes el top 5 de oportunidades ordenadas por APY:"
        else:
            return "Estoy esperando un momento antes de hacer otra consulta. Por favor, espera unos segundos."

    # Actualizamos el tiempo de la última consulta
    st.session_state.last_query_time = current_time

    # Consultamos la API
    response = get_defi_llama_yields()

    if "error" in response:
        return f"Lo siento, hubo un error al consultar la API: {response['error']}"

    # Obtenemos los datos
    data = response.get("data", [])

    if not data:
        return "No se encontraron datos en la respuesta de la API."

    # Filtramos según los criterios
    filtered_data = []

    for pool in data:
        # Aplicamos los filtros
        matches = True

        if st.session_state.token:
            if not (st.session_state.token in pool.get("symbol", "") or st.session_state.token in pool.get("project", "")):
                matches = False

        if st.session_state.blockchain:
            if st.session_state.blockchain != pool.get("chain", ""):
                matches = False

        if st.session_state.protocol:
            if st.session_state.protocol != pool.get("project", ""):
                matches = False

        if st.session_state.min_apy > 0:
            pool_apy = pool.get("apy", 0)
            if not isinstance(pool_apy, (int, float)):
                try:
                    pool_apy = float(pool_apy)
                except:
                    pool_apy = 0

            if pool_apy < st.session_state.min_apy:
                matches = False

        if st.session_state.min_tvl > 0:
            pool_tvl = pool.get("tvlUsd", 0)
            if not isinstance(pool_tvl, (int, float)):
                try:
                    pool_tvl = float(pool_tvl)
                except:
                    pool_tvl = 0

            if pool_tvl < st.session_state.min_tvl:
                matches = False

        if matches:
            filtered_data.append(pool)

    # Ordenamos por APY descendente
    filtered_data = sorted(filtered_data, key=lambda x: float(x.get('apy', 0) or 0), reverse=True)

    # Almacenamos los resultados en el estado de la sesión
    st.session_state.search_results = filtered_data

    if not filtered_data:
        return "No encontré oportunidades que coincidan con tus criterios. ¿Quieres ajustar alguno de los filtros?"

    return f"He encontrado {len(filtered_data)} oportunidades que coinciden con tus criterios. Aquí está el top 5 ordenado por APY:"

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
    llm, memory = setup_langchain()

    # Main AI Agent content
    st.title("AI Portfolio Agent")

    # Crear pestañas
    tab1, tab2 = st.tabs(["Oportunidades de Inversión", "Segunda Pestaña"])

    # Pestaña 1: Oportunidades de Inversión
    with tab1:
        st.subheader("Asistente de Inversión DeFi")

        # Mostrar el estado actual de los filtros
        st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
        st.write("### Filtros actuales")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f"**Token:** {st.session_state.token if st.session_state.token else 'No especificado'}")
            st.write(f"**Blockchain:** {st.session_state.blockchain if st.session_state.blockchain else 'No especificado'}")

        with col2:
            st.write(f"**Protocolo:** {st.session_state.protocol if st.session_state.protocol else 'No especificado'}")
            st.write(f"**APY Mínimo:** {st.session_state.min_apy}%")

        with col3:
            st.write(f"**TVL Mínimo:** ${st.session_state.min_tvl:,.2f}")
            if st.button("Reset Filtros"):
                st.session_state.token = None
                st.session_state.blockchain = None
                st.session_state.protocol = None
                st.session_state.min_apy = 0.0
                st.session_state.min_tvl = 0.0
                st.session_state.search_results = None
                st.session_state.defi_messages.append({"role": "assistant", "content": "He reiniciado todos los filtros. ¿En qué puedo ayudarte ahora?"})
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Mostrar chat usando chat_message para evitar el bucle
        for message in st.session_state.defi_messages:
            with st.chat_message(message["role"], avatar=assistant_avatar if message["role"] == "assistant" else user_avatar):
                st.write(message["content"])

        # Input del usuario con chat_input para mantener consistencia
        user_input = st.chat_input("Escribe tu mensaje aquí...", key="defi_chat_input")

        if user_input:
            # Mostrar mensaje del usuario
            with st.chat_message("user", avatar=user_avatar):
                st.write(user_input)
            
            # Agregar mensaje del usuario al historial
            st.session_state.defi_messages.append({"role": "user", "content": user_input})
            
            # Procesar con LangChain si está configurado
            if llm:
                response = process_message_with_langchain(llm, user_input)
            else:
                # Fallback básico si no hay API
                response = "Lo siento, necesito una clave API de OpenAI para procesar tu consulta de manera inteligente. Puedes intentar buscar directamente usando comandos como 'buscar oportunidades'."
                if "buscar" in user_input.lower() or "mostrar" in user_input.lower() or "ver" in user_input.lower():
                    response = search_defi_opportunities()
            
            # Mostrar respuesta del asistente
            with st.chat_message("assistant", avatar=assistant_avatar):
                st.write(response)
                
            # Agregar respuesta al historial
            st.session_state.defi_messages.append({"role": "assistant", "content": response})

        # Mostrar resultados de búsqueda si existen
        if st.session_state.search_results:
            st.subheader("Top 5 Oportunidades (Ordenadas por APY)")

            # Convertir a DataFrame para mejor visualización
            df_results = pd.DataFrame(st.session_state.search_results)

            # Seleccionar y renombrar columnas relevantes
            if not df_results.empty:
                try:
                    # Asegurarse que APY sea numérico para ordenar correctamente
                    df_results['apy'] = pd.to_numeric(df_results['apy'], errors='coerce')

                    # Ordenar por APY descendente
                    df_results = df_results.sort_values('apy', ascending=False)

                    # Limitar a top 5
                    df_top5 = df_results.head(5)

                    # Seleccionar columnas para mostrar
                    df_display = df_top5[['symbol', 'chain', 'project', 'apy', 'tvlUsd']].copy()
                    df_display.columns = ['Token', 'Blockchain', 'Protocolo', 'APY (%)', 'TVL (USD)']

                    # Formatear columnas numéricas
                    df_display['APY (%)'] = df_display['APY (%)'].apply(lambda x: f"{float(x):.2f}%" if pd.notnull(x) else "N/A")
                    df_display['TVL (USD)'] = df_display['TVL (USD)'].apply(lambda x: f"${float(x):,.2f}" if pd.notnull(x) else "N/A")

                    # Mostrar los resultados
                    st.dataframe(df_display, use_container_width=True)

                    # Mostrar más detalle sobre la mejor oportunidad
                    if not df_top5.empty:
                        st.subheader("Detalles de la mejor oportunidad")
                        best_opportunity = df_top5.iloc[0]

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Token", best_opportunity.get('symbol', 'N/A'))
                            st.metric("Protocolo", best_opportunity.get('project', 'N/A'))
                        with col2:
                            st.metric("APY", f"{best_opportunity.get('apy', 0):.2f}%")
                            st.metric("Blockchain", best_opportunity.get('chain', 'N/A'))
                        with col3:
                            st.metric("TVL", f"${best_opportunity.get('tvlUsd', 0):,.2f}")
                            risk = "Bajo" if best_opportunity.get('ilRisk') == "no" else "Medio-Alto"
                            st.metric("Riesgo IL", risk)

                except Exception as e:
                    st.error(f"Error al mostrar resultados: {str(e)}")
                    st.write(df_results.head())

    # Pestaña 2: Por implementar
    with tab2:
        st.subheader("Segunda pestaña - Por implementar")
        st.write("Esta funcionalidad estará disponible próximamente")
