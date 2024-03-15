import os
import yaml
import glob
import time
import pandas as pd
from loguru import logger
import sqlite3
from typing import Union, List, Any
from unidecode import unidecode


def Registro_tiempo(original_func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = original_func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(
            f"Tiempo de ejecución de {original_func.__name__}: {execution_time} segundos"
        )
        return result

    return wrapper


def Eliminar_acentos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina las tildes y caracteres acentuados de todas las columnas de un DataFrame.

    Args:
        df (pd.DataFrame): El DataFrame en el que se eliminarán los acentos.

    Returns:
        pd.DataFrame: El DataFrame modificado con los acentos eliminados.
    """
    try:
        logger.info("Iniciando proceso de eliminación de acentos...")
        for columna in df.columns:
            # Verifica si la columna es de tipo objeto (texto)
            if df[columna].dtype == "object":
                # Aplica unidecode a cada valor de la columna y asigna los resultados de nuevo a la columna
                df[columna] = df[columna].apply(
                    lambda x: unidecode(x) if pd.notna(x) else x
                )
        logger.success("Proceso de eliminación de acentos completado con éxito.")
        return df
    except Exception as e:
        # Manejo de excepciones: registra un mensaje crítico en lugar de imprimir el error
        logger.critical(f"Error en la función eliminar_acentos: {str(e)}")
        return df


def Procesar_configuracion(nom_archivo_configuracion: str) -> dict:
    """Lee un archivo YAML de configuración para un proyecto.

    Args:
        nom_archivo_configuracion (str): Nombre del archivo YAML que contiene
            la configuración del proyecto.

    Returns:
        dict: Un diccionario con la información de configuración leída del archivo YAML.
    """
    try:
        with open(nom_archivo_configuracion, "r", encoding="utf-8") as archivo:
            configuracion_yaml = yaml.safe_load(archivo)
        logger.success("Proceso de obtención de configuración satisfactorio")
    except Exception as e:
        logger.critical(f"Proceso de lectura de configuración fallido {e}")
        raise e

    return configuracion_yaml


def Crear_diccionario_desde_dataframe(
    df: pd.DataFrame, col_clave: str, col_valor: str
) -> dict:
    """
    Crea un diccionario a partir de un DataFrame utilizando dos columnas especificadas.

    Args:
        df (pd.DataFrame): El DataFrame de entrada.
        col_clave (str): El nombre de la columna que se utilizará como clave en el diccionario.
        col_valor (str): El nombre de la columna que se utilizará como valor en el diccionario.

    Returns:
        dict: Un diccionario creado a partir de las columnas especificadas.
    """
    try:
        # Verificar si las columnas existen en el DataFrame
        if col_clave not in df.columns or col_valor not in df.columns:
            raise ValueError("Las columnas especificadas no existen en el DataFrame.")

        # Crear el diccionario a partir de las columnas especificadas
        resultado_dict = df.set_index(col_clave)[col_valor].to_dict()

        return resultado_dict

    except ValueError as ve:
        # Registrar un mensaje crítico si hay un error
        logger.critical(f"Error: {ve}")
        raise ve


def agregar_al_final_dict(diccionario, texto):
    """
    Agrega texto al final de todas las claves de un diccionario.

    Args:
        diccionario (dict): El diccionario al que se agregarán los textos.
        texto (str): El texto que se agregará al final de cada clave.

    Returns:
        dict: El diccionario modificado con el texto agregado al final de cada clave.
    """
    diccionario_modificado = {}
    for clave, valor in diccionario.items():
        nueva_clave = clave + texto
        diccionario_modificado[nueva_clave] = valor
    return diccionario_modificado


@Registro_tiempo
def Lectura_insumos_excel(
    path: str, nom_insumo: str, nom_hoja: str, cols: Union[int, list]
) -> pd.DataFrame:
    """Lee archivos de Excel con cualquier extensión y carga los datos de una hoja específica.

    Lee el archivo especificado por `nom_insumo` ubicado en la ruta `path` y carga los datos de la hoja
    especificada por `nom_Hoja`. Selecciona solo las columnas indicadas por `cols`.

    Args:
        path (str): Ruta de la carpeta donde se encuentra el archivo.
        nom_insumo (str): Nombre del archivo con extensión.
        nom_Hoja (str): Nombre de la hoja del archivo que se quiere leer.
        cols (int): Número de columnas que se desean cargar.

    Returns:
        pd.DataFrame: Dataframe que contiene los datos leídos del archivo Excel.

    Raises:
        Exception: Si ocurre un error durante el proceso de lectura del archivo.
    """
    base_leida = None

    try:
        logger.info(f"Inicio lectura {nom_insumo} Hoja {nom_hoja}")
        base_leida = pd.read_excel(
            path + nom_insumo,
            sheet_name=nom_hoja,
            usecols=list(range(0, cols)),
            dtype=str,
            engine="openpyxl",
        )

        logger.success(
            f"Lectura de {nom_insumo} Hoja: {nom_hoja} realizada con éxito"
        )  # Se registrará correctamente con el método "success"
    except Exception as e:
        logger.error(f"Proceso de lectura fallido: {e}")
        raise Exception

    return base_leida


class ConsultaDB:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None

    def conectar(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
        except sqlite3.Error as e:
            logger.critical(f"Error al conectar a la base de datos: {e}")

    def desconectar(self):
        if self.conn:
            self.conn.close()

    @Registro_tiempo
    def consultar_tabla(self, Consulta, nombre_tabla):
        try:
            if not self.conn:
                self.conectar()

            # Ejecutar consulta.
            cursor = self.conn.cursor()

            cursor.execute(Consulta)
            logger.info(f"Ejecutando consulta en la tabla: {nombre_tabla}")
            resultados = cursor.fetchall()

            return resultados
        except sqlite3.Error as e:
            logger.critical(f"Error al consultar la tabla: {e}")
        finally:
            self.desconectar()


# Construir una consulta de una base de datos.
def construir_consulta_estatica_dinamica(meses: list, numeros_ceco: list, nom_tabla: str):
    meses_selecionados = "', '".join(meses)

    numeros_ceco_seleccionados = "', '".join(numeros_ceco)

    Consulta = f"SELECT * FROM {nom_tabla} WHERE (MES IN ('{meses_selecionados}') AND NUMERO_CECO IN ('{numeros_ceco_seleccionados}'));"

    return Consulta
