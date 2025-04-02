import pandas as pd
import re
import requests
import json
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import random

# Page configuration
st.set_page_config(
    page_title="Rocky - DeFi Assistant",
    page_icon="🚀",
    layout="wide"
)

# Clase para el agente con memoria
class CryptoAgent:
    def __init__(self):
        # Estado del agente - memoria para almacenar las variables
        self.state = {
            "blockchain": None,
            "token": None,
            "tvl_min": None,
            "apy_min": None,
            "protocol": None
        }

        # Almacenar las últimas oportunidades encontradas
        self.last_opportunities = []

        # Mapeo de nombres de blockchain para DeFiLlama
        self.chain_mapping = {
            "ethereum": "Ethereum",
            "arbitrum": "Arbitrum",
            "solana": "Solana",
            "avalanche": "Avalanche",
            "polygon": "Polygon",
            "binance": "BSC",
            "bsc": "BSC",
            "optimism": "Optimism",
            "fantom": "Fantom",
            "cardano": "Cardano",
            "base": "Base"
        }

    def process_tvl_value(self, value_str):
        """Procesa valores de TVL con K y M"""
        value_str = value_str.strip().lower()
        if value_str.endswith('k'):
            return str(float(value_str[:-1]) * 1000)
        elif value_str.endswith('m'):
            return str(float(value_str[:-1]) * 1000000)
        else:
            return value_str

    def detect_all_variables(self, query):
        """Detecta todas las variables mencionadas en la consulta"""
        query_lower = query.lower()
        updates = {}

        # PRIMERO detectar token para evitar conflictos con blockchain
        # Detectar token (priorizar patrones que mencionan explícitamente "token")
        token_patterns = [
            r'token\s+(?:de\s+)?(\w+)',
            r'el\s+token\s+(?:de\s+)?(\w+)',
            r'(\w+)\s+token',
            r'selecciona(?:r)?\s+(?:el\s+)?token\s+(?:de\s+)?(\w+)',
            r'buscar?\s+(?:el\s+)?token\s+(?:de\s+)?(\w+)',
            r'encontrar?\s+(?:el\s+)?token\s+(?:de\s+)?(\w+)',
            r'busca\s+(?:el\s+)?token\s+(?:de\s+)?(\w+)'
        ]

        for pattern in token_patterns:
            token_match = re.search(pattern, query_lower)
            if token_match:
                token = token_match.group(1)
                if token and token not in ["a", "el", "la", "los", "las", "de", "del"]:
                    updates["token"] = token
                    break

        # Luego detectar blockchain, evitando detectar tokens como blockchains
        if "token" not in updates:  # Solo buscar blockchain si no se detectó token explícitamente
            for chain_key, chain_value in self.chain_mapping.items():
                blockchain_patterns = [
                    r'blockchain\s+(?:de\s+)?'+chain_key,
                    r'en\s+'+chain_key,
                    r'de\s+(?:la\s+)?(?:blockchain|cadena|red)\s+(?:de\s+)?'+chain_key,
                    chain_key+r'\s+(?:blockchain|cadena|red)',
                    r'selecciona(?:r)?\s+(?:la\s+)?(?:blockchain|cadena|red)\s+(?:de\s+)?'+chain_key,
                    r'select\s+'+chain_key,
                    r'\b'+chain_key+r'\b'
                ]

                for pattern in blockchain_patterns:
                    if re.search(pattern, query_lower):
                        updates["blockchain"] = chain_key
                        break

                if "blockchain" in updates:
                    break

            # Detectar blockchain no soportada solo si no se detectó token
            blockchain_patterns = [
                r'blockchain\s+(?:de\s+)?(\w+)',
                r'en\s+(\w+)\b(?!\s+token)',
                r'de\s+(?:la\s+)?(?:blockchain|cadena|red)\s+(?:de\s+)?(\w+)',
                r'(\w+)\s+(?:blockchain|cadena|red)',
                r'selecciona(?:r)?\s+(?:la\s+)?(?:blockchain|cadena|red)\s+(?:de\s+)?(\w+)'
            ]

            if "blockchain" not in updates:
                for pattern in blockchain_patterns:
                    blockchain_match = re.search(pattern, query_lower)
                    if blockchain_match:
                        chain = blockchain_match.group(1)
                        if chain not in self.chain_mapping and chain not in ["a", "el", "la", "los", "las", "de", "del"]:
                            return {"error": f"Blockchain '{chain}' no soportada. Las blockchains disponibles son: {', '.join(self.chain_mapping.keys())}"}

        # Detectar protocolo
        protocol_patterns = [
            r'protocol(?:o)?\s+(?:de\s+)?(\w+)',
            r'(?:en|del|con)\s+protocol(?:o)?\s+(?:de\s+)?(\w+)',
            r'(?:el|del)\s+protocol(?:o)?\s+(?:de\s+)?(\w+)',
            r'(\w+)\s+protocol(?:o)?',
            r'selecciona(?:r)?\s+(?:el\s+)?protocol(?:o)?\s+(?:de\s+)?(\w+)'
        ]

        for pattern in protocol_patterns:
            protocol_match = re.search(pattern, query_lower)
            if protocol_match:
                protocol = protocol_match.group(1)
                if protocol not in ["a", "el", "la", "los", "las", "de", "del"]:
                    updates["protocol"] = protocol
                    break

        # Detectar TVL mínimo con soporte para K y M
        tvl_patterns = [
            r'tvl\s+(?:min(?:imo)?|mayor|superior)\s+(?:a|de)?\s*(\d+(?:\.\d+)?(?:[km])?)',
            r'tvl\s+de\s+(\d+(?:\.\d+)?(?:[km])?)',
            r'tvl\s+minimo\s+de\s+(\d+(?:\.\d+)?(?:[km])?)',
            r'minimo\s+(?:de\s+)?tvl\s+(?:de\s+)?(\d+(?:\.\d+)?(?:[km])?)',
            r'tvl\s+min(?:imo)?\s+(\d+(?:\.\d+)?(?:[km])?)'
        ]

        for pattern in tvl_patterns:
            tvl_match = re.search(pattern, query_lower)
            if tvl_match:
                tvl_value = tvl_match.group(1)
                updates["tvl_min"] = self.process_tvl_value(tvl_value)
                break

        # Detectar APY mínimo
        apy_patterns = [
            r'apy\s+(?:min(?:imo)?|mayor|superior)\s+(?:a|de)?\s*(\d+(?:\.\d+)?)',
            r'apy\s+de\s+(\d+(?:\.\d+)?)',
            r'apy\s+minimo\s+de\s+(\d+(?:\.\d+)?)',
            r'minimo\s+(?:de\s+)?apy\s+(?:de\s+)?(\d+(?:\.\d+)?)',
            r'apy\s+min(?:imo)?\s+(\d+(?:\.\d+)?)'
        ]

        for pattern in apy_patterns:
            apy_match = re.search(pattern, query_lower)
            if apy_match:
                updates["apy_min"] = apy_match.group(1)
                break

        # Detectar búsqueda libre de token (si no se ha detectado mediante patrones)
        if "token" not in updates and not any(key in updates for key in ["blockchain", "tvl_min", "apy_min", "protocol", "error"]):
            # Verificar si hay palabras clave de búsqueda
            search_keywords = ["buscar", "encontrar", "busca", "encuentra", "hallar", "mostrar", "ver", "listar"]
            if any(keyword in query_lower for keyword in search_keywords):
                # Eliminar palabras clave y palabras comunes
                common_words = ["me", "un", "una", "el", "la", "los", "las", "de", "del", "por", "para", "con", "y", "o", "a", "al", "se", "si", "en", "que", "por", "favor"]
                for word in search_keywords + common_words:
                    query_lower = query_lower.replace(f" {word} ", " ")

                # Limpiar y obtener palabras que podrían ser tokens
                tokens = query_lower.strip().split()
                if tokens:
                    updates["token"] = tokens[0]  # Tomar la primera palabra como token

        return updates

    def update_state(self, updates):
        """Actualiza el estado con las variables detectadas"""
        if not updates:
            return None

        # Verificar si hay error
        if "error" in updates:
            return updates["error"]

        # Actualizar el estado sin retornar mensajes
        for key, value in updates.items():
            self.state[key] = value

        # No retornamos mensaje de actualización, solo actualizamos silenciosamente
        return ""

    def detect_position_request(self, query):
        """Detecta si el usuario está pidiendo información detallada sobre una posición específica"""
        query_lower = query.lower()

        # Eliminar comillas y paréntesis para la detección
        query_clean = re.sub(r'[\'"\(\)]', '', query_lower)

        # Patrones para detectar consultas sobre posiciones específicas
        position_patterns = [
            r'(?:mas|más)\s*info(?:rmacion|rmación)?\s*(?:de|sobre)?\s*(?:la)?\s*(?:posicion|posición)?\s*(\d+)',
            r'info(?:rmacion|rmación)?\s*(?:de|sobre)?\s*(?:la)?\s*(?:posicion|posición)?\s*(\d+)',
            r'detalle(?:s)?\s*(?:de|sobre)?\s*(?:la)?\s*(?:posicion|posición)?\s*(\d+)',
            r'dame\s*(?:mas|más)?\s*(?:de|sobre)?\s*(?:la)?\s*(?:posicion|posición)?\s*(\d+)',
            r'ver\s*(?:la)?\s*(?:posicion|posición)?\s*(\d+)',
            r'mostrar\s*(?:la)?\s*(?:posicion|posición)?\s*(\d+)',
            r'detalles\s*(?:del|de la|de)?\s*(\d+)',
            r'mas\s*sobre\s*(?:el|la)?\s*(\d+)',
            r'informacion\s*(?:del|de la)?\s*(\d+)'
        ]

        for pattern in position_patterns:
            position_match = re.search(pattern, query_clean)
            if position_match:
                try:
                    position = int(position_match.group(1))
                    # Ajustar a base 0 para indexar el array
                    return position - 1
                except ValueError:
                    return None

        return None

    def detect_chart_request(self, query):
        """Detecta si el usuario está pidiendo un gráfico comparativo"""
        query_lower = query.lower()

        # Patrones para detectar solicitudes de gráficos
        chart_patterns = [
            r'(?:haz|crea|genera|muestra|visualiza)(?:me)?\s+(?:un)?\s*(?:grafico|gráfico|chart|visualizacion|visualización)',
            r'(?:comparar|compara)(?:me)?\s+(?:las)?\s*(?:oportunidades|posiciones|pools)',
            r'(?:ver|mostrar|visualizar)\s+(?:la)?\s*(?:evolucion|evolución|tendencia|historia)',
            r'(?:grafico|gráfico|chart)\s+(?:comparativo|de comparacion|comparación)',
            r'(?:evolución|evolucion)\s+(?:del|de la|de)?\s*apy'
        ]

        for pattern in chart_patterns:
            if re.search(pattern, query_lower):
                return True

        return False

    def get_ai_response(self, context):
        """Genera respuestas conversacionales según el contexto"""
        search_responses = [
            "Analizando datos de la blockchain en tiempo real...",
            "Explorando las oportunidades DeFi disponibles ahora mismo...",
            "Rastreando los mejores rendimientos en el ecosistema cripto...",
            "Consultando Smart Contracts en múltiples blockchains...",
            "Procesando datos on-chain para encontrar las mejores opciones...",
            "Evaluando pools de liquidez y sus rendimientos actuales...",
            "Comparando protocolos DeFi según tus criterios...",
            "Buscando oportunidades que maximicen tu APY con el menor riesgo..."
        ]

        details_responses = [
            "Profundizando en los datos de esta posición...",
            "Analizando métricas detalladas de este protocolo...",
            "Extrayendo información completa de este Smart Contract...",
            "Verificando la composición y seguridad de esta pool...",
            "Calculando estadísticas históricas de rendimiento..."
        ]

        chart_responses = [
            "Visualizando tendencias históricas para estas posiciones...",
            "Generando análisis comparativo de rendimientos en el tiempo...",
            "Trazando la evolución del APY durante el período seleccionado...",
            "Creando visualización para evaluar la estabilidad del rendimiento..."
        ]

        if context == "search":
            return random.choice(search_responses)
        elif context == "details":
            return random.choice(details_responses)
        elif context == "chart":
            return random.choice(chart_responses)
        else:
            return "Procesando tu solicitud en el ecosistema DeFi..."

    def search_defi_opportunities(self):
        """Busca oportunidades DeFi que cumplan con los criterios actuales"""
        try:
            # Hacer la llamada a la API de DeFiLlama
            response = requests.get('https://yields.llama.fi/pools')

            if response.status_code != 200:
                return None, f"Error al consultar la API de DeFiLlama: {response.status_code}"

            data = response.json()

            if data["status"] != "success" or "data" not in data:
                return None, "Error en la respuesta de la API de DeFiLlama"

            # Convertir los datos a un DataFrame para facilitar el filtrado
            opportunities = pd.DataFrame(data["data"])

            # Aplicar filtros según las variables de estado
            filtered_opps = opportunities.copy()

            if self.state["blockchain"]:
                chain_name = self.chain_mapping.get(self.state["blockchain"].lower(), self.state["blockchain"])
                filtered_opps = filtered_opps[filtered_opps['chain'].str.lower() == chain_name.lower()]

            if self.state["protocol"]:
                filtered_opps = filtered_opps[filtered_opps['project'].str.lower() == self.state["protocol"].lower()]

            # Filtrar por símbolo del token
            if self.state["token"]:
                filtered_opps = filtered_opps[filtered_opps['symbol'].str.lower().str.contains(self.state["token"].lower())]

            # Filtrar por TVL mínimo
            if self.state["tvl_min"]:
                filtered_opps = filtered_opps[filtered_opps['tvlUsd'] >= float(self.state["tvl_min"])]

            if self.state["apy_min"]:
                filtered_opps = filtered_opps[filtered_opps['apy'] >= float(self.state["apy_min"])]

            # Ordenar por APY descendente
            filtered_opps = filtered_opps.sort_values(by='apy', ascending=False)

            # Seleccionar las 5 mejores oportunidades
            top_opportunities = filtered_opps.head(5)

            if top_opportunities.empty:
                self.last_opportunities = []
                return None, "No se encontraron oportunidades que cumplan con los criterios actuales."

            # Guardar las oportunidades completas para consultas detalladas
            self.last_opportunities = top_opportunities.to_dict('records')

            # Preparar los datos para mostrar en Streamlit
            results = []
            for i, opp in enumerate(self.last_opportunities):
                result = {
                    "posicion": i + 1,
                    "chain": opp["chain"],
                    "project": opp["project"],
                    "symbol": opp["symbol"],
                    "tvlUsd": f"${opp['tvlUsd']:,.2f}",
                    "apy": f"{opp['apy']:.2f}%",
                    "ilRisk": opp["ilRisk"],
                    "exposure": opp["exposure"],
                    "pool": opp["pool"]  # Añadimos el ID de la pool para poder obtener el gráfico
                }
                results.append(result)

            return results, None  # Devolver resultados y None para el error

        except Exception as e:
            return None, f"Error al buscar oportunidades DeFi: {str(e)}"

    def get_position_details(self, position_index):
        """Obtiene los detalles completos de una posición específica"""
        if not self.last_opportunities or position_index < 0 or position_index >= len(self.last_opportunities):
            return None, "Posicion no disponible. Por favor, primero busca oportunidades."

        # Obtener la posición solicitada
        position = self.last_opportunities[position_index]

        # Formatear todos los datos disponibles
        formatted_position = {}
        for key, value in position.items():
            if key == 'tvlUsd':
                formatted_position[key] = f"${value:,.2f}"
            elif key in ['apy', 'apyBase', 'apyReward', 'apyPct1D', 'apyPct7D', 'apyPct30D', 'apyMean30d']:
                if value is not None:
                    formatted_position[key] = f"{value:.2f}%"
                else:
                    formatted_position[key] = "No disponible"
            elif key == 'rewardTokens' and value:
                formatted_position[key] = ", ".join(value) if value else "Ninguno"
            elif key == 'underlyingTokens' and value:
                formatted_position[key] = ", ".join(value) if value else "Ninguno"
            else:
                formatted_position[key] = value

        # Convertir a DataFrame para mostrarlo como tabla
        detail_df = pd.DataFrame([formatted_position])
        detail_df_transposed = detail_df.T.reset_index()
        detail_df_transposed.columns = ['Característica', 'Valor']

        return detail_df_transposed, None  # Devolver detalles y None para el error

    def generate_comparative_chart(self):
        """Genera un gráfico comparativo de la evolución del APY para las posiciones encontradas"""
        if not self.last_opportunities:
            return None, "No hay posiciones para comparar. Primero realiza una búsqueda."

        try:
            # Obtener datos históricos de cada posición
            position_data = []
            legends = []

            for i, position in enumerate(self.last_opportunities):
                if 'pool' not in position:
                    continue

                pool_id = position['pool']
                url = f'https://yields.llama.fi/chart/{pool_id}'

                response = requests.get(url)
                if response.status_code != 200:
                    continue

                data = response.json()
                if data["status"] != "success" or "data" not in data:
                    continue

                # Crear un DataFrame para esta posición
                pool_df = pd.DataFrame(data["data"])

                # Convertir timestamp a datetime y eliminar información de zona horaria
                pool_df['timestamp'] = pd.to_datetime(pool_df['timestamp']).dt.tz_localize(None)

                # Filtrar para los últimos 7 días
                last_7_days = datetime.now() - timedelta(days=7)
                pool_df = pool_df[pool_df['timestamp'] >= last_7_days]

                # Si hay datos, añadirlos a la lista
                if not pool_df.empty:
                    position_data.append(pool_df)
                    # Crear leyenda con información de la posición
                    legend = f"{i+1}: {position['symbol']} ({position['project']} - {position['chain']})"
                    legends.append(legend)

            if not position_data:
                return None, "No se pudieron obtener datos históricos para ninguna de las posiciones."

            # Crear figura de Plotly
            fig = go.Figure()

            # Añadir línea para cada posición
            for i, data in enumerate(position_data):
                fig.add_trace(go.Scatter(
                    x=data['timestamp'],
                    y=data['apy'],
                    mode='lines+markers',
                    name=legends[i],
                    line=dict(width=2),
                    marker=dict(size=6)
                ))

            # Configurar el diseño del gráfico
            fig.update_layout(
                title="Evolución del APY en los últimos 7 días",
                xaxis_title="Fecha",
                yaxis_title="APY (%)",
                legend_title="Posiciones",
                template="plotly_white",
                height=600
            )

            return fig, None

        except Exception as e:
            return None, f"Error al generar el gráfico comparativo: {str(e)}"

    def process_query(self, query):
        """Procesa la consulta del usuario de manera inteligente"""
        query_lower = query.lower()

        # Verificar si es una solicitud de reseteo
        if any(word in query_lower for word in ["reset", "resetear", "borrar", "limpiar", "reiniciar"]):
            self.reset_state()
            return "Variables reseteadas. Ahora puedes establecer nuevos criterios de búsqueda."

        # Verificar si es una solicitud de gráfico comparativo
        if self.detect_chart_request(query):
            ai_message = self.get_ai_response("chart")
            fig, error = self.generate_comparative_chart()
            if error:
                return f"{ai_message}\n\n{error}"
            return f"{ai_message}\n\nGráfico comparativo de APY de las últimas oportunidades:", "chart", fig

        # Verificar si el usuario está pidiendo detalles sobre una posición específica
        position_index = self.detect_position_request(query)
        if position_index is not None:
            ai_message = self.get_ai_response("details")
            details, error = self.get_position_details(position_index)
            if error:
                return f"{ai_message}\n\n{error}"
            return f"{ai_message}\n\nDetalles de la posición {position_index + 1}:", "details", details

        # Detectar y actualizar todas las variables mencionadas en la consulta
        updates = self.detect_all_variables(query)
        update_message = None
        if updates:
            update_message = self.update_state(updates)
            if "error" in updates or (update_message and update_message.startswith("Blockchain '")):
                return update_message  # Devolver mensaje de error

        # Añadir mensaje AI para búsqueda
        ai_message = self.get_ai_response("search")

        # Buscar y devolver resultados
        results, error = self.search_defi_opportunities()

        if error:
            return f"{ai_message}\n\n{error}"

        # Combinar mensajes y resultados
        return f"{ai_message}\n\nResultados de la búsqueda:", "results", results

    def reset_state(self):
        """Resetea todas las variables a None"""
        for key in self.state:
            self.state[key] = None
        self.last_opportunities = []

# Inicialización del estado de sesión
if "agent" not in st.session_state:
    st.session_state.agent = CryptoAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Título y descripción
st.title("🚀 Rocky - DeFi Assistant")
st.markdown("""
Asistente de DeFi que te ayuda a encontrar las mejores oportunidades según tus criterios.
Simplemente dime qué buscas y te mostraré opciones que cumplan tus requisitos.
""")

# Sidebar con variables actuales
st.sidebar.header("Criterios actuales")
if st.session_state.agent:
    agent = st.session_state.agent
    st.sidebar.markdown(f"**Blockchain:** {agent.state['blockchain'] or 'No especificado'}")
    st.sidebar.markdown(f"**Token:** {agent.state['token'] or 'No especificado'}")
    st.sidebar.markdown(f"**TVL mínimo:** {agent.state['tvl_min'] + '$' if agent.state['tvl_min'] else 'No especificado'}")
    st.sidebar.markdown(f"**APY mínimo:** {agent.state['apy_min'] + '%' if agent.state['apy_min'] else 'No especificado'}")
    st.sidebar.markdown(f"**Protocolo:** {agent.state['protocol'] or 'No especificado'}")

    if st.sidebar.button("Resetear criterios"):
        agent.reset_state()
        st.sidebar.success("Criterios reseteados")
        st.rerun()

# Mostrar mensajes anteriores
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])

        # Si hay datos para mostrar
        if "data_type" in message and "data" in message:
            if message["data_type"] == "results" or message["data_type"] == "details":
                # Mostrar tabla de resultados o detalles
                st.dataframe(message["data"], use_container_width=True)
            elif message["data_type"] == "chart" and message["data"] is not None:
                # Mostrar gráfico
                st.plotly_chart(message["data"], use_container_width=True)

# Input del usuario
prompt = st.chat_input("¿Qué quieres buscar? (Ej: 'Token ETH en Arbitrum con TVL mínimo 1M')")

if prompt:
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Procesar la consulta
    agent = st.session_state.agent
    response = agent.process_query(prompt)

    # Verificar si la respuesta contiene datos
    if isinstance(response, tuple) and len(response) == 3:
        message, data_type, data = response

        # Agregar mensaje a la sesión
        st.session_state.messages.append({
            "role": "assistant",
            "content": message,
            "data_type": data_type,
            "data": data
        })

        # Mostrar mensaje
        st.chat_message("assistant").write(message)

        # Mostrar datos según el tipo
        if data_type == "results" or data_type == "details":
            if data is not None:
                st.dataframe(data, use_container_width=True)
        elif data_type == "chart":
            if data is not None:
                st.plotly_chart(data, use_container_width=True)
    else:
        # Es un mensaje simple
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "data_type": None,
            "data": None
        })
        st.chat_message("assistant").write(response)

    # Actualizar sidebar
    st.rerun()
