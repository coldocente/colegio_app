"""
Punto de entrada de la aplicación
Sistema de Gestión Escolar con MVVM + ORM
"""
import sys
from pathlib import Path

# Agregar raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from models.database import init_db
from utils.file_manager import crear_estructura_completa
from models.database import SessionLocal
from models.entities import Periodo

def get_active_period():
    """Obtiene el periodo activo de la BD"""
    db = SessionLocal()
    try:
        periodo = db.query(Periodo).filter(Periodo.activo == True).first()
        if periodo:
            return periodo.id, periodo.nombre
        return 1, "Periodo 1"
    finally:
        db.close()

def main():
    """Inicializa todo y arranca la aplicación"""
    print("🚀 Iniciando Sistema de Gestión Escolar v1.0")
    print("=" * 50)
    
    # 1. Crear estructura de carpetas
    crear_estructura_completa()
    
    # 2. Inicializar base de datos con ORM
    init_db()
    
    # 3. Mostrar periodo activo
    periodo_id, periodo_nombre = get_active_period()
    print(f"📅 Periodo activo: {periodo_nombre}")
    
    # 4. Mostrar estadísticas básicas
    db = SessionLocal()
    try:
        from models.entities import Grado, Grupo, GradoGrupo
        grados_count = db.query(Grado).count()
        grupos_count = db.query(Grupo).count()
        combinaciones_count = db.query(GradoGrupo).count()
        print(f"📊 Grados: {grados_count} | Grupos: {grupos_count} | Clases: {combinaciones_count}")
    finally:
        db.close()
    
    print("=" * 50)
    print("✅ Sistema listo. Próximamente: interfaz gráfica con NiceGUI")
    print("💡 Ejecuta 'uv run main.py' cuando agreguemos las vistas")
    
    # Por ahora, mantener vivo
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()