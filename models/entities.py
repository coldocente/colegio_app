"""
Modelos de datos - Definición de todas las tablas usando SQLAlchemy ORM
"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# Importamos la base desde database.py (lo crearemos después)
from .database import Base

class Periodo(Base):
    """Periodos académicos: Periodo 1, 2, 3, 4"""
    __tablename__ = 'periodos'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    activo = Column(Boolean, default=False)
    
    # Relaciones
    actividades = relationship("Actividad", back_populates="periodo")
    
    def __repr__(self):
        return f"<Periodo {self.nombre}>"

class Grado(Base):
    """Grados: 6, 7, 8, 9, 10, 11"""
    __tablename__ = 'grados'
    
    id = Column(Integer, primary_key=True)
    numero = Column(Integer, unique=True, nullable=False)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    grado_grupos = relationship("GradoGrupo", back_populates="grado")
    actividades = relationship("Actividad", back_populates="grado")
    
    def __repr__(self):
        return f"<Grado {self.numero}°>"

class Grupo(Base):
    """Grupos: A, B, C"""
    __tablename__ = 'grupos'
    
    id = Column(Integer, primary_key=True)
    letra = Column(String, unique=True, nullable=False)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    grado_grupos = relationship("GradoGrupo", back_populates="grupo")
    actividades = relationship("Actividad", back_populates="grupo")
    
    def __repr__(self):
        return f"<Grupo {self.letra}>"

class GradoGrupo(Base):
    """Relación grado-grupo con contraseña específica"""
    __tablename__ = 'grado_grupo'
    
    id = Column(Integer, primary_key=True)
    grado_id = Column(Integer, ForeignKey('grados.id'))
    grupo_id = Column(Integer, ForeignKey('grupos.id'))
    password = Column(String, nullable=False)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    grado = relationship("Grado", back_populates="grado_grupos")
    grupo = relationship("Grupo", back_populates="grado_grupos")
    actividades = relationship("Actividad", back_populates="grado_grupo")
    
    def __repr__(self):
        return f"<GradoGrupo {self.grado.numero}{self.grupo.letra}>"

class Actividad(Base):
    """Actividades creadas por el docente"""
    __tablename__ = 'actividades'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    activa = Column(Boolean, default=True)
    fecha_limite = Column(String, nullable=True)  # Formato ISO
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Claves foráneas
    periodo_id = Column(Integer, ForeignKey('periodos.id'))
    grado_id = Column(Integer, ForeignKey('grados.id'))
    grupo_id = Column(Integer, ForeignKey('grupos.id'))
    grado_grupo_id = Column(Integer, ForeignKey('grado_grupo.id'))
    
    # Relaciones
    periodo = relationship("Periodo", back_populates="actividades")
    grado = relationship("Grado", back_populates="actividades")
    grupo = relationship("Grupo", back_populates="actividades")
    grado_grupo = relationship("GradoGrupo", back_populates="actividades")
    materiales = relationship("Material", back_populates="actividad", cascade="all, delete-orphan")
    entregas = relationship("Entrega", back_populates="actividad", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Actividad {self.nombre}>"

class Material(Base):
    """Materiales subidos por el docente (archivos o links)"""
    __tablename__ = 'materiales'
    
    id = Column(Integer, primary_key=True)
    actividad_id = Column(Integer, ForeignKey('actividades.id'))
    tipo = Column(String)  # 'archivo' o 'link'
    nombre = Column(String)  # Nombre para mostrar
    url = Column(String)  # Ruta del archivo o URL
    
    # Relaciones
    actividad = relationship("Actividad", back_populates="materiales")
    
    def __repr__(self):
        return f"<Material {self.nombre}>"

class Entrega(Base):
    """Entregas de los estudiantes"""
    __tablename__ = 'entregas'
    
    id = Column(Integer, primary_key=True)
    actividad_id = Column(Integer, ForeignKey('actividades.id'))
    estudiante_nombre = Column(String, nullable=False)
    companero_nombre = Column(String, nullable=True)
    comentarios = Column(String, nullable=True)
    archivo_nombre = Column(String)  # Nombre original
    archivo_ruta = Column(String)    # Ruta donde se guardó
    fecha_hora = Column(DateTime, default=datetime.now)
    
    # Relaciones
    actividad = relationship("Actividad", back_populates="entregas")
    
    def __repr__(self):
        return f"<Entrega {self.estudiante_nombre} - {self.actividad.nombre}>"