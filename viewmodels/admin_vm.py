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