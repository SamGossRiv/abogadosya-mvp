from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# 1. Configuración de Base de Datos (SQLite local para no fallar en la demo)
DATABASE_URL = "sqlite:///./abogadosya.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 2. Modelos de SQLAlchemy (Tablas relacionales)
class ServicioDB(Base):
    __tablename__ = "servicios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    precio_bs = Column(Integer, nullable=False)


class AbogadoDB(Base):
    __tablename__ = "abogados"
    id = Column(Integer, primary_key=True, index=True)
    iniciales = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    especialidad = Column(String, nullable=False)
    matricula = Column(String, unique=True, nullable=False)
    calificacion = Column(Float, default=4.9)
    resenas_count = Column(Integer, default=100)
    distancia_km = Column(Float, default=2.1)
    verificado = Column(Boolean, default=True)
    disponible = Column(Boolean, default=True)
    whatsapp = Column(String, nullable=False)


class SolicitudDB(Base):
    __tablename__ = "solicitudes"
    id = Column(Integer, primary_key=True, index=True)
    servicio_id = Column(Integer, ForeignKey("servicios.id"), nullable=True)
    abogado_id = Column(Integer, ForeignKey("abogados.id"), nullable=False)
    es_sos = Column(Boolean, default=False)
    estado = Column(String, default="ASIGNADO")


Base.metadata.create_all(bind=engine)


# 3. Carga inicial de datos de prueba (si la BD está vacía)
def cargar_datos_prueba():
    db = SessionLocal()
    if db.query(ServicioDB).count() == 0:
        db.add_all([
            ServicioDB(nombre="Revisión de Contrato", descripcion="Revisión, anotaciones y notas legales",
                       precio_bs=100),
            ServicioDB(nombre="Asesoría Legal (30 min)", descripcion="Consulta y orientación inmediata", precio_bs=150),
            ServicioDB(nombre="Representación Menor", descripcion="Trámites iniciales y memoriales breves",
                       precio_bs=300),
        ])
    if db.query(AbogadoDB).count() == 0:
        db.add_all([
            AbogadoDB(
                iniciales="AF", nombre="Lic. Ana Fernández", especialidad="Derecho Civil y Contratos",
                matricula="MJ-96412", calificacion=4.9, resenas_count=128, distancia_km=2.1,
                verificado=True, disponible=True, whatsapp="59170000001"
            ),
            AbogadoDB(
                iniciales="CR", nombre="Lic. Carlos Rivera", especialidad="Derecho Penal y Tránsito",
                matricula="MJ-88210", calificacion=4.8, resenas_count=64, distancia_km=3.8,
                verificado=True, disponible=True, whatsapp="59170000002"
            ),
            AbogadoDB(
                iniciales="FP", nombre="Falso Abogado (Prueba)", especialidad="Sin especialidad",
                matricula="INVALIDA", calificacion=1.0, resenas_count=0, distancia_km=1.0,
                verificado=False, disponible=True, whatsapp="59170000003"
            ),
        ])
    db.commit()
    db.close()


cargar_datos_prueba()


# 4. Schemas de Pydantic (Validación de entrada y contrato JSON)
class MatchRequest(BaseModel):
    servicio_id: int | None = None
    es_sos: bool = False


# 5. Instancia de FastAPI y CORS (para conectar con la SPA de Diego)
app = FastAPI(title="AbogadosYA API - Primer Incremento")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite peticiones desde React/SPA en desarrollo
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

# RF-02 / HU1: Obtener catálogo con tarifas fijas (y búsqueda opcional ?q=...)
@app.get("/api/servicios")
def listar_servicios(q: str | None = None, db: Session = Depends(get_db)):
    query = db.query(ServicioDB)
    if q:
        query = query.filter(ServicioDB.nombre.ilike(f"%{q}%"))
    return query.all()


# RF-01, RF-05, RF-06 / HU3: Matchmaking SOS o por servicio + persistencia
@app.post("/api/match")
def crear_match(datos: MatchRequest, db: Session = Depends(get_db)):
    servicio_info = {"nombre": "Asistencia SOS Legal", "total_bs": 150}

    if not datos.es_sos:
        servicio = db.query(ServicioDB).filter(ServicioDB.id == datos.servicio_id).first()
        if not servicio:
            raise HTTPException(status_code=404, detail="Servicio no encontrado en el catálogo.")
        servicio_info = {"nombre": servicio.nombre, "total_bs": servicio.precio_bs}

    # Regla de negocio: solo abogados verificados (Min. Justicia) y disponibles
    abogado = db.query(AbogadoDB).filter(
        AbogadoDB.verificado == True,
        AbogadoDB.disponible == True
    ).first()

    # Condición límite / Error (Riesgo R-02)
    if not abogado:
        raise HTTPException(
            status_code=404,
            detail="No hay abogados verificados disponibles en este momento. Intente en unos minutos."
        )

    # Persistencia en BD
    nueva_solicitud = SolicitudDB(
        servicio_id=datos.servicio_id if not datos.es_sos else None,
        abogado_id=abogado.id,
        es_sos=datos.es_sos,
        estado="ASIGNADO"
    )
    db.add(nueva_solicitud)
    db.commit()
    db.refresh(nueva_solicitud)

    return {
        "solicitud_id": nueva_solicitud.id,
        "estado": nueva_solicitud.estado,
        "tiempo_estimado": "1-3 minutes",
        "servicio_seleccionado": servicio_info,
        "abogado": {
            "id": abogado.id,
            "iniciales": abogado.iniciales,
            "nombre": abogado.nombre,
            "especialidad": abogado.especialidad,
            "matricula": abogado.matricula,
            "calificacion": abogado.calificacion,
            "resenas_count": abogado.resenas_count,
            "distancia_km": abogado.distancia_km,
            "verificado": abogado.verificado,
            "disponible": abogado.disponible,
            "whatsapp": abogado.whatsapp,
            "whatsapp_url": f"https://wa.me/{abogado.whatsapp}?text=Hola%20solicito%20asistencia%20legal%20desde%20AbogadosYA"
        }
    }


# Extra útil para la defensa: ver solicitudes guardadas en BD
@app.get("/api/solicitudes")
def listar_solicitudes(db: Session = Depends(get_db)):
    return db.query(SolicitudDB).all()


# Extra útil para probar el error 404 en vivo (cambiar disponibilidad de un abogado)
@app.patch("/api/abogados/{abogado_id}/disponibilidad")
def cambiar_disponibilidad(abogado_id: int, disponible: bool, db: Session = Depends(get_db)):
    abogado = db.query(AbogadoDB).filter(AbogadoDB.id == abogado_id).first()
    if not abogado:
        raise HTTPException(status_code=404, detail="Abogado no encontrado.")
    abogado.disponible = disponible
    db.commit()
    return {"id": abogado.id, "nombre": abogado.nombre, "disponible": abogado.disponible}