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

    # Main AI Agent content
    st.title("AI Portfolio Agent")
    st.write("This is where the AI agent will be implemented")
