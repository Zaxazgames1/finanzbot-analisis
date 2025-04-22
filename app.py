import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import random
import re
import numpy as np
from utils.nlp_utils import tokenizar_texto, lematizar_texto, pos_tagging, crear_embedding, similaridad_textos, extraer_keywords
from utils.analysis import analizar_empresa, generar_mensaje_resultado

# Configuración de la página
st.set_page_config(
    page_title="FinanzGPT - Asistente Financiero",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuraciones CSS personalizadas con estilo similar a ChatGPT
st.markdown("""
<style>
    /* Estilos generales */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #353740;
        background-color: #F7F7F8;
    }
    
    /* Títulos y encabezados */
    .main-title {
        font-size: 2.2rem;
        font-weight: 600;
        color: #10A37F;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .sub-title {
        font-size: 1.4rem;
        font-weight: 500;
        color: #444654;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Mensajes de chat */
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        padding: 10px;
        max-width: 900px;
        margin: 0 auto;
    }
    
    .chat-message-user {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 15px;
        margin: 5px 0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        color: #353740;
        font-size: 16px;
        position: relative;
        display: flex;
        align-items: flex-start;
    }
    
    .chat-message-bot {
        background-color: #F7F7F8;
        border-radius: 8px;
        padding: 15px;
        margin: 5px 0;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        color: #353740;
        font-size: 16px;
        position: relative;
        display: flex;
        align-items: flex-start;
    }
    
    .avatar {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-right: 15px;
        flex-shrink: 0;
    }
    
    .avatar-user {
        background-color: #10A37F;
        color: white;
        font-weight: bold;
    }
    
    .avatar-bot {
        background-color: #0FA47F;
        color: white;
        font-weight: bold;
    }
    
    .message-content {
        flex-grow: 1;
        line-height: 1.5;
    }
    
    /* Tarjetas y componentes */
    .card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        color: #353740;
    }
    
    .highlight-metric {
        background-color: #F8FAFC;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        font-weight: 500;
        color: #353740;
        border-left: 4px solid #10A37F;
        transition: all 0.3s ease;
    }
    
    .highlight-metric:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Estados financieros */
    .estado-excelente {
        background-color: #10A37F;
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(16, 163, 127, 0.3);
    }
    
    .estado-bueno {
        background-color: #3B82F6;
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    }
    
    .estado-regular {
        background-color: #F59E0B;
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
    }
    
    .estado-critico {
        background-color: #EF4444;
        color: white;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
    }
    
    /* Recomendaciones */
    .recomendacion {
        background-color: #FFFBEB;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #F59E0B;
        color: #353740;
        font-weight: 400;
        transition: transform 0.2s ease;
    }
    
    .recomendacion:hover {
        transform: translateX(5px);
    }
    
    /* Formulario */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        padding: 12px;
        font-size: 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10A37F;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
    }
    
    .stButton > button {
        background-color: #10A37F;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #0C8D6C;
        box-shadow: 0 4px 12px rgba(16, 163, 127, 0.3);
    }
    
    /* Chat input */
    .stChatInput > div > textarea {
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        padding: 12px;
        font-size: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .stChatInput > div > textarea:focus {
        border-color: #10A37F;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #FFFFFF;
    }
    
    /* Esconder elementos de streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Botones de navegación */
    .nav-button {
        background-color: #F8FAFC;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        display: block;
        width: 100%;
        margin-bottom: 8px;
        font-weight: 500;
        color: #444654;
    }
    
    .nav-button:hover {
        background-color: #F0F9F6;
        border-color: #10A37F;
        color: #10A37F;
    }
    
    .nav-button-active {
        background-color: #10A37F;
        color: white;
        border: 1px solid #10A37F;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        display: block;
        width: 100%;
        margin-bottom: 8px;
        font-weight: 500;
    }
    
    /* Animación de pensamiento */
    .thinking-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }
    
    .thinking-dot {
        width: 10px;
        height: 10px;
        margin: 0 5px;
        background-color: #10A37F;
        border-radius: 50%;
        animation: pulse 1.5s infinite ease-in-out;
    }
    
    .thinking-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .thinking-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        50% {
            transform: scale(1.2);
            opacity: 1;
        }
    }
    
    /* Tooltips y elementos informativos */
    .info-tooltip {
        display: inline-block;
        width: 18px;
        height: 18px;
        background-color: #E5E7EB;
        color: #6B7280;
        border-radius: 50%;
        text-align: center;
        line-height: 18px;
        margin-left: 5px;
        font-size: 12px;
        cursor: help;
    }
    
    /* Gráficos */
    .chart-container {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Menú de ayuda */
    .help-menu {
        background-color: #F0F9F6;
        border: 1px solid #10A37F;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .help-item {
        padding: 8px 12px;
        margin: 5px 0;
        background-color: #E6F7F1;
        border-radius: 5px;
        transition: all 0.2s ease;
    }
    
    .help-item:hover {
        background-color: #D1F0E6;
        transform: translateX(5px);
    }
</style>
""", unsafe_allow_html=True)

# Función para formatear números grandes
def formato_numero(numero):
    """
    Formatea un número grande para mejor legibilidad.
    Ejemplo: 1234567 -> 1,234,567
    
    Args:
        numero (float): Número a formatear
    
    Returns:
        str: Número formateado
    """
    return f"{numero:,.0f}"

# Función para mostrar animación de "pensando"
def mostrar_procesamiento():
    """Muestra una animación de procesamiento estilo ChatGPT"""
    with st.spinner(''):
        st.markdown("""
        <div class="thinking-animation">
            <div class="thinking-dot"></div>
            <div class="thinking-dot"></div>
            <div class="thinking-dot"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulación de procesamiento
        time.sleep(2)
        
        # Mostrar mensaje de éxito al completar
        st.success('Análisis completado')
        time.sleep(0.5)

# Función para validar entradas numéricas
def validar_numeros(valor, min_valor=0.0, nombre="valor"):
    """
    Valida que un valor numérico esté dentro de un rango aceptable.
    
    Args:
        valor (float): Valor a validar
        min_valor (float): Valor mínimo aceptable
        nombre (str): Nombre del campo para mensajes de error
        
    Returns:
        tuple: (bool, str) - (es_valido, mensaje_error)
    """
    if valor is None:
        return False, f"Por favor, ingresa un {nombre}."
    
    try:
        num_valor = float(valor)
        if num_valor < min_valor:
            return False, f"El {nombre} debe ser mayor o igual a {min_valor}."
        return True, ""
    except ValueError:
        return False, f"El {nombre} debe ser un número válido."

# Función para detectar si un mensaje está fuera del ámbito financiero
def es_mensaje_no_financiero(mensaje):
    """
    Detecta si un mensaje está fuera del ámbito financiero.
    
    Args:
        mensaje (str): Mensaje del usuario
        
    Returns:
        bool: True si el mensaje no es financiero, False si es financiero
    """
    # Palabras clave de saludos comunes
    saludos = ['hola', 'buenos días', 'buenas tardes', 'buenas noches', 'saludos', 'qué tal', 'como estas', 'cómo estás', 'como vas', 'qué hay']
    
    # Palabras clave de despedidas
    despedidas = ['adiós', 'chao', 'hasta luego', 'nos vemos', 'bye', 'hasta pronto', 'hasta mañana']
    
    # Palabras clave sobre estados emocionales
    emociones = ['triste', 'feliz', 'deprimido', 'ansioso', 'estresado', 'cansado', 'aburrido', 'mal', 'bien', 'enfermo']
    
    # Palabras clave sobre temas personales
    temas_personales = ['salud', 'vida', 'familia', 'amigo', 'amor', 'relación', 'matrimonio', 'hijo', 'niño', 'mascota']
    
    # Peticiones de ayuda generales
    ayuda_general = ['ayuda', 'ayúdame', 'socorro', 'sos', 'help']
    
    # Verificar si el mensaje coincide con alguna categoría
    mensaje_lower = mensaje.lower()
    
    # Detectar saludos simples
    if any(saludo == mensaje_lower for saludo in saludos):
        return True, "saludo"
    
    # Detectar despedidas simples
    if any(despedida == mensaje_lower for despedida in despedidas):
        return True, "despedida"
        
    # Detectar si es una petición de ayuda general
    if any(ayuda == mensaje_lower for ayuda in ayuda_general):
        return True, "ayuda"
    
    # Detectar emociones o temas personales
    if any(emocion in mensaje_lower for emocion in emociones):
        return True, "emocion"
    
    if any(tema in mensaje_lower for tema in temas_personales):
        return True, "personal"
    
    # Detectar mensajes muy cortos o sin palabras clave financieras
    if len(mensaje_lower.split()) < 2:
        # Puede ser una respuesta corta no financiera
        return True, "corto"
    
    # Palabras clave financieras para verificar si es un mensaje financiero
    palabras_financieras = [
        'finanza', 'empresa', 'dinero', 'capital', 'beneficio', 'ganancia', 'activo', 'pasivo', 
        'deuda', 'préstamo', 'inversion', 'cartera', 'crédito', 'liquidez', 'rentabilidad', 
        'margen', 'impuesto', 'pago', 'cobro', 'factura', 'balance', 'contabilidad', 'inventario',
        'flujo', 'costo', 'ingreso', 'gasto', 'ratio', 'indicador', 'estado', 'análisis',
        'endeudamiento', 'productividad', 'rotación'
    ]
    
    # Si contiene alguna palabra financiera, considerarlo como mensaje financiero
    if any(palabra in mensaje_lower for palabra in palabras_financieras):
        return False, "financiero"
    
    # Por defecto, considerar como no financiero
    return True, "otro"

# Función para responder a mensajes no financieros
def responder_mensaje_no_financiero(tipo):
    """
    Genera respuestas para mensajes que no son de índole financiera.
    
    Args:
        tipo (str): Tipo de mensaje no financiero
        
    Returns:
        str: Respuesta apropiada
    """
    if tipo == "saludo":
        saludos = [
            "👋 ¡Hola! Soy FinanzGPT, tu asistente financiero empresarial. ¿En qué puedo ayudarte hoy con respecto a tus finanzas?",
            "¡Hola! Estoy aquí para ayudarte con el análisis financiero de tu empresa. ¿Qué te gustaría saber?",
            "¡Saludos! Soy tu asistente especializado en análisis financiero empresarial. ¿Tienes alguna consulta sobre tus indicadores financieros?"
        ]
        return random.choice(saludos)
    
    elif tipo == "despedida":
        despedidas = [
            "¡Hasta pronto! Recuerda revisar periódicamente tus indicadores financieros para mantener el control de tu empresa.",
            "¡Adiós! Si tienes más preguntas sobre finanzas empresariales en el futuro, estaré aquí para ayudarte.",
            "¡Que tengas un buen día! Estaré disponible cuando necesites más análisis financieros para tu empresa."
        ]
        return random.choice(despedidas)
    
    elif tipo == "emocion" or tipo == "personal":
        respuestas = [
            "Como asistente financiero, estoy diseñado para ayudarte con indicadores y análisis económicos de tu empresa. ¿Te gustaría que analizáramos algún aspecto financiero específico?",
            "Mi especialidad es el análisis financiero empresarial. ¿Puedo ayudarte con alguna consulta sobre tus indicadores económicos?",
            "Estoy programado para asistirte en temas financieros empresariales. ¿Hay algún aspecto financiero de tu empresa sobre el que quieras información?"
        ]
        return random.choice(respuestas)
    
    elif tipo == "ayuda":
        # Mostrar menú de opciones de ayuda
        respuesta = """### 🔍 ¿En qué puedo ayudarte?

Soy FinanzGPT, tu asistente especializado en análisis financiero empresarial. Puedo ayudarte con:

1. **Análisis de endeudamiento**: Evaluación de tu ratio de deuda y recomendaciones para optimizarlo
2. **Análisis de rentabilidad**: Evaluación de tu ROA y estrategias para mejorar tus beneficios
3. **Análisis de productividad**: Evaluación del rendimiento por empleado y consejos para aumentarlo
4. **Análisis de rotación de cartera**: Evaluación de tu ciclo de cobro y métodos para acelerarlo
5. **Análisis de liquidez**: Evaluación de tu capacidad para cubrir obligaciones a corto plazo
6. **Resumen general financiero**: Visión global de todos tus indicadores financieros

Para consultar, simplemente pregunta por ejemplo: *"¿Cómo está mi endeudamiento?"* o *"¿Qué puedo hacer para mejorar mi rentabilidad?"*"""
        return respuesta
    
    elif tipo == "corto" or tipo == "otro":
        respuestas = [
            "Soy un asistente especializado en análisis financiero empresarial. ¿Puedo ayudarte con alguna consulta sobre indicadores financieros de tu empresa?",
            "Estoy aquí para ayudarte con análisis económico y financiero. ¿Qué indicador financiero te gustaría analizar?",
            "Como asistente financiero, puedo ayudarte a interpretar tus indicadores y darte recomendaciones para mejorar la salud económica de tu empresa. ¿Qué aspecto te interesa analizar?"
        ]
        return random.choice(respuestas)

# Función mejorada para respuestas del chatbot estilo ChatGPT
def chatbot_response(mensaje, datos_empresa=None):
    """
    Genera respuestas del chatbot basadas en el mensaje del usuario y los datos de la empresa.
    
    Args:
        mensaje (str): Mensaje del usuario
        datos_empresa (dict, optional): Datos de la empresa
        
    Returns:
        str: Respuesta del chatbot
    """
    # Verificar si es un mensaje no financiero
    es_no_financiero, tipo = es_mensaje_no_financiero(mensaje)
    
    if es_no_financiero:
        return responder_mensaje_no_financiero(tipo)
    
    # Si el mensaje es financiero, continuar con el análisis normal
    # Aplicar NLP al mensaje
    tokens = tokenizar_texto(mensaje)
    lemas = lematizar_texto(mensaje)
    pos_tags = pos_tagging(mensaje)
    keywords = extraer_keywords(mensaje, 3)
    
    # Mensajes predefinidos para diferentes situaciones
    mensajes_predefinidos = {
        'saludo': [
            "👋 ¡Hola! Soy FinanzGPT, tu asistente especializado en análisis financiero empresarial. ¿En qué puedo ayudarte hoy?",
            "¡Saludos! Estoy aquí para ayudarte a entender mejor la situación financiera de tu empresa. ¿Qué te gustaría saber?",
            "Hola, soy tu asistente de análisis económico. Puedo ayudarte a interpretar tus indicadores financieros y darte recomendaciones personalizadas."
        ],
        'agradecimiento': [
            "¡Es un placer ayudarte! El análisis financiero es mi especialidad. ¿Hay algo más que quieras saber?",
            "No hay de qué. Recuerda que puedo explicarte cualquier indicador financiero de tu empresa con más detalle.",
            "¡De nada! Si tienes más preguntas sobre la salud financiera de tu empresa, no dudes en consultarme."
        ],
        'despedida': [
            "¡Hasta pronto! Recuerda revisar periódicamente tus indicadores financieros para mantener el control de tu empresa.",
            "Adiós. No olvides implementar las recomendaciones para mejorar la salud financiera de tu negocio. ¡Éxito!",
            "Que tengas un excelente día. Estaré aquí cuando necesites más análisis o interpretaciones de tus datos financieros."
        ],
        'endeudamiento': [
            "El ratio de endeudamiento muestra qué proporción de tus activos está financiada por deuda. Un valor menor generalmente indica una situación más sólida, aunque depende del sector.\n\nTe invito a consultar este indicador específico para tu empresa escribiendo '¿Cómo está mi endeudamiento?'",
            "Para mejorar tu ratio de endeudamiento, podrías:\n• Aumentar el capital social\n• Reinvertir beneficios\n• Vender activos no productivos para reducir deuda\n• Renegociar plazos de pago.\n\nSi quieres un análisis más detallado de tu situación, pregúntame directamente.",
            "Es importante comparar tu ratio de endeudamiento con empresas similares del sector. Cada industria tiene sus particularidades y lo que es alto en un sector puede ser normal en otro.\n\nPuedo analizar la situación específica de tu empresa si me preguntas sobre tu nivel de endeudamiento."
        ],
        'rentabilidad': [
            "La rentabilidad sobre activos (ROA) indica cuánto beneficio generas por cada peso invertido en activos. Un ROA más alto significa que estás aprovechando mejor tus recursos.\n\nPara conocer cómo está tu rentabilidad, simplemente pregúntame '¿Cómo es mi rentabilidad?'",
            "Para mejorar tu rentabilidad podrías:\n• Aumentar precios si el mercado lo permite\n• Reducir costos operativos\n• Optimizar la gestión de inventarios\n• Deshacerte de activos poco productivos.\n\nPregúntame por un análisis específico para tu empresa.",
            "Tu ROA debe compararse con la media del sector. Si está por debajo, podría ser momento de replantearse la estrategia de negocio o buscar nuevas oportunidades de mercado.\n\nPuedo darte una evaluación personalizada si me preguntas directamente."
        ],
        'productividad': [
            "La productividad por empleado muestra cuánto genera cada trabajador en términos de ingresos. Es un indicador clave de la eficiencia operativa.\n\nSi quieres saber cómo está la productividad en tu empresa, pregúntame directamente.",
            "Para mejorar la productividad podrías:\n• Invertir en capacitación\n• Mejorar procesos y tecnología\n• Implementar sistemas de incentivos basados en resultados\n• Revisar la distribución de tareas.\n\nConsulta el estado de tu empresa preguntándome por tu nivel de productividad.",
            "Una baja productividad puede indicar exceso de personal, falta de tecnología adecuada, o procesos ineficientes. Análisis más profundos te ayudarán a identificar los cuellos de botella.\n\nPregúntame directamente por tu productividad para un análisis específico."
        ],
        'cartera': [
            "La rotación de cartera indica cuántos días tardas en cobrar tus ventas a crédito. Una rotación más baja es generalmente mejor, ya que mejora tu liquidez.\n\nPara saber cómo está tu rotación de cartera, puedes preguntarme directamente.",
            "Para mejorar tu rotación de cartera, considera:\n• Revisar políticas de crédito\n• Implementar descuentos por pronto pago\n• Mejorar el seguimiento de cobros\n• Evaluar factoring para cuentas problemáticas.\n\nPregúntame específicamente por tu rotación de cartera para un análisis personalizado.",
            "Una cartera que rota lentamente puede generar problemas de liquidez. Es importante balancear las políticas de crédito para no perder clientes pero tampoco arriesgar tu flujo de caja.\n\nSi quieres saber cómo está tu rotación de cartera, solo pregúntame."
        ],
        'liquidez': [
            "La liquidez se refiere a la capacidad de tu empresa para cumplir con sus obligaciones a corto plazo. Con los datos proporcionados, puedo hacer una estimación básica.\n\nSi quieres saber más sobre tu liquidez, pregúntame directamente.",
            "Un buen ratio de liquidez suele estar entre 1.5 y 2.0, indicando que puedes cubrir tus deudas a corto plazo sin problemas.\n\nPara un análisis específico de tu empresa, pregúntame por tu liquidez.",
            "Si tienes problemas de liquidez, podrías:\n• Mejorar la gestión de cobros\n• Renegociar plazos con proveedores\n• Establecer líneas de crédito\n• Revisar tu ciclo de conversión de efectivo.\n\nConsulta tu situación preguntándome directamente."
        ],
        'general': [
            "Basándome en los datos proporcionados, puedo analizar varios aspectos financieros de tu empresa. ¿Hay algún indicador específico que te interese conocer más a fondo?",
            "¿Sabías que el análisis financiero debe ser periódico? Te recomiendo revisar estos indicadores al menos trimestralmente para detectar tendencias y actuar a tiempo.",
            "Recuerda que cada sector tiene sus propios estándares para los indicadores financieros. Lo importante es identificar tendencias y compararte con empresas similares."
        ]
    }
    
    # Verificar el tipo de mensaje usando NLP
    # Enfoque mejorado analizando palabras clave y contexto
    if any(palabra in mensaje.lower() for palabra in ['hola', 'buenos', 'saludos', 'que tal']):
        categoria = 'saludo'
    elif any(palabra in mensaje.lower() for palabra in ['gracias', 'agradecido', 'agradezco', 'thank']):
        categoria = 'agradecimiento'
    elif any(palabra in mensaje.lower() for palabra in ['adios', 'chao', 'hasta luego', 'nos vemos', 'bye']):
        categoria = 'despedida'
    elif any(palabra in mensaje.lower() for palabra in ['deuda', 'endeudamiento', 'pasivo', 'prestamo', 'financiacion', 'apalancamiento']):
        categoria = 'endeudamiento'
    elif any(palabra in mensaje.lower() for palabra in ['rentabilidad', 'ganancia', 'beneficio', 'rendimiento', 'roa', 'margen','utilidad']):
        categoria = 'rentabilidad'
    elif any(palabra in mensaje.lower() for palabra in ['productividad', 'eficiencia', 'empleado', 'trabajador', 'personal', 'rendimiento']):
        categoria = 'productividad'
    elif any(palabra in mensaje.lower() for palabra in ['cartera', 'cobrar', 'credito', 'rotacion', 'cliente', 'factura', 'cobranza']):
        categoria = 'cartera'
    elif any(palabra in mensaje.lower() for palabra in ['liquidez', 'efectivo', 'caja', 'corriente', 'solvencia', 'flujo']):
        categoria = 'liquidez'
    else:
        # Análisis más avanzado basado en similitud semántica
        temas = {
            'endeudamiento': "deudas financiación pasivos préstamos créditos obligaciones financieras apalancamiento",
            'rentabilidad': "beneficios ganancias rentabilidad margen utilidad rendimiento roa roi retorno inversión",
            'productividad': "empleados trabajadores personal productividad eficiencia rendimiento laboral desempeño",
            'cartera': "cartera cobros créditos clientes facturas cuentas por cobrar cobranza",
            'liquidez': "liquidez efectivo caja flujo dinero solvencia corto plazo disponible"
        }
        
        # Calcular similitud con cada tema
        mejores_similitudes = {}
        for tema, descripcion in temas.items():
            similitud = similaridad_textos(mensaje.lower(), descripcion)
            mejores_similitudes[tema] = similitud
        
        # Elegir el tema con mayor similitud si supera un umbral
        mejor_tema = max(mejores_similitudes.items(), key=lambda x: x[1])
        if mejor_tema[1] > 0.1:  # Umbral de similitud
            categoria = mejor_tema[0]
        else:
            categoria = 'general'
    
    # Si hay datos de empresa, personalizar respuesta
    if datos_empresa and 'resultados' in datos_empresa:
        resultados = datos_empresa['resultados']
        
        if categoria == 'endeudamiento':
            ratio = resultados['indicadores']['ratio_endeudamiento']
            evaluacion = resultados['evaluacion']['endeudamiento']
            
            # Respuesta detallada y personalizada
            respuesta = f"### 📊 Análisis de Endeudamiento\n\nTu ratio de endeudamiento es **{ratio:.2f}**, lo cual es considerado **{evaluacion}** para el sector {resultados['sector']}.\n\n"
            
            # Añadir interpretación según el valor
            if ratio < 0.4:
                respuesta += "Este valor indica un bajo nivel de endeudamiento, lo que es positivo para la estabilidad financiera, pero podría estar perdiendo oportunidades de apalancamiento para crecer más rápido.\n\n"
            elif ratio < 0.6:
                respuesta += "Este valor muestra un endeudamiento moderado y saludable, un buen balance entre capital propio y ajeno.\n\n"
            else:
                respuesta += "Este nivel de endeudamiento es elevado, lo que podría aumentar el riesgo financiero y dificultar el acceso a nuevo financiamiento.\n\n"
            
            # Añadir recomendaciones específicas
            if ratio > 0.6:
                respuesta += "**Recomendaciones para reducir tu endeudamiento:**\n\n"
                respuesta += "1. Considera aumentar el capital social o reinvertir beneficios\n"
                respuesta += "2. Evalúa la posibilidad de vender activos no estratégicos\n"
                respuesta += "3. Establece un plan gradual de reducción de deuda\n"
                respuesta += "4. Renegocia condiciones de crédito con tus acreedores\n\n"
            
            return respuesta
            
        elif categoria == 'rentabilidad':
            rent = resultados['indicadores']['rentabilidad']
            evaluacion = resultados['evaluacion']['rentabilidad']
            
            # Respuesta detallada
            respuesta = f"### 💰 Análisis de Rentabilidad\n\nTu rentabilidad sobre activos (ROA) es **{rent:.2%}**, lo cual es considerada **{evaluacion}** para el sector {resultados['sector']}.\n\n"
            
            # Interpretación personalizada
            if rent < 0.05:
                respuesta += "Esta rentabilidad es baja. Cada $100 invertidos en activos están generando menos de $5 de beneficio, lo que sugiere revisar la eficiencia operativa y la estructura de costos.\n\n"
                
                # Añadir recomendaciones específicas para baja rentabilidad
                respuesta += "**Recomendaciones para mejorar tu rentabilidad:**\n\n"
                respuesta += "1. Realiza un análisis detallado de costos para identificar ineficiencias\n"
                respuesta += "2. Evalúa tu estrategia de precios y considera ajustes si el mercado lo permite\n"
                respuesta += "3. Revisa la productividad de tus activos y considera deshacerte de aquellos poco productivos\n"
                respuesta += "4. Analiza tus líneas de productos/servicios e identifica cuáles son más rentables\n\n"
                
            elif rent < 0.15:
                respuesta += "Esta rentabilidad es moderada. Tus activos están produciendo un retorno razonable, aunque siempre hay espacio para mejorar.\n\n"
                
                # Recomendaciones para rentabilidad moderada
                respuesta += "**Acciones para optimizar tu rentabilidad:**\n\n"
                respuesta += "1. Busca oportunidades de incremento de eficiencia operativa\n"
                respuesta += "2. Considera estrategias para aumentar el volumen de ventas\n"
                respuesta += "3. Evalúa posibilidades de diversificación hacia productos/servicios más rentables\n\n"
                
            else:
                respuesta += "¡Excelente rentabilidad! Tus activos están siendo muy productivos generando un alto retorno sobre la inversión.\n\n"
                
                # Consejos para mantener alta rentabilidad
                respuesta += "**Para mantener esta excelente rentabilidad:**\n\n"
                respuesta += "1. Documenta tus procesos exitosos para asegurar su continuidad\n"
                respuesta += "2. Considera reinvertir parte de los beneficios para sostener el crecimiento\n"
                respuesta += "3. Monitorea regularmente los indicadores para detectar cambios de tendencia\n\n"
            
            return respuesta
            
        elif categoria == 'productividad':
            productividad = resultados['indicadores']['productividad']
            evaluacion = resultados['evaluacion']['productividad']
            
            # Respuesta detallada
            respuesta = f"### 👥 Análisis de Productividad\n\nLa productividad por empleado es **${formato_numero(productividad)} COP**, lo cual es considerada **{evaluacion}** para el sector {resultados['sector']}.\n\n"
            
            # Interpretación personalizada según sector
            sector_limites = {
                'Tecnología': 100000000,
                'Comercio': 50000000,
                'Manufactura': 70000000,
                'Servicios': 60000000
            }
            
            limite = sector_limites.get(resultados['sector'], 60000000)
            
            if productividad < limite * 0.7:
                respuesta += "Esta productividad está por debajo del estándar del sector. Podría ser conveniente revisar procesos, capacitación y tecnología disponible para los empleados.\n\n"
                
                # Recomendaciones específicas para baja productividad
                respuesta += "**Estrategias para aumentar la productividad:**\n\n"
                respuesta += "1. Implementa programas de capacitación y desarrollo de habilidades\n"
                respuesta += "2. Revisa y optimiza los procesos operativos para eliminar ineficiencias\n"
                respuesta += "3. Evalúa la incorporación de tecnología para automatizar tareas repetitivas\n"
                respuesta += "4. Considera sistemas de incentivos basados en resultados\n\n"
                
            elif productividad < limite * 1.2:
                respuesta += "Esta productividad está alineada con los estándares del sector, mostrando una operación eficiente.\n\n"
                
                # Consejos para mantener buena productividad
                respuesta += "**Para mantener y mejorar tu productividad:**\n\n"
                respuesta += "1. Establece sistemas de mejora continua en tus procesos\n"
                respuesta += "2. Fomenta la participación de los empleados en la identificación de mejoras\n"
                respuesta += "3. Realiza evaluaciones periódicas de desempeño y productividad\n\n"
                
            else:
                respuesta += "¡Excelente productividad! Tus empleados generan un valor significativamente superior al promedio del sector.\n\n"
                
                # Estrategias para mantener alta productividad
                respuesta += "**Para mantener este excelente nivel:**\n\n"
                respuesta += "1. Documenta y estandariza las mejores prácticas actuales\n"
                respuesta += "2. Reconoce y premia el alto desempeño para mantener la motivación\n"
                respuesta += "3. Comparte el conocimiento entre equipos para extender el éxito\n\n"
            
            return respuesta
            
        elif categoria == 'cartera':
            rotacion = resultados['indicadores']['rotacion_cartera']
            evaluacion = resultados['evaluacion']['rotacion']
            
            # Respuesta detallada
            respuesta = f"### 📅 Análisis de Rotación de Cartera\n\nTu rotación de cartera es de **{rotacion:.1f} días**, lo cual es considerado **{evaluacion}** para el sector {resultados['sector']}.\n\n"
            
            # Interpretación personalizada
            if rotacion < 30:
                respuesta += "¡Excelente gestión de cobros! Tu empresa recupera el dinero rápidamente, lo que favorece la liquidez.\n\n"
                
                # Consejos para mantener buena rotación
                respuesta += "**Para mantener esta excelente rotación:**\n\n"
                respuesta += "1. Documenta tus políticas y procesos de cobranza actuales\n"
                respuesta += "2. Mantén actualizada tu base de datos de clientes\n"
                respuesta += "3. Continúa con los incentivos por pronto pago si los tienes implementados\n\n"
                
            elif rotacion < 60:
                respuesta += "Tu gestión de cobros es adecuada. Mantiene un buen equilibrio entre política comercial y necesidades de liquidez.\n\n"
                
                # Consejos para mejorar una rotación adecuada
                respuesta += "**Para optimizar aún más tu rotación:**\n\n"
                respuesta += "1. Segmenta a tus clientes por comportamiento de pago\n"
                respuesta += "2. Implementa recordatorios automáticos antes del vencimiento\n"
                respuesta += "3. Evalúa ofrecer pequeños descuentos por pronto pago\n\n"
                
            else:
                respuesta += "Tu periodo de cobro es extenso, lo que podría estar afectando tu flujo de caja. Considera revisar tus políticas de crédito y cobranza.\n\n"
                
                # Estrategias para mejorar rotación alta
                respuesta += "**Estrategias para reducir tu periodo de cobro:**\n\n"
                respuesta += "1. Revisa y actualiza tus políticas de crédito y criterios de selección de clientes\n"
                respuesta += "2. Implementa un sistema de seguimiento más estricto para facturas pendientes\n"
                respuesta += "3. Considera ofrecer descuentos significativos por pronto pago\n"
                respuesta += "4. Evalúa opciones de factoring para casos problemáticos o clientes estratégicos\n\n"
            
            return respuesta
            
        elif categoria == 'liquidez':
            # Estimación aproximada de liquidez basada en cartera y deudas
            cartera = resultados['datos']['cartera']
            deudas = resultados['datos']['deudas']
            
            # Cálculo simplificado (solo con los datos disponibles)
            est_liquidez = cartera / deudas if deudas > 0 else "Alta"
            
            # Respuesta
            if isinstance(est_liquidez, str):
                respuesta = f"### 💧 Estimación de Liquidez\n\nBasado en los datos proporcionados, tu empresa parece tener una liquidez **{est_liquidez}**, ya que tus deudas son mínimas en comparación con tu cartera.\n\n"
                
                respuesta += "**Recomendaciones para gestionar tu alta liquidez:**\n\n"
                respuesta += "1. Evalúa oportunidades de inversión para recursos excedentes\n"
                respuesta += "2. Considera expandir operaciones o diversificar\n"
                respuesta += "3. Revisa tu política de dividendos si corresponde\n\n"
                
            else:
                respuesta = f"### 💧 Estimación de Liquidez\n\nLa relación entre tu cartera y tus deudas es de **{est_liquidez:.2f}**.\n\n"
                
                if est_liquidez < 1:
                    respuesta += "Esto podría indicar problemas de liquidez a corto plazo, ya que tu cartera no cubriría todas tus deudas.\n\n"
                    
                    # Estrategias para mejorar liquidez baja
                    respuesta += "**Estrategias para mejorar tu liquidez:**\n\n"
                    respuesta += "1. Acelera la cobranza de cartera con incentivos de pronto pago\n"
                    respuesta += "2. Negocia extensiones de plazo con proveedores\n"
                    respuesta += "3. Evalúa líneas de crédito de contingencia\n"
                    respuesta += "4. Considera vender activos no esenciales si es necesario\n\n"
                    
                elif est_liquidez < 1.5:
                    respuesta += "Tu liquidez es ajustada pero manejable. Mantén un control cercano de tu flujo de caja.\n\n"
                    
                    # Consejos para liquidez ajustada
                    respuesta += "**Para mejorar tu posición de liquidez:**\n\n"
                    respuesta += "1. Implementa un sistema de proyección semanal de flujo de caja\n"
                    respuesta += "2. Revisa tus políticas de inventario para optimizar capital de trabajo\n"
                    respuesta += "3. Establece alertas tempranas para posibles problemas de liquidez\n\n"
                    
                else:
                    respuesta += "Tu posición de liquidez parece sólida, con suficiente cartera para cubrir tus obligaciones.\n\n"
                    
                    # Consejos para gestionar buena liquidez
                    respuesta += "**Para optimizar tu gestión de liquidez:**\n\n"
                    respuesta += "1. Evalúa opciones de inversión temporal para excedentes\n"
                    respuesta += "2. Considera negociar mejores condiciones con proveedores\n"
                    respuesta += "3. Mantén un fondo de contingencia para oportunidades o emergencias\n\n"
            
            return respuesta
            
        # Si la categoría no coincide con ninguna de las anteriores, dar respuesta general
        else:
            # Respuesta general sobre el estado de la empresa
            estado = resultados['estado_general']
            
            respuesta = f"### 📈 Estado General de la Empresa\n\nBasado en mis análisis, la situación financiera general de **{resultados['nombre']}** es **{estado}**.\n\n"
            
            # Añadir resumen de los puntos principales
            respuesta += "**Resumen de indicadores clave:**\n\n"
            respuesta += f"• Endeudamiento: {resultados['indicadores']['ratio_endeudamiento']:.2f} - {resultados['evaluacion']['endeudamiento']}\n"
            respuesta += f"• Rentabilidad: {resultados['indicadores']['rentabilidad']:.2%} - {resultados['evaluacion']['rentabilidad']}\n"
            respuesta += f"• Productividad: ${formato_numero(resultados['indicadores']['productividad'])} por empleado - {resultados['evaluacion']['productividad']}\n"
            respuesta += f"• Rotación de cartera: {resultados['indicadores']['rotacion_cartera']:.1f} días - {resultados['evaluacion']['rotacion']}\n\n"
            
            respuesta += "Para recibir un análisis detallado de cualquiera de estos indicadores, puedes preguntarme específicamente por ello.\n\n"
            
            # Sugerir próximos pasos según el estado general
            if estado == "Excelente":
                respuesta += "**¿Qué te interesaría saber para mantener este excelente desempeño?**"
            elif estado == "Bueno":
                respuesta += "**¿Qué aspecto te gustaría mejorar para llevar tu empresa al siguiente nivel?**"
            elif estado == "Regular":
                respuesta += "**¿Sobre qué área te gustaría trabajar primero para mejorar la situación?**"
            else:  # Crítico
                respuesta += "**Es importante actuar pronto. ¿Qué aspecto te preocupa más y quieres abordar primero?**"
                
            return respuesta
    
    # Si no hay datos de empresa o la consulta es general
    # Usar POS tagging para identificar verbos y sustantivos clave
    verbos = [word for word, tag in pos_tags if tag == 'VERB']
    sustantivos = [word for word, tag in pos_tags if tag in ['NOUN', 'PROPN']]
    
    # Personalización básica basada en palabras extraídas
    if verbos and sustantivos:
        accion = verbos[0]
        tema = sustantivos[0] if sustantivos else "empresa"
        respuesta = f"Entiendo que quieres {accion} sobre {tema}. "
        respuesta += random.choice(mensajes_predefinidos[categoria])
        return respuesta
    
    # Si no hay suficiente contexto para personalizar, usar respuesta predefinida
    return random.choice(mensajes_predefinidos[categoria])

# Variables para almacenar datos de la empresa y resultados
if 'datos_empresa' not in st.session_state:
    st.session_state.datos_empresa = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'page_view' not in st.session_state:
    st.session_state.page_view = "welcome"  # Opciones: "welcome", "chat", "form", "results"

if 'thinking' not in st.session_state:
    st.session_state.thinking = False

# Sidebar con información y navegación
with st.sidebar:
    st.markdown('<div class="main-title">FinanzGPT</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Asistente Financiero Empresarial</div>', unsafe_allow_html=True)
    
    # Opciones de navegación
    st.markdown("### Navegación")
    
    # Contenedor para botones de navegación
    nav_col1, nav_col2 = st.columns([1, 1])
    
    with nav_col1:
        # Botón de Inicio
        if st.session_state.page_view == "welcome":
            st.markdown('<div class="nav-button-active">🏠 Inicio</div>', unsafe_allow_html=True)
        else:
            if st.button("🏠 Inicio", key="home_btn", use_container_width=True):
                st.session_state.page_view = "welcome"
                st.rerun()
        
        # Botón de Chat
        if st.session_state.page_view == "chat":
            st.markdown('<div class="nav-button-active">💬 Chat</div>', unsafe_allow_html=True)
        else:
            if st.button("💬 Chat", key="chat_btn", use_container_width=True):
                st.session_state.page_view = "chat"
                st.rerun()
    
    with nav_col2:
        # Botón de Formulario
        if st.session_state.page_view == "form":
            st.markdown('<div class="nav-button-active">📝 Datos</div>', unsafe_allow_html=True)
        else:
            if st.button("📝 Datos", key="form_btn", use_container_width=True):
                st.session_state.page_view = "form"
                st.rerun()
        
        # Botón de Resultados
        if st.session_state.page_view == "results":
            st.markdown('<div class="nav-button-active">📊 Análisis</div>', unsafe_allow_html=True)
        else:
            if st.button("📊 Análisis", key="results_btn", use_container_width=True):
                if st.session_state.datos_empresa:
                    st.session_state.page_view = "results"
                    st.rerun()
                else:
                    st.warning("Primero debes ingresar los datos de tu empresa.")
    
    st.markdown("---")
    
    # Información sobre la aplicación
    with st.expander("ℹ️ Acerca de FinanzGPT"):
        st.markdown("""
        FinanzGPT utiliza técnicas avanzadas de procesamiento de lenguaje natural para analizar y evaluar la salud financiera de empresas.
        
        **Tecnologías utilizadas:**
        
        * **Tokenización**: Divide el texto en unidades individuales
        * **Lematización**: Reduce palabras a su forma base
        * **POS Tagging**: Etiquetado gramatical
        * **Embedding**: Representación vectorial del texto
        
        **Indicadores financieros analizados:**
        * Ratio de endeudamiento
        * Rentabilidad sobre activos
        * Productividad por empleado
        * Rotación de cartera
        """)
    
    # Botón para limpiar historial de chat
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.chat_history = []
        st.info("Historial de chat borrado")
        time.sleep(1)
        st.rerun()
    
    st.markdown("---")
    st.markdown('<div style="text-align: center; color: #888;">Desarrollado con ❤️ usando Python y Streamlit</div>', unsafe_allow_html=True)

# Pantalla de bienvenida
if st.session_state.page_view == "welcome":
    st.markdown('<div class="main-title">Bienvenido a FinanzGPT</div>', unsafe_allow_html=True)
    
    # Contenedor principal
    welcome_container = st.container()
    
    with welcome_container:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        ### Tu asistente inteligente para análisis financiero empresarial
        
        FinanzGPT te permite analizar la salud económica de tu empresa a través de un análisis detallado de tus principales indicadores financieros.
        
        **¿Cómo funciona?**
        
        1. Ingresa los datos básicos de tu empresa
        2. Nuestro sistema realiza un análisis completo
        3. Conversa con FinanzGPT y recibe respuestas personalizadas
        
        Utiliza el poder del procesamiento de lenguaje natural para obtener insights valiosos sobre tu negocio.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de inicio
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📝 Ingresar datos de mi empresa", use_container_width=True):
                st.session_state.page_view = "form"
                st.rerun()
        
        with col2:
            if st.session_state.datos_empresa:
                if st.button("💬 Ir al chat", use_container_width=True):
                    st.session_state.page_view = "chat"
                    st.rerun()
            else:
                st.button("💬 Ir al chat (primero ingresa datos)", use_container_width=True, disabled=True)
        
        # Ejemplos de preguntas
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        ### Ejemplos de preguntas que puedes hacer
        
        Una vez que hayas ingresado los datos de tu empresa, podrás consultar a FinanzGPT sobre:
        
        - "¿Cómo está mi nivel de endeudamiento?"
        - "¿Es buena mi rentabilidad?"
        - "¿Qué puedo hacer para mejorar la productividad?"
        - "¿Cómo optimizar mi rotación de cartera?"
        - "Dame un resumen general de mi empresa"
        - "Ayuda" (para ver un menú de opciones)
        """)
        st.markdown('</div>', unsafe_allow_html=True)

# Vista de chat
elif st.session_state.page_view == "chat":
    st.markdown('<div class="main-title">💬 Chat con FinanzGPT</div>', unsafe_allow_html=True)
    
    # Si no hay datos de empresa, mostrar mensaje
    if not st.session_state.datos_empresa:
        st.info("👋 Para obtener respuestas personalizadas sobre tu empresa, primero debes ingresar tus datos financieros en la sección 'Datos'.")
    
    # Contenedor para el historial de chat
    chat_container = st.container()
    
    # Mostrar historial de chat con estilos mejorados
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align: center; margin: 50px 0; color: #888;">
                <p>👋 ¡Hola! Soy FinanzGPT, tu asistente financiero.</p>
                <p>Puedes preguntarme sobre indicadores financieros, recomendaciones para tu empresa, o cualquier duda sobre análisis económico.</p>
                <p>Escribe "ayuda" si necesitas ver un menú de opciones.</p>
            </div>
            """, unsafe_allow_html=True)
        
        for sender, message in st.session_state.chat_history:
            if sender == "user":
                st.markdown(f"""
                <div class="chat-message-user">
                    <div class="avatar avatar-user">U</div>
                    <div class="message-content">{message}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Convertir marcadores markdown en mensaje HTML
                # Procesar encabezados
                message = re.sub(r'### (.*)', r'<h3>\1</h3>', message)
                # Procesar negritas
                message = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', message)
                # Procesar itálicas
                message = re.sub(r'\*(.*?)\*', r'<em>\1</em>', message)
                # Procesar listas con viñetas
                message = re.sub(r'• (.*)', r'<li>\1</li>', message)
                message = message.replace('<li>', '<ul><li>').replace('</li>\n\n', '</li></ul>\n\n')
                
                st.markdown(f"""
                <div class="chat-message-bot">
                    <div class="avatar avatar-bot">F</div>
                    <div class="message-content">{message}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Manejar el estado "pensando"
    if st.session_state.thinking:
        st.markdown("""
        <div class="thinking-animation">
            <div class="thinking-dot"></div>
            <div class="thinking-dot"></div>
            <div class="thinking-dot"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # Input para chatbot
    mensaje_usuario = st.chat_input("Escribe tu pregunta aquí...")
    
    if mensaje_usuario:
        # Agregar mensaje del usuario al historial
        st.session_state.chat_history.append(("user", mensaje_usuario))
        
        # Activar animación de pensamiento
        st.session_state.thinking = True
        st.rerun()

# Este código se ejecuta después del rerun cuando thinking es True
if st.session_state.thinking and st.session_state.chat_history:
    # Desactivar el estado "pensando"
    st.session_state.thinking = False
    
    # Obtener la última pregunta del usuario
    ultima_pregunta = [msg for sender, msg in st.session_state.chat_history if sender == "user"][-1]
    
    # Generar respuesta del chatbot
    respuesta = chatbot_response(ultima_pregunta, st.session_state.datos_empresa)
    
    # Agregar respuesta al historial
    st.session_state.chat_history.append(("bot", respuesta))
    
    # Actualizar chat
    st.rerun()

# Vista de formulario
elif st.session_state.page_view == "form":
    st.markdown('<div class="main-title">📝 Datos de la Empresa</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Ingresa la información financiera para obtener un análisis personalizado</div>', unsafe_allow_html=True)
    
    with st.form("formulario_empresa"):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Información General")
        
        nombre_empresa = st.text_input("Nombre de la Empresa", 
                                       value="" if not st.session_state.datos_empresa else st.session_state.datos_empresa.get('datos', {}).get('nombre', ""))
        
        sector = st.selectbox(
            "Sector",
            ["Tecnología", "Comercio", "Manufactura", "Servicios", "Otro"],
            index=0 if not st.session_state.datos_empresa else 
                  ["Tecnología", "Comercio", "Manufactura", "Servicios", "Otro"].index(st.session_state.datos_empresa.get('datos', {}).get('sector', "Tecnología"))
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Información Financiera")
        # Crear dos columnas para los inputs numéricos
        col1_form, col2_form = st.columns(2)
        
        with col1_form:
            ganancias = st.number_input(
                "Ganancias Anuales (COP)", 
                min_value=0.0, 
                format="%f",
                value=0.0 if not st.session_state.datos_empresa else st.session_state.datos_empresa.get('datos', {}).get('ganancias', 0.0)
            )
            st.markdown("""<div style="font-size: 12px; color: #666;">Ingresos totales menos gastos</div>""", unsafe_allow_html=True)
            
            num_empleados = st.number_input(
                "Número de Empleados", 
                min_value=1, 
                step=1,
                value=1 if not st.session_state.datos_empresa else st.session_state.datos_empresa.get('datos', {}).get('empleados', 1)
            )
            st.markdown("""<div style="font-size: 12px; color: #666;">Personal en nómina</div>""", unsafe_allow_html=True)
            
            valor_cartera = st.number_input(
                "Valor en Cartera (COP)", 
                min_value=0.0, 
                format="%f",
                value=0.0 if not st.session_state.datos_empresa else st.session_state.datos_empresa.get('datos', {}).get('cartera', 0.0)
            )
            st.markdown("""<div style="font-size: 12px; color: #666;">Total de cuentas por cobrar</div>""", unsafe_allow_html=True)
        
        with col2_form:
            valor_activos = st.number_input(
                "Valor en Activos (COP)", 
                min_value=0.0, 
                format="%f",
                value=0.0 if not st.session_state.datos_empresa else st.session_state.datos_empresa.get('datos', {}).get('activos', 0.0)
            )
            st.markdown("""<div style="font-size: 12px; color: #666;">Total de bienes y derechos</div>""", unsafe_allow_html=True)
            
            valor_deudas = st.number_input(
                "Valor Deudas (COP)", 
                min_value=0.0, 
                format="%f",
                value=0.0 if not st.session_state.datos_empresa else st.session_state.datos_empresa.get('datos', {}).get('deudas', 0.0)
            )
            st.markdown("""<div style="font-size: 12px; color: #666;">Total de obligaciones financieras</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Analizar Empresa", use_container_width=True)
        with col2:
            if st.session_state.datos_empresa:
                cancel = st.form_submit_button("Cancelar", use_container_width=True)
                if cancel:
                    st.session_state.page_view = "welcome"
                    st.rerun()
        
        if submitted:
            # Validar entradas
            errores = []
            
            if not nombre_empresa.strip():
                errores.append("El nombre de la empresa es obligatorio.")
            
            valid_ganancias, msg = validar_numeros(ganancias, 0.0, "valor de ganancias")
            if not valid_ganancias:
                errores.append(msg)
            
            valid_activos, msg = validar_numeros(valor_activos, 0.0, "valor de activos")
            if not valid_activos:
                errores.append(msg)
                
            valid_empleados, msg = validar_numeros(num_empleados, 1, "número de empleados")
            if not valid_empleados:
                errores.append(msg)
                
            valid_cartera, msg = validar_numeros(valor_cartera, 0.0, "valor en cartera")
            if not valid_cartera:
                errores.append(msg)
                
            valid_deudas, msg = validar_numeros(valor_deudas, 0.0, "valor en deudas")
            if not valid_deudas:
                errores.append(msg)
            
            # Si hay errores, mostrarlos
            if errores:
                error_text = "\n".join([f"• {error}" for error in errores])
                st.error(f"Por favor, corrige los siguientes errores:\n\n{error_text}")
            else:
                # Preparar datos
                datos = {
                    'nombre': nombre_empresa,
                    'ganancias': ganancias,
                    'sector': sector,
                    'empleados': num_empleados,
                    'activos': valor_activos,
                    'cartera': valor_cartera,
                    'deudas': valor_deudas
                }
                
                # Mostrar animación de procesamiento
                mostrar_procesamiento()
                
                # Realizar análisis
                resultados = analizar_empresa(datos)
                mensaje = generar_mensaje_resultado(resultados)
                
                # Guardar datos y resultados en sesión
                st.session_state.datos_empresa = {
                    'datos': datos,
                    'resultados': resultados,
                    'mensaje': mensaje
                }
                
                # Agregar mensaje de bienvenida al chat si es el primer análisis
                if not st.session_state.chat_history:
                    bienvenida = f"¡Hola! He analizado los datos de **{nombre_empresa}**. El estado financiero general de tu empresa es **{resultados['estado_general']}**.\n\n¿Qué te gustaría saber específicamente sobre tus indicadores financieros?"
                    st.session_state.chat_history.append(("bot", bienvenida))
                
                # Cambiar a vista de resultados
                st.session_state.page_view = "results"
                st.rerun()

# Vista de resultados
elif st.session_state.page_view == "results":
    if not st.session_state.datos_empresa:
        st.warning("No hay datos de empresa para mostrar. Por favor, completa el formulario primero.")
        st.session_state.page_view = "form"
        st.rerun()
    else:
        resultados = st.session_state.datos_empresa['resultados']
        
        st.markdown('<div class="main-title">📊 Análisis Financiero</div>', unsafe_allow_html=True)
        st.markdown(f"<div class='sub-title'>Empresa: {resultados['nombre']} | Sector: {resultados['sector']}</div>", unsafe_allow_html=True)
        
        # Estado general con estilo mejorado
        estado = resultados['estado_general'].lower()
        st.markdown(f"""
        <div class="card">
            <div class="estado-{estado}">
                <h2>Estado Financiero: {resultados['estado_general']}</h2>
            </div>
            <div style="text-align: center; margin-top: 15px; font-style: italic;">
                <p>El análisis se basa en la comparación de tus indicadores con estándares del sector {resultados['sector']}.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Contenedor para los indicadores principales
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📈 Indicadores Clave")
        
        # Crear 4 columnas para mostrar los indicadores principales
        col1_ind, col2_ind = st.columns(2)
        
        with col1_ind:
            ratio = resultados['indicadores']['ratio_endeudamiento']
            eval_ind = resultados['evaluacion']['endeudamiento']
            color = "green" if eval_ind == "bueno" else "red"
            
            st.markdown(f"""
            <div class="highlight-metric">
                <strong>⚖️ Endeudamiento</strong><br>
                <span style="font-size: 1.4rem; color: {'#10A37F' if eval_ind == 'bueno' else '#EF4444'}">{ratio:.2f}</span><br>
                <span style="font-size: 0.9rem;">Evaluación: {eval_ind.capitalize()}</span>
            </div>
            """, unsafe_allow_html=True)
            
            rent = resultados['indicadores']['rentabilidad']
            eval_ind = resultados['evaluacion']['rentabilidad']
            color = "green" if eval_ind == "buena" else "red"
            
            st.markdown(f"""
            <div class="highlight-metric">
                <strong>💰 Rentabilidad</strong><br>
                <span style="font-size: 1.4rem; color: {'#10A37F' if eval_ind == 'buena' else '#EF4444'}">{rent:.2%}</span><br>
                <span style="font-size: 0.9rem;">Evaluación: {eval_ind.capitalize()}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2_ind:
            prod = resultados['indicadores']['productividad']
            eval_ind = resultados['evaluacion']['productividad']
            color = "green" if eval_ind == "buena" else "red"
            
            st.markdown(f"""
            <div class="highlight-metric">
                <strong>👥 Productividad</strong><br>
                <span style="font-size: 1.4rem; color: {'#10A37F' if eval_ind == 'buena' else '#EF4444'}">${formato_numero(prod)}</span><br>
                <span style="font-size: 0.9rem;">Evaluación: {eval_ind.capitalize()}</span>
            </div>
            """, unsafe_allow_html=True)
            
            rot = resultados['indicadores']['rotacion_cartera']
            eval_ind = resultados['evaluacion']['rotacion']
            color = "green" if eval_ind == "buena" else "red"
            
            st.markdown(f"""
            <div class="highlight-metric">
                <strong>📅 Rotación Cartera</strong><br>
                <span style="font-size: 1.4rem; color: {'#10A37F' if eval_ind == 'buena' else '#EF4444'}">{rot:.1f} días</span><br>
                <span style="font-size: 0.9rem;">Evaluación: {eval_ind.capitalize()}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Recomendaciones
        if resultados['recomendaciones']:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 💡 Recomendaciones")
            
            for i, rec in enumerate(resultados['recomendaciones'], 1):
                st.markdown(f"""
                <div class="recomendacion">
                    <strong>Recomendación {i}:</strong> {rec}
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráfico de indicadores
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📊 Visualización de Indicadores")
        
        # Creamos la figura con un estilo más moderno
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True), facecolor='#FFFFFF')
        
        # Normalizar valores para el gráfico
        endeudamiento_norm = 1 - min(1, resultados['indicadores']['ratio_endeudamiento'] / 1.0)
        rentabilidad_norm = min(1, resultados['indicadores']['rentabilidad'] / 0.3)
        
        # Para productividad, normalizar según sector
        sector_limites = {
            'Tecnología': 100000000,
            'Comercio': 50000000,
            'Manufactura': 70000000,
            'Servicios': 60000000,
            'Otro': 60000000
        }
        
        limite_prod = sector_limites.get(resultados['sector'], 60000000)
        productividad_norm = min(1, resultados['indicadores']['productividad'] / limite_prod)
        
        # Para rotación, menor es mejor (normalizar de forma inversa)
        rotacion_norm = 1 - min(1, resultados['indicadores']['rotacion_cartera'] / 90)
        
        # Datos para el gráfico
        categorias = ['Endeudamiento', 'Rentabilidad', 'Productividad', 'Rot. Cartera']
        valores = [endeudamiento_norm, rentabilidad_norm, productividad_norm, rotacion_norm]
        
        # Completar el círculo repitiendo el primer valor
        valores += [valores[0]]
        categorias += [categorias[0]]
        
        # Configuración estética
        N = len(categorias) - 1
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += [angles[0]]  # Cerrar el círculo
        
        # Dibujar los ejes y el gráfico
        ax.plot(angles, valores, linewidth=2.5, linestyle='solid', color='#10A37F')
        ax.fill(angles, valores, alpha=0.25, color='#10A37F')
        
        # Agregar etiquetas con mejor formato
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categorias[:-1], size=12, fontweight='bold', color='#444654')
        
        # Mejorar las líneas de la cuadrícula
        ax.set_rlabel_position(0)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], color="grey", size=10)
        ax.set_ylim(0, 1)
        
        # Agregar título
        plt.title('Perfil Económico de la Empresa', size=16, color='#444654', pad=20, fontweight='bold')
        
        # Mostramos el gráfico
        st.pyplot(fig)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Análisis NLP
        with st.expander("🧠 Procesamiento de Lenguaje Natural"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            tab1, tab2, tab3, tab4 = st.tabs(["Tokenización", "Lematización", "POS Tagging", "Embedding"])
            
            with tab1:
                st.markdown("#### 🔍 Tokenización")
                st.markdown("La tokenización divide el texto en unidades individuales (tokens):")
                st.code(str(resultados['nlp_ejemplo']['tokens']))
                st.markdown("""
                **¿Para qué sirve?** Permite analizar el texto palabra por palabra, lo que es fundamental para el procesamiento del lenguaje natural.
                """)
            
            with tab2:
                st.markdown("#### 📝 Lematización")
                st.markdown("La lematización reduce las palabras a su forma base o lema:")
                st.code(str(resultados['nlp_ejemplo']['lemas']))
                st.markdown("""
                **¿Para qué sirve?** Permite considerar diferentes formas de una palabra como la misma, mejorando el análisis semántico del texto.
                """)
            
            with tab3:
                st.markdown("#### 🏷️ POS Tagging")
                st.markdown("El etiquetado gramatical (Part-of-Speech) identifica la función gramatical de cada palabra:")
                st.code(str(resultados['nlp_ejemplo']['pos_tags']))
                st.markdown("""
                **¿Para qué sirve?** Ayuda a entender la estructura gramatical del texto, identificando verbos, sustantivos, adjetivos, etc.
                """)
            
            with tab4:
                st.markdown("#### 🧮 Embedding")
                st.markdown("El embedding transforma el texto en vectores numéricos que capturan significado semántico:")
                st.code(f"Dimensión del embedding: {resultados['nlp_ejemplo']['embedding_dim']}")
                st.markdown("""
                **¿Para qué sirve?** Permite representar palabras y frases como vectores, facilitando cálculos de similitud semántica y otros análisis avanzados.
                """)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Botones de acción
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💬 Consultar al Chatbot", use_container_width=True):
                st.session_state.page_view = "chat"
                st.rerun()
        
        with col2:
            if st.button("📝 Modificar datos", use_container_width=True):
                st.session_state.page_view = "form"
                st.rerun()

# Código principal
if __name__ == "__main__":
    # Todo el código ya está definido arriba
    pass