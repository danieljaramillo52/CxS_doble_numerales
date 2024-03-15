# Main del proyecto


def CxS_dinamico():
    """1. Configuración Rutas, importaciones del proyecto"""
    # Importaciones librerias necesarias.
    import sys
    import os
    from datetime import datetime
    from loguru import logger

    Inicio = datetime.now()

    # Configuramos la rutas para traer modulos de las funciones.
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    """Agregamos al path las direcciones de los directorios "Utils => funciones del proyecto, Scrits => Modulos del proyecto )"""
    sys.path.extend([f"{parent_dir}\\Utils", f"{parent_dir}\\Scripts"])

    """Ubicamos la ruta de ejecución."""
    lugar_de_ejecucion = input(
        "Está ejecutando esta automatización desde Python IDLE ó desde cmd?: (si/no): "
    )

    if lugar_de_ejecucion == "si":
        ruta_actual = os.getcwd()
        ruta_padre = os.path.dirname(ruta_actual)
        os.chdir(ruta_padre)
    else:
        pass

    # Importamos los modulos de funciones necesarios.
    import General_Functions as GF
    import Transformation_Functions as TF
    import Lectura_bases_drivers_excel as LBE
    import Transformaciones_cadenas as TF_Cad
    import Transformaciones_directa as TF_dta
    import Transformaciones_indirecta as TF_indta
    import Transformaciones_droguerias as TF_drogs
    import Depuracion_CxS_Est as D_CXS_est

    """ 2. Carga archivo config.yml para arbitrar el proyecto, definición de constantes"""
    config = GF.Procesar_configuracion("config.yml")

    """ 3. Ejecución: """
    # Instanciar modulo de lectura y cargue de archivos del proyecto
    # Lectura de archivos en directorio "Insumos".
    bases_plano_drivers_cxs = LBE.Lectura_archivos(
        funcion_lectura=GF.Lectura_insumos_excel,
        funcion_acentos=GF.Eliminar_acentos,
        dict_archivos=config["Insumos"],
    )

    DICT_SEGMENTOS = GF.Crear_diccionario_desde_dataframe(
        df=bases_plano_drivers_cxs["driver_segmento"],
        col_clave=config["dict_posibles_cols"]["Segmentos"],
        col_valor=config["dict_posibles_cols"]["Segmento_Agrupado"],
    )

    DICT_NOM_CLIE = GF.Crear_diccionario_desde_dataframe(
        df=bases_plano_drivers_cxs["driver_nom_clie"].dropna(),
        col_clave=config["Insumos"]["Driver_CxS_P2"]["cols_necesarias_nc"][0],
        col_valor=config["Insumos"]["Driver_CxS_P2"]["cols_necesarias_nc"][1],
    )

    # Transformar Dataframes de pandas a Tablas de PyArrow.

    # Tomamos las claves necesarias.
    keys = config["keys_tablas_transform"]

    # Diccionario para almacenar las tablas transformadas
    tablas_transformadas = {}

    # Bucle para transformar cada DataFrame y almacenarlo en el diccionario
    for key in keys:
        tablas_transformadas[key] = TF.Transform_dfs_pandas_a_pyarrow(
            df=bases_plano_drivers_cxs[key]
        )

    # Segmentamos la tabla driver.
    dict_drivers_planos = {}

    Filtros = config["Insumos"]["Driver_cols_faltantes_planos"]["Filtros"]

    # Instancia de la clase de filtrado.
    Filtrar_drv_cad = TF.PyArrowColumnTransformer.PyArrowTablefilter(
        tablas_transformadas["driver_completar_planos"]
    )
    for cada_tipo in Filtros.keys():
        # Crear mascara para filtrar las bases
        mask = Filtrar_drv_cad.mask_equivalente_pa(
            columna=Filtros[cada_tipo]["Columna"], valor=cada_tipo
        )

        # Filtrar la tabla.
        table_filtrada = Filtrar_drv_cad.Filtrar_tabla_pa(mask)

        # Seleccionar columnas
        table_filtrada_select = TF.PyArrowColumnTransformer.seleccionar_columnas_pa(
            tabla=table_filtrada, columnas=Filtros[cada_tipo]["cols_necesarias"]
        )

        # Agregar tabla filtrada.
        dict_drivers_planos[cada_tipo] = table_filtrada_select

    # Ejecutamos las modificaciones para cada base encapsuladas en los modulos 'Transformaciones_cadenas'
    base_cadenas_final_pa = TF_Cad.Transformaciones_cadenas(
        Pyarrow_Functions=TF.PyArrowColumnTransformer,
        base_cadenas=tablas_transformadas["plano_cxs_cadenas"],
        config=config,
        dicts_auxiliares=[DICT_SEGMENTOS],
        drv_completar_cadenas=dict_drivers_planos["Cadenas"],
    )
    # Ejecutamos las modificaciones para cada base encapsuladas en los modulos Transformaciones_directa'
    base_directa_final_pa = TF_dta.Transformaciones_directa(
        Pyarrow_Functions=TF.PyArrowColumnTransformer,
        base_directa=tablas_transformadas["plano_cxs_directa"],
        config=config,
        dicts_auxiliares=[DICT_SEGMENTOS],
        drv_completar_directa=dict_drivers_planos["Directa"],
    )
    # Ejecutamos las modificaciones para cada base encapsuladas en los modulos Transformaciones_indirecta'
    base_indirecta_final_pa = TF_indta.Transformaciones_indirecta(
        Pyarrow_Functions=TF.PyArrowColumnTransformer,
        base_indirecta=tablas_transformadas["plano_cxs_indirecta"],
        config=config,
        dicts_auxiliares=[
            DICT_SEGMENTOS,
            DICT_NOM_CLIE,
            config["dict_ofic_vtas"],
            config["dict_sector"],
        ],
        drv_auxiliares=[
            dict_drivers_planos["Indirecta"],
            tablas_transformadas["driver_nit_agentes"],
        ],
    )
    # Ejecutamos las modifciaciones para cada base encapsuladas en los modulos 'Transformaciones_droguerias'
    base_drog_final_pa = TF_drogs.Transformaciones_droguerias(
        Pyarrow_Functions=TF.PyArrowColumnTransformer,
        base_droguerias=tablas_transformadas["plano_cxs_droguerias"],
        config=config,
        dicts_auxiliares=[DICT_SEGMENTOS],
        drv_completar_droguerias=dict_drivers_planos["Droguerias"],
    )

    # Proceso de no numerales integración de la bases dinámica.
    base_numerales_final = TF.PyArrowColumnTransformer.Concatenar_tablas_pa(
        tablas=[
            base_cadenas_final_pa,
            base_directa_final_pa,
            base_indirecta_final_pa,
            base_drog_final_pa,
        ]
    )
    base_numerales_final_agrup = TF.PyArrowColumnTransformer.Group_and_sum_columns_pa(
        base_numerales_final,
        group_column=config["Insumos"]["db_cxs_dinamico"]["cols_agrup_planos_final"],
        sum_columns=config["Insumos"]["db_cxs_dinamico"]["cols_sum_planos_final"],
    )
    base_numerales_final_agrup_rename = (
        TF.PyArrowColumnTransformer.Renombrar_cols_con_dict_pa(
            tabla=base_numerales_final_agrup,
            dict_renombrar=config["Insumos"]["db_cxs_dinamico"][
                "cols_sum_agrup_rename"
            ],
        )
    )
    # Agrupar base total.

    D_CXS_est.Base_cxs_estatico(
        Pyarrow_Functions=TF.PyArrowColumnTransformer,
        DB_Functions=GF.ConsultaDB,
        Pandas_Functions=TF.PandasBaseTransformer,
        config=config,
        base_doble_numerales=base_numerales_final_agrup_rename,
    )

    Fin = datetime.now()
    print(Fin - Inicio)


if __name__ == "__main__":
    CxS_dinamico()
