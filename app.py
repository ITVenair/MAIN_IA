import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import io

# --- ⚙️ Configuración de la Página Streamlit ---
st.set_page_config(
    page_title="AsisBot Pro Departamental ✨",
    page_icon="🤖",
    layout="wide"
)

# --- ✨ Título y Encabezado ---
st.title("🤖 AsisBot Pro Departamental ✨")
st.caption("Tu asistente inteligente potenciado por Gemini. Carga archivos TXT/PDF para análisis.")
st.divider()

# --- 🔑 Gestión de la API Key ---
google_api_key = st.secrets.get("GOOGLE_API_KEY")
if not google_api_key:
    google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.warning("🔑 API Key no encontrada. Por favor, ingrésala en la barra lateral.")
    google_api_key = st.sidebar.text_input("Ingresa tu Google API Key:", type="password")
if not google_api_key:
    st.info("Ingresa tu Google API Key en la barra lateral para comenzar.")
    st.stop()

# --- 🧠 Configuración del Modelo Gemini ---
try:
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-pro')
    st.sidebar.success("✅ Conectado a Gemini")
except Exception as e:
    st.error(f"❌ Error al configurar o conectar con Gemini: {e}")
    st.sidebar.error("Error conectando a Gemini.")
    st.stop()

# --- 📄 Funciones Auxiliares ---
def extract_text_from_upload(uploaded_file):
    """Extrae texto de archivos TXT o PDF subidos."""
    text = ""
    try:
        if uploaded_file.type == "text/plain":
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            text = stringio.read()
        elif uploaded_file.type == "application/pdf":
            reader = pdf.PdfReader(uploaded_file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if not text:
                 st.sidebar.warning(f"No se pudo extraer texto útil del PDF '{uploaded_file.name}'.")
                 return None
        else:
            st.sidebar.warning(f"Tipo de archivo no soportado: {uploaded_file.type}")
            return None
    except Exception as e:
        st.sidebar.error(f"Error al procesar '{uploaded_file.name}': {e}")
        return None
    return text

def chunk_text(text, chunk_size=8000): # Tamaño del trozo (ajustable)
    """Divide el texto en trozos de tamaño aproximado."""
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    print(f"DEBUG: Texto dividido en {len(chunks)} trozos.")
    return chunks

# --- 💾 Inicialización del Historial y Estado en Session State ---
if "chat" not in st.session_state:
    # Define instrucciones iniciales (puedes personalizarlas)
    st.session_state.chat_history = [
        {'role':'user', 'parts': ["Eres 'AsisBot Pro', un asistente virtual avanzado para el departamento X. Ayudas con tareas, respondes preguntas sobre procesos y analizas documentos proporcionados por el usuario. Mantén un tono amigable, profesional y estructurado. Si te proporcionan contexto de un archivo, basa tu respuesta PRINCIPALMENTE en él. Si no sabes algo o no está en el contexto, indícalo claramente."]},
        {'role':'model', 'parts': ["¡Hola! Soy AsisBot Pro 🤖. Puedes chatear conmigo o subir un archivo (TXT/PDF) en la barra lateral para hacer preguntas sobre él."]}
    ]
    st.session_state.gemini_chat = model.start_chat(history=st.session_state.chat_history) # Objeto de chat de Gemini
    st.session_state.file_chunks = None
    st.session_state.uploaded_file_name = None
    print("Historial y estado inicializados.")

# --- 📤 Barra Lateral ---
st.sidebar.header("⚙️ Opciones")
uploaded_file = st.sidebar.file_uploader(
    "📁 Cargar Archivo (TXT/PDF)",
    type=["txt", "pdf"],
    help="Sube un documento para analizar su contenido."
)

if uploaded_file:
    # Procesa solo si es un archivo nuevo
    if uploaded_file.name != st.session_state.get("uploaded_file_name"):
        st.session_state.file_chunks = None # Limpia trozos anteriores
        st.session_state.uploaded_file_name = uploaded_file.name
        with st.sidebar:
            with st.spinner(f"⏳ Procesando '{uploaded_file.name}'..."):
                extracted_text = extract_text_from_upload(uploaded_file)
                if extracted_text:
                    st.session_state.file_chunks = chunk_text(extracted_text) # Guarda los trozos
                    st.success(f"✅ '{uploaded_file.name}' procesado ({len(st.session_state.file_chunks)} partes).")
                    st.caption("ℹ️ Se usará el inicio del documento como contexto.")
                else:
                    st.session_state.uploaded_file_name = None # Resetea nombre si falla

# Mostrar archivo cargado y opción de limpiar
if st.session_state.get("file_chunks"):
    st.sidebar.info(f"Archivo cargado: **{st.session_state.uploaded_file_name}** ({len(st.session_state.file_chunks)} partes)")
    if st.sidebar.button("🧹 Limpiar Contexto del Archivo"):
        st.session_state.file_chunks = None
        st.session_state.uploaded_file_name = None
        st.sidebar.success("Contexto del archivo limpiado.")
        st.rerun()

# Limpiar historial de chat
if st.sidebar.button("🗑️ Limpiar Historial de Chat"):
    st.session_state.chat_history = [ # Reinicia solo el historial, no el objeto chat de gemini
        {'role':'user', 'parts': ["Eres 'AsisBot Pro'... (mismas instrucciones)"]}, # Re-añade instrucciones si quieres
        {'role':'model', 'parts': ["Historial limpiado. ¿Empezamos de nuevo?"]}
    ]
    # Reinicia el objeto de chat de Gemini también para limpiar su memoria interna
    st.session_state.gemini_chat = model.start_chat(history=st.session_state.chat_history)
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("Hecho con ❤️ usando [Streamlit](https://streamlit.io) & [Google Gemini](https://ai.google.dev/)")

# --- 💬 Interfaz Principal de Chat ---

# Mostrar historial guardado en st.session_state.chat_history
for message in st.session_state.chat_history:
     # Evitar mostrar el prompt inicial del sistema si es muy largo
     is_system_prompt = "Eres 'AsisBot Pro'" in (message['parts'][0] if message['parts'] else "")
     role = message['role'] if message['role'] in ["user", "model"] else "assistant" # Ajusta rol si es necesario
     if message['parts'] and message['parts'][0] and not is_system_prompt :
          with st.chat_message(role):
             st.markdown(message['parts'][0]) # Muestra el texto guardado

# Input del usuario
user_prompt = st.chat_input("❓ Pregúntame algo o sobre el archivo cargado...")

if user_prompt:
    # Añadir mensaje del usuario al historial local y mostrarlo
    st.session_state.chat_history.append({"role": "user", "parts": [user_prompt]})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Preparar el prompt para Gemini
    prompt_final = user_prompt
    context_notice = "" # Para añadir una nota visual si se usa contexto

    if st.session_state.get("file_chunks"):
        # Usar el primer trozo como contexto
        context_excerpt = st.session_state.file_chunks[0]
        prompt_final = f"""**Contexto (Extracto Inicial del archivo '{st.session_state.uploaded_file_name}'):**
---
{context_excerpt}
---
**Fin del Extracto**

**Instrucción:** Responde a la siguiente pregunta basándote **únicamente** en el extracto del documento proporcionado. Si la información no está en el extracto, indícalo claramente.

**Pregunta:** {user_prompt}
"""
        context_notice = f"*(Analizando inicio de '{st.session_state.uploaded_file_name}')*"
        print(f"DEBUG: Enviando pregunta con contexto del archivo (chunk 1): {st.session_state.uploaded_file_name}")
    else:
        print("DEBUG: Enviando pregunta sin contexto de archivo.")

    # --- CRITICAL PART: Envío a Gemini y Visualización ---
    try:
        # Envía usando el objeto de chat de Gemini (que maneja el historial interno)
        # ¡ASEGÚRATE DE USAR stream=True!
        response = st.session_state.gemini_chat.send_message(prompt_final, stream=True)

        # Muestra la respuesta usando st.write_stream
        with st.chat_message("model"): # Rol del asistente
            # ¡ESTA ES LA FORMA CORRECTA DE MOSTRAR LA RESPUESTA EN STREAMING!
            full_response_text = st.write_stream(response)

            # Añadir la respuesta del modelo al historial local *después* de mostrarla
            st.session_state.chat_history.append({"role": "model", "parts": [full_response_text]})

            # Añadir nota de contexto si se usó un archivo
            if context_notice:
                 st.caption(context_notice)

    except Exception as e:
        st.error(f"❌ Error al contactar a Gemini: {e}")
        # Eliminar el último mensaje del usuario del historial si la llamada falló
        if st.session_state.chat_history[-1]['role'] == 'user':
             st.session_state.chat_history.pop()
