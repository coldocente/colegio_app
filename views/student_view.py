"""
Vista de estudiantes - Interfaz con NiceGUI
"""
from nicegui import ui
from viewmodels.student_vm import StudentViewModel
from pathlib import Path

class StudentView:
    """Vista del panel de estudiantes"""
    
    def __init__(self):
        self.vm = StudentViewModel()
        self.is_authenticated = False
        self.estudiante_actual = ""
    
    def mostrar_login(self):
        """Muestra la pantalla de login para estudiantes"""
        
        with ui.card().classes('w-96 mx-auto mt-32 p-8'):
            ui.icon('groups').classes('text-7xl mx-auto text-green-600')
            ui.label('Acceso Estudiante').classes('text-2xl font-bold text-center mt-4')
            ui.label('Ingresa tus datos para acceder').classes('text-gray-500 text-center mb-6')
            
            # Campo de nombre
            nombre_input = ui.input('Tu nombre completo', placeholder='Ej: Juan Pérez').classes('w-full')
            
            # Selector de grado
            grados = self.vm.get_grados_activos()
            grado_opciones = [f"{g['numero']}°" for g in grados]
            grado_ids = {f"{g['numero']}°": g['id'] for g in grados}
            grado_select = ui.select(
                label='Grado',
                options=grado_opciones,
                value=grado_opciones[0] if grado_opciones else None
            ).classes('w-full mt-2')
            
            # Selector de grupo
            grupos = self.vm.get_grupos_activos()
            grupo_opciones = [f"Grupo {g['letra']}" for g in grupos]
            grupo_ids = {f"Grupo {g['letra']}": g['id'] for g in grupos}
            grupo_select = ui.select(
                label='Grupo',
                options=grupo_opciones,
                value=grupo_opciones[0] if grupo_opciones else None
            ).classes('w-full mt-2')
            
            # Campo de contraseña
            password_input = ui.input('Contraseña del grupo', password=True, password_toggle_button=True).classes('w-full mt-2')
            
            error_label = ui.label('').classes('text-red-500 text-sm mt-2')
            
            def ingresar():
                if not nombre_input.value:
                    error_label.set_text('El nombre es requerido')
                    return
                
                if not grado_select.value or not grupo_select.value:
                    error_label.set_text('Selecciona grado y grupo')
                    return
                
                grado_id = grado_ids[grado_select.value]
                grupo_id = grupo_ids[grupo_select.value]
                
                if self.vm.validar_contraseña(grado_id, grupo_id, password_input.value):
                    self.is_authenticated = True
                    self.estudiante_actual = nombre_input.value  # Guardar el nombre
                    error_label.set_text('')
                    ui.notify('✅ Acceso concedido', type='positive')
                    ui.navigate.to('/estudiante/panel')
                else:
                    error_label.set_text('❌ Contraseña incorrecta o grupo inactivo')
                    ui.notify('Contraseña incorrecta', type='negative')
            
            ui.button('Ingresar', on_click=ingresar, icon='login', color='green').classes('w-full mt-4')
            ui.link('← Volver al inicio', '/').classes('text-center mt-4 block')
    
    def mostrar_panel(self):
        """Muestra el panel de actividades para el estudiante"""
        
        periodo = self.vm.get_periodo_activo()
        periodo_nombre = periodo.nombre if periodo else "Periodo activo"
        
        with ui.header(elevated=True).classes('bg-green-800'):
            with ui.row().classes('w-full justify-between items-center p-4'):
                ui.label(f'Panel de Estudiante - {periodo_nombre}').classes('text-2xl font-bold text-white')
                with ui.row().classes('gap-4 items-center'):
                    grado_letra = f"{self.vm.current_grado.numero}°{self.vm.current_grupo.letra}" if self.vm.current_grado else ""
                    ui.label(f'👤 {self.estudiante_actual}').classes('text-white')
                    ui.label(f'📚 {grado_letra}').classes('text-white')
                    ui.button('🚪 Salir', on_click=self.cerrar_sesion, icon='logout', color='red').props('flat')
        
        with ui.column().classes('p-8 w-full'):
            ui.label('Actividades Disponibles').classes('text-2xl font-bold mb-4')
            
            actividades = self.vm.get_actividades_activas(periodo.id if periodo else 1)
            
            if not actividades:
                with ui.card().classes('w-full p-8 text-center bg-gray-50'):
                    ui.icon('inbox').classes('text-6xl text-gray-400 mx-auto')
                    ui.label('No hay actividades activas en este momento').classes('text-gray-500 mt-4')
                return
            
            for actividad in actividades:
                with ui.card().classes('w-full mb-6 border-l-8 border-green-500'):
                    with ui.row().classes('w-full justify-between items-start p-4'):
                        with ui.column().classes('flex-1'):
                            ui.label(actividad.nombre).classes('text-xl font-bold')
                            if actividad.descripcion:
                                ui.label(actividad.descripcion).classes('text-gray-600 mt-1')
                            
                            # Materiales
                            materiales = self.vm.get_materiales_actividad(actividad.id)
                            if materiales:
                                ui.label('Materiales:').classes('font-bold mt-3')
                                with ui.row().classes('gap-2 mt-1 flex-wrap'):
                                    for material in materiales:
                                        if material.tipo == 'archivo':
                                            ui.button(
                                                f'📄 {material.nombre}', 
                                                on_click=lambda m=material: ui.download(m.url),
                                                color='blue'
                                            ).props('flat')
                                        else:
                                            ui.link(
                                                f'🔗 {material.nombre}', 
                                                material.url, 
                                                new_tab=True
                                            ).classes('text-blue-500')
                            
                            # Mostrar si ya entregó
                            # Mostrar si ya entregó
                            from models.entities import Entrega
                            entrega_existente = self.vm.db.query(Entrega).filter(
                                Entrega.actividad_id == actividad.id,
                                Entrega.estudiante_nombre == self.estudiante_actual
                            ).first()

                            if entrega_existente:
                                with ui.row().classes('mt-3 items-center gap-2'):
                                    ui.icon('check_circle', size='20px').classes('text-green-600')
                                    # Mostrar si es entrega en pareja
                                    if entrega_existente.companero_nombre:
                                        ui.label(f'✅ Entregaste con {entrega_existente.companero_nombre}: {entrega_existente.archivo_nombre}').classes('text-green-600 text-sm')
                                    else:
                                        ui.label(f'✅ Entregaste: {entrega_existente.archivo_nombre}').classes('text-green-600 text-sm')
                                    ui.label(f'({entrega_existente.fecha_hora.strftime("%d/%m/%Y %H:%M")})').classes('text-gray-500 text-xs')
                        
                        with ui.column().classes('gap-2'):
                            # Botón para subir entrega (solo si no ha entregado)
                            # Botón para subir entrega
                            if not entrega_existente:
                                ui.button(
                                    '📤 Subir Entrega', 
                                    on_click=lambda a_id=actividad.id, a_nom=actividad.nombre: self.mostrar_subir_entrega(a_id, a_nom),
                                    color='green'
                                )
                            else:
                                ui.button(
                                    '🔄 Reemplazar Entrega', 
                                    on_click=lambda a_id=actividad.id, a_nom=actividad.nombre: self.mostrar_subir_entrega(a_id, a_nom),
                                    color='orange'
                                ).props('flat')

    def mostrar_subir_entrega(self, actividad_id: int, actividad_nombre: str):
        """Muestra el diálogo para subir una entrega"""
        
        # Crear el diálogo
        dialog = ui.dialog()
        
        with dialog, ui.card().classes('w-[550px]'):
            ui.label(f'Subir Entrega: {actividad_nombre}').classes('text-xl font-bold mb-4')
            
            # Mostrar nombre del estudiante (solo lectura)
            ui.label('Estudiante:').classes('text-sm text-gray-600 mt-2')
            ui.label(self.estudiante_actual).classes('text-gray-800 bg-gray-100 p-2 rounded w-full')
            
            # Campo de compañero
            ui.label('Compañero/a (opcional):').classes('text-sm text-gray-600 mt-2')
            companero_input = ui.input(placeholder='Ej: María Gómez').classes('w-full')
            
            # Campo de comentarios
            ui.label('Comentarios (opcional):').classes('text-sm text-gray-600 mt-2')
            comentarios_input = ui.textarea(placeholder='Notas adicionales para el profesor').classes('w-full')
            
            # Archivo
            ui.label('Archivo a entregar (máx 5MB):').classes('text-sm text-gray-600 mt-2 font-bold')
            
            # Mostrar estado del archivo
            archivo_seleccionado = ui.label('').classes('text-green-600 text-sm mt-1')
            
            # Variable para almacenar el archivo
            archivo_guardado = {'archivo': None, 'nombre': None}
            
            def on_upload(e):
                """Cuando se selecciona un archivo"""
                archivo_guardado['archivo'] = e.file
                archivo_guardado['nombre'] = e.file.name
                archivo_seleccionado.set_text(f'✅ Archivo seleccionado: {e.file.name}')
                ui.notify(f'Archivo cargado: {e.file.name}', type='positive')
            
            ui.upload(on_upload=on_upload).classes('w-full mt-1')
            
            # Mensajes de error
            error_label = ui.label('').classes('text-red-500 text-sm mt-2')
            
            async def guardar_entrega():
                """Guarda la entrega"""
                try:
                    # Validaciones
                    if not archivo_guardado['archivo']:
                        error_label.set_text('❌ Debes seleccionar un archivo')
                        return
                    
                    archivo = archivo_guardado['archivo']
                    nombre_archivo_original = archivo_guardado['nombre']
                    
                    # Validar tamaño
                    if archivo.size() > 5 * 1024 * 1024:
                        error_label.set_text('❌ El archivo excede 5MB')
                        return
                    
                    from pathlib import Path
                    from utils.file_manager import get_entregas_path
                    import re
                    
                    # Obtener rutas
                    periodo = self.vm.get_periodo_activo()
                    grado_num = self.vm.current_grado.numero
                    grupo_letra = self.vm.current_grupo.letra
                    
                    entregas_path = get_entregas_path(periodo.id, grado_num, grupo_letra, actividad_id)
                    entregas_path.mkdir(parents=True, exist_ok=True)
                    
                    # Obtener nombres
                    nombre_estudiante = self.estudiante_actual
                    nombre_companero = companero_input.value if companero_input.value else None
                    
                    # Limpiar nombres
                    def limpiar_nombre(nombre):
                        return re.sub(r'[^a-z0-9]', '_', nombre.lower())
                    
                    nombre_estudiante_limpio = limpiar_nombre(nombre_estudiante)
                    
                    if nombre_companero:
                        nombre_companero_limpio = limpiar_nombre(nombre_companero)
                        nombre_base = f"{nombre_estudiante_limpio}_{nombre_companero_limpio}"
                    else:
                        nombre_base = nombre_estudiante_limpio
                    
                    # Limpiar nombre del archivo
                    nombre_sin_ext = Path(nombre_archivo_original).stem
                    nombre_archivo_limpio = limpiar_nombre(nombre_sin_ext)
                    
                    # Contar entregas existentes
                    patron = re.compile(rf"^{re.escape(nombre_base)}_.*")
                    existentes = [f for f in entregas_path.iterdir() if patron.match(f.name)]
                    identificador = len(existentes) + 1
                    
                    # Nombre final
                    extension = Path(nombre_archivo_original).suffix
                    nombre_final = f"{nombre_base}_{nombre_archivo_limpio}_{identificador:03d}{extension}"
                    
                    # Guardar archivo
                    file_path = entregas_path / nombre_final
                    await archivo.save(str(file_path))
                    
                    # Guardar en BD
                    from models.entities import Entrega
                    
                    entrega_existente = self.vm.db.query(Entrega).filter(
                        Entrega.actividad_id == actividad_id,
                        Entrega.estudiante_nombre == nombre_estudiante
                    ).first()
                    
                    if entrega_existente:
                        # Eliminar archivo viejo
                        ruta_vieja = Path(entrega_existente.archivo_ruta)
                        if ruta_vieja.exists():
                            ruta_vieja.unlink()
                        
                        entrega_existente.companero_nombre = nombre_companero
                        entrega_existente.comentarios = comentarios_input.value
                        entrega_existente.archivo_nombre = nombre_archivo_original
                        entrega_existente.archivo_ruta = str(file_path)
                        self.vm.db.commit()
                        ui.notify('✅ Entrega reemplazada', type='positive')
                    else:
                        nueva_entrega = Entrega(
                            actividad_id=actividad_id,
                            estudiante_nombre=nombre_estudiante,
                            companero_nombre=nombre_companero,
                            comentarios=comentarios_input.value,
                            archivo_nombre=nombre_archivo_original,
                            archivo_ruta=str(file_path)
                        )
                        self.vm.db.add(nueva_entrega)
                        self.vm.db.commit()
                        ui.notify('✅ Entrega guardada', type='positive')
                    
                    dialog.close()
                    ui.navigate.to('/estudiante/panel')
                    
                except Exception as err:
                    error_label.set_text(f'❌ Error: {err}')
                    print(f"Error: {err}")
                    import traceback
                    traceback.print_exc()
            
            # Botones
            with ui.row().classes('gap-2 w-full mt-4 justify-end'):
                ui.button('Cancelar', on_click=dialog.close).props('flat')
                ui.button('Guardar Entrega', on_click=guardar_entrega, color='green')
        
        # Abrir el diálogo
        dialog.open()
    
    def cerrar_sesion(self):
        """Cierra la sesión del estudiante"""
        self.is_authenticated = False
        self.estudiante_actual = None
        self.vm.cerrar()
        ui.navigate.to('/estudiante')
        ui.notify('Sesión cerrada', type='info')   