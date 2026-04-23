"""
Punto de entrada de la aplicación con NiceGUI
"""
import sys
from pathlib import Path


from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from utils.file_manager import STORAGE_ROOT
import os

sys.path.insert(0, str(Path(__file__).parent))

from nicegui import ui
from models.database import init_db
from utils.file_manager import crear_estructura_completa
from views.admin_view import AdminView
from views.student_view import StudentView

# Instancias globales
admin_view = AdminView()
student_view = StudentView()

# Crear directorio para PDFs temporales si no existe
TEMP_PDF_DIR = STORAGE_ROOT / "temp_pdfs"
TEMP_PDF_DIR.mkdir(parents=True, exist_ok=True)

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

@ui.page('/ver_pdf/{filename}')
def ver_pdf(filename: str):
    """Muestra un PDF en una página completa"""
    import os
    from pathlib import Path
    
    pdf_path = TEMP_PDF_DIR / filename
    
    if not pdf_path.exists():
        ui.label('Archivo no encontrado').classes('text-center text-red-500 mt-32 text-xl')
        return
    
    # Leer el PDF
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    from base64 import b64encode
    pdf_base64 = b64encode(pdf_data).decode('utf-8')
    
    # Página completa para el PDF
    with ui.column().classes('w-full h-screen p-0 m-0'):
        ui.add_body_html(f'''
            <style>
                body {{ margin: 0; padding: 0; }}
                .pdf-container {{
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 1000;
                }}
            </style>
            <div class="pdf-container">
                <iframe
                    src="data:application/pdf;base64,{pdf_base64}"
                    width="100%"
                    height="100%"
                    style="border: none;"
                ></iframe>
                <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1001;">
                    <button onclick="window.location.href='/admin/dashboard'" 
                            style="background: #ef4444; color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-size: 14px;">
                        ❌ Cerrar y volver
                    </button>
                </div>
            </div>
        ''')

def main():
    print("🚀 Iniciando Sistema de Gestión Escolar...")
    print("=" * 50)
    
    crear_estructura_completa()
    init_db()
    
    print("✅ Sistema listo")
    print("🌐 Abre: http://localhost:8081")
    print("🔑 Admin: admin123")
    print("=" * 50)
    
    ui.run(
        title="Gestión Escolar",
        favicon="🏫",
        port=8081,
        reload=False
    )

if __name__ == "__main__":
    main()