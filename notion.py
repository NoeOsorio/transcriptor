import os
from notion_client import Client
from dotenv import load_dotenv
import inquirer
from datetime import datetime
import re
from utils import dividir_texto

# Cargar variables de entorno
load_dotenv()

# Token de la integración de Notion
NOTION_API_KEY = os.getenv('NOTION_API_KEY')

# Inicializar el cliente de Notion
notion = Client(auth=NOTION_API_KEY)

# Función para obtener las bases de datos disponibles


def listar_bases_de_datos():
    try:
        # Buscamos bases de datos utilizando la búsqueda de la API
        response = notion.search(
            filter={"property": "object", "value": "database"})

        # Extraemos los nombres y los IDs de las bases de datos
        bases_de_datos = [(db["title"][0]["text"]["content"], db["id"])
                          for db in response["results"] if "title" in db and db["title"]]

        # Verificamos si hay bases de datos disponibles
        if not bases_de_datos:
            print("No se encontraron bases de datos disponibles.")
            return None

        # Creamos una lista seleccionable usando inquirer
        preguntas = [
            inquirer.List(
                "base_de_datos",
                message="Selecciona una base de datos en Notion:",
                choices=[db[0]
                         for db in bases_de_datos]  # Mostrar solo los nombres
            )
        ]
        respuesta = inquirer.prompt(preguntas)

        # Devolver el ID de la base de datos seleccionada
        for nombre, db_id in bases_de_datos:
            if nombre == respuesta["base_de_datos"]:
                return db_id

    except Exception as e:
        print(f"Error al obtener las bases de datos: {e}")
        return None


# Función para crear una nueva página en Notion en la base de datos seleccionada
def guardar_en_notion(texto_md, titulo):
    # Obtener la base de datos seleccionada
    database_id = os.getenv('NOTION_DEFAULT_DB') or listar_bases_de_datos()
    # database_id = listar_bases_de_datos()

    if database_id is None:
        print("No se pudo seleccionar ninguna base de datos.")
        return

    try:
        # Crear una nueva página en la base de datos seleccionada
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "title": [
                    {
                        "text": {
                            "content": titulo
                        }
                    }
                ]
            },
            children=[
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {
                                    "content": texto_md
                                }
                            }
                        ]
                    }
                }
            ]
        )
        print(f"Página '{titulo}' guardada exitosamente en Notion.")
    except Exception as e:
        print(f"Error al guardar en Notion: {e}")

# Función para guardar todo en una página de Notion, agregando solo los campos que se pasan
# Función para guardar en Notion en varios lotes si excede los 100 bloques


def guardar_en_notion_en_misma_pagina(titulo, transcripcion=None, script=None, key_points=None):
    # Obtener la base de datos seleccionada
    database_id = os.getenv('NOTION_DEFAULT_DB') or listar_bases_de_datos()

    if database_id is None:
        print("No se pudo seleccionar ninguna base de datos.")
        return

    try:
        # Crear bloques de contenido
        children_blocks = []

        # Agregar la sección de los puntos clave solo si se proporciona
        if key_points:
            children_blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Puntos clave"}}]
                }
            })
            key_points_bloques = convertir_md_a_bloques(key_points)
            children_blocks.extend(key_points_bloques)

         # Agregar la sección del script solo si se proporciona
        if script:
            children_blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Script"}}]
                }
            })
            script_bloques = convertir_md_a_bloques(script)
            children_blocks.extend(script_bloques)

        # Agregar la sección de transcripción solo si se proporciona
        if transcripcion:
            children_blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Transcripción"}}]
                }
            })
            transcripcion_bloques = convertir_md_a_bloques(transcripcion)
            children_blocks.extend(transcripcion_bloques)

        # Verificar que haya al menos un bloque para crear la página
        if not children_blocks:
            print("No hay contenido para agregar a Notion.")
            return

        # Dividir los bloques en lotes de 100
        bloques_en_lotes = dividir_texto(children_blocks, max_length=100)

        # Crear la página con el primer lote de bloques
        response = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "title": [
                    {
                        "text": {
                            "content": titulo
                        }
                    }
                ]
            },
            children=bloques_en_lotes[0]  # Primer lote de hasta 100 bloques
        )

        # Si hay más de 100 bloques, hacer solicitudes adicionales para agregar el resto
        if len(bloques_en_lotes) > 1:
            page_id = response["id"]  # Obtener el ID de la página creada
            for lote in bloques_en_lotes[1:]:
                notion.blocks.children.append(block_id=page_id, children=lote)

        print(f"Página '{
              titulo}' guardada exitosamente en Notion con todas las secciones proporcionadas.")
    except Exception as e:
        print(f"Error al guardar en Notion: {e}")

# Función para procesar y agregar a Notion después de la transcripción


def procesar_y_guardar_en_notion(nombre_del_archivo, transcripcion, script=None, key_points=None):
    fecha_actual = datetime.now().strftime('%Y-%m-%d')

    # Guardar todo en la misma página en Notion
    guardar_en_notion_en_misma_pagina(
        f"{nombre_del_archivo} - {fecha_actual}", transcripcion, script, key_points)


# Función para convertir Markdown a bloques de Notion con negritas, cursivas y otros formatos
def convertir_md_a_bloques(texto_md, max_length=2000):
    bloques = []
    lineas = texto_md.splitlines()

    for linea in lineas:
        # Convertir encabezados
        if linea.startswith("### "):
            bloques.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": linea[4:]}}]
                }
            })
        elif linea.startswith("## "):
            bloques.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": linea[3:]}}]
                }
            })
        elif linea.startswith("# "):
            bloques.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": linea[2:]}}]
                }
            })
        # Convertir separadores ---
        elif linea.strip() == "---":
            bloques.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        # Convertir listas ordenadas
        elif re.match(r"^\d+\.\s", linea):
            bloques.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": linea}}]
                }
            })
        # Convertir listas no ordenadas
        elif linea.startswith("- "):
            bloques.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": linea[2:]}}]
                }
            })
        else:
            # Procesar negritas y cursivas dentro de la línea
            rich_text = []
            posicion = 0

            # Buscar patrones de negritas (**texto**) y cursivas (*texto*)
            for match in re.finditer(r"(\*\*(.*?)\*\*|\*(.*?)\*)", linea):
                start, end = match.span()
                if start > posicion:
                    fragmentos_texto = dividir_texto(linea[posicion:start], max_length)  # Dividir si es muy largo
                    for fragmento in fragmentos_texto:
                        rich_text.append({
                            "type": "text",
                            "text": {
                                "content": fragmento
                            }
                        })
                if match.group(1).startswith("**"):
                    # Negrita
                    fragmentos_negrita = dividir_texto(match.group(2), max_length)  # Dividir si es muy largo
                    for fragmento in fragmentos_negrita:
                        rich_text.append({
                            "type": "text",
                            "text": {
                                "content": fragmento
                            },
                            "annotations": {"bold": True}
                        })
                elif match.group(1).startswith("*"):
                    # Cursiva
                    fragmentos_cursiva = dividir_texto(match.group(3), max_length)  # Dividir si es muy largo
                    for fragmento in fragmentos_cursiva:
                        rich_text.append({
                            "type": "text",
                            "text": {
                                "content": fragmento
                            },
                            "annotations": {"italic": True}
                        })
                posicion = end

            # Agregar el resto del texto después del último formato encontrado
            if posicion < len(linea):
                fragmentos_restantes = dividir_texto(linea[posicion:], max_length)  # Dividir si es muy largo
                for fragmento in fragmentos_restantes:
                    rich_text.append({
                        "type": "text",
                        "text": {
                            "content": fragmento
                        }
                    })

            # Dividir la línea en fragmentos si excede los 2000 caracteres
            if len(rich_text) > 0:
                bloques.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": rich_text
                    }
                })

    return bloques
