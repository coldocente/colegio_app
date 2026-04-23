"""
ViewModel para el panel de administrador
"""
from typing import List, Dict, Optional
from pathlib import Path
import shutil

from models.database import SessionLocal
from models.entities import (
    Periodo, Grado, Grupo, GradoGrupo, 
    Actividad, Material, Entrega
)
from utils.file_manager import (
    get_entregas_count
)
from config import ADMIN_PASSWORD

class AdminViewModel:
    """ViewModel para el administrador (docente)"""
    
    def __init__(self):
        self.db = SessionLocal()
        self._periodo_activo = None
        
    def cerrar(self):
        """Cerrar sesión al destruir el objeto"""
        if hasattr(self, 'db'):
            self.db.close()
    
    # ========== AUTENTICACIÓN ==========
    
    def verificar_login(self, password: str) -> bool:
        return password == ADMIN_PASSWORD
    
    # ========== PERIODOS ==========
    
    def get_periodo_activo(self) -> Optional[Periodo]:
        if not self._periodo_activo:
            self._periodo_activo = self.db.query(Periodo).filter(Periodo.activo == True).first()
        return self._periodo_activo
    
    def get_todos_periodos(self) -> List[Periodo]:
        return self.db.query(Periodo).order_by(Periodo.id).all()
    
    # ========== GRADOS Y GRUPOS ==========
    
    def get_grados_activos(self) -> List[Grado]:
        return self.db.query(Grado).filter(Grado.activo == True).order_by(Grado.numero).all()
    
    def get_grupos_activos(self) -> List[Grupo]:
        return self.db.query(Grupo).filter(Grupo.activo == True).order_by(Grupo.letra).all()
    
    def get_combinaciones_grado_grupo(self) -> List[Dict]:
        """Retorna todas las combinaciones grado-grupo con su estado y contraseña"""
        # Expirar la sesión antes de consultar para obtener datos actualizados
        self.db.expire_all()
        
        resultados = []
        combinaciones = self.db.query(GradoGrupo).all()
        
        for combo in combinaciones:
            resultados.append({
                'id': combo.id,
                'grado_numero': combo.grado.numero,
                'grupo_letra': combo.grupo.letra,
                'password': combo.password,
                'activo': combo.activo,
                'grado_id': combo.grado_id,
                'grupo_id': combo.grupo_id
            })
        
        return resultados
    
    def toggle_combinacion_activa(self, grado_grupo_id: int) -> bool:
        """Activa o desactiva una combinación grado-grupo"""
        try:
            combo = self.db.query(GradoGrupo).filter(GradoGrupo.id == grado_grupo_id).first()
            if combo:
                combo.activo = not combo.activo
                self.db.commit()
                # Forzar refresh de la instancia para que los cambios sean visibles
                self.db.refresh(combo)
                # Expirar toda la sesión para que las próximas consultas traigan datos frescos
                self.db.expire_all()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error al cambiar estado de combinación: {e}")
            return False
    
    # ========== ACTIVIDADES ==========
    
    def get_actividades_por_grupo(self, grado_id: int, grupo_id: int, periodo_id: int) -> List[Actividad]:
        return self.db.query(Actividad).filter(
            Actividad.grado_id == grado_id,
            Actividad.grupo_id == grupo_id,
            Actividad.periodo_id == periodo_id
        ).order_by(Actividad.fecha_creacion.desc()).all()
    
    def get_contador_entregas(self, actividad_id: int, periodo_id: int, grado_num: int, grupo_letra: str) -> int:
        return get_entregas_count(periodo_id, grado_num, grupo_letra, actividad_id)
    
    # ========== ACTIVIDADES (CRUD) ==========

    def crear_actividad(self, nombre: str, descripcion: str, grado_id: int, 
                    grupo_id: int, periodo_id: int, grado_grupo_id: int) -> Optional[Actividad]:
        """Crea una nueva actividad y sus carpetas correspondientes"""
        try:
            # Obtener datos para las rutas
            grado = self.db.query(Grado).filter(Grado.id == grado_id).first()
            grupo = self.db.query(Grupo).filter(Grupo.id == grupo_id).first()
            periodo = self.db.query(Periodo).filter(Periodo.id == periodo_id).first()
            
            if not all([grado, grupo, periodo]):
                return None
            
            # Crear actividad en BD
            actividad = Actividad(
                nombre=nombre,
                descripcion=descripcion,
                grado_id=grado_id,
                grupo_id=grupo_id,
                periodo_id=periodo_id,
                grado_grupo_id=grado_grupo_id,
                activa=True
            )
            self.db.add(actividad)
            self.db.commit()
            self.db.refresh(actividad)
            
            # Crear carpetas físicas
            from utils.file_manager import crear_carpeta_actividad
            crear_carpeta_actividad(
                periodo_id=periodo_id,
                grado_num=grado.numero,
                grupo_letra=grupo.letra,
                actividad_id=actividad.id
            )
            
            return actividad
            
        except Exception as e:
            self.db.rollback()
            print(f"Error al crear actividad: {e}")
            return None

    def editar_actividad(self, actividad_id: int, nombre: str, descripcion: str) -> bool:
        """Edita una actividad existente"""
        try:
            actividad = self.db.query(Actividad).filter(Actividad.id == actividad_id).first()
            if actividad:
                actividad.nombre = nombre
                actividad.descripcion = descripcion
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error al editar actividad: {e}")
            return False

    def toggle_actividad_activa(self, actividad_id: int) -> bool:
        """Activa o desactiva una actividad"""
        try:
            actividad = self.db.query(Actividad).filter(Actividad.id == actividad_id).first()
            if actividad:
                actividad.activa = not actividad.activa
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error al cambiar estado de actividad: {e}")
            return False

    def eliminar_actividad(self, actividad_id: int) -> bool:
        """Elimina una actividad y sus archivos físicos"""
        try:
            actividad = self.db.query(Actividad).filter(Actividad.id == actividad_id).first()
            if actividad:
                # Eliminar carpetas físicas
                import shutil
                from pathlib import Path
                
                grado = actividad.grado
                grupo = actividad.grupo
                
                actividad_path = Path(__file__).parent.parent / "storage" / f"periodo_{actividad.periodo_id}" / f"grado_{grado.numero}" / f"grupo_{grupo.letra}" / "actividades" / f"actividad_{actividad_id}"
                
                if actividad_path.exists():
                    shutil.rmtree(actividad_path)
                
                # Eliminar de BD
                self.db.delete(actividad)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error al eliminar actividad: {e}")
            return False

    def get_actividades_por_grupo(self, grado_id: int, grupo_id: int, periodo_id: int) -> List[Actividad]:
        """Retorna todas las actividades de un grupo específico"""
        return self.db.query(Actividad).filter(
            Actividad.grado_id == grado_id,
            Actividad.grupo_id == grupo_id,
            Actividad.periodo_id == periodo_id
        ).order_by(Actividad.fecha_creacion.desc()).all()

    def get_actividad(self, actividad_id: int) -> Optional[Actividad]:
        """Retorna una actividad por ID"""
        return self.db.query(Actividad).filter(Actividad.id == actividad_id).first()

    # ========== MATERIALES ==========

    def agregar_material_archivo(self, actividad_id: int, nombre: str, ruta_archivo: str) -> bool:
        """Agrega un material tipo archivo a una actividad"""
        try:
            material = Material(
                actividad_id=actividad_id,
                tipo='archivo',
                nombre=nombre,
                url=ruta_archivo
            )
            self.db.add(material)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error al agregar material: {e}")
            return False

    def agregar_material_link(self, actividad_id: int, nombre: str, url: str) -> bool:
        """Agrega un material tipo link a una actividad"""
        try:
            material = Material(
                actividad_id=actividad_id,
                tipo='link',
                nombre=nombre,
                url=url
            )
            self.db.add(material)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error al agregar link: {e}")
            return False

    def eliminar_material(self, material_id: int) -> bool:
        """Elimina un material"""
        try:
            material = self.db.query(Material).filter(Material.id == material_id).first()
            if material:
                # Si es archivo, eliminar el archivo físico
                if material.tipo == 'archivo':
                    from pathlib import Path
                    archivo_path = Path(material.url)
                    if archivo_path.exists():
                        archivo_path.unlink()
                self.db.delete(material)
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error al eliminar material: {e}")
            return False

    def get_materiales_actividad(self, actividad_id: int) -> List[Material]:
        """Retorna los materiales de una actividad"""
        return self.db.query(Material).filter(Material.actividad_id == actividad_id).all()

    # ========== ENTREGAS ==========

    def get_entregas_actividad(self, actividad_id: int) -> List[Entrega]:
        """Retorna todas las entregas de una actividad"""
        return self.db.query(Entrega).filter(Entrega.actividad_id == actividad_id).order_by(Entrega.fecha_hora.desc()).all()

    def get_contador_entregas_fisico(self, actividad_id: int, periodo_id: int, grado_num: int, grupo_letra: str) -> int:
        """Cuenta entregas físicas en la carpeta"""
        from utils.file_manager import get_entregas_count
        return get_entregas_count(periodo_id, grado_num, grupo_letra, actividad_id)
    
    # ========== PERIODOS ==========

    def get_todos_periodos(self) -> List[Periodo]:
        """Retorna todos los periodos"""
        return self.db.query(Periodo).order_by(Periodo.id).all()

    def activar_periodo(self, periodo_id: int) -> bool:
        """Activa un periodo y desactiva los demás"""
        try:
            # Desactivar todos
            self.db.query(Periodo).update({Periodo.activo: False})
            # Activar el seleccionado
            periodo = self.db.query(Periodo).filter(Periodo.id == periodo_id).first()
            if periodo:
                periodo.activo = True
                self.db.commit()
                self._periodo_activo = periodo
                return True
            return False
        except Exception as e:
            self.db.rollback()
            print(f"Error al activar periodo: {e}")
            return False

    def get_periodo_activo(self) -> Optional[Periodo]:
        """Retorna el periodo activo"""
        if not self._periodo_activo:
            self._periodo_activo = self.db.query(Periodo).filter(Periodo.activo == True).first()
        return self._periodo_activo