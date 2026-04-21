"""
Punto de entrada de la aplicación con NiceGUI
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nicegui import ui
from models.database import init_db
from utils.file_manager import crear_estructura_completa
from views.admin_view import AdminView

admin_view = AdminView()

@ui.page('/')
def inicio():
    # Contenedor principal centrado
    with ui.column().classes('items-center justify-center min-h-screen w-full'):
        with ui.card().classes('text-center p-8 w-96'):
            ui.icon('school').classes('text-8xl text-blue-600 mx-auto')
            ui.label('Sistema de Gestión Escolar').classes('text-3xl font-bold mt-4 text-center')
            ui.label('Bienvenido').classes('text-xl text-gray-600 mt-2 text-center')
            
            with ui.row().classes('gap-6 mt-8 justify-center w-full'):
                ui.button('👨‍🏫 Acceso Docente', on_click=lambda: ui.navigate.to('/admin'), 
                         color='blue').classes('px-6 py-2 text-lg')
                ui.button('👩‍🎓 Acceso Estudiante', on_click=lambda: ui.navigate.to('/estudiante'), 
                         color='green').classes('px-6 py-2 text-lg')

@ui.page('/admin')
def admin_login():
    if admin_view.is_authenticated:
        ui.navigate.to('/admin/dashboard')
    else:
        admin_view.mostrar_login()

@ui.page('/admin/dashboard')
def admin_dashboard():
    if not admin_view.is_authenticated:
        ui.navigate.to('/admin')
    else:
        admin_view.mostrar_dashboard()

@ui.page('/estudiante')
def estudiante_panel():
    with ui.card().classes('w-96 mx-auto mt-32 text-center p-8'):
        ui.icon('students').classes('text-6xl text-green-600 mx-auto')
        ui.label('Panel de Estudiantes').classes('text-2xl font-bold mt-4')
        ui.label('Próximamente disponible').classes('text-gray-500 mt-2')
        ui.button('Volver al inicio', on_click=lambda: ui.navigate.to('/'), color='gray').classes('mt-6')

def main():
    print("🚀 Iniciando Sistema de Gestión Escolar...")
    print("=" * 50)
    
    crear_estructura_completa()
    init_db()
    
    print("✅ Sistema listo")
    print("🌐 Abre: http://localhost:8080")
    print("🔑 Admin: admin123")
    print("=" * 50)
    
    ui.run(
        title="Gestión Escolar",
        favicon="🏫",
        port=8080,
        reload=False
    )

if __name__ == "__main__":
    main()