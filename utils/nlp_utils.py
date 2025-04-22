import re
import nltk
import spacy
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Descargar recursos necesarios de NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Cargar el modelo de spaCy para español
nlp = spacy.load('es_core_news_sm')

def tokenizar_texto(texto):
    """
    Tokeniza un texto en palabras individuales.
    
    Args:
        texto (str): Texto a tokenizar
        
    Returns:
        list: Lista de tokens
    """
    return word_tokenize(texto.lower())

def lematizar_texto(texto):
    """
    Lematiza un texto utilizando spaCy.
    
    Args:
        texto (str): Texto a lematizar
        
    Returns:
        list: Lista de lemas
    """
    doc = nlp(texto.lower())
    return [token.lemma_ for token in doc]

def pos_tagging(texto):
    """
    Realiza el etiquetado gramatical (POS tagging) de un texto.
    
    Args:
        texto (str): Texto para etiquetar
        
    Returns:
        list: Lista de tuplas (palabra, etiqueta)
    """
    doc = nlp(texto.lower())
    return [(token.text, token.pos_) for token in doc]

def crear_embedding(texto):
    """
    Crea un embedding simple para un texto utilizando CountVectorizer.
    
    Args:
        texto (str): Texto para crear embedding
        
    Returns:
        numpy.ndarray: Vector de embedding
    """
    vectorizer = CountVectorizer()
    return vectorizer.fit_transform([texto]).toarray()[0]

def similaridad_textos(texto1, texto2):
    """
    Calcula la similaridad coseno entre dos textos.
    
    Args:
        texto1 (str): Primer texto
        texto2 (str): Segundo texto
        
    Returns:
        float: Valor de similaridad
    """
    vectorizer = CountVectorizer().fit([texto1, texto2])
    vectores = vectorizer.transform([texto1, texto2])
    return cosine_similarity(vectores[0:1], vectores[1:2])[0][0]

def normalizar_texto(texto):
    """
    Normaliza un texto: elimina caracteres especiales, convierte a minúsculas.
    
    Args:
        texto (str): Texto a normalizar
        
    Returns:
        str: Texto normalizado
    """
    # Convertir a minúsculas
    texto = texto.lower()
    # Eliminar caracteres especiales
    texto = re.sub(r'[^\w\s]', '', texto)
    # Eliminar números
    texto = re.sub(r'\d+', '', texto)
    # Eliminar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def extraer_keywords(texto, num_palabras=5):
    """
    Extrae palabras clave de un texto basado en frecuencia y relevancia.
    
    Args:
        texto (str): Texto para extraer palabras clave
        num_palabras (int): Número de palabras clave a extraer
        
    Returns:
        list: Lista de palabras clave
    """
    doc = nlp(texto.lower())
    palabras = [token.text for token in doc if not token.is_stop and token.is_alpha]
    frecuencia = {}
    
    for palabra in palabras:
        if palabra in frecuencia:
            frecuencia[palabra] += 1
        else:
            frecuencia[palabra] = 1
    
    # Ordenar por frecuencia
    keywords = sorted(frecuencia.items(), key=lambda x: x[1], reverse=True)
    return [palabra for palabra, _ in keywords[:num_palabras]]