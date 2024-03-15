# Trasformaciones de la base de indrecta.
import copy
import pyarrow as pa
from typing import Type


def Transformaciones_indirecta(
    base_indirecta: pa.Table,
    Pyarrow_Functions: Type,
    config: dict,
    dicts_auxiliares: list,
    drv_auxiliares: pa.Table,
) -> pa.Table:
    """Encapsula el procedimiento para modificar la base_indirecta y retorna la base_indirecta modificada.
    Modula el proceso de modificación de la base_indirecta para evitar aplicarlo directamente en el módulo main.py.

    Args:
        base_indirecta (pa.Table): Tabla bidimensional de PyArrow que contiene la información original del archivo en: config['Insumos']['plano_cxs_indirecta']['nom_base']"

        Pyarrow_Functions (pa.Type): Clase que contiene métodos necesarios para modificar el objeto base_indirecta. Localizada en: "Utils/Trasformation_functions/clase"

        config (dict): Diccionario extraido de config.yaml. Del mismo se extraen los conjuntos de información necesarios.

        dicts_auxiliares (list): lista de diccionarios generados por la automatización. No parámetrizados en config.yaml. Se extrae información util para la modificación de los planos.

    Returns:
        base_directa_def (pa.Table) : base_indirecta modificada.
    """

    """ Tener en cuenta que se toma parte de la configuración para esta ejecución: """

    # Creamos una copia profunda de la base original para trabajar con ella.
    base_indirecta_copy = copy.deepcopy(base_indirecta)

    # Enlistamos diccionarios necesarios.
    DICT_SEGMENTOS = dicts_auxiliares[0]
    DICT_NOM_CLIENTE = dicts_auxiliares[1]
    DICT_OFIC_VTAS = dicts_auxiliares[2]
    DICT_SECTOR = dicts_auxiliares[3]
    drv_completar_indirecta = drv_auxiliares[0]
    table_drv_nit_agente_indirecta = drv_auxiliares[1]

    # Creamos el dict_maestro.
    dict_reemplazar_cols = {
        config["dict_posibles_cols"]["Mes"]: config["dict_meses"],
        config["dict_posibles_cols"]["Oficina_ventas_Agrup"]: config[
            "dict_ofic_vtas_agrup"
        ],
        config["dict_posibles_cols"]["Segmento"]: DICT_SEGMENTOS,
        config["dict_posibles_cols"]["Oficina"]: DICT_OFIC_VTAS,
        config["dict_posibles_cols"]["Negocio"]: DICT_SECTOR,
        config["dict_posibles_cols"]["Nombre_cliente"]: DICT_NOM_CLIENTE,
    }

    # Cambiamos el tipo de dato de las columnas de ventas.
    base_indirecta_copy = Pyarrow_Functions.cambiar_tipo_dato_columnas_pa(
        tabla=base_indirecta_copy,
        columnas=config["Insumos"]["plano_cxs_indirecta"]["cols_cambiar_tipo"],
        nuevo_tipo=pa.float64(),
    )
    # Calcular columna ventas_Efectivas.
    col_ventas_efectivas = Pyarrow_Functions.OpAritmeticasPa.sumar_columnas_pa(
        tabla=base_indirecta_copy,
        columnas_a_sumar=config["cols_calculadas_indir"]["sum_cols"][
            "Ventas_Efectivas"
        ],
    )

    # Agregar columna ventas_Efectivas a la base indirecta
    base_indirecta_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_indirecta_copy,
        array_resultado=col_ventas_efectivas,
        nombre_nueva_columna=config["dict_posibles_cols"]["Ventas_Efectivas"],
    )

    # Calcular la columna Descuentos
    col_descuentos = Pyarrow_Functions.OpAritmeticasPa.sumar_columnas_pa(
        tabla=base_indirecta_copy,
        columnas_a_sumar=config["cols_calculadas_indir"]["sum_cols"]["Descuentos"],
    )

    # Calcular la columna Ventas_Netas_Grupo
    col_ventas_netas_grupo = Pyarrow_Functions.OpAritmeticasPa.restar_columnas_pa(
        tabla=base_indirecta_copy,
        columna_minuendo=config["cols_calculadas_indir"]["sustrac_cols"][
            "Ventas_Netas_Grupo"
        ]["col_minuendo"],
        columna_sustraendo=config["cols_calculadas_indir"]["sustrac_cols"][
            "Ventas_Netas_Grupo"
        ]["col_sustrayendo"],
    )

    # Agregar columna Ventas_Netas_Grupo a la base indirecta
    base_indirecta_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_indirecta_copy,
        array_resultado=col_ventas_netas_grupo,
        nombre_nueva_columna=config["dict_posibles_cols"]["Ventas_Netas_Grupo"],
    )

    # Agregar columna Descuentos a la base indirecta
    base_indirecta_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_indirecta_copy,
        array_resultado=col_descuentos,
        nombre_nueva_columna=config["dict_posibles_cols"]["Descuentos"],
    )

    base_indirecta_copy = Pyarrow_Functions.reemplazar_valores_con_diccionario_pa(
            tabla=base_indirecta_copy,
            nombre_columna=config["dict_posibles_cols"]["Oficina"],
            diccionario_de_mapeo=config["dict_ofic_vtas"],
        )
    # Generar columnas duplicadas para base de la indirecta.
    cols_a_duplicar = config["cols_calculadas_indir"]["duplicar_cols"]

    for cada_col_a_duplicar in cols_a_duplicar.keys():
        base_indirecta_copy = Pyarrow_Functions.duplicar_columna_n_veces_pa(
            tabla=base_indirecta_copy,
            nombre_columna=cols_a_duplicar[cada_col_a_duplicar]["key"],
            nombres_nuevas_columnas=cols_a_duplicar[cada_col_a_duplicar]["cols"],
        )
    # Columnas de valor constante para agregar. 1) Crear 2.) agregar.
    # base.nom_rows = Retorna el numero de filas, donde base => tabla de pyarrow.

    # Crear col: Devoluciones_malas
    col_dev_malas = Pyarrow_Functions.crear_columna_constante_pa(
        num_filas=base_indirecta_copy.num_rows,
        valor_constante=config["cols_calculadas_indir"]["cols_nul"][
            "Devoluciones_malas"
        ],
        tipo_dato=pa.float64(),
    )

    # Crear col: Total_Gastos_CN
    col_total_gastos_cn = Pyarrow_Functions.crear_columna_constante_pa(
        num_filas=base_indirecta_copy.num_rows,
        valor_constante=config["cols_calculadas_indir"]["cols_nul"]["Total_Gastos_CN"],
        tipo_dato=pa.float64(),
    )

    # Agregar columna Devoluciones_malas a la base cadenas
    base_indirecta_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_indirecta_copy,
        array_resultado=col_dev_malas,
        nombre_nueva_columna=config["dict_posibles_cols"]["Devoluciones_malas"],
    )

    # Agregar columna "Total_Gastos_CN" a la base cadenas
    base_indirecta_copy = Pyarrow_Functions.agregar_nueva_columna_pa(
        tabla=base_indirecta_copy,
        array_resultado=col_total_gastos_cn,
        nombre_nueva_columna=config["dict_posibles_cols"]["Total_Gastos_CN"],
    )

    for cada_columna, cada_dict in dict_reemplazar_cols.items():
        base_indirecta_copy = Pyarrow_Functions.reemplazar_valores_con_diccionario_pa(
            tabla=base_indirecta_copy,
            nombre_columna=cada_columna,
            diccionario_de_mapeo=cada_dict,
        )

    # 1) Renombrar columnas.
    base_indirecta_copy = Pyarrow_Functions.Renombrar_cols_con_dict_pa(
        tabla=base_indirecta_copy,
        dict_renombrar=config["Insumos"]["plano_cxs_indirecta"][
            "Renombrar_cols_indirecta"
        ],
    )

    base_indirecta_copy_completo = Pyarrow_Functions.Join_combine_pyarrow(
        table_left=base_indirecta_copy,
        table_right=drv_completar_indirecta,
        join_key=config["dict_posibles_cols"]["Segmento_Agrup"],
    )

    # Actualizar col formato NIT
    base_indirecta_copy_completo = Pyarrow_Functions.Join_combine_pyarrow(
        table_left=base_indirecta_copy_completo,
        table_right=table_drv_nit_agente_indirecta,
        join_key="Cod cliente",
    )

    # 2) Selecionar cols_correspondientes.
    base_indirecta_final_pa = Pyarrow_Functions.seleccionar_columnas_pa(
        tabla=base_indirecta_copy_completo,
        columnas=config["Insumos"]["db_cxs_dinamico"]["cols_finales_planos"],
    )

    return base_indirecta_final_pa
