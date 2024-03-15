# Trasformaciones de la base de cadenas.
import copy
import pyarrow as pa
from typing import Type


def Transformaciones_cadenas(
    base_cadenas: pa.Table,
    Pyarrow_Functions: Type,
    config: dict,
    dicts_auxiliares: list,
    drv_completar_cadenas = pa.Table
) -> pa.Table:
    """Encapsula el procedimiento para modificar la base_cadenas y retorna la base_cadenas modificada.
    Modula el proceso de modificación de la base_cadenas para evitar aplicarlo directamente en el módulo main.py.

    Args:
        base_cadenas (pa.Table): Tabla bidimensional de PyArrow que contiene la información original del archivo en: config['Insumos']['plano_cxs_cadenas']['nom_base']"

        Pyarrow_Functions (pa.Type): Clase que contiene métodos necesarios para modificar el objeto base_cadenas. Localizada en: "Utils/Trasformation_functions/clase"

        config (dict): Diccionario extraido de config.yaml. Del mismo se extraen los conjuntos de información necesarios.

        dicts_auxiliares (list): lista de diccionarios generados por la automatización. No parámetrizados en config.yaml. Se extrae información util para la modificación de los planos.

        drv_completar_cadenas (pa.Table): tabla de pyarrow auxiliar 

    Returns:
        base_cadenas_final_pa (pa.Table) : base_cadenas modificada.
    """

    """ Tener en cuenta que se toma parte de la configuración para esta ejecución: """

    # Creamos una copia profunda de la base original para trabajar con ella.
    base_cadenas_copy = copy.deepcopy(base_cadenas)

    # Enlistamos diccionarios necesarios.
    DICT_SEGMENTOS = dicts_auxiliares[0]
    # Modificar dict_meses.

    # Cambiamos el tipo de dato de las columnas de ventas.
    base_cadenas_copy = Pyarrow_Functions.cambiar_tipo_dato_columnas_pa(
        tabla=base_cadenas_copy,
        columnas=config["Insumos"]["plano_cxs_cadenas"]["cols_cambiar_tipo"],
        nuevo_tipo=pa.float64(),
    )

    # Reemplazar ajustar lo meses necesarios. Con base al diccionario meses.
    base_cadenas_copy = Pyarrow_Functions.reemplazar_valores_con_diccionario_pa(
        tabla=base_cadenas_copy,
        nombre_columna=config["dict_posibles_cols"]["Mes"],
        diccionario_de_mapeo=config["dict_meses"],
    )

    # Calcular columna ventas_Efectivas.
    col_ventas_efectivas = Pyarrow_Functions.OpAritmeticasPa.sumar_columnas_pa(
        tabla=base_cadenas_copy,
        columnas_a_sumar=config["cols_calculadas_cad_drog_dir"]["sum_cols"][
            "Ventas_Efectivas"
        ],
    )

    # Agregar columna ventas_Efectivas a la base cadenas
    base_cadenas_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_cadenas_copy,
        array_resultado=col_ventas_efectivas,
        nombre_nueva_columna=config["dict_posibles_cols"]["Ventas_Efectivas"],
    )

    # Generar columna duplicada a partir de la columna Total Descuentos.
    base_cadenas_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
        tabla=base_cadenas_copy,
        nombre_columna=config["dict_posibles_cols"]["Total_Descuentos"],
        nombres_nuevas_columnas=config["cols_calculadas_cad_drog_dir"]["duplicar_cols"][
            "Total Descuentos"
        ],
    )

    # Generar columnas duplicadas de a partir de la columna Dctos_NG
    base_cadenas_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
        tabla=base_cadenas_copy,
        nombre_columna=config["dict_posibles_cols"]["Dctos_NG"],
        nombres_nuevas_columnas=config["cols_calculadas_cad_drog_dir"]["duplicar_cols"][
            "Dctos_NG"
        ],
    )

    # Generar columnas duplicada a partir de la columna Ventas Netas
    base_cadenas_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
        tabla=base_cadenas_copy,
        nombre_columna=config["dict_posibles_cols"]["Ventas Netas"],
        nombres_nuevas_columnas=config["cols_calculadas_cad_drog_dir"]["duplicar_cols"][
            "Ventas Netas"
        ],
    )

    # Generar columnas duplicadas a partir de la columna Ventas_Efectivas
    base_cadenas_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
        tabla=base_cadenas_copy,
        nombre_columna=config["dict_posibles_cols"]["Ventas_Efectivas"],
        nombres_nuevas_columnas=config["cols_calculadas_cad_drog_dir"]["duplicar_cols"][
            "Ventas_Efectivas"
        ],
    )

    # Columnas de valor constante para agregar. 1) Crear 2.) agregar.
    # base.nom_rows = Retorna el numero de filas, donde base => tabla de pyarrow.

    # Crear col: Devoluciones_malas
    col_dev_malas = Pyarrow_Functions.crear_columna_constante_pa(
        num_filas=base_cadenas_copy.num_rows,
        valor_constante=config["cols_calculadas_cad_drog_dir"]["cols_nul"][
            "Devoluciones_malas"
        ],
        tipo_dato=pa.float64(),
    )

    # Crear col: Gasto_Prom_Comercializadores
    col_gastos_prom_comer = Pyarrow_Functions.crear_columna_constante_pa(
        num_filas=base_cadenas_copy.num_rows,
        valor_constante=config["cols_calculadas_cad_drog_dir"]["cols_nul"][
            "Gasto_Prom_Comercializadores"
        ],
        tipo_dato=pa.float64(),
    )

    # Crear col: Total_Gastos_CN
    col_gastos_prom_comer = Pyarrow_Functions.crear_columna_constante_pa(
        num_filas=base_cadenas_copy.num_rows,
        valor_constante=config["cols_calculadas_cad_drog_dir"]["cols_nul"][
            "Total_Gastos_CN"
        ],
        tipo_dato=pa.float64(),
    )

    # Agregar columna Devoluciones_malas a la base cadenas
    base_cadenas_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_cadenas_copy,
        array_resultado=col_dev_malas,
        nombre_nueva_columna=config["dict_posibles_cols"]["Devoluciones_malas"],
    )

    # Agregar columna "Gasto_Prom_Comercializadores" a la base cadenas
    base_cadenas_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_cadenas_copy,
        array_resultado=col_gastos_prom_comer,
        nombre_nueva_columna=config["dict_posibles_cols"][
            "Gasto_Prom_Comercializadores"
        ],
    )

    # Agregar columna "Total_Gastos_CN" a la base cadenas
    base_cadenas_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_cadenas_copy,
        array_resultado=col_gastos_prom_comer,
        nombre_nueva_columna=config["dict_posibles_cols"]["Total_Gastos_CN"],
    )

    # Actualizar los valores del segmento, por segmento agrupado.
    base_cadenas_copy = Pyarrow_Functions.reemplazar_valores_con_diccionario_pa(
        tabla=base_cadenas_copy,
        nombre_columna=config["dict_posibles_cols"]["Segmento"],
        diccionario_de_mapeo=DICT_SEGMENTOS,
    )

    # Agregar oficina de Ventas agrupada.

    # 1.) Duplicar columna (Desc Oficina de Ventas)
    base_cadenas_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
        tabla=base_cadenas_copy,
        nombre_columna=config["dict_posibles_cols"]["Desc Oficina de Ventas"],
        nombres_nuevas_columnas=config["cols_calculadas_cad_drog_dir"]["duplicar_cols"][
            "Desc Oficina de Ventas"
        ],
    )
    
    # 2.) Reemplazar valores con base en diccionario de mapeo.
    base_cadenas_copy = Pyarrow_Functions.reemplazar_valores_con_diccionario_pa(
        tabla=base_cadenas_copy,
        nombre_columna=config["dict_posibles_cols"]["Oficina_ventas_Agrup"],
        diccionario_de_mapeo=config["dict_ofic_vtas_agrup"],
    )

    # Renombrar las columnas correspondientes, previo a la última adicion de columnas restantes
    base_cadenas_copy = Pyarrow_Functions.Renombrar_cols_con_dict_pa(
        tabla=base_cadenas_copy,
        dict_renombrar=config["Insumos"]["plano_cxs_cadenas"]["Renombrar_cols_cadenas"],
    )
    
    key_base_cadenas = Pyarrow_Functions.concatenar_cols_seleccionadas(
        table=base_cadenas_copy,
        column_names=["Formato","Segmento_Agrup"]
    )
    key_cadenas_driver = Pyarrow_Functions.concatenar_cols_seleccionadas(
        table=drv_completar_cadenas,
        column_names=["Formato","Segmento_Agrup"]
    )
    drv_completar_cadenas = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=drv_completar_cadenas,
        array_resultado=key_cadenas_driver,
        nombre_nueva_columna="Llave_cadenas",
    )
    base_cadenas_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_cadenas_copy,
        array_resultado=key_base_cadenas,
        nombre_nueva_columna="Llave_cadenas",
    )
    
    drv_completar_cadenas = drv_completar_cadenas.drop(['Segmento_Agrup', 'Formato']) 
    
    # Agregar columnas faltantes para la directa con ayuda del driver.
    base_cadenas_copy_completa = Pyarrow_Functions.Join_combine_pyarrow(
        table_left=base_cadenas_copy,
        table_right=drv_completar_cadenas,
        join_key="Llave_cadenas",
    )
    
    base_cadenas_final_pa = Pyarrow_Functions.seleccionar_columnas_pa(
        tabla=base_cadenas_copy_completa,
        columnas=config["Insumos"]["db_cxs_dinamico"]["cols_finales_planos"],
    )
    

    return base_cadenas_final_pa
