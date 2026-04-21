"""
Utilidades para manejar archivos y carpetas
"""
from pathlib import Path

# Carpeta raíz de almacenamiento
STORAGE_ROOT = Path(__file__).parent.parent / "storage"

def crear_estructura_completa():
    """Crea todas las carpetas necesarias (4 periodos × 6 grados × 3 grupos)"""
    for periodo in range(1, 5):
        for grado in range(6, 12):
            for grupo in ['A', 'B', 'C']:
                # Ruta: storage/periodo_1/grado_6/grupo_A/actividades/
                actividades_path = STORAGE_ROOT / f"periodo_{periodo}" / f"grado_{grado}" / f"grupo_{grupo}" / "actividades"
                actividades_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ Estructura de carpetas creada en storage/")

def get_actividad_path(periodo_id, grado_num, grupo_letra, actividad_id):
    """Retorna la ruta de la carpeta de una actividad específica"""
    return STORAGE_ROOT / f"periodo_{periodo_id}" / f"grado_{grado_num}" / f"grupo_{grupo_letra}" / "actividades" / f"actividad_{actividad_id}"

def get_materiales_path(periodo_id, grado_num, grupo_letra, actividad_id):
    """Ruta de la carpeta 'materiales' dentro de una actividad"""
    return get_actividad_path(periodo_id, grado_num, grupo_letra, actividad_id) / "materiales"

def get_entregas_path(periodo_id, grado_num, grupo_letra, actividad_id):
    """Ruta de la carpeta 'entregas' dentro de una actividad"""
    return get_actividad_path(periodo_id, grado_num, grupo_letra, actividad_id) / "entregas"

def crear_carpeta_actividad(periodo_id, grado_num, grupo_letra, actividad_id):
    """Crea las carpetas materiales y entregas para una actividad nueva"""
    materiales_path = get_materiales_path(periodo_id, grado_num, grupo_letra, actividad_id)
    entregas_path = get_entregas_path(periodo_id, grado_num, grupo_letra, actividad_id)
    
    materiales_path.mkdir(parents=True, exist_ok=True)
    entregas_path.mkdir(parents=True, exist_ok=True)
    
    return materiales_path, entregas_path

def get_entregas_count(periodo_id, grado_num, grupo_letra, actividad_id):
    """Cuenta cuántos archivos hay en la carpeta de entregas"""
    entregas_path = get_entregas_path(periodo_id, grado_num, grupo_letra, actividad_id)
    if entregas_path.exists():
        return len(list(entregas_path.glob("*")))
    return 0