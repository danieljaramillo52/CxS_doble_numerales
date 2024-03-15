import pandas as pd
import pyarrow as pa
import sqlite3
import pyarrow.compute as pc
from typing import Type
from loguru import logger
from os import chdir
from datetime import datetime
from sqlalchemy import create_engine


def Base_cxs_estatico(
    Pyarrow_Functions: Type,
    DB_Functions: Type,
    Pandas_Functions: Type,
    config: dict,
    base_doble_numerales: pa.Table,
) -> pa.Table:
    """Encapsula el procedimiento para modificar la consulta CxS_estatico tabla: isnumo_cxs, y dejarla preparada para su actualización.
    Modula el proceso de consulta y modificación de la data_base para evitar aplicarlo directamente en el módulo main.py.
    """

    """1.) Definicion de constantes."""
    Ruta_base = config["ruta_base"]

    # Consultas de la Base de datos Santi Lopez (CxS estatico)
    nom_base = config["Insumos"]["db_cxs_dinamico"]["nom_base"]["Estatica"]
    nom_tabla = config["Insumos"]["db_cxs_dinamico"]["nom_tabla"]["Estatica"]

    # Moverse a la ruta dada.
    Ruta_completa = chdir(Ruta_base)

    # Conectar a la base de datos SQLite
    conn = sqlite3.connect(nom_base)
    cur = conn.cursor()
    # Paso 1: Eliminar registros específicos
    # Asegúrate de ajustar el nombre de la columna y el valor según tus necesidades
    meses_a_actualizar = config["Meses_a_actualizar"]

    meses_filtrados = "'" + "', '".join(meses_a_actualizar) + "'"
    logger.info("Eliminando registros a reemplazar... ")
    cur.execute(
        f"DELETE FROM {nom_tabla} WHERE Centro_Costo = '#/#' AND Mes IN ({meses_filtrados});"
    )

    # Guardar los cambios de la eliminación
    conn.commit()

    # Paso 2: Preparar la instrucción SQL para insertar los nuevos datos
    columnas = base_doble_numerales.schema.names
    placeholders = ", ".join(["?"] * len(columnas))
    sql = f"INSERT INTO {nom_tabla} ({', '.join(columnas)}) VALUES ({placeholders})"

    # Función para convertir los datos de PyArrow a tuplas, preparados para la inserción
    def arrow_to_tuples(table):
        Inicio = datetime.now()

        # Convertir la tabla de PyArrow a DataFrame de pandas
        df = table.to_pandas()

        # Iterar sobre las filas del DataFrame de pandas y convertirlas en tuplas
        for row in df.itertuples(index=False, name=None):
            yield row

        Fin = datetime.now()
        print(Fin - Inicio)

    logger.info("Insertando nuevos registros")
    # Insertar los nuevos datos en la tabla
    cur.executemany(sql, arrow_to_tuples(base_doble_numerales))

    # Guardar los cambios de la inserción y cerrar la conexión
    conn.commit()
    conn.close()
