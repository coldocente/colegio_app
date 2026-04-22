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
from views.student_view import StudentView

# Instancias globales
admin_view = AdminView()
student_view = StudentView()

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
def estudiante_login():
    """Pantalla de login de estudiantes"""
    if student_view.is_authenticated:
        ui.navigate.to('/estudiante/panel')
    else:
        student_view.mostrar_login()

@ui.page('/estudiante/panel')
def estudiante_panel():
    """Panel de actividades del estudiante"""
    if not student_view.is_authenticated:
        ui.navigate.to('/estudiante')
    else:
        student_view.mostrar_panel()

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