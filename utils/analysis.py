import numpy as np
import pandas as pd
from .nlp_utils import tokenizar_texto, lematizar_texto, pos_tagging, crear_embedding

def calcular_ratio_endeudamiento(valor_deudas, valor_activos):
    """
    Calcula el ratio de endeudamiento de la empresa.
    
    Args:
        valor_deudas (float): Valor total de deudas
        valor_activos (float): Valor total de activos
        
    Returns:
        float: Ratio de endeudamiento
    """
    if valor_activos == 0:
        return float('inf')
    return valor_deudas / valor_activos

def calcular_rentabilidad(ganancias_anuales, valor_activos):
    """
    Calcula la rentabilidad económica (ROA).
    
    Args:
        ganancias_anuales (float): Ganancias anuales
        valor_activos (float): Valor total de activos
        
    Returns:
        float: Rentabilidad sobre activos
    """
    if valor_activos == 0:
        return 0
    return ganancias_anuales / valor_activos

def calcular_productividad_empleado(ganancias_anuales, num_empleados):
    """
    Calcula la productividad por empleado.
    
    Args:
        ganancias_anuales (float): Ganancias anuales
        num_empleados (int): Número de empleados
        
    Returns:
        float: Productividad por empleado
    """
    if num_empleados == 0:
        return 0
    return ganancias_anuales / num_empleados

def calcular_rotacion_cartera(valor_cartera, ganancias_anuales):
    """
    Calcula la rotación de cartera.
    
    Args:
        valor_cartera (float): Valor en cartera
        ganancias_anuales (float): Ganancias anuales
        
    Returns:
        float: Rotación de cartera (días)
    """
    if ganancias_anuales == 0:
        return float('inf')
    return (valor_cartera / ganancias_anuales) * 365  # Días de rotación

def analizar_empresa(datos):
    """
    Realiza un análisis completo de la situación económica de la empresa.
    
    Args:
        datos (dict): Diccionario con datos de la empresa
        
    Returns:
        dict: Resultados del análisis
    """
    # Extraer datos
    nombre = datos['nombre']
    ganancias = float(datos['ganancias'])
    sector = datos['sector']
    empleados = int(datos['empleados'])
    activos = float(datos['activos'])
    cartera = float(datos['cartera'])
    deudas = float(datos['deudas'])
    
    # Calcular indicadores
    ratio_endeudamiento = calcular_ratio_endeudamiento(deudas, activos)
    rentabilidad = calcular_rentabilidad(ganancias, activos)
    productividad = calcular_productividad_empleado(ganancias, empleados)
    rotacion_cartera = calcular_rotacion_cartera(cartera, ganancias)
    
    # Definir límites según sector (simplificados para este ejemplo)
    limites = {
        'tecnologia': {
            'endeudamiento': 0.6,
            'rentabilidad': 0.15,
            'productividad': 100000000,  # 100 millones COP por empleado
            'rotacion': 60
        },
        'comercio': {
            'endeudamiento': 0.5,
            'rentabilidad': 0.08,
            'productividad': 50000000,  # 50 millones COP por empleado
            'rotacion': 45
        },
        'manufactura': {
            'endeudamiento': 0.55,
            'rentabilidad': 0.1,
            'productividad': 70000000,  # 70 millones COP por empleado
            'rotacion': 50
        },
        'servicios': {
            'endeudamiento': 0.45,
            'rentabilidad': 0.12,
            'productividad': 60000000,  # 60 millones COP por empleado
            'rotacion': 30
        },
        'otro': {
            'endeudamiento': 0.5,
            'rentabilidad': 0.1,
            'productividad': 60000000,  # 60 millones COP por empleado
            'rotacion': 45
        }
    }
    
    # Si el sector no está en los predefinidos, usar "otro"
    if sector.lower() not in limites:
        sector_analisis = 'otro'
    else:
        sector_analisis = sector.lower()
    
    # Evaluación por indicador
    evaluacion = {
        'endeudamiento': 'bueno' if ratio_endeudamiento <= limites[sector_analisis]['endeudamiento'] else 'alto',
        'rentabilidad': 'buena' if rentabilidad >= limites[sector_analisis]['rentabilidad'] else 'baja',
        'productividad': 'buena' if productividad >= limites[sector_analisis]['productividad'] else 'baja',
        'rotacion': 'buena' if rotacion_cartera <= limites[sector_analisis]['rotacion'] else 'alta'
    }
    
    # Evaluación general
    puntos_positivos = sum(1 for valor in evaluacion.values() if valor in ['bueno', 'buena'])
    
    if puntos_positivos >= 3:
        estado_general = "Excelente"
    elif puntos_positivos == 2:
        estado_general = "Bueno"
    elif puntos_positivos == 1:
        estado_general = "Regular"
    else:
        estado_general = "Crítico"
    
    # Preparar recomendaciones basadas en puntos débiles
    recomendaciones = []
    
    if evaluacion['endeudamiento'] == 'alto':
        recomendaciones.append("Reducir el nivel de endeudamiento, considerar reestructuración de deuda.")
    
    if evaluacion['rentabilidad'] == 'baja':
        recomendaciones.append("Mejorar la eficiencia operativa y revisar la estructura de costos.")
    
    if evaluacion['productividad'] == 'baja':
        recomendaciones.append("Optimizar procesos y/o implementar programas de capacitación para los empleados.")
    
    if evaluacion['rotacion'] == 'alta':
        recomendaciones.append("Mejorar las políticas de cobro y gestión de cartera.")
    
    # Tokenización para procesamiento NLP de ejemplo
    tokens_nombre = tokenizar_texto(nombre)
    lemas_sector = lematizar_texto(sector)
    pos_tags = pos_tagging(f"{nombre} es una empresa del sector {sector}")
    
    # Crear embedding para futuras comparaciones
    embedding = crear_embedding(f"Empresa {nombre} del sector {sector} con {empleados} empleados")
    
    # Resultados completos
    resultados = {
        'nombre': nombre,
        'sector': sector,
        'indicadores': {
            'ratio_endeudamiento': ratio_endeudamiento,
            'rentabilidad': rentabilidad,
            'productividad': productividad,
            'rotacion_cartera': rotacion_cartera
        },
        'evaluacion': evaluacion,
        'estado_general': estado_general,
        'recomendaciones': recomendaciones,
        'nlp_ejemplo': {
            'tokens': tokens_nombre,
            'lemas': lemas_sector,
            'pos_tags': pos_tags,
            'embedding_dim': len(embedding) if isinstance(embedding, np.ndarray) else 0
        }
    }
    
    return resultados

def generar_mensaje_resultado(resultados):
    """
    Genera un mensaje personalizado basado en los resultados del análisis.
    
    Args:
        resultados (dict): Resultados del análisis
        
    Returns:
        str: Mensaje personalizado
    """
    nombre = resultados['nombre']
    sector = resultados['sector']
    estado = resultados['estado_general']
    
    ind = resultados['indicadores']
    eval_ind = resultados['evaluacion']
    
    # Crear mensaje base
    mensaje = f"Análisis económico para {nombre} (Sector: {sector}):\n\n"
    
    # Agregar estado general
    mensaje += f"Estado económico general: {estado}\n\n"
    
    # Detallar indicadores
    mensaje += "Indicadores analizados:\n"
    mensaje += f"• Ratio de endeudamiento: {ind['ratio_endeudamiento']:.2f} ({eval_ind['endeudamiento']})\n"
    mensaje += f"• Rentabilidad sobre activos: {ind['rentabilidad']:.2%} ({eval_ind['rentabilidad']})\n"
    mensaje += f"• Productividad por empleado: ${ind['productividad']:,.0f} COP ({eval_ind['productividad']})\n"
    mensaje += f"• Rotación de cartera: {ind['rotacion_cartera']:.1f} días ({eval_ind['rotacion']})\n\n"
    
    # Agregar recomendaciones
    if resultados['recomendaciones']:
        mensaje += "Recomendaciones:\n"
        for i, rec in enumerate(resultados['recomendaciones'], 1):
            mensaje += f"{i}. {rec}\n"
    
    return mensaje