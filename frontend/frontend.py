import flet as ft
import requests

# Dirección de la API.
API_URL = "http://127.0.0.1:8000/libros/"

def main(page: ft.Page):
    # Ajustes de la ventana.
    page.title = "Libros asteca"
    page.padding = 45
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO

    # Guarda el libro que se está editando.
    libro_id_en_edicion = None

    # Datos del formulario.
    txt_titulo = ft.TextField(label="Título")
    txt_autor = ft.TextField(label="Autor")
    txt_genero = ft.TextField(label="Género")
    txt_anio = ft.TextField(label="Año de publicación")
    txt_ejemplares = ft.TextField(label="Número de Ejemplares")

    # Tabla donde aparecen los libros.
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Título")),
            ft.DataColumn(ft.Text("Autor")),
            ft.DataColumn(ft.Text("Género")),
            ft.DataColumn(ft.Text("Año de publicación")),
            ft.DataColumn(ft.Text("Número de Ejemplares")),
            ft.DataColumn(ft.Text("Acciones")), 
        ],
        rows=[]
    )
    
    # Muestra avisos al usuario.
    def mostrar_mensaje(texto, es_error=False):
        # Rojo indica error; verde, éxito.
        aviso = ft.SnackBar(
            content=ft.Text(texto, color=ft.Colors.WHITE),
            bgcolor=(ft.Colors.RED_600 if es_error else ft.Colors.GREEN_600),
            open=True,
        )
        page.overlay.append(aviso)
        page.update()

    # Deja el formulario vacío.
    def limpiar_formulario():
        # Regresa al modo de creación.
        nonlocal libro_id_en_edicion
        libro_id_en_edicion = None
        txt_titulo.value = ""
        txt_autor.value = ""
        txt_genero.value = ""
        txt_anio.value = ""
        txt_ejemplares.value = ""
        btn_guardar.text = "guardar libro"
        page.update()

    # Carga un libro para editarlo.
    def cargar_datos_para_editar(libro):
        # Copia sus datos en los campos.
        nonlocal libro_id_en_edicion
        libro_id_en_edicion = libro["id"]
        txt_titulo.value = str(libro.get("titulo", ""))
        txt_autor.value = str(libro.get("autor", ""))
        txt_genero.value = str(libro.get("genero", ""))
        txt_anio.value = str(libro.get("anio_publicacion", ""))
        txt_ejemplares.value = str(libro.get("ejemplares", ""))
        btn_guardar.text = "actualizar libro"
        page.update()

    # Elimina un libro.
    def eliminar_libro_click(libro_id):
        # Envía el ID a la API.
        try:
            url = f"{API_URL.rstrip('/')}/{libro_id}"
            respuesta = requests.delete(url, timeout=5)
            if respuesta.status_code == 200:
                mostrar_mensaje("Libro eliminado correctamente", es_error=False)
                cargar_libros()
            else:
                mostrar_mensaje("Error al eliminar el libro", es_error=True)
        except requests.ConnectionError:
            mostrar_mensaje("No se puede conectar a la API", es_error=True)

    # Consulta todos los libros.
    def cargar_libros():
        # Actualiza las filas de la tabla.
        try:
            respuesta = requests.get(API_URL, timeout=5)
            respuesta.raise_for_status()

            libros = respuesta.json()
            tabla.rows.clear()
            
            for libro in libros:
                # Acción para modificar.
                btn_update = ft.ElevatedButton(
                    "UPDATE",
                    color=ft.Colors.BLACK,
                    bgcolor=ft.Colors.AMBER_400,
                    on_click=lambda e, l=libro: cargar_datos_para_editar(l)
                )
                
                # Acción para borrar.
                btn_delete = ft.ElevatedButton(
                    "DELETE",
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.RED_600,
                    on_click=lambda e, id_l=libro["id"]: eliminar_libro_click(id_l)
                )

                # Fila con los datos del libro.
                fila = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(libro["id"]))),
                        ft.DataCell(ft.Text(str(libro["titulo"]))),
                        ft.DataCell(ft.Text(str(libro["autor"]))),
                        ft.DataCell(ft.Text(str(libro["genero"]))),
                        ft.DataCell(ft.Text(str(libro["anio_publicacion"]))),
                        ft.DataCell(ft.Text(str(libro["ejemplares"]))),
                        ft.DataCell(ft.Row([btn_update, btn_delete])),
                    ]
                )
                tabla.rows.append(fila)
            page.update()
        except requests.exceptions.RequestException as e:
            print("Error al cargar los libros:", e)

    def obtener_datos_formulario():
        # Prepara los datos para enviar.
        return {
            "titulo": txt_titulo.value,
            "autor": txt_autor.value, 
            "genero": txt_genero.value,
            "anio_publicacion": txt_anio.value,
            "ejemplares": txt_ejemplares.value, 
        }
        
    # Crea o actualiza un registro.
    def crear_o_actualizar_libro(e):
        # El ID decide entre POST y PUT.
        if not txt_titulo.value or not txt_autor.value:
            mostrar_mensaje("por favor, complete los datos obligatorios", es_error=True)
            return
        
        datos = obtener_datos_formulario()

        try:
            # Sin ID: crear.
            if libro_id_en_edicion is None:
                respuesta = requests.post(API_URL, json=datos, timeout=60)
                if respuesta.status_code == 201:
                    mostrar_mensaje("libro creado exitosamente", es_error=False) 
                    limpiar_formulario()
                    cargar_libros()
                else:
                    mostrar_mensaje("Error al crear el libro", es_error=True)
            # Con ID: actualizar.
            else:
                url = f"{API_URL.rstrip('/')}/{libro_id_en_edicion}"
                respuesta = requests.put(url, json=datos, timeout=50)
                if respuesta.status_code == 200:
                    mostrar_mensaje("libro actualizado exitosamente", es_error=False)
                    limpiar_formulario()
                    cargar_libros()
                else:
                    mostrar_mensaje("Error al actualizar el libro", es_error=True)

        except requests.ConnectionError:
            mostrar_mensaje("no se puede conectar a la API", es_error=True)
            
    # Botón principal del formulario.
    btn_guardar = ft.ElevatedButton(
        "guardar libro",
        on_click=crear_o_actualizar_libro,
    )
    
    # Coloca los controles en pantalla.
    page.add(
        ft.Text("Libros asteca", size=30, weight=ft.FontWeight.BOLD),
        ft.Column(
            [txt_titulo, txt_autor, txt_genero, txt_anio, txt_ejemplares],
        ),
        btn_guardar,
        tabla,
    )
    
    # Carga los datos al iniciar.
    cargar_libros()

# Inicia la aplicación web.
if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER)