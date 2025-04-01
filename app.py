import streamlit as st
import google.generativeai as genai
import os

# --- Configuración de la Página Streamlit ---
st.set_page_config(
    page_title="Chatbot Departamental Gemini",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Chatbot Departamental con Gemini")
st.caption("Un asistente para ayudarte en tus tareas diarias.")

# --- Gestión de la API Key ---
# MÉTODO 1: Usando Streamlit Secrets (Recomendado para despliegue)
# Intenta obtener la clave desde los secretos de Streamlit
google_api_key = st.secrets.get("GOOGLE_API_KEY")

# MÉTODO 2: Usando variable de entorno (Para pruebas locales)
# Si no se encontró en secrets, intenta obtenerla del entorno
if not google_api_key:
    google_api_key = os.getenv("GOOGLE_API_KEY")

# MÉTODO 3: Input manual (Menos seguro, SÓLO para pruebas locales rápidas)
# Si aún no hay clave, pide al usuario que la introduzca (en la barra lateral)
if not google_api_key:
    st.warning("API Key no encontrada en st.secrets ni en variables de entorno.")
    google_api_key = st.sidebar.text_input("Ingresa tu Google API Key:", type="password")

if not google_api_key:
    st.error("Por favor, proporciona tu Google API Key para continuar.")
    st.stop() # Detiene la ejecución si no hay clave

# --- Configuración del Modelo Gemini ---
try:
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Error al configurar Gemini: {e}")
    st.stop()

# --- Inicialización del Historial de Chat en Session State ---
# Session State es la forma en que Streamlit recuerda variables entre interacciones
if "chat" not in st.session_state:
    # Define el prompt inicial o instrucciones para el chatbot
    # Puedes personalizar esto extensamente para tu departamento
    initial_prompt = [
        {
            "role": "user",
            "parts": ["Eres 'AsisBot', un asistente virtual para el departamento X. Tu objetivo es ayudar con las tareas diarias, responder preguntas sobre procesos internos (basándote en la información que te proporcionen) y mantener un tono amigable y profesional. Si no sabes la respuesta a algo, indícalo claramente en lugar de inventar."]
        },
        {
            "role": "model",
            "parts": ["¡Hola! Soy AsisBot, tu asistente departamental. ¿En qué puedo ayudarte hoy?"]
        }
    ]
    # Inicia la sesión de chat con el historial inicial
    st.session_state.chat = model.start_chat(history=initial_prompt)
    print("Historial de chat inicializado.") # Para depuración en la consola

# --- Mostrar Mensajes Anteriores ---
# Itera sobre el historial guardado en session_state y muéstralo
for message in st.session_state.chat.history:
    # Asegúrate de que 'parts' no esté vacío y tenga texto
    if message.parts and message.parts[0].text:
        with st.chat_message(message.role):
            st.markdown(message.parts[0].text) # Usa markdown para mejor formato

# --- Input del Usuario ---
user_prompt = st.chat_input("Escribe tu mensaje aquí...")

if user_prompt:
    # Mostrar el mensaje del usuario inmediatamente
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Enviar el mensaje al modelo y obtener la respuesta
    try:
        response = st.session_state.chat.send_message(user_prompt, stream=True)

        # Mostrar la respuesta del modelo usando streaming
        with st.chat_message("model"): # 'assistant' o 'model' son roles comunes
            # response_container = st.empty() # Contenedor para ir mostrando la respuesta
            # full_response = ""
            # for chunk in response:
            #     full_response += chunk.text
            #     response_container.markdown(full_response + "▌") # Simula cursor
            # response_container.markdown(full_response) # Respuesta final sin cursor
            st.write_stream(response) # ¡Más fácil con write_stream!

    except Exception as e:
        st.error(f"Error al enviar/recibir mensaje: {e}")
        # Considera si quieres reiniciar el chat o manejar el error de otra forma
        # del st.session_state.chat # Podría reiniciar el chat
        # st.rerun()

# --- Sidebar para Opciones (Opcional) ---
st.sidebar.header("Opciones")
if st.sidebar.button("Limpiar Historial"):
    # Reinicia el historial manteniendo las instrucciones iniciales si las usaste
    initial_prompt = [
        {
            "role": "user",
            "parts": ["Eres 'AsisBot', un asistente virtual para el departamento X. Tu objetivo es ayudar con las tareas diarias, responder preguntas sobre procesos internos (basándote en la información que te proporcionen) y mantener un tono amigable y profesional. Si no sabes la respuesta a algo, indícalo claramente en lugar de inventar."]
        },
        {
            "role": "model",
            "parts": ["¡Hola! Soy AsisBot, tu asistente departamental. ¿En qué puedo ayudarte hoy?"]
        }
    ]
    st.session_state.chat = model.start_chat(history=initial_prompt)
    st.rerun() # Recarga la página para reflejar el cambio