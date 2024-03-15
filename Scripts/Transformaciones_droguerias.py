# Trasformaciones de la base de Directas.
import copy
import pyarrow as pa
from typing import Type


def Transformaciones_droguerias(
    base_droguerias: pa.Table,
    Pyarrow_Functions: Type,
    config: dict,
    dicts_auxiliares: list,
    drv_completar_droguerias: pa.Table,
) -> pa.Table:
    """Encapsula el procedimiento para modificar la base_droguerias y retorna la base_droguerias modificada.
    Modula el proceso de modificación de la base_droguerias para evitar aplicarlo directamente en el módulo main.py.

    Args:
        base_droguerias (pa.Table): Tabla bidimensional de PyArrow que contiene la información original del archivo en: config['Insumos']['plano_cxs_droguerias']['nom_base']"

        Pyarrow_Functions (pa.Type): Clase que contiene métodos necesarios para modificar el objeto base_droguerias. Localizada en: "Utils/Trasformation_functions/clase"

        config (dict): Diccionario extraido de config.yaml. Del mismo se extraen los conjuntos de información necesarios.

        dicts_auxiliares (list): lista de diccionarios generados por la automatización. No parámetrizados en config.yaml. Se extrae información util para la modificación de los planos.

        drv_completar_drogueras (pa.Table): tabla de pyarrow auxiliar 
    Returns:
        base_droguerias_final (pa.Table) : base_droguerias modificada.
    """

    """ Tener en cuenta que se toma parte de la configuración para esta ejecución: """

    # Creamos una copia profunda de la base original para trabajar con ella.
    base_droguerias_copy = copy.deepcopy(base_droguerias)

    # Enlistamos diccionarios necesarios.
    DICT_SEGMENTOS = dicts_auxiliares[0]

    # Cambiamos el tipo de dato de las columnas de ventas.
    base_droguerias_copy = Pyarrow_Functions.cambiar_tipo_dato_columnas_pa(
        tabla=base_droguerias_copy,
        columnas=config["Insumos"]["plano_cxs_droguerias"]["cols_cambiar_tipo"],
        nuevo_tipo=pa.float64(),
    )

    # Calcular columna ventas_Efectivas.
    col_ventas_efectivas = Pyarrow_Functions.OpAritmeticasPa.sumar_columnas_pa(
        tabla=base_droguerias_copy,
        columnas_a_sumar=config["cols_calculadas_cad_drog_dir"]["sum_cols"][
            "Ventas_Efectivas"
        ],
    )

    # Reemplazar ajustar lo meses necesarios. Con base al diccionario meses.
    base_droguerias_copy = Pyarrow_Functions.reemplazar_valores_con_diccionario_pa(
        tabla=base_droguerias_copy,
        nombre_columna=config["dict_posibles_cols"]["Mes"],
        diccionario_de_mapeo=config["dict_meses"],
    )

    # Agregar columna ventas_Efectivas a la base droguerias
    base_droguerias_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_droguerias_copy,
        array_resultado=col_ventas_efectivas,
        nombre_nueva_columna=config["dict_posibles_cols"]["Ventas_Efectivas"],
    )

    # Generar columna duplicada a partir de la columna Total Descuentos.
    base_droguerias_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
        tabla=base_droguerias_copy,
        nombre_columna=config["dict_posibles_cols"]["Total_Descuentos"],
        nombres_nuevas_columnas=config["cols_calculadas_cad_drog_dir"]["duplicar_cols"][
            "Total Descuentos"
        ],
    )

    # Generar columnas duplicadas de a partir de la columna Dctos_NG
    base_droguerias_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
        tabla=base_droguerias_copy,
        nombre_columna=config["dict_posibles_cols"]["Dctos_NG"],
        nombres_nuevas_columnas=config["cols_calculadas_cad_drog_dir"]["duplicar_cols"][
            "Dctos_NG"
        ],
    )

    # Generar columnas duplicada a partir de la columna Ventas Netas
    base_droguerias_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
        tabla=base_droguerias_copy,
        nombre_columna=config["dict_posibles_cols"]["Ventas Netas"],
        nombres_nuevas_columnas=config["cols_calculadas_cad_drog_dir"]["duplicar_cols"][
            "Ventas Netas"
        ],
    )

    # Generar columnas duplicadas a partir de la columna Ventas_Efectivas
    base_droguerias_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
        tabla=base_droguerias_copy,
        nombre_columna=config["dict_posibles_cols"]["Ventas_Efectivas"],
        nombres_nuevas_columnas=config["cols_calculadas_cad_drog_dir"]["duplicar_cols"][
            "Ventas_Efectivas"
        ],
    )

    # Columnas de valor constante para agregar. 1) Crear 2.) agregar.
    # base.nom_rows = Retorna el numero de filas, donde base => tabla de pyarrow.

    # Crear col: Devoluciones_malas
    col_dev_malas = Pyarrow_Functions.crear_columna_constante_pa(
        num_filas=base_droguerias_copy.num_rows,
        valor_constante=config["cols_calculadas_cad_drog_dir"]["cols_nul"][
            "Devoluciones_malas"
        ],
        tipo_dato=pa.float64(),
    )

    # Crear col: Gasto_Prom_Comercializadores
    col_gastos_prom_comer = Pyarrow_Functions.crear_columna_constante_pa(
        num_filas=base_droguerias_copy.num_rows,
        valor_constante=config["cols_calculadas_cad_drog_dir"]["cols_nul"][
            "Gasto_Prom_Comercializadores"
        ],
        tipo_dato=pa.float64(),
    )

    # Crear col: Total_Gastos_CN
    col_gastos_prom_comer = Pyarrow_Functions.crear_columna_constante_pa(
        num_filas=base_droguerias_copy.num_rows,
        valor_constante=config["cols_calculadas_cad_drog_dir"]["cols_nul"][
            "Total_Gastos_CN"
        ],
        tipo_dato=pa.float64(),
    )

    # Agregar columna Devoluciones_malas a la base droguerias

    base_droguerias_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_droguerias_copy,
        array_resultado=col_dev_malas,
        nombre_nueva_columna=config["dict_posibles_cols"]["Devoluciones_malas"],
    )

    # Agregar columna "Gasto_Prom_Comercializadores" a la base droguerias

    base_droguerias_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_droguerias_copy,
        array_resultado=col_gastos_prom_comer,
        nombre_nueva_columna=config["dict_posibles_cols"][
            "Gasto_Prom_Comercializadores"
        ],
    )

    # Agregar columna "Total_Gastos_CN" a la base droguerias

    base_droguerias_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_droguerias_copy,
        array_resultado=col_gastos_prom_comer,
        nombre_nueva_columna=config["dict_posibles_cols"]["Total_Gastos_CN"],
    )


    # Actualizar los valores del segmento, por segmento agrupado.
    base_droguerias_copy = Pyarrow_Functions.reemplazar_valores_con_diccionario_pa(
        tabla=base_droguerias_copy,
        nombre_columna=config["dict_posibles_cols"]["Segmento"],
        diccionario_de_mapeo=DICT_SEGMENTOS,
    )

    # Agregar oficina de Ventas agrupada.

    # 1.) Duplicar columna (Desc Oficina de Ventas)
    base_droguerias_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
        tabla=base_droguerias_copy,
        nombre_columna=config["dict_posibles_cols"]["Desc Oficina de Ventas"],
        nombres_nuevas_columnas=config["cols_calculadas_cad_drog_dir"]["duplicar_cols"][
            "Desc Oficina de Ventas"
        ],
    )
    # 2.) Reemplazar valores con base en diccionario de mapeo.
    base_droguerias_copy = Pyarrow_Functions.reemplazar_valores_con_diccionario_pa(
        tabla=base_droguerias_copy,
        nombre_columna=config["dict_posibles_cols"]["Oficina_ventas_Agrup"],
        diccionario_de_mapeo=config["dict_ofic_vtas_agrup"],
    )
    base_droguerias_copy = Pyarrow_Functions.Renombrar_cols_con_dict_pa(
        tabla=base_droguerias_copy,
        dict_renombrar=config["Insumos"]["plano_cxs_droguerias"]["Renombrar_cols_droguerias"],
    )
    # Agregar columnas faltantes para la directa con ayuda del driver.
    base_droguerias_copy_completo = Pyarrow_Functions.Join_combine_pyarrow(
        table_left=base_droguerias_copy,
        table_right=drv_completar_droguerias,
        join_key=config["dict_posibles_cols"]["Segmento_Agrup"],
    )

    base_droguerias_final = Pyarrow_Functions.seleccionar_columnas_pa(
        tabla=base_droguerias_copy_completo,
        columnas=config["Insumos"]["db_cxs_dinamico"]["cols_finales_planos"],
    )

    return base_droguerias_final
