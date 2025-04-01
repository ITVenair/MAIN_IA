# Chatbot Departamental Gemini con Streamlit

Este es un chatbot simple construido con Streamlit y potenciado por la API de Google Gemini Pro.

## Descripción

Un asistente virtual diseñado para ayudar al departamento X con tareas diarias y preguntas frecuentes.

## Configuración Local

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_REPOSITORIO>
    ```
2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # Windows: .\venv\Scripts\activate
    # macOS/Linux: source venv/bin/activate
    ```
3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configurar la API Key:** Establece tu clave API de Google como una variable de entorno:
    ```bash
    # Windows (cmd): set GOOGLE_API_KEY=TU_CLAVE_API
    # Windows (PowerShell): $env:GOOGLE_API_KEY="TU_CLAVE_API"
    # macOS/Linux: export GOOGLE_API_KEY='TU_CLAVE_API'
    ```
    *(Alternativamente, la aplicación te pedirá la clave en la barra lateral si no la encuentra).*
5.  **Ejecutar la aplicación:**
    ```bash
    streamlit run app.py
    ```

## Despliegue en Streamlit Community Cloud

1.  Asegúrate de que tu código esté en un repositorio público o privado de GitHub.
2.  Ve a [share.streamlit.io](https://share.streamlit.io/).
3.  Haz clic en "New app" y conecta tu repositorio de GitHub.
4.  Selecciona el repositorio, la rama y el archivo principal (`app.py`).
5.  En las configuraciones avanzadas ("Advanced settings..."), ve a la sección "Secrets".
6.  Añade tu clave API de Google con el nombre `GOOGLE_API_KEY`:
    ```toml
    GOOGLE_API_KEY="TU_CLAVE_API_REAL_AQUI"
    ```
7.  Haz clic en "Deploy!".

**IMPORTANTE:** Nunca subas tu clave API directamente al código en GitHub. Usa Streamlit Secrets para el despliegue.