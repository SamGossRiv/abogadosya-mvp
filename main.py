from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Table, Column, Integer, String, Boolean, ForeignKey, or_
from sqlalchemy.orm import sessionmaker, declarative_base, Session, relationship

# 1. Base de datos SQLite
DATABASE_URL = "sqlite:///./abogadosya.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Tabla intermedia (Muchos a Muchos: un abogado tiene varias skills/servicios)
abogado_servicios = Table(
    "abogado_servicios",
    Base.metadata,
    Column("abogado_id", Integer, ForeignKey("abogados.id"), primary_key=True),
    Column("servicio_id", Integer, ForeignKey("servicios.id"), primary_key=True),
)

# 2. Modelos de SQLAlchemy
class ServicioDB(Base):
    __tablename__ = "servicios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False)

class AbogadoDB(Base):
    __tablename__ = "abogados"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    especialidad = Column(String, nullable=False)
    ubicacion = Column(String, nullable=True)
    contacto = Column(String, nullable=True)
    verificado = Column(Boolean, default=True)
    servicios = relationship("ServicioDB", secondary=abogado_servicios, lazy="joined")

class CasoDB(Base):
    __tablename__ = "casos"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    nombre_referencia = Column(String, nullable=True)
    fecha_publicacion = Column(String, nullable=False)
    resuelto = Column(Boolean, default=False)

Base.metadata.create_all(bind=engine)

# 3. Datos iniciales basados en el Figma
def cargar_datos_prueba():
    db = SessionLocal()
    if db.query(ServicioDB).count() == 0:
        skills = [
            "asesoramiento",
            "representación legal",
            "elaboración de contratos",
            "defensa penal",
            "derecho laboral",
            "trámites inmobiliarios",
            "conciliación",
        ]
        db.add_all([ServicioDB(nombre=s) for s in skills])
        db.commit()

    if db.query(AbogadoDB).count() == 0:
        s_asesoramiento = db.query(ServicioDB).filter_by(nombre="asesoramiento").first()
        s_representacion = db.query(ServicioDB).filter_by(nombre="representación legal").first()
        s_contratos = db.query(ServicioDB).filter_by(nombre="elaboración de contratos").first()
        s_penal = db.query(ServicioDB).filter_by(nombre="defensa penal").first()
        s_inmuebles = db.query(ServicioDB).filter_by(nombre="trámites inmobiliarios").first()

        db.add_all([
            AbogadoDB(
                nombre="Dr. Carlos Eduardo Méndez",
                especialidad="Derecho civil y comercial.",
                ubicacion="C. San Martin & C. Colombia - Cochabamba, Bolivia",
                contacto="+591 7777777",
                verificado=True,
                servicios=[s_asesoramiento, s_representacion, s_contratos],
            ),
            AbogadoDB(
                nombre="Dra. Ana Fernández",
                especialidad="Derecho penal y litigios.",
                ubicacion="Av. Ballivián #450 - Cochabamba, Bolivia",
                contacto="+591 70000001",
                verificado=True,
                servicios=[s_asesoramiento, s_penal, s_inmuebles],
            ),
            AbogadoDB(
                nombre="Usuario No Verificado (Prueba)",
                especialidad="Sin especialidad",
                ubicacion="Cochabamba, Bolivia",
                contacto="+591 70000099",
                verificado=False,
                servicios=[s_asesoramiento],
            ),
        ])
        db.commit()

    if db.query(CasoDB).count() == 0:
        db.add_all([
            CasoDB(
                titulo="Incumplimiento de acuerdo comercial",
                descripcion="Realicé un acuerdo comercial con otra persona para desarrollar un negocio. Sin embargo, la otra parte no está cumpliendo con las condiciones acordadas y ha dejado de responder a mis comunicaciones. Busco asesoramiento para resolver el conflicto.",
                nombre_referencia="Diego Solano",
                fecha_publicacion="11 oct",
                resuelto=False,
            ),
            CasoDB(
                titulo="Conflicto por propiedad de un inmueble",
                descripcion="Tengo problemas con otra persona respecto a los límites de un terreno que adquirí. Cuento con documentos que respaldan la compra y busco representación legal.",
                nombre_referencia=None,
                fecha_publicacion="17 ago",
                resuelto=False,
            ),
        ])
        db.commit()
    db.close()

cargar_datos_prueba()

# 4. Schemas de Pydantic
class CasoCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=150)
    descripcion: str = Field(..., min_length=10)
    nombre_referencia: str | None = None

class AbogadoUpdate(BaseModel):
    nombre: str | None = None
    especialidad: str | None = None
    ubicacion: str | None = None
    contacto: str | None = None
    servicios: list[str] | None = None  # Lista de nombres de skills

# Helper para devolver formato limpio al frontend
def serializar_abogado(abogado: AbogadoDB) -> dict:
    return {
        "id": abogado.id,
        "nombre": abogado.nombre,
        "especialidad": abogado.especialidad,
        "servicios": [s.nombre for s in abogado.servicios],
        "ubicacion": abogado.ubicacion,
        "contacto": abogado.contacto,
        "verificado": abogado.verificado,
    }

# 5. App FastAPI + CORS
app = FastAPI(title="AbogadosYA API - Primer Incremento")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINTS ---

# 1. CLIENTE (Inicio): Buscar abogados verificados por nombre, especialidad o skills
@app.get("/api/abogados")
def listar_abogados(q: str | None = None, db: Session = Depends(get_db)):
    query = db.query(AbogadoDB).filter(AbogadoDB.verificado == True)
    if q and q.strip():
        termino = q.strip()
        # Quita 's' final simple para que "asesoramientos" encuentre "asesoramiento"
        termino_alt = termino[:-1] if len(termino) > 4 and termino.lower().endswith("s") else termino
        query = query.outerjoin(AbogadoDB.servicios).filter(
            or_(
                AbogadoDB.nombre.ilike(f"%{termino}%"),
                AbogadoDB.especialidad.ilike(f"%{termino}%"),
                ServicioDB.nombre.ilike(f"%{termino}%"),
                ServicioDB.nombre.ilike(f"%{termino_alt}%"),
            )
        ).distinct()
    return [serializar_abogado(a) for a in query.all()]

# 2. CLIENTE Y ABOGADO (Perfil): Obtener perfil completo de un abogado
@app.get("/api/abogados/{abogado_id}")
def obtener_abogado(abogado_id: int, db: Session = Depends(get_db)):
    abogado = db.query(AbogadoDB).filter(AbogadoDB.id == abogado_id).first()
    if not abogado:
        raise HTTPException(status_code=404, detail="Abogado no encontrado.")
    return serializar_abogado(abogado)

# 3. ABOGADO (Editar perfil): Actualizar nombre, especialidad, skills, ubicación o contacto
@app.put("/api/abogados/{abogado_id}")
def editar_abogado(abogado_id: int, datos: AbogadoUpdate, db: Session = Depends(get_db)):
    abogado = db.query(AbogadoDB).filter(AbogadoDB.id == abogado_id).first()
    if not abogado:
        raise HTTPException(status_code=404, detail="Abogado no encontrado.")

    cambios = datos.model_dump(exclude_unset=True)

    if "nombre" in cambios and cambios["nombre"] is not None:
        abogado.nombre = cambios["nombre"]
    if "especialidad" in cambios and cambios["especialidad"] is not None:
        abogado.especialidad = cambios["especialidad"]
    if "ubicacion" in cambios:
        abogado.ubicacion = cambios["ubicacion"]  # Permite null si elimina ubicación
    if "contacto" in cambios:
        abogado.contacto = cambios["contacto"]    # Permite null si elimina contacto

    if "servicios" in cambios and cambios["servicios"] is not None:
        nuevas_skills = []
        for nombre_skill in cambios["servicios"]:
            skill = db.query(ServicioDB).filter(ServicioDB.nombre.ilike(nombre_skill.strip())).first()
            if not skill:
                raise HTTPException(
                    status_code=400,
                    detail=f"La skill '{nombre_skill}' no existe en el catálogo de servicios."
                )
            nuevas_skills.append(skill)
        abogado.servicios = nuevas_skills

    db.commit()
    db.refresh(abogado)
    return serializar_abogado(abogado)

# 4. ABOGADO (Editar perfil): Buscar skills disponibles por palabra clave
@app.get("/api/servicios")
def listar_servicios(q: str | None = None, db: Session = Depends(get_db)):
    query = db.query(ServicioDB)
    if q and q.strip():
        query = query.filter(ServicioDB.nombre.ilike(f"%{q.strip()}%"))
    return query.all()

# 5. ABOGADO (Inicio): Buscar casos sin resolver por palabras clave
@app.get("/api/casos")
def listar_casos(q: str | None = None, db: Session = Depends(get_db)):
    query = db.query(CasoDB).filter(CasoDB.resuelto == False)
    if q and q.strip():
        termino = f"%{q.strip()}%"
        query = query.filter(
            or_(
                CasoDB.titulo.ilike(termino),
                CasoDB.descripcion.ilike(termino),
            )
        )
    return query.order_by(CasoDB.id.desc()).all()

# 6. CLIENTE (Publicar): Publicar un nuevo caso
@app.post("/api/casos", status_code=201)
def publicar_caso(datos: CasoCreate, db: Session = Depends(get_db)):
    meses = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
    hoy = datetime.now()
    fecha_str = f"{hoy.day} {meses[hoy.month - 1]}"

    nuevo_caso = CasoDB(
        titulo=datos.titulo.strip(),
        descripcion=datos.descripcion.strip(),
        nombre_referencia=datos.nombre_referencia.strip() if datos.nombre_referencia else None,
        fecha_publicacion=fecha_str,
        resuelto=False,
    )
    db.add(nuevo_caso)
    db.commit()
    db.refresh(nuevo_caso)
    return nuevo_caso

# 7. Ver detalle de un caso específico (útil para probar 404)
@app.get("/api/casos/{caso_id}")
def obtener_caso(caso_id: int, db: Session = Depends(get_db)):
    caso = db.query(CasoDB).filter(CasoDB.id == caso_id).first()
    if not caso:
        raise HTTPException(status_code=404, detail="Caso no encontrado.")
    return caso