# Tabla de Contenido

[introduccion](#Introduccion)
   1.1 [Glosario](#Glosario-de-terminos)
   1.2 [Consultas](#Lista-de-planos-para-la-automatizacion-de-Comercial-Nutresa)
   1.3 [Objetivo](#objetivo-de-la-automatizacion)
   1.4 [Etapas_de_desarrollo](#etapas-del-desarrollo-del-proceso-de-CxS_parte2)
   1.6 [Aclaraciones](#aclaraciones)
   
[Archivos_necesarios_para_la_automatizacion](#archivos-necesarios-para-la-automatización)
   2.1 [Consultas](#Lista-de-consultas-para-la-automatización-de-Comercial-Nutresa)
    2.1.1 [Descripcion_consultas](#descripcion-consultas)
    2.1.2 [Estructura_consultas](#estructura-de-las-consultas)
    2.1.3 [Recomendaciones_consultas](#recomendaciones-consultas)
    2.1.4 [Ubicacion_de_las_consultas_de_ventas.](#ubicacion-de-las-consultas-de-ventas)
   2.2[Drivers](#drivers)
    2.2.1[Driver](#driver)
    2.2.5[Recomendaciones y obligaciones para la manipulación de los Drivers.](#recomendaciones-y-obligaciones-drivers)
   2.3[Archivos_de_ventas](#archivos-de-ventas)
    2.3.1[Archivos_necesarios_de ventas](#archivos-necesarios-de-ventas)

3. [Archivo_config.yml](#archivo-configyml)
   3.1 [Estructura y Desglose. (Resumen)](#Estructura-y-Desglose-(Resumen))
   2.2 [Visualizaciones](#Visualizaciones-del-archivo-(config_yml))
   3.3 [Contenido_y_estructura](#contenido-y-estructura-resumen)
   3.4 [Glosario de constantes](#glosario-de-constantes-de-la-automatización)
   3.5 [Parámetrizaciones_seguimiento a la inversión](#Parametrizaciones-requeridas-para-el-proceso-de-Seguimiento-a-la-inversión)
   3.6 [NO_permitido_modificar](#NO-modificable)
   3.7 [SI_permitido_modificar](#SI-modificable)
   3.8 [Adicional_NO_modificables](#listas-de-información-adicionales-no-modificables)

4. [Responsables](#responsables)

5. [Manual_de_usuario](#enlace-al-manual-de-usuario)

# Proyecto de CxS (Costo por Servil) Parte 2

## Introducción
Este manual contiene toda la información necesaria para el buen uso del asistente del proceso "Automatización de  CxS_P2". Además, se incluye una descripción detallada de archivos, procedimientos e instrucciones sobre el contenido del ejecutable y la estructura de los archivos finales, entre otros.

## Glosario de terminos

| **Término** | **Definición** |
|-------------|----------------|
| **Consultas de información** | Las consultas son las fuentes de información principales, contienen toda la información de relacionada la CXS_P2. En esencia se refieren a archivos del tipo xlsx o csv, que serán cargados procesados y cargados en memoria con diferentes funciones. Se divide en 4 categorías: Plano CXS Directa, Indirecta, Droguerías y Cadenas. Cada consulta contiene un tipo especifico de clientes de CN, y a su vez; a cada consulta se le hacen modificaciones y transformaciones para prepararlas antes de consolidarlas en el insumo del CXS_P2. |
| **Drivers** | En este contexto de trabajo, un driver tiene un significado similar a una consulta. Son las fuentes de información adicionales, contienen toda la información de relacionada el CXS_P2. En esencia se refieren a archivos del tipo xlsx o csv, que serán cargados procesados y cargados en memoria con diferentes funciones. Estos son los archivos auxiliares, modificables, y parametrizables que sirven para modificar principalmente los datos, más no las estructuras de las consultas. |
| **Automatización CXS_P2** | El proceso de CXS_P2 es un asistente que utiliza información de múltiples fuentes de la compañía Comercial Nutresa. De los dos tipos de atención conocidos (Directa e Indirecta), se emplea información de tres consultas de clientes en diferentes etapas conocidas como plantillas. |
| **CXS_P2** | Proceso que genera todas las plantillas necesarias, para actualizar la base de datos del CXS, tanto en los Centros de Costo definidos como en los Centros de Costo del tipo #/#. En la categoría de Tipo "Presupuesto". El proceso permite de manera eficiente recopilar los datos necesarios para el correcto funcionamiento de este proceso en CN. |
| **Centros de Costo** | También llamados Cecos, son clasificaciones donde se cargan todos los gastos operativos y no operativos, que conlleven un costo cuantificable y que se agrupan con el fin de, valga la redundancia, tener un panorama sobre costos, operativos, funcionales, logísticos, nominales y demás dentro de Comercial Nutresa. |



## Objetivo de la automatización
El objetivo se centra en actualizar la base de datos del CxS. Se actualizaran los valores númericos. dados por las columnas: 

      - Ventas_Efectivas
      - Descuentos
      - Gasto_Prom_Comercializadores
      - Descuentos_NG
      - Depuracion_Dctos
      - Dctos_Grupo
      - Ventas_Efectivas_Grupo
      - Descuentos_CN
      - Ventas_Netas_CN
      - Ventas_Netas_Grupo
      - Devoluciones_malas
      - Ventas_Efectivas_Final
      - Total_Gastos_CN

Las columnas en la lista anterior se actualizan de diferente forma dependiendo de un tipo de Centro de Costo especifico los cuales se dividen en: 

### 1.) Centro_Costo #/#
Registros de la base de datos cuyo Centro_Costo = "#/#
Los registros se actualizan utilizando los planos: 
- Plano CXS B2 - Cadenas.xlsx 
- Plano CXS B2 - Directa.xlsx
- Plano CXS B2 - Droguerías.xlsx
- Plano CXS B2 - Indirecta.xlsx 

   ### Columnas que actualiza:

      - Ventas_Efectivas
      - Descuentos
      - Gasto_Prom_Comercializadores
      - Descuentos_NG
      - Depuracion_Dctos
      - Dctos_Grupo
      - Ventas_Efectivas_Grupo
      - Descuentos_CN
      - Ventas_Netas_CN
      - Ventas_Netas_Grupo
      - Devoluciones_malas
      - Ventas_Efectivas_Final
      

### 2.) Centros_Costo (*NO*) #/#
Registros de la base de datos cuyo Centro_Costo != "#/#

Los registros se actualizan utilizando una base de datos auxiliar que se trata como un insumo: La base de datos se conoce como **DistribucionCXS.db** 

   ### Columnas que actualiza
      - Total_Gastos_CN
   
<hr></hr>

### Archivo de actualización. 
El archivo de base de datos sql, sobre el cual se realizan los cambios: **Insumo_cxs_dinamico.bd**

<hr></hr>

## Etapas-del-desarrollo-del-proceso-de-CxS_parte2

| Etapa | Descripción |
|---|---|
| Lectura y procesamiento inicial | Se leen y cargan en memoria los archivos de insumo. (Drivers / Planos / Archivos.db,  todos ubicados en la carpeta insumos y sus subcarpetas.)
| Limpieza y transformación de datos | Se limpian y transforman los diferentes insumos según los requerimientos |
| Creación de drivers | Con base en la información de diferentes insumos se consolida la información correspondiente en un driver que sirven como apoyo para la automatización
| Cálculo de columnas adicionales | Se calculan columnas adicionales con la información disponible. Con base en información que tenemos dentro de los planos modificados y refinados anteriormente. |
| Adición de datos | Se agregan las nuevas columnas calculadas a los planos originales. |

<br></br>
## Aclaraciones

- El proceso de CxS parte 2 tiene como objetivo la modificación de la Base del CXS, generada por la primera parte de esta automatización. Se modifica de dos formas como se aclaró anteriormente. De acuerdo al tipo de centro de Costo. Sea #/# o un Centro de Costo definido (Ejm: GNCH/43000900).

<hr></hr>
<br></br>


# Archivos necesarios para la automatización.

**Nota: Las siglas (NP) se refieren a nombre parámetrizable, es decir, manipulable el nombre del archivo que se debe actualizar posteriormente en el archivo config.yml**

#### <font color=red>**Plano CXS B2 Cadenas.xlsx**</font>

- **Hoja necesaria:**  (NP) 
  - Plano Cadenas
- **Driver necesario:**  (NP) 
  - Drivers.xlxs
- **Insumo generado:** (NP)
  - Plano Cadenas ( Modificación del mismo.)
-  **Tipo de archivo:** Archivo de Excel
- **Formato de archivo:** Archivos Dinámicos / No contiene macros
- **Macros necesarias para el proceso:** Ninguna

![Consulta_No_DS](Img_Readme/Consulta_DS.png)


#### <font color=red>**Plano CXS B2 Directa.xlsx**</font>

* **Nombre:** Consulta CXS Cliente NO_DS
* **Tipo de archivo:** Archivo de Excel
* **Formato de archivo:** Archivos Dinámicos / No contiene macros
* **Macros necesarias para el proceso:** Ninguna
* **Drivers necesarios para el proceso:** Si (Driver_ds, Driver_no_ds)
* **Extensión del archivo:** xlsx
* **Hoja necesaria:** (A parametrizar)
* **Hoja 1**
    * **Nota:** Esta Hoja debe parametrizarse se explicará cómo más adelante.

#### <font color=red>**Plano CXS B2 Directa.xlsx**</font>

#### <font color=red>**Plano CXS B2 Indirecta.xlsx**</font>

#### <font color=red>**Plano CXS B2 Droguerías.xlsx**</font>




