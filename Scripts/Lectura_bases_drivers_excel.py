# Modulo de lectura de insumos
def Lectura_archivos(funcion_lectura: callable, funcion_acentos: callable, dict_archivos: dict) -> tuple:
    """Lectura_plantillas : funcion que instancia repetidamente a function_lectura.
        Plantilla: Archivo de excel.
    Args:
        funcion_lectura: Lectura insumos excel (Localizada en: Utils/General_functions)
            Acerca función_lectura:
                Description:
                    Funcion que lee archivos excel en formato xlsx/xlsm y los carga en memoria.
                Args:
                    - path: (type : str)
                    - nom_insumo (type : str)
                    - nom_hoja (type: str)
                    - cols (type: int)
                Returns:
                    - pd.DataFrame:

        * dict_archivos (type : dict)  diccionario con los información de los insumos a cargar en memoria.

    Returns: dataframes: (type: tuple) Tupla con todos los datasframes leidos."""

    plano_cxs_cadenas = funcion_acentos(funcion_lectura(
        path=dict_archivos["path_insumos"],
        nom_insumo=dict_archivos["plano_cxs_cadenas"]["nom_base"],
        nom_hoja=dict_archivos["plano_cxs_cadenas"]["nom_hoja"],
        cols=dict_archivos["plano_cxs_cadenas"]["cols"],
    ))
    plano_cxs_directa = funcion_acentos(funcion_lectura(
        path=dict_archivos["path_insumos"],
        nom_insumo=dict_archivos["plano_cxs_directa"]["nom_base"],
        nom_hoja=dict_archivos["plano_cxs_directa"]["nom_hoja"],
        cols=dict_archivos["plano_cxs_directa"]["cols"],
    ))
    plano_cxs_droguerias = funcion_acentos(funcion_lectura(
        path=dict_archivos["path_insumos"],
        nom_insumo=dict_archivos["plano_cxs_droguerias"]["nom_base"],
        nom_hoja=dict_archivos["plano_cxs_droguerias"]["nom_hoja"],
        cols=dict_archivos["plano_cxs_droguerias"]["cols"],
    ))
    plano_cxs_indirecta = funcion_acentos(funcion_lectura(
        path=dict_archivos["path_insumos"],
        nom_insumo=dict_archivos["plano_cxs_indirecta"]["nom_base"],
        nom_hoja=dict_archivos["plano_cxs_indirecta"]["nom_hoja"],
        cols=dict_archivos["plano_cxs_indirecta"]["cols"],
    ))
    driver_completo = funcion_acentos(funcion_lectura(
        path=dict_archivos["path_drivers"],
        nom_insumo=dict_archivos["Driver_CxS_P2"]["nom_base"],
        nom_hoja=dict_archivos["Driver_CxS_P2"]["nom_hoja"],
        cols=dict_archivos["Driver_CxS_P2"]["cols"],
    ))
    driver_nit_agentes = funcion_lectura(
        path=dict_archivos["path_drivers"],
        nom_insumo=dict_archivos["Driver_Nit_agente"]["nom_base"],
        nom_hoja=dict_archivos["Driver_Nit_agente"]["nom_hoja"],
        cols=dict_archivos["Driver_Nit_agente"]["cols"],
    )
    driver_completar_planos = funcion_lectura(
        path=dict_archivos["path_drivers"],
        nom_insumo=dict_archivos["Driver_cols_faltantes_planos"]["nom_base"],
        nom_hoja=dict_archivos["Driver_cols_faltantes_planos"]["nom_hoja"],
        cols=dict_archivos["Driver_cols_faltantes_planos"]["cols"],
    )

    # Seleccionamos las columnas necesarias de cada base.
    plano_cxs_cadenas = plano_cxs_cadenas[
        dict_archivos["plano_cxs_cadenas"]["cols_necesarias"]
    ]
    plano_cxs_directa = plano_cxs_directa[
        dict_archivos["plano_cxs_directa"]["cols_necesarias"]
    ]
    plano_cxs_droguerias = plano_cxs_droguerias[
       dict_archivos["plano_cxs_droguerias"]["cols_necesarias"]
    ]
    plano_cxs_indirecta = plano_cxs_indirecta[
        dict_archivos["plano_cxs_indirecta"]["cols_necesarias"]
    ]
    driver_segmento = driver_completo[
         dict_archivos["Driver_CxS_P2"]["cols_necesarias_sa"]
    ]
    driver_nom_clie = driver_completo[
         dict_archivos["Driver_CxS_P2"]["cols_necesarias_nc"]
    ]
    driver_nit_agentes = driver_nit_agentes[dict_archivos["Driver_Nit_agente"]["cols_necesarias"]]

    return {
        "plano_cxs_cadenas" : plano_cxs_cadenas,
        "plano_cxs_directa" : plano_cxs_directa,
        "plano_cxs_indirecta": plano_cxs_indirecta,
        "plano_cxs_droguerias"  : plano_cxs_droguerias,
        "driver_segmento": driver_segmento,
        "driver_nit_agentes": driver_nit_agentes,
        "driver_nom_clie": driver_nom_clie,
        "driver_completar_planos":driver_completar_planos
    }
