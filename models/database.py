"""
Configuración de la base de datos con SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Ruta de la base de datos
DB_PATH = Path(__file__).parent.parent / "data" / "colegio.db"
DB_PATH.parent.mkdir(exist_ok=True)

# URL de conexión SQLite
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Motor de base de datos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necesario para SQLite con múltiples hilos
)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

def get_db():
    """Dependencia para obtener una sesión de BD"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa la base de datos: crea tablas y datos iniciales"""
    from . import entities  # Importar modelos para que SQLAlchemy los conozca
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Insertar datos iniciales usando una sesión
    db = SessionLocal()
    try:
        # Verificar si ya hay datos
        if db.query(entities.Periodo).count() == 0:
            # Insertar periodos
            periodos = [
                entities.Periodo(id=1, nombre="Periodo 1", activo=True),
                entities.Periodo(id=2, nombre="Periodo 2", activo=False),
                entities.Periodo(id=3, nombre="Periodo 3", activo=False),
                entities.Periodo(id=4, nombre="Periodo 4", activo=False),
            ]
            for periodo in periodos:
                db.add(periodo)
            
            # Insertar grados (6 al 11)
            grados = []
            for numero in range(6, 12):
                grado = entities.Grado(numero=numero, activo=True)
                grados.append(grado)
                db.add(grado)
            db.flush()  # Para obtener los IDs
            
            # Insertar grupos (A, B, C)
            grupos = []
            for letra in ['A', 'B', 'C']:
                grupo = entities.Grupo(letra=letra, activo=True)
                grupos.append(grupo)
                db.add(grupo)
            db.flush()
            
            # Insertar combinaciones grado-grupo con contraseñas
            for grado in grados:
                for idx, grupo in enumerate(grupos, start=1):
                    # Contraseña: ej. 6A -> 601, 7B -> 702
                    password = f"{grado.numero}{idx:02d}"
                    grado_grupo = entities.GradoGrupo(
                        grado_id=grado.id,
                        grupo_id=grupo.id,
                        password=password,
                        activo=True
                    )
                    db.add(grado_grupo)
            
            db.commit()
            print("✅ Datos iniciales insertados")
        else:
            print("✅ Base de datos ya existente")
            
    finally:
        db.close()
    
    print("✅ Base de datos inicializada correctamente")