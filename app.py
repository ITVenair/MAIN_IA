import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import io # Para manejar los bytes del archivo subido

# --- ⚙️ Configuración de la Página Streamlit ---
st.set_page_config(
    page_title="AsisBot Pro MAIN ✨",
    page_icon="🤖",
    layout="wide" # Usa el ancho completo de la página
)

# --- ✨ Título y Encabezado ---
st.title("🤖 AsisBot Pro MAIN ✨")
st.caption("Tu asistente inteligente potenciado por Gemini.")
st.divider() # Línea divisoria para separar

# --- 🔑 Gestión de la API Key (igual que antes) ---
# Método 1: Streamlit Secrets (Recomendado para despliegue)
google_api_key = st.secrets.get("GOOGLE_API_KEY")
# Método 2: Variable de entorno (Pruebas locales)
if not google_api_key:
    google_api_key = os.getenv("GOOGLE_API_KEY")
# Método 3: Input manual (Pruebas locales rápidas)
if not google_api_key:
    st.warning("🔑 API Key no encontrada. Por favor, ingrésala en la barra lateral.")
    google_api_key = st.sidebar.text_input("Ingresa tu Google API Key:", type="password")

if not google_api_key:
    st.info("Ingresa tu Google API Key en la barra lateral para comenzar.")
    st.stop()

# --- 🧠 Configuración del Modelo Gemini ---
try:
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
    st.sidebar.success("✅ Conectado a Gemini")
except Exception as e:
    st.error(f"❌ Error al configurar Gemini: {e}")
    st.stop()

# --- 📄 Función para Extraer Texto de Archivos ---
def extract_text_from_upload(uploaded_file):
    """Extrae texto de archivos TXT o PDF subidos."""
    text = ""
    try:
        if uploaded_file.type == "text/plain":
            # Leer archivo de texto
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            text = stringio.read()
        elif uploaded_file.type == "application/pdf":
            # Leer archivo PDF
            reader = pdf.PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() or "" # Añadir texto de cada página
        else:
            st.sidebar.warning(f"Tipo de archivo no soportado: {uploaded_file.type}")
            return None # Retorna None si el tipo no es soportado
    except Exception as e:
        st.sidebar.error(f"Error al procesar el archivo {uploaded_file.name}: {e}")
        return None # Retorna None en caso de error
    return text

# --- 💾 Inicialización del Historial y Estado en Session State ---
if "chat" not in st.session_state:
    # Instrucciones iniciales personalizadas
    initial_prompt = [
         {
            "role": "user",
            "parts": ["Eres 'AsisBot Pro', un asistente virtual avanzado para el departamento X. Ayudas con tareas, respondes preguntas sobre procesos y analizas documentos proporcionados por el usuario. Mantén un tono amigable, profesional y estructurado. Si te proporcionan contexto de un archivo, basa tu respuesta PRINCIPALMENTE en él. Si no sabes algo o no está en el contexto, indícalo claramente."]
        },
        {
            "role": "model",
            "parts": ["¡Hola! Soy AsisBot Pro 🤖. Estoy listo para ayudarte. Puedes chatear conmigo o subir un archivo TXT o PDF en la barra lateral y hacerme preguntas sobre él."]
        }
    ]
    st.session_state.chat = model.start_chat(history=initial_prompt)
    st.session_state.uploaded_file_text = None # Para guardar el texto del archivo
    st.session_state.uploaded_file_name = None # Para guardar el nombre del archivo
    print("Historial y estado inicializados.") # Debug

# --- 📤 Barra Lateral para Carga de Archivos y Opciones ---
st.sidebar.header("⚙️ Opciones")

uploaded_file = st.sidebar.file_uploader(
    "📁 Carga un archivo (TXT o PDF)",
    type=["txt", "pdf"],
    help="Sube un documento para que pueda responder preguntas sobre su contenido."
)

if uploaded_file:
    # Procesa el archivo SOLO si es diferente al anterior o si no hay texto guardado
    if uploaded_file.name != st.session_state.get("uploaded_file_name") or not st.session_state.get("uploaded_file_text"):
        with st.sidebar:
            with st.spinner(f"⏳ Procesando '{uploaded_file.name}'..."):
                extracted_text = extract_text_from_upload(uploaded_file)
                if extracted_text is not None:
                    st.session_state.uploaded_file_text = extracted_text
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.success(f"✅ Archivo '{uploaded_file.name}' procesado.")
                    st.caption("Ahora puedes hacer preguntas sobre este archivo en el chat.")
                else:
                    # Si la extracción falla, limpia el estado
                    st.session_state.uploaded_file_text = None
                    st.session_state.uploaded_file_name = None
                    st.error("No se pudo extraer texto del archivo.")

# Botón para limpiar el contexto del archivo
if st.session_state.get("uploaded_file_text"):
    st.sidebar.info(f"Archivo cargado: **{st.session_state.uploaded_file_name}**")
    if st.sidebar.button("🧹 Limpiar Contexto del Archivo"):
        st.session_state.uploaded_file_text = None
        st.session_state.uploaded_file_name = None
        st.sidebar.success("Contexto del archivo limpiado.")
        st.rerun() # Recarga para reflejar el cambio

# Botón para limpiar historial de chat
if st.sidebar.button("🗑️ Limpiar Historial de Chat"):
    initial_prompt = [ # Re-define por si acaso
         {
            "role": "user",
            "parts": ["Eres 'AsisBot Pro', un asistente virtual avanzado para MAIN. Ayudas con tareas, respondes preguntas sobre procesos y analizas documentos proporcionados por el usuario. Mantén un tono amigable, profesional y estructurado. Si te proporcionan contexto de un archivo, basa tu respuesta PRINCIPALMENTE en él. Si no sabes algo o no está en el contexto, indícalo claramente."]
        },
        {
            "role": "model",
            "parts": ["¡Hola! Soy AsisBot Pro 🤖. ¿Cómo puedo ayudarte ahora?"]
        }
    ]
    st.session_state.chat = model.start_chat(history=initial_prompt)
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("Hecho con ❤️ usando [Streamlit](https://streamlit.io) y [Google Gemini](https://ai.google.dev/)")

# --- 💬 Interfaz Principal de Chat ---

# Mostrar mensajes anteriores
for message in st.session_state.chat.history:
    # Evita mostrar el prompt inicial del sistema si es muy largo o técnico
    # O puedes personalizar qué mostrar aquí
    is_system_prompt = "Eres 'AsisBot Pro'" in message.parts[0].text if message.parts else False
    if message.parts and message.parts[0].text and not is_system_prompt:
         with st.chat_message(message.role):
            st.markdown(message.parts[0].text)

# Input del usuario
user_prompt = st.chat_input("❓ Escribe tu pregunta o pide ayuda sobre el archivo cargado...")

if user_prompt:
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Preparar el prompt para Gemini
    context_to_send = ""
    if st.session_state.get("uploaded_file_text"):
        context_to_send = f"""
        --- INICIO DEL CONTEXTO DEL DOCUMENTO ({st.session_state.uploaded_file_name}) ---
        {st.session_state.uploaded_file_text[:8000]}
        --- FIN DEL CONTEXTO DEL DOCUMENTO ---

        Basándote **principalmente** en el contexto del documento proporcionado arriba, responde a la siguiente pregunta. Si la respuesta no está en el contexto, indícalo.
        Pregunta: {user_prompt}
        """
        # Limitamos el contexto a 8000 caracteres para evitar exceder límites fácilmente
        # En una app real, se usarían técnicas más avanzadas (chunking, embeddings)
        print(f"DEBUG: Enviando pregunta con contexto del archivo: {st.session_state.uploaded_file_name}") # Debug
    else:
        context_to_send = user_prompt # Sin contexto de archivo
        print("DEBUG: Enviando pregunta sin contexto de archivo.") # Debug

    # Enviar al modelo y mostrar respuesta
    try:
        response = st.session_state.chat.send_message(context_to_send, stream=True)
        with st.chat_message("model"): # Rol del asistente
            st.write_stream(response)
    except Exception as e:
        st.error(f"❌ Ocurrió un error al contactar a Gemini: {e}")
