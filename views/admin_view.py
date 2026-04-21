"""
Vista de administrador - Interfaz con NiceGUI
"""
from nicegui import ui
from viewmodels.admin_vm import AdminViewModel

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
            
            # Panel Actividades (placeholder)
            with ui.tab_panel(actividades_tab):
                with ui.card().classes('w-full p-6'):
                    ui.label('Gestión de Actividades').classes('text-2xl font-bold mb-4')
                    ui.label('Próximamente: crear y gestionar actividades').classes('text-gray-600')
    
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
    
    def cerrar_sesion(self):
        """Cierra la sesión del administrador"""
        self.is_authenticated = False
        self.vm.cerrar()
        ui.navigate.to('/admin')
        ui.notify('Sesión cerrada', type='info')