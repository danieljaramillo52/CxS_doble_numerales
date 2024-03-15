# Transformaciones
import pyarrow as pa
import pyarrow.types as pt
import pyarrow.compute as pc
import pandas as pd
from loguru import logger
from typing import Union, List, Any
from General_Functions import Registro_tiempo
from memory_profiler import profile


class TableColumnConcatenator:
    @staticmethod
    def select_columns(table, column_names):
        try:
            selected_columns = [table[col] for col in column_names]
        except KeyError as e:
            logger.error(f"Error al seleccionar columnas: {e}")
            raise ValueError("Una o más columnas especificadas no existen en la tabla.")
        return selected_columns

    @staticmethod
    def convert_to_strings(columns):
        try:
            cols_convertidas = [pc.cast(col, pa.string()) for col in columns]
        except (
            pa.ArrowInvalid,
            pa.ArrowNotImplementedError,
            pa.ArrowInvalidValueError,
        ) as e:
            logger.error(f"Error al convertir columnas a tipo string: {e}")
            raise TypeError(
                "No se pudo convertir una o más columnas a tipo de datos string."
            )
        return cols_convertidas

    @staticmethod
    def concatenate_strings(columns):
        try:
            concatenated_column = pc.binary_join_element_wise(*columns, "")
        except ValueError as e:
            logger.error(f"Error al concatenar columnas: {e}")
            raise ValueError(
                "Las columnas no tienen la misma longitud y no se pueden concatenar."
            )
        return concatenated_column

    @staticmethod
    def concatenar_cols_seleccionadas(table: pa.Table, column_names: list):
        try:
            selected_cols = TableColumnConcatenator.select_columns(table, column_names)
            string_columns = TableColumnConcatenator.convert_to_strings(selected_cols)
            concatenated_column = TableColumnConcatenator.concatenate_strings(
                string_columns
            )
        except Exception as e:
            logger.error(f"Error en la función 'concatenar_cols_seleccionadas': {e}")
            raise
        return concatenated_column


@Registro_tiempo
def Transform_dfs_pandas_a_pyarrow(df: pd.DataFrame) -> pa.table:
    """Funcion que toma un dataframe de pandas y lo transforma en una tabla de pyarrow
    Args:
      df (pd.DataFrame): Dataframe de pandas a ser transformado
    Returns:
      pa.table: Tabla bidimensional de datos de PyArrow
    """
    try:
        # Verificar si la entrada es un DataFrame de pandas
        if not isinstance(df, pd.DataFrame):
            raise TypeError("El argumento 'df' debe ser un DataFrame de pandas.")
        else:
            table = pa.Table.from_pandas(df)
    except Exception as e:
        raise ValueError(f"Error al convertir el DataFrame a PyArrow: {e}") from e

    return table


@Registro_tiempo
def Transform_pyarrow_a_pandas(table: pa.Table) -> pd.DataFrame:
    """
    Función que toma una tabla de PyArrow y la transforma en un DataFrame de Pandas.

    Args:
      table (pa.Table): Tabla de PyArrow a ser transformada.

    Returns:
      pd.DataFrame: DataFrame de Pandas resultante de la transformación.
    """
    try:
        # Verificar si la entrada es una tabla de PyArrow
        if not isinstance(table, pa.Table):
            raise TypeError("El argumento 'table' debe ser una tabla de PyArrow.")
        else:
            df = table.to_pandas()
    except Exception as e:
        raise ValueError(f"Error al convertir la tabla PyArrow a DataFrame: {e}") from e

    return df


@Registro_tiempo
def Eliminar_primeros_n_caracteres_pandas(
    df: pd.DataFrame, columna: str, n: int
) -> pd.DataFrame:
    """
    Elimina los primeros n caracteres de cada fila en la columna especificada del DataFrame.

    Parámetros:
    df (pd.DataFrame): DataFrame a modificar.
    columna (str): Nombre de la columna en la que se realizará la operación.
    n (int): Número de caracteres a eliminar de cada fila en la columna.

    Retorna:
    pd.DataFrame: DataFrame con la columna modificada.
    """
    try:
        # Verificar si df es un DataFrame de pandas y columna es una columna válida en df
        if not isinstance(df, pd.DataFrame):
            raise TypeError("El argumento 'df' debe ser un DataFrame de pandas.")
        if columna not in df.columns:
            raise ValueError(f"La columna '{columna}' no existe en el DataFrame.")

        # Modificar la columna en el DataFrame
        df[columna] = df[columna].apply(
            lambda x: x[n:] if isinstance(x, str) and len(x) > n else x
        )

        # Registrar el proceso
        logger.info(
            f"Se eliminaron los primeros {n} caracteres de la columna '{columna}'."
        )

        return df

    except Exception as e:
        # Registrar el error y retornar None en caso de fallo
        logger.critical(
            f"Error al eliminar los primeros {n} caracteres de la columna '{columna}': {str(e)}"
        )
        return None


@Registro_tiempo
def concatenar_columnas_pd(
    dataframe: pd.DataFrame, cols_elegidas: List[str], nueva_columna: str
) -> Union[pd.DataFrame, None]:
    """
    Concatena las columnas especificadas y agrega el resultado como una nueva columna al DataFrame.

    Parámetros:
    dataframe (pd.DataFrame): DataFrame del cual se concatenarán las columnas.
    cols_elegidas (list): Lista de nombres de las columnas a concatenar.
    nueva_columna (str): Nombre de la nueva columna que contendrá el resultado de la concatenación.

    Retorna:
    pd.DataFrame: DataFrame con la nueva columna agregada.
    """
    try:
        # Verificar si dataframe es un DataFrame de pandas
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("El argumento 'dataframe' debe ser un DataFrame de pandas.")

        # Verificar si las columnas especificadas existen en el DataFrame
        for col in cols_elegidas:
            if col not in dataframe.columns:
                raise KeyError(f"La columna '{col}' no existe en el DataFrame.")

        # Concatenar las columnas especificadas y agregar el resultado como una nueva columna
        dataframe[nueva_columna] = (
            dataframe[cols_elegidas].fillna("").agg("".join, axis=1)
        )

        # Registrar el proceso
        logger.info(
            f"Columnas '{', '.join(cols_elegidas)}' concatenadas y almacenadas en '{nueva_columna}'."
        )

        return dataframe

    except Exception as e:
        logger.critical(f"Error inesperado al concatenar columnas: {str(e)}")
        return None


class PyArrowColumnTransformer:
    @Registro_tiempo
    @staticmethod
    def remove_first_n_characters(
        table: pa.Table, column_name: str, n: int
    ) -> pa.Table:
        """
        Elimina los primeros 'n' caracteres de cada cadena en la columna especificada de una tabla PyArrow.

        Parameters:
        table (pa.Table): La tabla PyArrow a modificar.
        column_name (str): El nombre de la columna a modificar.
        n (int): Número de caracteres a eliminar desde el inicio de cada cadena.

        Returns:
        pa.Table: Una nueva tabla PyArrow con la columna modificada.

        Example:
        >>> table = pa.Table.from_pydict({'Nombre': ['Alice', 'Bob', 'Charlie']})
        >>> modified_table = PyArrowTableModifier.remove_first_n_characters(table, 'Nombre', 2)
        >>> modified_table.column('Nombre').to_pylist()
        ['ice', 'b', 'arlie']
        """
        try:
            pattern = "^.{" + str(n) + "}"
            modified_column = pc.replace_substring_regex(
                table[column_name], pattern=pattern, replacement=""
            )
            return table.set_column(
                table.schema.get_field_index(column_name), column_name, modified_column
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error al eliminar los primeros {n} caracteres: {e}")
        except pa.lib.ArrowInvalid as e:
            logger.error(f"Error de PyArrow: {e}")

    @Registro_tiempo
    @staticmethod
    def remove_last_n_characters(table: pa.Table, column_name: str, n: int) -> pa.Table:
        """
        Elimina los últimos 'n' caracteres de cada cadena en la columna especificada de una tabla PyArrow.

        Parameters:
        table (pa.Table): La tabla PyArrow a modificar.
        column_name (str): El nombre de la columna a modificar.
        n (int): Número de caracteres a eliminar desde el final de cada cadena.

        Returns:
        pa.Table: Una nueva tabla PyArrow con la columna modificada.

        Example:
        >>> table = pa.Table.from_pydict({'Nombre': ['Alice', 'Bob', 'Charlie']})
        >>> modified_table = PyArrowTableModifier.remove_last_n_characters(table, 'Nombre', 2)
        >>> modified_table.column('Nombre').to_pylist()
        ['Al', 'B', 'Charl']
        """
        try:
            pattern = ".{" + str(n) + "}$"
            modified_column = pc.replace_substring_regex(
                table[column_name], pattern=pattern, replacement=""
            )
            return table.set_column(
                table.schema.get_field_index(column_name), column_name, modified_column
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error al eliminar los últimos {n} caracteres: {e}")
        except pa.lib.ArrowInvalid as e:
            logger.error(f"Error de PyArrow: {e}")

    @Registro_tiempo
    @staticmethod
    def remove_digits(table: pa.Table, column_name: str) -> pa.Table:
        """
        Elimina todos los dígitos numéricos de las cadenas en la columna especificada de una tabla PyArrow.

        Parameters:
        table (pa.Table): La tabla PyArrow a modificar.
        column_name (str): El nombre de la columna a modificar.

        Returns:
        pa.Table: Una nueva tabla PyArrow con la columna modificada.

        Example:
        >>> table = pa.Table.from_pydict({'ID': ['User1', 'User2', 'User3']})
        >>> modified_table = PyArrowTableModifier.remove_digits(table, 'ID')
        >>> modified_table.column('ID').to_pylist()
        ['User', 'User', 'User']
        """
        pattern = "\d+"
        modified_column = pc.replace_substring_regex(
            table[column_name], pattern=pattern, replacement=""
        )
        return table.set_column(
            table.schema.get_field_index(column_name), column_name, modified_column
        )

    @Registro_tiempo
    @staticmethod
    def remove_non_alpha_characters(table: pa.Table, column_name: str) -> pa.Table:
        """
        Elimina todos los caracteres no alfabéticos de las cadenas en la columna especificada de una tabla PyArrow.

        Parameters:
        table (pa.Table): La tabla PyArrow a modificar.
        column_name (str): El nombre de la columna a modificar.

        Returns:
        pa.Table: Una nueva tabla PyArrow con la columna modificada.

        Example:
        >>> table = pa.Table.from_pydict({'Texto': ['Hola!123', 'Mundo?456', 'Python#789']})
        >>> modified_table = PyArrowTableModifier.remove_non_alpha_characters(table, 'Texto')
        >>> modified_table.column('Texto').to_pylist()
        ['Hola', 'Mundo', 'Python']
        """
        try:
            pattern = "[^a-zA-Z]"
            modified_column = pc.replace_substring_regex(
                table[column_name], pattern=pattern, replacement=""
            )
            return table.set_column(
                table.schema.get_field_index(column_name), column_name, modified_column
            )
        except TypeError as e:
            logger.error(f"Error de tipo de dato en remove_non_alpha_characters: {e}")
        except pa.lib.ArrowInvalid as e:
            logger.error(f"Error de PyArrow: {e}")

    @Registro_tiempo
    def reemplazar_valores_con_diccionario_pa(
        tabla: pa.Table, nombre_columna: str, diccionario_de_mapeo: dict
    ) -> pa.Table:
        """
        Reemplaza valores en una columna específica de una tabla Arrow utilizando un diccionario de mapeo.

        Args:
            tabla (pa.Table): La tabla Arrow de entrada.
            nombre_columna (str): El nombre de la columna que se va a reemplazar.
            diccionario_de_mapeo (dict): Un diccionario que mapea valores antiguos a nuevos valores.

        Returns:
            pa.Table: Una nueva tabla Arrow con los valores de la columna especificada reemplazados según el diccionario_de_mapeo.

        Raises:
            ValueError: Si nombre_columna no existe en el esquema de la tabla.
            TypeError: Si diccionario_de_mapeo no es un diccionario o si tabla no es una tabla Arrow.

        Ejemplo:
            tabla = pa.table({'A': [1, 2, 3, 4, 5]})
            mapeo = {2: 10, 4: 20}
            tabla_resultante = reemplazar_valores_con_diccionario(tabla, 'A', mapeo)
        """
        try:
            # Verificar si la columna existe en el esquema de la tabla
            if nombre_columna not in tabla.column_names:
                raise ValueError(
                    f"Columna '{nombre_columna}' no encontrada en el esquema de la tabla."
                )

            keys_array = pa.array(list(diccionario_de_mapeo.keys()))
            values_array = pa.array(list(diccionario_de_mapeo.values()))

            # Crear una máscara booleana
            mascara = pc.is_in(tabla[nombre_columna], value_set=keys_array)

            # Crear un array de valores reemplazados
            valores_reemplazados = pc.take(
                values_array, pc.index_in(tabla[nombre_columna], value_set=keys_array)
            )

            # Usar if_else para elegir entre el valor original y el valor reemplazado
            columna_final = pc.if_else(
                mascara, valores_reemplazados, tabla[nombre_columna]
            )

            # Reemplazar la columna en la tabla
            return tabla.set_column(
                tabla.schema.get_field_index(nombre_columna),
                nombre_columna,
                columna_final,
            )

        except ValueError as ve:
            logger.error(ve)
            raise ve
        except TypeError as te:
            logger.error(te)
            raise te

    @Registro_tiempo
    @staticmethod
    def tuples_to_table(tuples_list, columnas):
        logger.info("Construyendo tabla Pyarrow por bloques para procesar...")
        # Dividir los datos en bloques más manejables
        block_size = 100000  # Ajusta este tamaño según la capacidad de tu sistema
        blocks = [
            tuples_list[i : i + block_size]
            for i in range(0, len(tuples_list), block_size)
        ]

        tables = []
        for block in blocks:
            # Convertir el bloque de tuplas a formato columnar
            columns = list(zip(*block))

            # Crear arrays de PyArrow para cada columna
            arrays = [pa.array(col) for col in columns]

            # Crear un esquema para la tabla, si es necesario. Asumiendo que conoces los tipos  de datos
            schema = pa.schema([(name, pa.string()) for name in columnas])
            # O simplemente crea la tabla sin un esquema predefinido
            table = pa.Table.from_arrays(arrays, schema=schema)

            tables.append(table)

        # Concatenar todas las tablas pequeñas en una tabla grande
        logger.info("Unificando los bloques de la tabla...")
        final_table = pa.concat_tables(tables)

        return final_table

    @Registro_tiempo
    @staticmethod
    def cambiar_tipo_dato_columnas_pa(
        tabla: pa.Table, columnas: list, nuevo_tipo
    ) -> pa.Table:
        """
        Cambia el tipo de dato de múltiples columnas en una tabla PyArrow.

        Parameters:
        tabla (pa.Table): La tabla PyArrow original.
        columnas (list): Lista de nombres de columnas cuyos tipos se van a cambiar.
        nuevo_tipo: El nuevo tipo de dato al que se van a cambiar las columnas.

        Returns:
        pa.Table: Una nueva tabla PyArrow con los tipos de columna actualizados.

        Example:
        >>> data = {'columna1': [1, 2, 3], 'columna2': [4, 5, 6], 'columna3': ['a', 'b', 'c']}
        >>> tabla_original = pa.Table.from_pydict(data)
        >>> tabla_modificada = cambiar_tipo_columnas(tabla_original, ['columna1', 'columna2'], pa.float64())
        >>> print(tabla_modificada.schema)
        """
        tabla_modificada = tabla

        for columna in columnas:
            if columna in tabla_modificada.column_names:
                logger.info(
                    f"Cambiando el tipo de la columna '{columna}' a {nuevo_tipo}."
                )
                columna_casteada = pc.cast(tabla_modificada[columna], nuevo_tipo)
                tabla_modificada = tabla_modificada.set_column(
                    tabla_modificada.schema.get_field_index(columna),
                    columna,
                    columna_casteada,
                )
            else:
                logger.error(f"La columna '{columna}' no se encuentra en la tabla.")
                raise KeyError(f"La columna '{columna}' no se encuentra en la tabla.")

        logger.success("Cambio de tipo de columna(s) completado con éxito.")
        return tabla_modificada

    @staticmethod
    def columns_to_dict_pa(
        table: pa.Table, key_column_name: str, value_column_name: str
    ):
        """
        Convierte dos columnas de una tabla PyArrow directamente en un diccionario,
        con controles de errores utilizando try-except para verificar la existencia de las columnas
        y el tipo de los nombres de las columnas.

        Args:
            table (pa.Table): La tabla de PyArrow que contiene las columnas.

            key_column_name (str): El nombre de la columna que se utilizará como clave del diccionario.

            value_column_name (str): El nombre de la columna que se utilizará como valor del diccionario.

        Returns:
            dict: Un diccionario construido directamente a partir de las columnas especificadas.

        throw:
        - ValueError: Si los nombres de las columnas no son strings o las columnas no existen en la tabla.
        """
        try:
            # Verifica que los nombres de las columnas sean strings
            if not isinstance(key_column_name, str) or not isinstance(
                value_column_name, str
            ):
                raise TypeError("Los nombres de las columnas deben ser strings.")

            # Intenta acceder a las columnas para verificar su existencia
            key_array = table.column(key_column_name)
            value_array = table.column(value_column_name)

        except KeyError:
            # Lanzado por table.column si el nombre de la columna no existe
            raise ValueError(
                f"Una o ambas columnas especificadas ('{key_column_name}' o '{value_column_name}') no existen en la tabla."
            )
        except TypeError as e:
            # Captura errores de tipo, como pasar un nombre de columna no string
            raise ValueError(str(e))

        # Construye el diccionario directamente si no hay errores
        result_dict = {
            key.as_py(): value.as_py() for key, value in zip(key_array, value_array)
        }

        return result_dict

    @Registro_tiempo
    @staticmethod
    def seleccionar_columnas_pa(tabla: pa.Table, columnas: list) -> pa.Table:
        """Selecciona columnas específicas de una tabla PyArrow.

        Esta función toma una tabla PyArrow y una lista de nombres de columnas,
        y devuelve una nueva tabla que contiene solo las columnas especificadas.

        Parameters:
        tabla (pa.Table): La tabla PyArrow de la que seleccionar columnas.
        columnas (list): Lista de nombres de columnas a seleccionar.

        Returns:
        pa.Table: Una nueva tabla PyArrow que contiene solo las columnas seleccionadas.

        Raises:
        KeyError: Si alguna de las columnas especificadas no existe en la tabla.

        Example:
        >>> data = {'columna1': [1, 2], 'columna2': ['a', 'b']}
        >>> tabla_original = pa.Table.from_pydict(data)
        >>> tabla_seleccionada = seleccionar_columnas(tabla_original, ['columna1'])
        >>> print(tabla_seleccionada)
        """
        try:
            columnas_existentes = set(tabla.column_names)
            columnas_solicitadas = set(columnas)

            if not columnas_solicitadas.issubset(columnas_existentes):
                columnas_faltantes = columnas_solicitadas - columnas_existentes
                raise KeyError(
                    f"Las columnas {columnas_faltantes} no existen en la tabla. No puede ser seleccionada."
                )

            return tabla.select(columnas)

        except KeyError as e:
            logger.error(f"Error al seleccionar columnas: {e}")
            raise

    @staticmethod
    def Eliminar_columnas_pa(
        tabla: pa.Table, columnas_a_eliminar: str | list
    ) -> pa.Table:
        """
        Elimina una o varias columnas de una tabla PyArrow.

        Args:
            tabla (pa.Table): La tabla de PyArrow de la cual eliminar las columnas.
            columnas_a_eliminar (Union[str, List[str]]): Nombre(s) de la(s) columna(s) a eliminar. Puede ser un string único o una lista de strings.

        Returns:
            pa.Table: Una nueva tabla de PyArrow sin las columnas especificadas.
        """
        # Convertir el nombre de la columna a eliminar en una lista si es un string único
        if isinstance(columnas_a_eliminar, str):
            columnas_a_eliminar = [columnas_a_eliminar]

        # Comprobar que todas las columnas a eliminar existen en la tabla
        columnas_existentes = tabla.column_names
        for columna in columnas_a_eliminar:
            if columna not in columnas_existentes:
                raise ValueError(f"La columna '{columna}' no existe en la tabla.")

        # Eliminar las columnas especificadas y retornar la nueva tabla
        tabla_modificada = tabla.drop(columnas_a_eliminar)
        return tabla_modificada

    @staticmethod
    def unique_values_colum_pa(tabla: pa.Table, columna: str) -> pa.Table:
        """
        Devuelve los valores únicos de una columna de PyArrow.

        Parámetros:
        - column (pa.Array o pa.ChunkedArray): La columna de PyArrow de la cual obtener los     valores únicos.

        Retorna:
        - pa.Array: Un array de PyArrow con los valores únicos de la columna.
        """
        # Usamos la función unique de pyarrow.compute
        unique_values = pc.unique(tabla[columna])
        return unique_values

    @Registro_tiempo
    @staticmethod
    def Concatenar_tablas_pa(tablas: List[pa.Table]) -> pa.Table:
        """
        Concatena verticalmente las tablas de PyArrow en la lista.

        Args:
            tablas (list): Una lista de tablas de PyArrow.

        Returns:
            pa.Table: La tabla resultante después de la concatenación.

        Raises:
            TypeError: Si algún elemento de la lista no es una tabla de PyArrow.

        """
        try:
            # Verificar que cada elemento sea una tabla de PyArrow
            for tabla in tablas:
                if not isinstance(tabla, pa.Table):
                    raise TypeError("Cada elemento debe ser una tabla de PyArrow.")

            # Concatenar verticalmente las tablas
            tabla_concatenada = pa.concat_tables(tablas)

            # Registrar mensaje informativo
            logger.info("Tablas concatenadas exitosamente.")

            return tabla_concatenada

        except TypeError as e:
            # Registrar mensaje de error crítico
            logger.critical(f"Error al concatenar tablas: {e}")
            raise

    class PyArrowTablefilter:

        def __init__(self, tabla):
            if not isinstance(tabla, pa.Table):
                raise ValueError(
                    "El argumento 'tabla' debe ser una instancia de pa.Table."
                )
            self.tabla = tabla

        def Mascara_is_in_pa(self, columna: str, valores: list):
            """
            Crea una máscara booleana basada en si los valores de una columna específica están  contenidos en una lista dada.

            Esta función genera una máscara booleana para filtrar las filas de una tabla PyArrow,   donde cada elemento de la máscara
            es True si el valor correspondiente en la columna especificada está presente en la  lista de 'valores' proporcionada,
            y False en caso contrario. Esta operación es útil para seleccionar subconjuntos de  datos basados en múltiples criterios.

            Args:
                Columna (str): Nombre de la columna en la tabla PyArrow sobre la cual se desea aplicar el filtro.

                Valores (lsit): Lista de valores que se buscan en la columna especificada. Cada    elemento en esta lista se compara con los valores de la columna, y si hay una coincidencia, la máscara    en esa posición se establece en True.

            Return:
                Un pyarrow.Array de tipo booleano que representa la máscara de filtrado.   Puede usarse para filtrar la tabla original y seleccionar solo las filas que cumplen con el criterio  especificado.
            """

            if not isinstance(valores, list):
                raise ValueError("El argumento 'valores' debe ser una lista.")
            try:
                mask = pc.is_in(self.tabla[columna], value_set=pa.array(valores))
                return mask
            except KeyError:
                raise ValueError(f"La columna '{columna}' no existe en la tabla.")
            except Exception as e:
                raise RuntimeError(f"Error al crear la máscara: {e}")

        @staticmethod
        def Invertir_mascara_pa(mask):
            """
            Invierte una máscara booleana dada.

            Esta función toma una máscara booleana como entrada y devuelve una nueva máscara booleana donde todos los valores True se convierten en False, y viceversa. Esta operación es útil para cambiar el criterio de filtrado de los datos en operaciones que involucran tablas
            o arrays de PyArrow.

            Args:
                mask (pyarrow.Array de tipo booleano). La máscara booleana a ser invertida.

            Return:
                inverted_mask (pyarrow.Array de tipo booleano). La máscara booleana invertida.
            """
            # Invertir la mascara.
            if not isinstance(mask, pa.lib.ChunkedArray):
                raise ValueError("El argumento 'mask' debe ser de tipo pa.Array.")
            try:
                inverted_mask = pc.invert(mask)
                return inverted_mask
            except Exception as e:
                raise RuntimeError(f"Error al invertir la máscara: {e}")

        def mask_equivalente_pa(self, columna, valor):
            """
            Crea una máscara booleana que indica si los valores en una columna específica no son iguales a un valor dado.

            Esta función utiliza la operación de comparación 'equal' de PyArrow para comparar   cada elemento en la columna especificada
            con el valor proporcionado. Retorna una máscara booleana donde cada posición    corresponde a la comparación de un elemento
            de la columna, siendo True si el elemento es igual al valor y False en caso  contrario.

            Args:
                columna (str): Nombre de la columna en la tabla PyArrow sobre la cual se realizará la comparación.

                valor (Union[int, str]) : Valor con el que se compararán los elementos de la columna.

            Return:
                mask (pa.Array) Máscara booleana de PyArrow que representa el resultado de la comparación.
            """
            try:
                mask = pc.equal(self.tabla[columna], valor)
                return mask
            except KeyError:
                raise ValueError(f"La columna '{columna}' no existe en la tabla.")
            except Exception as e:
                raise RuntimeError(f"Error al crear la máscara de equivalencia: {e}")

        def mask_no_equivalente_pa(self, columna: str, valor: str) -> pa.Array:
            """
            Crea una máscara booleana que indica si los valores en una columna específica no son iguales a un valor dado.

            Esta función utiliza la operación de comparación 'not_equal' de PyArrow para comparar   cada elemento en la columna especificada
            con el valor proporcionado. Retorna una máscara booleana donde cada posición    corresponde a la comparación de un elemento
            de la columna, siendo True si el elemento no es igual al valor y False en caso  contrario.

            Args:
                columna (str): Nombre de la columna en la tabla PyArrow sobre la cual se realizará la comparación.

                valor (str) : Valor con el que se compararán los elementos de la columna.

            Return:
                mask (pa.Array) Máscara booleana de PyArrow que representa el resultado de la comparación.
            """
            try:
                mask = pc.not_equal(self.tabla[columna], valor)
                return mask
            except KeyError:
                raise ValueError(f"La columna '{columna}' no existe en la tabla.")
            except Exception as e:
                raise RuntimeError(f"Error al crear la máscara de no equivalencia: {e}")

        def filter_non_null_rows(self, column_name: str) -> pa.Table:
            """
            Filtra las filas de una tabla de PyArrow basándose en los valores no nulos de una columna específica.

            Parámetros:
            - column_name (str): El nombre de la columna a evaluar para el filtrado.

            Retorna:
            - mask_non_null (pa.Array): Una mascara para tabla de PyArrow que contiene solo filas con valores no nulos en la columna especificada.
            """
            # Crear un filtro de booleanos que sea True para filas no nulas en la columna especificada
            mask_non_null = pc.is_not_null(self.column(column_name))

            return mask_non_null

        def filter_rows_starting_with(self, column: str, start_string: str) -> pa.Table:
            """
            Filtra las filas de una tabla de PyArrow basándose en si los valores de una columna específica
            comienzan con una cadena de caracteres determinada.

            Args:
                - column (str): El nombre de la columna a evaluar para el filtrado.
                - start_string (str): La cadena de caracteres con la que deben comenzar los valores de la columna.

            Returns:
                - mask_start_with_condition (pa.Array): Una mascara de filtrado que contiene los valores que cumple con la condición
            """

            # Crear una expresión que evalúe si los valores de la columna comienzan con la cadena especificada

            mask_start_with_condition = pa.compute.starts_with(
                self.column(column), start_string
            )

            return mask_start_with_condition

        @staticmethod
        def Combinar_mask_and_pa(*masks) -> pa.Array:
            """
            Combina múltiples condiciones/máscaras booleanas utilizando el operador lógico AND.

            Args:
                mask (pa.Array()) :Máscaras booleanas individuales como argumentos variables.

            Return:
                condicion_combinada (pa.Array()) : Una máscara booleana combinada que es la operación AND de todas las máscaras de entrada.
            """
            if not masks:
                raise ValueError("Se debe proporcionar al menos una máscara.")
            try:
                condicion_combinada = masks[0]
                for mascara in masks[1:]:
                    condicion_combinada = pc.and_(condicion_combinada, mascara)
                return condicion_combinada
            except Exception as e:
                raise RuntimeError(f"Error al combinar máscaras con AND: {e}")

        def Filtrar_tabla_pa(self, mask):
            """Filtra la tabla de acuerdo a una Mascara que actua como condicion de filtrado
            Args:
                tabla (pa.Table): tabla de pyarrow a filtrar.
                mask : condición de filtrado

            Returns:
                tabla_filtrada (pa.Table)  Tabla de pyarrow a la que se le aplicó el filtro
                correspondiente.
            """
            if not isinstance(mask, pa.lib.ChunkedArray):
                raise ValueError("El argumento 'mask' debe ser de tipo pa.Array.")
            try:
                tabla_filtrada = self.tabla.filter(mask)
                return tabla_filtrada
            except Exception as e:
                raise RuntimeError(f"Error al filtrar la tabla: {e}")

    class OpAritmeticasPa:
        @Registro_tiempo
        @staticmethod
        def sumar_columnas_pa(tabla: pa.Table, columnas_a_sumar: list) -> pa.Array:
            """
            Suma las columnas especificadas de una tabla PyArrow.

            Parameters:
            tabla (pa.Table): La tabla PyArrow a modificar.
            columnas_a_sumar (list of str): Lista de nombres de las columnas que se van a sumar.

            Returns:
            pa.Array: Un array con la suma de las columnas especificadas.

            Raises:
            KeyError: Si alguna de las columnas especificadas no existe en la tabla.
            TypeError: Si alguna de las columnas especificadas no es de tipo numérico.
            """
            try:
                suma = None
                for col in columnas_a_sumar:
                    if suma is None:
                        suma = tabla[col]
                    else:
                        suma = pc.add(suma, tabla[col])

                return suma
            except Exception as e:
                logger.exception("Error al sumar las columnas: {}", e)
                raise

        @Registro_tiempo
        @staticmethod
        def restar_columnas_pa(
            tabla: pa.Table, columna_minuendo: str, columna_sustraendo: str
        ) -> pa.Array:
            """
            Resta los valores de las filas de dos columnas especificadas de una tabla PyArrow.

            Parameters:
            tabla (pa.Table): La tabla PyArrow a modificar.
            columna_minuendo (str): Nombre de la columna de la cual se restarán los valores.
            columna_sustraendo (str): Nombre de la columna cuyos valores se restarán de la columna minuendo.

            Returns:
            pa.Array: Un array con la resta de las columnas especificadas.

            Raises:
            KeyError: Si alguna de las columnas especificadas no existe en la tabla.
            TypeError: Si alguna de las columnas especificadas no es de tipo numérico.
            """
            try:
                if (
                    columna_minuendo not in tabla.column_names
                    or columna_sustraendo not in tabla.column_names
                ):
                    raise KeyError(
                        "Una de las columnas especificadas no existe en la tabla."
                    )

                col_minuendo = tabla[columna_minuendo]
                col_sustraendo = tabla[columna_sustraendo]

                if not (
                    pa.types.is_integer(col_minuendo.type)
                    and pa.types.is_integer(col_sustraendo.type)
                    or (
                        pa.types.is_floating(col_minuendo.type)
                        and pa.types.is_floating(col_sustraendo.type)
                    )
                ):
                    raise TypeError(
                        "Una de las columnas especificadas no es de tipo numérico."
                    )

                resta = pc.subtract(col_minuendo, col_sustraendo)

                return resta
            except Exception as e:
                logger.exception("Error al restar las columnas: {}", e)
                raise

        def divide_columns_pa(
            table: pa.Table,
            col_divid: str,
            col_divis: str,
            fill_value=pa.scalar(None, type=pa.float64()),
        ):
            """
            Divide los valores de una columna por los valores de otra columna en una tabla de PyArrow, manejando divisiones por cero.

            Parámetros:
            - table: pa.Table, la tabla de PyArrow que contiene las columnas a dividir.
            - col_divis: str, el nombre de la columna cuyos valores serán divididos.
            - col_divis: str, el nombre de la columna por la cual se dividirán los valores.
            - fill_value: pa.Scalar, valor a utilizar cuando el divisor es cero. Por defecto, None.

            Retorna:
            - pa.Array: Un array de PyArrow con el resultado de la división de las columnas especificadas, manejando divisiones por cero.
            """
            # Verifica si el divisor (col_divis) es cero y realiza la división o aplica el valor de llenado

            result = pc.if_else(
                pc.equal(table[col_divis], 0),
                fill_value,
                pc.divide(table[col_divid], table[col_divis]),
            )

            return result

        @staticmethod
        def multiplicar_columnas(tabla, columna1, columna2):
            """
            Multiplica los valores de dos columnas en una tabla de PyArrow.
            Args:
                tabla (pa.Table): La tabla de PyArrow.
                columna1 (str): Nombre de la primera columna.
                columna2 (str): Nombre de la segunda columna.
            Returns:
                pa.Array: La columna resultante después de la multiplicación.
            Raises:
                KeyError: Si alguna de las columnas no existe en la tabla.
            """
            try:
                # Verificar que las columnas existan en la tabla
                if (
                    columna1 not in tabla.column_names
                    or columna2 not in tabla.column_names
                ):
                    raise KeyError(
                        f"Las columnas especificadas no existen en la tabla. {columna1} ó {columna2}"
                    )

                # Multiplicar los valores de las columnas
                resultado = pa.compute.multiply(tabla[columna1], tabla[columna2])

                # Registrar mensaje informativo
                logger.info(
                    f"Columnas {columna1} y {columna2} multiplicadas exitosamente."
                )

                return resultado

            except KeyError as e:
                # Registrar mensaje de error crítico
                logger.critical(f"Error al multiplicar columnas: {e}")
                raise

    @Registro_tiempo
    @staticmethod
    def agregar_nueva_columna_pa(
        tabla: pa.Table, array_resultado: pa.Array, nombre_nueva_columna: str
    ) -> pa.Table:
        """
        Agrega un array como una nueva columna a una tabla PyArrow.

        Parameters:
        tabla (pa.Table): La tabla PyArrow original.
        array_resultado (pa.Array): Array que se agregará como nueva columna.
        nombre_nueva_columna (str): El nombre de la nueva columna.

        Returns:
        pa.Table: Una nueva tabla PyArrow con la nueva columna agregada.

        Example:
        >>> data = {'columna1': [1, 2, 3], 'columna2': [4, 5, 6]}
        >>> tabla_original = pa.Table.from_pydict(data)
        >>> suma_columnas = sumar_columnas(tabla_original, ['columna1', 'columna2'])
        >>> tabla_modificada = agregar_nueva_columna(tabla_original, suma_columnas, 'suma_total')
        >>> print(tabla_modificada)
        """
        try:
            logger.success(f"Columna {nombre_nueva_columna} agregada exitosamente.")
            return tabla.append_column(nombre_nueva_columna, array_resultado)
        except Exception as e:
            logger.exception("Error al agregar la nueva columna: {}", e)
            raise

    @Registro_tiempo
    @staticmethod
    def duplicar_columna_n_veces_pa(
        tabla: pa.Table, nombre_columna: str, nombres_nuevas_columnas: list
    ) -> pa.Table:
        """
        Duplica una columna específica de una tabla PyArrow y agrega las duplicaciones con  nuevos nombres.

        Parameters:
        tabla (pa.Table): La tabla PyArrow a modificar.
        nombre_columna (str): El nombre de la columna que se va a duplicar.
        nombres_nuevas_columnas (list of str): Lista de nombres para las nuevas columnas    duplicadas.

        Returns:
        pa.Table: Una nueva tabla PyArrow con las columnas duplicadas agregadas.

        Raises:
        KeyError: Si la columna especificada no existe en la tabla.
        ValueError: Si no se proporcionan nombres para las columnas duplicadas.
        ValueError: Si el número de nombres proporcionados no es adecuado para el número de     duplicaciones.

        Example:
        >>> data = {'columna1': [1, 2, 3], 'columna2': [4, 5, 6]}
        >>> tabla_original = pa.Table.from_pydict(data)
        >>> nombres_nuevas_columnas = ['columna1_copia1', 'columna1_copia2']
        >>> tabla_modificada = duplicar_columna(tabla_original, 'columna1',     nombres_nuevas_columnas)
        >>> print(tabla_modificada)
        """
        if nombre_columna not in tabla.column_names:
            logger.error(f"La columna '{nombre_columna}' no se encuentra en la tabla.")
            raise KeyError(
                f"La columna '{nombre_columna}' no se encuentra en la tabla."
            )

        if len(nombres_nuevas_columnas) == 0:
            logger.error("No se proporcionaron nombres para las columnas duplicadas.")
            raise ValueError(
                "Es necesario proporcionar nombres para las columnas duplicadas."
            )

        try:
            for nuevo_nombre in nombres_nuevas_columnas:
                tabla = tabla.append_column(nuevo_nombre, tabla[nombre_columna])
            logger.success("Columna duplicada y agregada con éxito.")
            return tabla
        except Exception as e:
            logger.exception("Error al duplicar la columna: {}", e)
            raise

    @Registro_tiempo
    @staticmethod
    def crear_columna_constante_pa(
        num_filas: int, valor_constante, tipo_dato: pa.DataType
    ) -> pa.Array:
        """
        Crea un array de PyArrow con un valor constante.

        Parámetros:
        num_filas (int): Número de filas (elementos) en el array.
        valor_constante: El valor constante para llenar el array. Puede ser de cualquier tipo.
        tipo_dato (pa.DataType): Tipo de dato de PyArrow para el array. Debe ser un tipo de dato válido de PyArrow.

        Devoluciones:
        pa.Array: Un array de PyArrow lleno con el valor constante.

        Excepciones:
        TypeError: Si el tipo de dato no es compatible con el valor constante.
        ValueError: Si el número de filas es no positivo.

        Ejemplo:
        >>> array_constante = crear_columna_constante(5, 100, pa.int64())
        >>> print(array_constante)
        """
        try:
            if num_filas <= 0:
                raise ValueError("El número de filas debe ser positivo.")

            return pa.array([valor_constante] * num_filas, type=tipo_dato)
        except TypeError as error_de_tipo:
            logger.error(
                f"Se produjo un error de tipo al crear el array: {error_de_tipo}"
            )
            raise
        except ValueError as error_de_valor:
            logger.error(f"Se produjo un error de valor: {error_de_valor}")
            raise
        except Exception as error_general:
            logger.exception(f"Se produjo un error inesperado: {error_general}")
            raise

    @staticmethod
    def Renombrar_cols_con_dict_pa(tabla: pa.Table, dict_renombrar: dict) -> pa.Table:
        """
        Renombra las columnas de una tabla PyArrow basándose en un diccionario proporcionado.

        Parameters:
        tabla (pa.Table): La tabla PyArrow que se va a modificar.
        dict_renombrar (dict): Un diccionario donde las claves son los nombres actuales de las columnas y los valores son los nuevos nombres.

        Returns:
        pa.Table: Una nueva tabla PyArrow con las columnas renombradas.

        Raises:
        KeyError: Si alguna clave del diccionario no corresponde a una columna en la tabla.

        Example:
        >>> data = {'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']}
        >>> original_table = pa.Table.from_pydict(data)
        >>> rename_dict = {'col1': 'new_col1', 'col2': 'new_col2'}
        >>> renamed_table = renombrar_columnas_tabla(original_table, rename_dict)
        >>> print(renamed_table)
        """
        try:
            # Verificar que todas las claves del diccionario son nombres de columnas existentes
            columnas_existentes = set(tabla.column_names)
            columnas_renombrar = set(dict_renombrar.keys())
            if not columnas_renombrar.issubset(columnas_existentes):
                columnas_faltantes = columnas_renombrar - columnas_existentes
                raise KeyError(
                    f"Las siguientes columnas a renombrar no existen en la tabla: {columnas_faltantes}"
                )

            # Crear la lista de nuevos nombres manteniendo el orden original
            new_column_names = [
                dict_renombrar.get(name, name) for name in tabla.column_names
            ]

            # Renombrar las columnas de la tabla
            table_renamed = tabla.rename_columns(new_column_names)
            logger.info("Las columnas han sido renombradas exitosamente.")

            return table_renamed

        except KeyError as e:
            logger.error(f"Error al renombrar las columnas: {e}")
            raise
        except Exception as e:
            logger.exception(f"Error inesperado al renombrar las columnas: {e}")
            raise

    @Registro_tiempo
    @staticmethod
    def replace_substring_based_on_dict(
        table: pa.Table, column_name: str, replacement_dict: dict
    ) -> pa.Table:
        """
        Reemplaza subcadenas en una columna de una tabla PyArrow basándose en un diccionario de reemplazos.
        """
        column = table[column_name]
        # Inicializa la columna modificada como una copia de la columna original
        modified_column = column.cast(pa.string())

        for key, value in replacement_dict.items():
            # Encuentra las filas donde la clave está presente
            mask = pc.match_substring(column, key)
            # Crea una versión de la columna donde apariciones de la clave se reemplazan por el valor
            temp_replaced = pc.replace_substring(column, pattern=key, replacement=value)

            # Aplica condicionalmente el reemplazo
            modified_column = pc.if_else(mask, temp_replaced, modified_column)

        return modified_column

    def Transform_dfs_pandas_a_pyarrow(df: pd.DataFrame) -> pa.Table:
        """
        Función que toma un dataframe de pandas y lo transforma en una tabla de pyarrow.

        Args:
        df (pd.DataFrame): Dataframe de pandas a ser transformado.

        Returns:
        pa.table: Tabla bidimensional de datos de PyArrow.

        Raises:
        TypeError: Si el argumento 'df' no es un DataFrame de pandas.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("El argumento 'df' debe ser un DataFrame de pandas.")

        try:
            table = pa.Table.from_pandas(df)
            return table
        except Exception as e:
            raise ValueError(f"Error al convertir el DataFrame a PyArrow: {e}")

    @staticmethod
    def reemplazar_columna_pa(tabla: pa.Table, columna: str, columna_nueva: pa.Array):
        """
        Reemplaza una columna en una tabla de PyArrow.

        Args:
            tabla: La tabla de PyArrow.
            columna: El nombre de la columna a reemplazar.
            columna_nueva: La nueva columna.

        Returns:
            La tabla modificada.
        """

        # Obtenemos el índice de la columna a reemplazar.
        try:
            indice_columna = tabla.schema.get_field_index(columna)
        except KeyError:
            raise ValueError(f"La columna '{columna}' no existe.")

        # Reemplazamos la columna.
        tabla = tabla.set_column(indice_columna, columna, columna_nueva)

        return tabla

    @staticmethod
    def concatenar_cols_seleccionadas(table: pa.Table, column_names: list):
        """_summary_
        Args:
            table (pa.Table): Tabla de pyarrow base que contiene las columnas a concatenar.
            column_names (list): Nombres de las columnas a concatenar
        Returns:
            pa.lib.ChunkedArray: Arreglo de pyarrow con las columnas seleccionadas.
        """
        selected_cols = TableColumnConcatenator.select_columns(table, column_names)
        string_columns = TableColumnConcatenator.convert_to_strings(selected_cols)
        concatenated_column = TableColumnConcatenator.concatenate_strings(
            string_columns
        )
        return concatenated_column

    @Registro_tiempo
    @staticmethod
    def Group_and_sum_columns_pa(
        table, group_column: list| str, sum_columns: list
    ) -> pa.Table:
        """
        Agrupa una tabla PyArrow por una columna y suma las columnas numéricas especificadas.

        Args:
            table (pa.Table): La tabla PyArrow a agrupar.
            group_column Union [list, str]: El nombre de la columna por la cual agrupar,
            o la lista de columnas por las cuales se quiere agrupar.
            sum_columns (list): Lista de nombres de columnas numéricas a sumar.

        Returns:
            pa.Table: Tabla agrupada con las sumas calculadas.
        """
        # Agrupar por la columna deseada y sumar las columnas numéricas
        grouped_table = table.group_by(group_column).aggregate(
            [(col, "sum") for col in sum_columns]
        )

        return grouped_table

    @staticmethod
    def obtener_columnas_string_numericas(tabla):
        """
        Esta función toma una tabla PyArrow y retorna dos listas:
        una con los nombres de las columnas de tipo string y otra con los nombres de las columnas de tipo numérico.

        Arg:
            tabla: pyarrow.Table

        Returns:
            tuple (list, list) : Tupla que contiene dos listas 1 con los nombres de las columnas tipo "String" y otra con las columnas tipo "Númerico" sin mucho nivel de detalle, es decir: abarca columnas de todo tipo "integer" o "floating"
        """
        columnas_string = [
            name
            for name, tipo in zip(tabla.schema.names, tabla.schema.types)
            if pa.types.is_string(tipo)
        ]
        columnas_numericas = [
            name
            for name, tipo in zip(tabla.schema.names, tabla.schema.types)
            if pa.types.is_integer(tipo) or pa.types.is_floating(tipo)
        ]

        return columnas_string, columnas_numericas

    @staticmethod
    def Join_combine_pyarrow(
        table_left: pa.Table, table_right: pa.Table, join_key: str
    ):
        """
        Realiza un join entre dos tablas de PyArrow, combina los chunks de la tabla resultante,
        y ordena la tabla por una columna especificada.

        Parámetros:
        - table_left (pa.Table): La tabla de PyArrow del lado izquierdo para el join.
        - table_right (pa.Table): La tabla de PyArrow del lado derecho para el join.
        - join_key (str): El nombre de la columna en ambas tablas por la cual realizar el join.

        Retorna:
        - pa.Table: Una nueva tabla de PyArrow resultante del join, que ha sido combinada en chunks
                    y ordenada por la columna especificada en `join_key`.
        """
        # Realiza el join entre las dos tablas en la columna especificada
        joined_table = table_left.join(table_right, keys=join_key)

        # Combina los chunks de la tabla resultante para optimizar el rendimiento
        combined_table = joined_table.combine_chunks()

        return combined_table

    @staticmethod
    def Join_combine_pyarrow(
        table_left: pa.Table, table_right: pa.Table, join_key: str
    ):
        """
        Realiza un join entre dos tablas de PyArrow, combina los chunks de la tabla resultante,
        y ordena la tabla por una columna especificada.

        Parámetros:
        - table_left (pa.Table): La tabla de PyArrow del lado izquierdo para el join.
        - table_right (pa.Table): La tabla de PyArrow del lado derecho para el join.
        - join_key (str): El nombre de la columna en ambas tablas por la cual realizar el join.

        Retorna:
        - pa.Table: Una nueva tabla de PyArrow resultante del join, que ha sido combinada en chunks
                    y ordenada por la columna especificada en `join_key`.
        """
        # Realiza el join entre las dos tablas en la columna especificada
        joined_table = table_left.join(table_right, keys=join_key)

        # Combina los chunks de la tabla resultante para optimizar el rendimiento
        combined_table = joined_table.combine_chunks()

        return combined_table

    class TableColumnConcatenator:

        @staticmethod
        def select_columns(table, column_names):
            try:
                selected_columns = [table[col] for col in column_names]
            except KeyError as e:
                logger.error(f"Error al seleccionar columnas: {e}")
                raise ValueError(
                    "Una o más columnas especificadas no existen en la tabla."
                )
            return selected_columns

        @staticmethod
        def convert_to_strings(columns):
            try:
                cols_convertidas = [pc.cast(col, pa.string()) for col in columns]
            except (
                pa.ArrowInvalid,
                pa.ArrowNotImplementedError,
                pa.ArrowInvalidValueError,
            ) as e:
                logger.error(f"Error al convertir columnas a tipo string: {e}")
                raise TypeError(
                    "No se pudo convertir una o más columnas a tipo de datos string."
                )
            return cols_convertidas

        @staticmethod
        def concatenate_strings(columns):
            try:
                concatenated_column = pc.binary_join_element_wise(*columns, "")
            except ValueError as e:
                logger.error(f"Error al concatenar columnas: {e}")
                raise ValueError(
                    "Las columnas no tienen la misma longitud y no se pueden concatenar."
                )
            return concatenated_column

        @staticmethod
        def concatenar_cols_seleccionadas(table: pa.Table, column_names: list):
            try:
                selected_cols = TableColumnConcatenator.select_columns(
                    table, column_names
                )
                string_columns = TableColumnConcatenator.convert_to_strings(
                    selected_cols
                )
                concatenated_column = TableColumnConcatenator.concatenate_strings(
                    string_columns
                )
            except Exception as e:
                logger.error(
                    f"Error en la función 'concatenar_cols_seleccionadas': {e}"
                )
                raise
            return concatenated_column


class PandasBaseTransformer:
    @staticmethod
    def Cambiar_tipo_dato_multiples_columnas_pd(
        base: pd.DataFrame, list_columns: list, type_data: type
    ) -> pd.DataFrame:
        """
        Función que toma un DataFrame, una lista de sus columnas para hacer un cambio en el tipo de dato de las mismas.

        Args:
            base (pd.DataFrame): DataFrame que es la base del cambio.
            list_columns (list): Columnas a modificar su tipo de dato.
            type_data (type): Tipo de dato al que se cambiarán las columnas (ejemplo: str, int, float).

        Returns:
            pd.DataFrame: Copia del DataFrame con los cambios.
        """
        try:
            # Verificar que el DataFrame tenga las columnas especificadas
            for columna in list_columns:
                if columna not in base.columns:
                    raise KeyError(f"La columna '{columna}' no existe en el DataFrame.")

            # Cambiar el tipo de dato de las columnas
            base_copy = (
                base.copy()
            )  # Crear una copia para evitar problemas de SettingWithCopyWarning
            base_copy[list_columns] = base_copy[list_columns].astype(type_data)

            return base_copy

        except Exception as e:
            logger.critical(f"Error en Cambiar_tipo_dato_multiples_columnas: {e}")

    @staticmethod
    @Registro_tiempo
    def Group_by_and_sum_cols_pd(df=pd.DataFrame, group_col=list, sum_col=list):
        """
        Agrupa un DataFrame por una columna y calcula la suma de otra columna.

        Args:
            df (pandas.DataFrame): El DataFrame que se va a agrupar y sumar.
            group_col (list or str): El nombre de la columna o lista de nombres de columnas por la cual se va a agrupar.
            sum_col (list or str): El nombre de la columna o lista de nombres de columnas que se va a sumar.

        Returns:
            pandas.DataFrame: El DataFrame con las filas agrupadas y la suma calculada.
        """

        try:
            if isinstance(group_col, str):
                group_col = [group_col]

            if isinstance(sum_col, str):
                sum_col = [sum_col]

            result_df = df.groupby(group_col, as_index=False)[sum_col].sum()

            # Registro de éxito
            logger.info(f"Agrupación y suma realizadas con éxito en las columnas.")

        except Exception as e:
            # Registro de error crítico
            logger.critical(
                f"Error al realizar la agrupación y suma en las columnas. {e}"
            )
            result_df = None

        return result_df

    @staticmethod
    @Registro_tiempo
    def Agregar_columna_constante_pd(
        dataframe: pd.DataFrame, nombre_columna: str, valor_constante: Any
    ) -> Union[pd.DataFrame, None]:
        """
        Añade una nueva columna con un valor constante a un DataFrame.

        Args:
            dataframe (pd.DataFrame): DataFrame al que se añadirá la nueva columna.
            nombre_columna (str): Nombre de la nueva columna.
            valor_constante (Any): Valor constante que se asignará a todas las filas de la columna.

        Returns:
            Union[pd.DataFrame, None]: DataFrame con la nueva columna añadida o None si ocurre un error.
        """
        try:
            # Verificar si dataframe es un DataFrame de pandas
            if not isinstance(dataframe, pd.DataFrame):
                raise TypeError(
                    "El argumento 'dataframe' debe ser un DataFrame de pandas."
                )

            # Crear una copia del dataframe.
            df = dataframe.copy()
            # Añadir la nueva columna con el valor constante
            df[nombre_columna] = valor_constante

            # Registrar el evento
            logger.info(
                f"Se añadió la columna '{nombre_columna}' con el valor constante '{valor_constante}' al DataFrame."
            )

            return df

        except Exception as e:
            logger.critical(
                f"Error inesperado al añadir columna con valor constante: {str(e)}"
            )
        return None

    @staticmethod
    def Filtrar_por_valores_pd(
        df: pd.DataFrame, columna: str, valores_filtrar: List[Union[str, int]]
    ) -> pd.DataFrame:
        """
        Filtra el DataFrame basándose en los valores de una columna específica.

        Args:
            columna (pd.Series): Columna del DataFrame a filtrar.
            valores_filtrar (List[Union[str, int]]): Lista de valores a utilizar para filtrar   la columna.

        Returns:
            pd.DataFrame: DataFrame filtrado basándose en los valores especificados.
        """
        try:
            if isinstance(valores_filtrar, str):
                valores_filtrar = [valores_filtrar]

            # Filtrar el DataFrame basándose en los valores de la columna
            df_filtrado = df[df[columna].isin(valores_filtrar)]

            return df_filtrado

        except Exception as e:
            logger.critical(f"Error inesperado al filtrar por valores: {str(e)}")
            return None

    @staticmethod
    def pd_left_merge(
        base_left: pd.DataFrame, base_right: pd.DataFrame, key: str
    ) -> pd.DataFrame:
        """Función que retorna el left join de dos dataframe de pandas.

        Args:
            base_left (pd.DataFrame): Dataframe que será la base del join.
            base_right (pd.DataFrame): Dataframe del cuál se extraerá la información    complementaria.
            key (str): Llave mediante la cual se va a realizar el merge o join.

        Returns:
            pd.DataFrame: Dataframe con el merge de las dos fuentes de datos.
        """

        # Validar que base_left y base_right sean DataFrames de pandas
        if not isinstance(base_left, (pd.DataFrame, pd.Series)):
            raise ValueError("El argumento base_left no es un DataFrame de pandas")
        if not isinstance(base_right, (pd.DataFrame, pd.Series)):
            raise ValueError("El argumento base_right no es un DataFrame de pandas")

        base = None

        try:
            base = pd.merge(left=base_left, right=base_right, how="left", on=key)
            logger.success("Proceso de merge satisfactorio")
        except pd.errors.MergeError as e:
            logger.critical(f"Proceso de merge fallido: {e}")
            raise e

        return base

    @staticmethod
    def rellenar_columnas_nulas(
        df: Union[pd.DataFrame, pd.Series],
        columna: Union[str, List[str]],
        valor: Union[int, str],
    ) -> pd.DataFrame:
        """
        Rellena las columnas nulas de un DataFrame con un valor especificado y reasigna los     valores de la columna.

        Args:
            df (pd.DataFrame): DataFrame a rellenar.
            columna ( (str): Nombre de la columna a rellenar ,  list[str] : lista con los   nombres de las columnas a rellenar)
            valor (int, str): Valor a utilizar para rellenar las celdas nulas.

        Returns:
            pd.DataFrame: DataFrame con las columnas nulas rellenadas y reasignadas.
        """
        try:
            # Comprueba que la columna/columnas existen en el DataFrame
            if isinstance(columna, list):
                for cada_columna in columna:
                    if cada_columna not in df.columns:
                        raise KeyError(
                            f"Columna '{cada_columna}' no existe en el DataFrame."
                        )

                # Crea una copia de las columnas y llena los nulos
                df.loc[:, columna] = df.loc[:, columna].fillna(valor)

            elif columna not in df.columns:
                raise KeyError(f"Columna '{columna}' no existe en el DataFrame.")
            else:
                # Crea una copia de la columna y llena los nulos
                df[columna] = df[columna].fillna(valor)

            logger.success(
                f"Remplazo de datos nulos exitoso para las columnas: {columna}"
            )
            return df
        except Exception as e:
            # Manejar cualquier excepción generada durante el proceso
            logger.critical(f"Error: {e}")
            return None  # Puedes cambiar esto según tus necesidades, por ejemplo, raise la     excepción nuevamente o devolver un valor predeterminado.

    @Registro_tiempo
    def arrow_to_tuples(table):

        try:
            logger.info("Iniciando la conversión de la tabla PyArrow a tuplas.")

            for batch in table.to_batches():
                if batch.num_rows == 0:
                    continue  # O manejar específicamente un lote vacío
                for row in range(batch.num_rows):
                    yield tuple(
                        batch.column(i)[row].as_py() for i in range(batch.num_columns)
                    )

        # except ArrowTypeError as e:
        #    logger.error(f"Error de tipo al convertir datos de PyArrow a Python: {e}")
        #    raise

        # except ArrowInvalid as e:
        #    logger.error(f"Operación inválida con PyArrow: {e}")
        #    raise

        except IndexError as e:
            logger.error(f"Error de índice al acceder a columnas o filas: {e}")
            raise

        except Exception as e:
            logger.error(
                f"Error inesperado al convertir la tabla PyArrow a tuplas: {e}"
            )
            raise


