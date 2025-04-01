import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
import io # Para manejar los bytes del archivo subido

# --- ⚙️ Configuración de la Página Streamlit ---
st.set_page_config(
    page_title="AsisBot Pro Departamental ✨",
    page_icon="🤖",
    layout="wide"
)

# --- ✨ Título y Encabezado ---
st.title("🤖 AsisBot Pro Departamental ✨")
st.caption("Tu asistente inteligente potenciado por Gemini. Ahora con carga de archivos 📄.")
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
    # Verifica que el modelo 'gemini-pro' esté disponible y sea correcto
    model = genai.GenerativeModel('gemini-pro')
    # Pequeña prueba de conexión (opcional, pero útil para diagnóstico)
    # model.generate_content("Test", generation_config=genai.types.GenerationConfig(max_output_tokens=5))
    st.sidebar.success("✅ Conectado a Gemini")
except Exception as e:
    st.error(f"❌ Error al configurar o conectar con Gemini: {e}")
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
            st.sidebar.success(f"Texto extraído de '{uploaded_file.name}' (TXT).")
        elif uploaded_file.type == "application/pdf":
            # Leer archivo PDF
            reader = pdf.PdfReader(uploaded_file)
            st.sidebar.write(f"El PDF tiene {len(reader.pages)} páginas.") # Info útil
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n" # Añade texto de cada página con salto de línea
                else:
                     st.sidebar.write(f"Advertencia: No se pudo extraer texto de la página {i+1}.")
            if text:
                 st.sidebar.success(f"Texto extraído de '{uploaded_file.name}' (PDF).")
            else:
                 st.sidebar.warning(f"No se pudo extraer texto útil del PDF '{uploaded_file.name}'.")
                 return None
        else:
            st.sidebar.warning(f"Tipo de archivo no soportado: {uploaded_file.type}")
            return None
    except Exception as e:
        st.sidebar.error(f"Error al procesar el archivo '{uploaded_file.name}': {e}")
        return None
    return text

# --- 💾 Inicialización del Historial y Estado en Session State ---
if "chat" not in st.session_state:
    # Instrucciones iniciales personalizadas
    initial_prompt_parts = [
         "Eres 'AsisBot Pro', un asistente virtual avanzado para el departamento X. Ayudas con tareas, respondes preguntas sobre procesos y analizas documentos proporcionados por el usuario. Mantén un tono amigable, profesional y estructurado. Si te proporcionan contexto de un archivo, basa tu respuesta PRINCIPALMENTE en él. Si no sabes algo o no está en el contexto, indícalo claramente."
    ]
    # La respuesta inicial del modelo
    initial_response_parts = [
        "¡Hola! Soy AsisBot Pro 🤖. Estoy listo para ayudarte. Puedes chatear conmigo o subir un archivo TXT o PDF en la barra lateral y hacerme preguntas sobre él."
    ]
    st.session_state.chat = model.start_chat(history=[
        {'role':'user', 'parts': initial_prompt_parts},
        {'role':'model', 'parts': initial_response_parts}
        ])
    st.session_state.uploaded_file_text = None
    st.session_state.uploaded_file_name = None
    print("Historial y estado inicializados.")

# --- 📤 Barra Lateral para Carga de Archivos y Opciones ---
st.sidebar.header("⚙️ Opciones")

uploaded_file = st.sidebar.file_uploader(
    "📁 Carga un archivo (TXT o PDF)",
    type=["txt", "pdf"],
    help="Sube un documento para que pueda responder preguntas sobre su contenido."
)

# Procesar archivo subido
if uploaded_file:
    if uploaded_file.name != st.session_state.get("uploaded_file_name"):
        st.session_state.uploaded_file_text = None # Limpia texto anterior al subir nuevo archivo
        st.session_state.uploaded_file_name = uploaded_file.name # Guarda nombre nuevo
        with st.sidebar:
            with st.spinner(f"⏳ Procesando '{uploaded_file.name}'..."):
                extracted_text = extract_text_from_upload(uploaded_file)
                if extracted_text:
                    st.session_state.uploaded_file_text = extracted_text
                    # st.success(f"✅ Archivo '{uploaded_file.name}' procesado.") # Ya se muestra en la función
                    st.caption("Ahora puedes hacer preguntas sobre este archivo.")
                # else: # El error/warning ya se muestra en la función
                #     st.error("No se pudo extraer texto del archivo.")

# Mostrar archivo cargado y botón para limpiar
if st.session_state.get("uploaded_file_text"):
    st.sidebar.info(f"Archivo cargado: **{st.session_state.uploaded_file_name}**")
    if st.sidebar.button("🧹 Limpiar Contexto del Archivo"):
        st.session_state.uploaded_file_text = None
        st.session_state.uploaded_file_name = None
        st.sidebar.success("Contexto del archivo limpiado.")
        st.rerun()

# Botón para limpiar historial de chat
if st.sidebar.button("🗑️ Limpiar Historial de Chat"):
    # Reinicia el historial
    initial_prompt_parts = [
        "Eres 'AsisBot Pro', un asistente virtual avanzado para el departamento X. Ayudas con tareas, respondes preguntas sobre procesos y analizas documentos proporcionados por el usuario. Mantén un tono amigable, profesional y estructurado. Si te proporcionan contexto de un archivo, basa tu respuesta PRINCIPALMENTE en él. Si no sabes algo o no está en el contexto, indícalo claramente."
    ]
    initial_response_parts = [
        "¡Hola! Soy AsisBot Pro 🤖. Historial limpiado. ¿Cómo puedo ayudarte ahora?"
    ]
    st.session_state.chat = model.start_chat(history=[
        {'role':'user', 'parts': initial_prompt_parts},
        {'role':'model', 'parts': initial_response_parts}
        ])
    st.rerun()

st.sidebar.divider()
st.sidebar.markdown("Hecho con ❤️ usando [Streamlit](https://streamlit.io) y [Google Gemini](https://ai.google.dev/)")

# --- 💬 Interfaz Principal de Chat ---

# Mostrar mensajes anteriores (excluyendo el prompt inicial del sistema si se desea)
for message in st.session_state.chat.history:
     # Simple heurística para no mostrar el primer prompt de sistema largo
     is_system_prompt = "Eres 'AsisBot Pro'" in (message.parts[0].text if message.parts else "")
     if message.parts and message.parts[0].text and not is_system_prompt:
          # Asegúrate de que el rol sea válido para st.chat_message ('user' o 'assistant'/'model')
          role = message.role if message.role in ["user", "model"] else "assistant"
          with st.chat_message(role):
             st.markdown(message.parts[0].text)

# Input del usuario
user_prompt = st.chat_input("❓ Escribe tu pregunta o pide ayuda sobre el archivo cargado...")

if user_prompt:
    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Preparar el prompt para Gemini, añadiendo contexto si existe
    context_to_send = user_prompt # Por defecto, solo la pregunta
    if st.session_state.get("uploaded_file_text"):
        # Prepara el contexto del archivo (limitado para evitar errores de tamaño)
        # Puedes ajustar el límite de caracteres según necesites
        file_context = st.session_state.uploaded_file_text[:10000]
        if len(st.session_state.uploaded_file_text) > 10000:
             st.warning("⚠️ El contexto del archivo es muy largo, se usarán solo los primeros 10000 caracteres.", icon="⚠️")

        context_to_send = f"""
        **Contexto del Documento: '{st.session_state.uploaded_file_name}'**
        ---
        {file_context}
        ---
        **Fin del Contexto**

        **Instrucción:** Usando el contexto anterior como fuente principal, responde a la siguiente pregunta del usuario de forma clara y concisa. Si la respuesta no está en el contexto, indícalo. No inventes información que no esté presente.

        **Pregunta del Usuario:** {user_prompt}
        """
        print(f"DEBUG: Enviando pregunta con contexto del archivo: {st.session_state.uploaded_file_name}")
    else:
        print("DEBUG: Enviando pregunta sin contexto de archivo.")

    # Enviar al modelo y mostrar respuesta CORRECTAMENTE
    try:
        # ASEGÚRATE DE USAR stream=True
        response = st.session_state.chat.send_message(context_to_send, stream=True)

        with st.chat_message("model"): # Usar 'model' o 'assistant' como rol
            # USA st.write_stream para manejar la respuesta correctamente
            st.write_stream(response)

    except Exception as e:
        st.error(f"❌ Ocurrió un error al contactar a Gemini: {e}")
        # Podrías añadir lógica para reintentar o informar al usuario
