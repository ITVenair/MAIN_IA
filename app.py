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
# Intenta obtener la clave desde los secretos de Streamlit (Ideal para despliegue)
google_api_key = st.secrets.get("GOOGLE_API_KEY")

# Si no, intenta desde variable de entorno (Pruebas locales)
if not google_api_key:
    google_api_key = os.getenv("GOOGLE_API_KEY")

# Si aún no hay clave, pide al usuario que la introduzca (Pruebas locales rápidas)
if not google_api_key:
    st.warning("🔑 API Key no encontrada. Por favor, ingrésala en la barra lateral.")
    google_api_key = st.sidebar.text_input("Ingresa tu Google API Key:", type="password")

# Detiene si no hay clave
if not google_api_key:
    st.info("Ingresa tu Google API Key en la barra lateral para comenzar.")
    st.stop()

# --- 🧠 Configuración del Modelo Gemini ---
try:
    genai.configure(api_key=google_api_key)
    model = genai.GenerativeModel('gemini-pro')
    # Pequeña verificación para asegurar que la configuración fue correcta
    # model.generate_content("Test rápido", generation_config=genai.types.GenerationConfig(max_output_tokens=5))
    st.sidebar.success("✅ Conectado a Gemini")
except Exception as e:
    st.error(f"❌ Error al configurar o conectar con Gemini: {e}")
    st.sidebar.error("Error conectando a Gemini.")
    st.stop()

# --- 📄 Funciones Auxiliares ---
def extract_text_from_upload(uploaded_file):
    """Extrae texto de archivos TXT o PDF subidos."""
    text = ""
    file_type = uploaded_file.type
    file_name = uploaded_file.name
    try:
        if file_type == "text/plain":
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            text = stringio.read()
            st.sidebar.info(f"Texto extraído de '{file_name}' (TXT).")
        elif file_type == "application/pdf":
            reader = pdf.PdfReader(uploaded_file)
            num_pages = len(reader.pages)
            # st.sidebar.write(f"Leyendo PDF '{file_name}' ({num_pages} páginas)...")
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text:
                 st.sidebar.info(f"Texto extraído de '{file_name}' (PDF - {num_pages} pág.).")
            else:
                 st.sidebar.warning(f"No se pudo extraer texto útil del PDF '{file_name}'.")
                 return None
        else:
            st.sidebar.warning(f"Tipo de archivo no soportado: {file_type}")
            return None
    except Exception as e:
        st.sidebar.error(f"Error al procesar '{file_name}': {e}")
        return None
    return text

def chunk_text(text, chunk_size=8000): # Tamaño del trozo (ajustable)
    """Divide el texto en trozos de tamaño aproximado."""
    if not text: return [] # Devuelve lista vacía si no hay texto
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    print(f"DEBUG: Texto dividido en {len(chunks)} trozos.")
    return chunks

# --- 💾 Inicialización del Historial y Estado en Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {'role':'user', 'parts': ["Eres 'AsisBot Pro'... (mismas instrucciones)"]}, # Prompt inicial (puede ocultarse si se prefiere)
        {'role':'model', 'parts': ["¡Hola! Soy AsisBot Pro 🤖. Puedes chatear o subir un archivo (TXT/PDF) para analizarlo."]}
    ]
    # El historial para la API se maneja internamente por el objeto 'chat'
    st.session_state.gemini_chat = model.start_chat(history=st.session_state.chat_history)
    st.session_state.file_chunks = None
    st.session_state.uploaded_file_name = None
    print("Historial y estado inicializados.")

# --- 📤 Barra Lateral ---
st.sidebar.header("⚙️ Opciones")
uploaded_file = st.sidebar.file_uploader(
    "📁 Cargar Archivo (TXT/PDF)",
    type=["txt", "pdf"],
    key="file_uploader", # Añadir una key puede ayudar a Streamlit
    help="Sube un documento para analizar su contenido."
)

# Procesar archivo subido
if uploaded_file:
    # Compara el objeto archivo directamente, si cambia, reprocesa
    if uploaded_file != st.session_state.get("processed_file_object"):
        st.session_state.file_chunks = None # Limpia trozos anteriores
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.processed_file_object = uploaded_file # Guarda el objeto actual

        with st.sidebar:
            with st.spinner(f"⏳ Procesando '{uploaded_file.name}'..."):
                extracted_text = extract_text_from_upload(uploaded_file)
                if extracted_text:
                    st.session_state.file_chunks = chunk_text(extracted_text)
                    st.success(f"✅ '{uploaded_file.name}' procesado ({len(st.session_state.file_chunks)} partes).")
                    st.caption("ℹ️ Se usará el inicio del documento como contexto.")
                else:
                    # Resetea si la extracción falla
                    st.session_state.file_chunks = None
                    st.session_state.uploaded_file_name = None
                    st.session_state.processed_file_object = None

# Mostrar archivo cargado y opción de limpiar
if st.session_state.get("file_chunks"):
    st.sidebar.info(f"Archivo cargado: **{st.session_state.uploaded_file_name}** ({len(st.session_state.file_chunks)} partes)")
    if st.sidebar.button("🧹 Limpiar Contexto del Archivo", key="clear_context_button"):
        st.session_state.file_chunks = None
        st.session_state.uploaded_file_name = None
        st.session_state.processed_file_object = None
        st.sidebar.success("Contexto del archivo limpiado.")
        st.rerun()

# Limpiar historial de chat
if st.sidebar.button("🗑️ Limpiar Historial de Chat", key="clear_history_button"):
    # Reinicia historial local y objeto chat de Gemini
    st.session_state.chat_history = [
        {'role':'user', 'parts': ["Eres 'AsisBot Pro'... (mismas instrucciones)"]},
        {'role':'model', 'parts': ["Historial limpiado. ¿Empezamos de nuevo?"]}
    ]
    st.session_state.gemini_chat = model.start_chat(history=st.session_state.chat_history)
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("Hecho con ❤️ usando [Streamlit](https://streamlit.io) & [Google Gemini](https://ai.google.dev/)")

# --- 💬 Interfaz Principal de Chat ---

# Mostrar historial guardado en st.session_state.chat_history
for i, message in enumerate(st.session_state.chat_history):
     # Ocultar los dos primeros mensajes (instrucciones user/model)
     if i >= 2 and message['parts'] and message['parts'][0]:
        role = message['role'] if message['role'] in ["user", "model"] else "assistant"
        with st.chat_message(role):
             st.markdown(message['parts'][0])

# Input del usuario
user_prompt = st.chat_input("❓ Pregúntame algo o sobre el archivo cargado...")

if user_prompt:
    # Añadir mensaje del usuario al historial local y mostrarlo
    st.session_state.chat_history.append({"role": "user", "parts": [user_prompt]})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Preparar el prompt final para enviar a Gemini
    prompt_final = user_prompt
    context_notice = "" # Nota para mostrar al usuario

    if st.session_state.get("file_chunks"):
        # Usa el primer trozo como contexto
        context_excerpt = st.session_state.file_chunks[0]
        prompt_final = f"""**Contexto (Extracto Inicial del archivo '{st.session_state.uploaded_file_name}'):**
---
{context_excerpt}
---
**Fin del Extracto**

**Instrucción:** Responde a la siguiente pregunta basándote **únicamente** en el extracto del documento proporcionado. Si la información no está en el extracto, indícalo claramente. No inventes información que no esté presente.

**Pregunta:** {user_prompt}
"""
        context_notice = f"*(Analizando inicio de '{st.session_state.uploaded_file_name}')*"
        print(f"DEBUG: Enviando pregunta CON contexto del archivo (chunk 1).")
    else:
        print(f"DEBUG: Enviando pregunta SIN contexto de archivo.")

    # --- PUNTO CRÍTICO: Envío a Gemini y Visualización ---
    try:
        # Envía usando el objeto de chat de Gemini, CON stream=True
        response = st.session_state.gemini_chat.send_message(prompt_final, stream=True)

        # Muestra la respuesta USANDO st.write_stream
        with st.chat_message("model"):
            # ESTA ES LA LÍNEA CLAVE PARA MOSTRAR BIEN LA RESPUESTA
            full_response_text = st.write_stream(response)

            # Solo añade la respuesta al historial local después de mostrarla
            st.session_state.chat_history.append({"role": "model", "parts": [full_response_text]})

            # Añade la nota de contexto si aplica
            if context_notice:
                st.caption(context_notice)

    except Exception as e:
        st.error(f"❌ Error al contactar a Gemini: {e}")
        # Opcional: Eliminar el último mensaje del usuario del historial si la llamada falló
        if st.session_state.chat_history and st.session_state.chat_history[-1]['role'] == 'user':
             st.session_state.chat_history.pop()

    # Forzar la recarga de la interfaz para asegurar que el historial se muestre actualizado
    # Puede que no sea necesario siempre, pero puede ayudar en algunos casos
    # st.rerun() # Descomentar si la interfaz no se actualiza bien tras la respuesta
