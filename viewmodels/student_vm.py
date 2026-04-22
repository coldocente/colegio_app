"""
ViewModel para el panel de estudiantes
"""
from sqlalchemy.orm import Session
from models.database import SessionLocal
from models.entities import Grado, Grupo, GradoGrupo, Actividad, Material, Entrega
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class StudentViewModel:
    """ViewModel para los estudiantes"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.current_grado_grupo = None
        self.current_grado = None
        self.current_grupo = None
        
    def cerrar(self):
        """Cierra la sesión de la BD"""
        if hasattr(self, 'db'):
            self.db.close()
    
    def get_grados_activos(self) -> List[Dict]:
        """Retorna grados activos"""
        grados = self.db.query(Grado).filter(Grado.activo == True).order_by(Grado.numero).all()
        return [{'id': g.id, 'numero': g.numero} for g in grados]
    
    def get_grupos_activos(self) -> List[Dict]:
        """Retorna grupos activos"""
        grupos = self.db.query(Grupo).filter(Grupo.activo == True).order_by(Grupo.letra).all()
        return [{'id': g.id, 'letra': g.letra} for g in grupos]
    
    def validar_contraseña(self, grado_id: int, grupo_id: int, password: str) -> bool:
        """Valida la contraseña del grupo"""
        grado_grupo = self.db.query(GradoGrupo).filter(
            GradoGrupo.grado_id == grado_id,
            GradoGrupo.grupo_id == grupo_id,
            GradoGrupo.activo == True
        ).first()
        
        if grado_grupo and grado_grupo.password == password:
            self.current_grado_grupo = grado_grupo
            self.current_grado = self.db.query(Grado).filter(Grado.id == grado_id).first()
            self.current_grupo = self.db.query(Grupo).filter(Grupo.id == grupo_id).first()
            return True
        return False
    
    def get_actividades_activas(self, periodo_id: int) -> List[Actividad]:
        """Retorna actividades activas del grupo actual"""
        if not self.current_grado_grupo:
            return []
        
        return self.db.query(Actividad).filter(
            Actividad.grado_grupo_id == self.current_grado_grupo.id,
            Actividad.periodo_id == periodo_id,
            Actividad.activa == True
        ).order_by(Actividad.fecha_creacion.desc()).all()
    
    def get_materiales_actividad(self, actividad_id: int) -> List[Material]:
        """Retorna materiales de una actividad"""
        return self.db.query(Material).filter(Material.actividad_id == actividad_id).all()
    
    def get_entrega_estudiante(self, actividad_id: int, estudiante_nombre: str) -> Optional[Entrega]:
        """Verifica si un estudiante ya entregó esta actividad"""
        return self.db.query(Entrega).filter(
            Entrega.actividad_id == actividad_id,
            Entrega.estudiante_nombre == estudiante_nombre
        ).first()
    
    def get_periodo_activo(self):
        """Retorna el periodo activo"""
        from models.entities import Periodo
        return self.db.query(Periodo).filter(Periodo.activo == True).first()