"""
Vista de administrador - Interfaz con NiceGUI
"""
from nicegui import ui
from viewmodels.admin_vm import AdminViewModel
from models.entities import Grado, Grupo, GradoGrupo, Actividad  # Importar todo lo necesario

class AdminView:
    """Vista del panel de administrador"""
    
    def __init__(self):
        self.vm = AdminViewModel()
        self.is_authenticated = False
        
    def mostrar_login(self):
        """Muestra la pantalla de login del administrador"""
        
        with ui.card().classes('w-96 mx-auto mt-32 p-8'):
            ui.icon('school').classes('text-7xl mx-auto text-blue-600')
            ui.label('Acceso Docente').classes('text-2xl font-bold text-center mt-4')
            ui.label('Ingresa tu contraseña').classes('text-gray-500 text-center mb-6')
            
            password_input = ui.input('Contraseña', password=True, password_toggle_button=True).classes('w-full')
            
            error_label = ui.label('').classes('text-red-500 text-sm mt-2')
            
            def verificar():
                if self.vm.verificar_login(password_input.value):
                    self.is_authenticated = True
                    error_label.set_text('')
                    ui.notify('✅ Acceso concedido', type='positive')
                    ui.navigate.to('/admin/dashboard')
                else:
                    error_label.set_text('❌ Contraseña incorrecta')
                    ui.notify('Contraseña incorrecta', type='negative')
            
            ui.button('Ingresar', on_click=verificar, icon='login').classes('w-full mt-4 py-2')
            ui.link('← Volver al inicio', '/').classes('text-center mt-4 block')
    
    def mostrar_dashboard(self):
        """Muestra el dashboard principal del administrador"""
        
        periodo = self.vm.get_periodo_activo()
        periodo_nombre = periodo.nombre if periodo else "No definido"
        
        with ui.header(elevated=True).classes('bg-blue-800'):
            with ui.row().classes('w-full justify-between items-center p-4'):
                ui.label('Panel de Administración').classes('text-2xl font-bold text-white')
                with ui.row().classes('gap-4 items-center'):
                    ui.label(f'📅 {periodo_nombre}').classes('text-white')
                    ui.button('🚪 Cerrar sesión', on_click=self.cerrar_sesion, icon='logout', color='red').props('flat')
        
        # Tabs
        with ui.tabs().classes('w-full bg-gray-100') as tabs:
            dashboard_tab = ui.tab('📊 Dashboard')
            grados_tab = ui.tab('📚 Grados y Grupos')
            actividades_tab = ui.tab('📝 Actividades')
        
        with ui.tab_panels(tabs, value=dashboard_tab).classes('w-full p-4'):
            # Panel Dashboard
            with ui.tab_panel(dashboard_tab):
                with ui.card().classes('w-full p-6'):
                    ui.label('Bienvenido al Dashboard').classes('text-2xl font-bold')
                    ui.label('Estadísticas generales del sistema').classes('text-gray-600 mt-2')
                    
                    # Contenedor para tarjetas de estadísticas (para poder actualizarlas)
                    stats_container = ui.column()
                    
                    def refresh_stats():
                        """Actualiza las tarjetas de estadísticas"""
                        stats_container.clear()
                        with stats_container:
                            with ui.row().classes('gap-6 mt-6 w-full justify-center'):
                                # Tarjeta Grados
                                with ui.card().classes('text-center p-4 w-48 bg-blue-50'):
                                    ui.icon('school').classes('text-4xl text-blue-600 mx-auto')
                                    ui.label('Grados').classes('text-gray-600 mt-2')
                                    grados_activos = len(self.vm.get_grados_activos())
                                    ui.label(str(grados_activos)).classes('text-3xl font-bold text-blue-600')
                                
                                # Tarjeta Grupos
                                with ui.card().classes('text-center p-4 w-48 bg-green-50'):
                                    ui.icon('group').classes('text-4xl text-green-600 mx-auto')
                                    ui.label('Grupos').classes('text-gray-600 mt-2')
                                    grupos_activos = len(self.vm.get_grupos_activos())
                                    ui.label(str(grupos_activos)).classes('text-3xl font-bold text-green-600')
                                
                                # Tarjeta Clases activas (ahora se actualizará correctamente)
                                with ui.card().classes('text-center p-4 w-48 bg-orange-50'):
                                    ui.icon('class').classes('text-4xl text-orange-600 mx-auto')
                                    ui.label('Clases activas').classes('text-gray-600 mt-2')
                                    combinaciones = self.vm.get_combinaciones_grado_grupo()
                                    clases_activas = sum(1 for c in combinaciones if c['activo'])
                                    ui.label(str(clases_activas)).classes('text-3xl font-bold text-orange-600')
                    
                    # Inicializar stats
                    refresh_stats()
                    
                    # Nota: las stats se actualizarán cuando se cambie el estado desde la pestaña Grados
                    ui.label('💡 Los cambios en grados/grupos se reflejan automáticamente').classes('text-gray-400 text-sm mt-6 text-center')
            
            # Panel Grados y Grupos
            with ui.tab_panel(grados_tab):
                with ui.card().classes('w-full p-6'):
                    ui.label('Gestión de Grados y Grupos').classes('text-2xl font-bold mb-4')
                    ui.label('Organizados por grado (cada fila es un grado)').classes('text-gray-600 mb-6')
                    self.mostrar_gestion_grados_grupos(refresh_stats_callback=refresh_stats)
            
            # Panel Actividades (completo corregido - con strings en selects)
            with ui.tab_panel(actividades_tab):
                with ui.card().classes('w-full p-6'):
                    ui.label('Gestión de Actividades').classes('text-2xl font-bold mb-4')
                    ui.label('Selecciona un grado y grupo para gestionar sus actividades').classes('text-gray-600 mb-6')
                    
                    # Selectores de grado y grupo
                    # Selectores de grado y grupo - con on_change automático
                    with ui.row().classes('gap-4 mb-6 w-full'):
                        # Selector de grado
                        grados = self.vm.get_grados_activos()
                        grado_opciones = [f"{g.numero}°" for g in grados]
                        grado_ids = {f"{g.numero}°": g.id for g in grados}
                        
                        def on_grado_change():
                            print(f"DEBUG - Grado cambiado a: {grado_select.value}")
                            refresh_actividades()
                        
                        grado_select = ui.select(
                            label='Grado',
                            options=grado_opciones,
                            value=grado_opciones[0] if grado_opciones else None,
                            on_change=on_grado_change
                        ).classes('w-48')
                        
                        # Selector de grupo
                        grupos = self.vm.get_grupos_activos()
                        grupo_opciones = [f"Grupo {g.letra}" for g in grupos]
                        grupo_ids = {f"Grupo {g.letra}": g.id for g in grupos}
                        
                        def on_grupo_change():
                            print(f"DEBUG - Grupo cambiado a: {grupo_select.value}")
                            refresh_actividades()
                        
                        grupo_select = ui.select(
                            label='Grupo',
                            options=grupo_opciones,
                            value=grupo_opciones[0] if grupo_opciones else None,
                            on_change=on_grupo_change
                        ).classes('w-48')
                        
                        # Botón para crear actividad
                        def abrir_crear_actividad():
                            with ui.dialog() as dialog, ui.card():
                                ui.label('Nueva Actividad').classes('text-xl font-bold mb-4')
                                nombre_input = ui.input('Nombre de la actividad').classes('w-full')
                                desc_input = ui.textarea('Descripción').classes('w-full')
                                
                                def guardar():
                                    if not nombre_input.value:
                                        ui.notify('El nombre es requerido', type='warning')
                                        return
                                    
                                    periodo_activo = self.vm.get_periodo_activo()
                                    grado_id = grado_ids[grado_select.value]
                                    grupo_id = grupo_ids[grupo_select.value]
                                    
                                    grado_grupo = self.vm.db.query(GradoGrupo).filter(
                                        GradoGrupo.grado_id == grado_id,
                                        GradoGrupo.grupo_id == grupo_id
                                    ).first()
                                    
                                    actividad = self.vm.crear_actividad(
                                        nombre=nombre_input.value,
                                        descripcion=desc_input.value,
                                        grado_id=grado_id,
                                        grupo_id=grupo_id,
                                        periodo_id=periodo_activo.id,
                                        grado_grupo_id=grado_grupo.id if grado_grupo else None
                                    )
                                    
                                    if actividad:
                                        ui.notify(f'✅ Actividad "{nombre_input.value}" creada', type='positive')
                                        dialog.close()
                                        refresh_actividades()
                                    else:
                                        ui.notify('❌ Error al crear actividad', type='error')
                                
                                ui.button('Guardar', on_click=guardar, color='green')
                                ui.button('Cancelar', on_click=dialog.close).props('flat')
                            
                            dialog.open()
                        
                        ui.button('➕ Nueva Actividad', on_click=abrir_crear_actividad, color='blue').classes('self-end')
                    # Contenedor para lista de actividades
                    actividades_container = ui.column()

                    def refresh_actividades():
                        """Actualiza la lista de actividades según grado/grupo seleccionado"""
                        actividades_container.clear()
                        
                        # Obtener valores actuales de los selects
                        grado_label = grado_select.value
                        grupo_label = grupo_select.value
                        
                        print(f"DEBUG - Refrescando: Grado={grado_label}, Grupo={grupo_label}")
                        
                        if not grado_label or not grupo_label:
                            with actividades_container:
                                ui.label('Selecciona un grado y grupo').classes('text-gray-500')
                            return
                        
                        # Obtener IDs
                        grado_id = grado_ids.get(grado_label)
                        grupo_id = grupo_ids.get(grupo_label)
                        
                        if not grado_id or not grupo_id:
                            with actividades_container:
                                ui.label('Error: Selección no válida').classes('text-red-500')
                            return
                        
                        periodo_activo = self.vm.get_periodo_activo()
                        actividades = self.vm.get_actividades_por_grupo(
                            grado_id=grado_id,
                            grupo_id=grupo_id,
                            periodo_id=periodo_activo.id
                        )
                        
                        print(f"DEBUG - Actividades encontradas: {len(actividades)}")
                        
                        if not actividades:
                            with actividades_container:
                                ui.label('No hay actividades para este grupo').classes('text-gray-500')
                            return
                        
                        periodo_activo = self.vm.get_periodo_activo()
                        actividades = self.vm.get_actividades_por_grupo(
                            grado_id=grado_id,
                            grupo_id=grupo_id,
                            periodo_id=periodo_activo.id
                        )
                        
                        print(f"DEBUG - Actividades encontradas: {len(actividades)}")
                        
                        if not actividades:
                            with actividades_container:
                                ui.label('No hay actividades para este grupo').classes('text-gray-500')
                            return
                        
                        with actividades_container:
                            for actividad in actividades:
                                # Obtener contador de entregas
                                grado_obj = self.vm.db.query(Grado).filter(Grado.id == grado_id).first()
                                grupo_obj = self.vm.db.query(Grupo).filter(Grupo.id == grupo_id).first()
                                entregas_count = self.vm.get_contador_entregas_fisico(
                                    actividad.id, periodo_activo.id, grado_obj.numero, grupo_obj.letra
                                )
                                
                                # Tarjeta de actividad
                                estado_color = 'green' if actividad.activa else 'gray'
                                estado_texto = 'Activa' if actividad.activa else 'Inactiva'
                                
                                with ui.card().classes(f'w-full mb-4 border-l-8 border-{estado_color}-500'):
                                    with ui.row().classes('w-full justify-between items-start p-4'):
                                        with ui.column().classes('flex-1'):
                                            with ui.row().classes('items-center gap-2'):
                                                ui.label(actividad.nombre).classes('text-xl font-bold')
                                                ui.badge(estado_texto, color=estado_color).classes('text-sm')
                                                ui.label(f'📊 {entregas_count} entregas').classes('text-sm text-gray-500')
                                                # Dentro de los botones de acción, añadir:
                                                ui.button(
                                                    '📄 PDF', 
                                                    on_click=lambda a_id=actividad.id, g_num=grado_obj.numero, g_let=grupo_obj.letra: self.generar_pdf_entregas(a_id, g_num, g_let),
                                                    color='purple'
                                                ).props('flat sm')
                                            if actividad.descripcion:
                                                ui.label(actividad.descripcion).classes('text-gray-600 mt-1')
                                            
                                            ui.label(f'📅 Creada: {actividad.fecha_creacion.strftime("%d/%m/%Y %H:%M")}').classes('text-xs text-gray-400 mt-2')
                                        
                                        with ui.column().classes('gap-2'):
                                            # Botones de acción
                                            def editar_actividad(a_id=actividad.id, a_nombre=actividad.nombre, a_desc=actividad.descripcion):
                                                with ui.dialog() as dialog, ui.card():
                                                    ui.label('Editar Actividad').classes('text-xl font-bold mb-4')
                                                    nombre_input = ui.input('Nombre', value=a_nombre).classes('w-full')
                                                    desc_input = ui.textarea('Descripción', value=a_desc).classes('w-full')
                                                    
                                                    def guardar():
                                                        if self.vm.editar_actividad(a_id, nombre_input.value, desc_input.value):
                                                            ui.notify('✅ Actividad actualizada', type='positive')
                                                            dialog.close()
                                                            refresh_actividades()
                                                        else:
                                                            ui.notify('❌ Error al actualizar', type='error')
                                                    
                                                    ui.button('Guardar', on_click=guardar, color='green')
                                                    ui.button('Cancelar', on_click=dialog.close).props('flat')
                                                dialog.open()
                                                    
                                            
                                            def toggle_actividad(a_id=actividad.id, activa_actual=actividad.activa):
                                                if self.vm.toggle_actividad_activa(a_id):
                                                    estado = "activada" if not activa_actual else "desactivada"
                                                    ui.notify(f'✅ Actividad {estado}', type='success')
                                                    refresh_actividades()
                                                else:
                                                    ui.notify('❌ Error', type='error')
                                            
                                            def eliminar_actividad_conf(a_id=actividad.id, a_nombre=actividad.nombre):
                                                with ui.dialog() as dialog, ui.card():
                                                    ui.label('Confirmar eliminación').classes('text-xl font-bold mb-4')
                                                    ui.label(f'¿Eliminar "{a_nombre}"?').classes('mb-4')
                                                    ui.label('Se borrarán también todos los materiales y entregas').classes('text-red-500 text-sm')
                                                    
                                                    with ui.row().classes('gap-2 justify-end w-full mt-4'):
                                                        def eliminar():
                                                            if self.vm.eliminar_actividad(a_id):
                                                                ui.notify('✅ Actividad eliminada', type='positive')
                                                                dialog.close()
                                                                refresh_actividades()
                                                            else:
                                                                ui.notify('❌ Error al eliminar', type='error')
                                                        
                                                        ui.button('Eliminar', on_click=eliminar, color='red')
                                                        ui.button('Cancelar', on_click=dialog.close).props('flat')
                                                dialog.open()
                                            
                                            def gestionar_materiales(a_id=actividad.id, a_nombre=actividad.nombre):
                                                with ui.dialog() as dialog, ui.card().classes('w-[600px]'):
                                                    ui.label(f'Materiales: {a_nombre}').classes('text-xl font-bold mb-4')
                                                    
                                                    ui.label('Subir archivo').classes('font-bold mt-2')
                                                    ui.upload(
                                                        label='Seleccionar archivo',
                                                        on_upload=lambda e: subir_archivo(e, a_id),
                                                        multiple=False
                                                    ).classes('w-full')
                                                    
                                                    ui.separator().classes('my-4')
                                                    
                                                    ui.label('Añadir enlace web').classes('font-bold')
                                                    link_nombre = ui.input('Nombre del enlace').classes('w-full')
                                                    link_url = ui.input('URL').classes('w-full')
                                                    
                                                    def guardar_link():
                                                        if link_nombre.value and link_url.value:
                                                            if self.vm.agregar_material_link(a_id, link_nombre.value, link_url.value):
                                                                ui.notify('✅ Enlace añadido', type='positive')
                                                                link_nombre.value = ''
                                                                link_url.value = ''
                                                                refresh_materiales()
                                                            else:
                                                                ui.notify('❌ Error', type='error')
                                                        else:
                                                            ui.notify('Completa ambos campos', type='warning')
                                                    
                                                    ui.button('Guardar enlace', on_click=guardar_link, color='blue').classes('mt-2')
                                                    
                                                    ui.separator().classes('my-4')
                                                    
                                                    materiales_container = ui.column()
                                                    
                                                    async def subir_archivo(e, a_id_local):
                                                        """Maneja la subida de archivos"""
                                                        try:
                                                            actividad = self.vm.get_actividad(a_id_local)
                                                            if not actividad:
                                                                ui.notify('❌ No se encontró la actividad', type='error')
                                                                return
                                                            
                                                            from utils.file_manager import get_materiales_path
                                                            grado_obj = actividad.grado
                                                            grupo_obj = actividad.grupo
                                                            materiales_path = get_materiales_path(
                                                                actividad.periodo_id, grado_obj.numero, grupo_obj.letra, a_id_local
                                                            )
                                                            materiales_path.mkdir(parents=True, exist_ok=True)
                                                            
                                                            archivo = e.file
                                                            nombre_archivo = archivo.name
                                                            
                                                            # Validar tamaño
                                                            if archivo.size() > 5 * 1024 * 1024:
                                                                ui.notify('❌ El archivo excede 5MB', type='error')
                                                                return
                                                            
                                                            file_path = materiales_path / nombre_archivo
                                                            
                                                            # Leer contenido de forma asíncrona
                                                            contenido = await archivo.read()
                                                            
                                                            # Guardar archivo
                                                            with open(file_path, 'wb') as f:
                                                                f.write(contenido)
                                                            
                                                            # Guardar en BD
                                                            if self.vm.agregar_material_archivo(a_id_local, nombre_archivo, str(file_path)):
                                                                ui.notify(f'✅ Archivo "{nombre_archivo}" subido', type='positive')
                                                                refresh_materiales()
                                                            else:
                                                                ui.notify('❌ Error al guardar en BD', type='error')
                                                                
                                                        except Exception as err:
                                                            ui.notify(f'❌ Error: {err}', type='error')
                                                            print(f"Error detallado: {err}")
                                                    
                                                    def refresh_materiales():
                                                        materiales_container.clear()
                                                        materiales = self.vm.get_materiales_actividad(a_id)
                                                        
                                                        if not materiales:
                                                            with materiales_container:
                                                                ui.label('No hay materiales aún').classes('text-gray-500')
                                                            return
                                                        
                                                        with materiales_container:
                                                            for material in materiales:
                                                                with ui.row().classes('w-full justify-between items-center p-2 border rounded'):
                                                                    icono = '📄' if material.tipo == 'archivo' else '🔗'
                                                                    with ui.row().classes('gap-2 items-center'):
                                                                        ui.label(icono).classes('text-xl')
                                                                        ui.label(material.nombre).classes('font-medium')
                                                                        if material.tipo == 'link':
                                                                            ui.link('Abrir', material.url, new_tab=True).classes('text-blue-500 text-sm')
                                                                    
                                                                    def eliminar_material(m_id=material.id):
                                                                        if self.vm.eliminar_material(m_id):
                                                                            ui.notify('✅ Material eliminado', type='positive')
                                                                            refresh_materiales()
                                                                        else:
                                                                            ui.notify('❌ Error', type='error')
                                                                    
                                                                    ui.button('🗑️', on_click=eliminar_material, color='red').props('flat sm')
                                                    
                                                    refresh_materiales()
                                                    ui.button('Cerrar', on_click=dialog.close).classes('mt-4 w-full')
                                                dialog.open()
                                            
                                            with ui.row().classes('gap-1'):
                                                ui.button('✏️', on_click=editar_actividad, color='blue').props('flat sm')
                                                ui.button('📎', on_click=gestionar_materiales, color='green').props('flat sm')
                                                estado_btn_texto = '🔴' if actividad.activa else '🟢'
                                                ui.button(estado_btn_texto, on_click=toggle_actividad, color='orange').props('flat sm')
                                                ui.button('🗑️', on_click=eliminar_actividad_conf, color='red').props('flat sm')

                    # Función para manejar cambios en los selects
                    def on_grado_change():
                        print(f"DEBUG - Grado cambiado a: {grado_select.value}")
                        refresh_actividades()

                    def on_grupo_change():
                        print(f"DEBUG - Grupo cambiado a: {grupo_select.value}")
                        refresh_actividades()

                    # Eventos de cambio en selects
                    grado_select.on('change', on_grado_change)
                    grupo_select.on('change', on_grupo_change)

                    # Inicializar
                    refresh_actividades()

    def mostrar_gestion_grados_grupos(self, refresh_stats_callback=None):
        """Muestra los grados y grupos organizados por filas"""
        
        # Contenedor principal
        grados_container = ui.column()
        
        def refresh_grados():
            """Refresca completamente la vista de grados"""
            grados_container.clear()
            with grados_container:
                build_grados_ui()
            ui.update()
            # También actualizar las estadísticas del dashboard si se proporcionó callback
            if refresh_stats_callback:
                refresh_stats_callback()
        
        def build_grados_ui():
            combinaciones = self.vm.get_combinaciones_grado_grupo()
            
            # Agrupar por grado
            grados_agrupados = {}
            for combo in combinaciones:
                grado_num = combo['grado_numero']
                if grado_num not in grados_agrupados:
                    grados_agrupados[grado_num] = []
                grados_agrupados[grado_num].append(combo)
            
            # Mostrar cada grado
            for grado_num in sorted(grados_agrupados.keys()):
                with ui.card().classes('w-full p-4 mb-4 bg-gray-50'):
                    with ui.row().classes('w-full justify-between items-center mb-3'):
                        ui.label(f"{grado_num}° GRADO").classes('text-xl font-bold text-blue-800')
                        activos = sum(1 for c in grados_agrupados[grado_num] if c['activo'])
                        ui.badge(f"{activos}/{len(grados_agrupados[grado_num])} activos", color='blue').classes('text-sm')
                    
                    ui.separator().classes('mb-3')
                    
                    with ui.row().classes('gap-4 w-full flex-wrap justify-start'):
                        for combo in sorted(grados_agrupados[grado_num], key=lambda x: x['grupo_letra']):
                            combo_id = combo['id']
                            grado_letra = f"{combo['grado_numero']}{combo['grupo_letra']}"
                            activo_actual = combo['activo']
                            password_actual = combo['password']
                            
                            estado_color = 'green' if activo_actual else 'gray'
                            estado_icono = '✅' if activo_actual else '❌'
                            fondo_color = 'bg-green-50' if activo_actual else 'bg-gray-100'
                            
                            with ui.card().classes(f'w-56 p-3 {fondo_color} border-l-4 border-{estado_color}-500'):
                                with ui.row().classes('justify-between items-center w-full'):
                                    ui.label(f"Grupo {combo['grupo_letra']}").classes('text-lg font-bold')
                                    ui.label(estado_icono).classes(f'text-xl text-{estado_color}-600')
                                
                                ui.separator().classes('my-2')
                                
                                with ui.row().classes('items-center gap-2'):
                                    ui.icon('key', size='16px').classes('text-gray-500')
                                    ui.label('Contraseña:').classes('text-xs text-gray-600')
                                    ui.label(password_actual).classes('font-mono text-sm font-bold')
                                
                                with ui.row().classes('gap-2 mt-3 w-full justify-end'):
                                    edit_btn = ui.button('✏️', color='blue').props('flat sm')
                                    edit_btn.on('click', lambda c_id=combo_id, c_grado=grado_letra: ui.notify(f'📝 Editar contraseña de {c_grado} - Próximamente', type='info'))
                                    
                                    estado_texto = '❌ Desactivar' if activo_actual else '✅ Activar'
                                    toggle_btn = ui.button(estado_texto, color='red' if activo_actual else 'green').props('flat sm')
                                    
                                    def toggle(c_id=combo_id, g_letra=grado_letra, act_actual=activo_actual):
                                        if self.vm.toggle_combinacion_activa(c_id):
                                            estado = "activada" if not act_actual else "desactivada"
                                            ui.notify(f'✅ Clase {g_letra} {estado}', type='success')
                                            refresh_grados()  # Actualizar grados
                                        else:
                                            ui.notify('❌ Error al cambiar estado', type='error')
                                    
                                    toggle_btn.on('click', toggle)
            
            # Mensaje informativo
            with ui.card().classes('w-full p-3 mt-2 bg-yellow-50'):
                ui.label('💡 Click en "Activar/Desactivar" para habilitar/deshabilitar una clase').classes('text-sm text-yellow-800')
                ui.label('   La edición de contraseñas estará disponible en la próxima versión').classes('text-xs text-yellow-600 mt-1')
        
        with grados_container:
            build_grados_ui()
    
    def generar_pdf_entregas(self, actividad_id: int, grado_num: int, grupo_letra: str):
        """Genera un PDF con las entregas de una actividad"""
        from fpdf import FPDF
        from datetime import datetime
        import tempfile
        from pathlib import Path
        
        # Obtener datos
        actividad = self.vm.get_actividad(actividad_id)
        entregas = self.vm.get_entregas_actividad(actividad_id)
        
        if not entregas:
            ui.notify('No hay entregas para generar el PDF', type='warning')
            return
        
        # Crear PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Título
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, f"Informe de Entregas", ln=True, align='C')
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Actividad: {actividad.nombre}", ln=True, align='C')
        pdf.cell(200, 10, f"Grupo: {grado_num}°{grupo_letra}", ln=True, align='C')
        pdf.cell(200, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
        pdf.ln(10)
        
        # Encabezados de tabla
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 10, "Estudiante", 1)
        pdf.cell(50, 10, "Archivo Entregado", 1)
        pdf.cell(60, 10, "Comentarios", 1)
        pdf.cell(30, 10, "Fecha/Hora", 1)
        pdf.ln()
        
        # Datos
        pdf.set_font("Arial", size=9)
        for entrega in entregas:
            pdf.cell(50, 8, entrega.estudiante_nombre[:30], 1)
            pdf.cell(50, 8, entrega.archivo_nombre[:30], 1)
            pdf.cell(60, 8, (entrega.comentarios or "")[:40], 1)
            pdf.cell(30, 8, entrega.fecha_hora.strftime("%d/%m/%y %H:%M"), 1)
            pdf.ln()
        
        # Guardar PDF temporal
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(temp_file.name)
        
        # Descargar
        ui.download(temp_file.name, f"entregas_{actividad.nombre}_{grado_num}{grupo_letra}.pdf")
        ui.notify('PDF generado correctamente', type='positive')

    def cerrar_sesion(self):
        """Cierra la sesión del administrador"""
        self.is_authenticated = False
        self.vm.cerrar()
        ui.navigate.to('/admin')
        ui.notify('Sesión cerrada', type='info')