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
        self.estudiante_nombre = ""
    
    def mostrar_login(self):
        """Muestra la pantalla de login para estudiantes"""
        
        with ui.card().classes('w-96 mx-auto mt-32 p-8'):
            ui.icon('groups').classes('text-7xl mx-auto text-green-600')
            ui.label('Acceso Estudiante').classes('text-2xl font-bold text-center mt-4')
            ui.label('Ingresa tus datos para acceder').classes('text-gray-500 text-center mb-6')
            
            # Selector de grado
            grados = self.vm.get_grados_activos()
            grado_opciones = [f"{g['numero']}°" for g in grados]
            grado_ids = {f"{g['numero']}°": g['id'] for g in grados}
            grado_select = ui.select(
                label='Grado',
                options=grado_opciones,
                value=grado_opciones[0] if grado_opciones else None
            ).classes('w-full')
            
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
                if not grado_select.value or not grupo_select.value:
                    error_label.set_text('Selecciona grado y grupo')
                    return
                
                grado_id = grado_ids[grado_select.value]
                grupo_id = grupo_ids[grupo_select.value]
                
                if self.vm.validar_contraseña(grado_id, grupo_id, password_input.value):
                    self.is_authenticated = True
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
                                            # Descargar archivo
                                            ui.button(
                                                f'📄 {material.nombre}', 
                                                on_click=lambda m=material: ui.download(m.url),
                                                color='blue'
                                            ).props('flat')
                                        else:
                                            # Abrir link
                                            ui.link(
                                                f'🔗 {material.nombre}', 
                                                material.url, 
                                                new_tab=True
                                            ).classes('text-blue-500')
                        
                        with ui.column().classes('gap-2'):
                            # Botón para subir entrega
                            ui.button(
                                '📤 Subir Entrega', 
                                on_click=lambda a_id=actividad.id, a_nom=actividad.nombre: self.mostrar_subir_entrega(a_id, a_nom),
                                color='green'
                            )
    
    def mostrar_subir_entrega(self, actividad_id: int, actividad_nombre: str):
        """Muestra el diálogo para subir una entrega"""
        
        with ui.dialog() as dialog, ui.card().classes('w-[500px]'):
            ui.label(f'Subir Entrega: {actividad_nombre}').classes('text-xl font-bold mb-4')
            
            nombre_input = ui.input('Tu nombre completo', placeholder='Ej: Juan Pérez').classes('w-full')
            companero_input = ui.input('Compañero/a (opcional)', placeholder='Ej: María Gómez').classes('w-full mt-2')
            comentarios_input = ui.textarea('Comentarios (opcional)', placeholder='Notas adicionales para el profesor').classes('w-full mt-2')
            
            ui.label('Archivo a entregar (máx 5MB):').classes('mt-4 font-bold')
            file_input = ui.upload(
                label='Seleccionar archivo',
                on_upload=lambda e: guardar_entrega(e)
            ).classes('w-full')
            
            error_label = ui.label('').classes('text-red-500 text-sm mt-2')
            
            async def guardar_entrega(e):
                if not nombre_input.value:
                    error_label.set_text('El nombre es requerido')
                    return
                
                archivo = e.file
                nombre_archivo = archivo.name
                
                # Validar tamaño
                if archivo.size() > 5 * 1024 * 1024:
                    error_label.set_text('El archivo excede 5MB')
                    return
                
                from datetime import datetime
                import shutil
                from utils.file_manager import get_entregas_path
                
                # Obtener rutas
                periodo = self.vm.get_periodo_activo()
                grado_num = self.vm.current_grado.numero
                grupo_letra = self.vm.current_grupo.letra
                entregas_path = get_entregas_path(periodo.id, grado_num, grupo_letra, actividad_id)
                entregas_path.mkdir(parents=True, exist_ok=True)
                
                # Contar entregas existentes del estudiante para el identificador
                entregas_existentes = list(entregas_path.glob(f"{nombre_input.value}*"))
                identificador = len(entregas_existentes) + 1
                
                # Crear nombre final: nombreestudiante_archivo_identificador.ext
                from pathlib import Path
                extension = Path(nombre_archivo).suffix
                nombre_final = f"{nombre_input.value}_{Path(nombre_archivo).stem}_{identificador:03d}{extension}"
                
                # Guardar archivo
                file_path = entregas_path / nombre_final
                await archivo.save(str(file_path))
                
                # Guardar en BD
                from models.entities import Entrega
                nueva_entrega = Entrega(
                    actividad_id=actividad_id,
                    estudiante_nombre=nombre_input.value,
                    companero_nombre=companero_input.value if companero_input.value else None,
                    comentarios=comentarios_input.value if comentarios_input.value else None,
                    archivo_nombre=nombre_archivo,
                    archivo_ruta=str(file_path)
                )
                self.vm.db.add(nueva_entrega)
                self.vm.db.commit()
                
                ui.notify(f'✅ Entrega "{nombre_archivo}" subida', type='positive')
                dialog.close()
            
            ui.button('Cancelar', on_click=dialog.close).classes('mt-4 w-full')
    
    def cerrar_sesion(self):
        """Cierra la sesión del estudiante"""
        self.is_authenticated = False
        self.vm.cerrar()
        ui.navigate.to('/estudiante')
        ui.notify('Sesión cerrada', type='info')