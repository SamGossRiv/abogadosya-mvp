import hashlib
import hmac
import secrets
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# 1. Base de datos SQLite
DATABASE_URL = "sqlite:///./abogadosya.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Seguridad (Hash con salt usando librería estándar, sin dependencias extra)
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
    return f"{salt}${dk}"

def verificar_password(password: str, stored_hash: str) -> bool:
    try:
        salt, dk = stored_hash.split("$")
    except ValueError:
        return False
    nuevo_dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000).hex()
    return hmac.compare_digest(nuevo_dk, dk)

def validar_politica_password(password: str) -> None:
    errores = []
    if len(password) < 8:
        errores.append("8 o más caracteres")
    if not any(c.isupper() for c in password):
        errores.append("al menos una mayúscula")
    if not any(c.islower() for c in password):
        errores.append("al menos una minúscula")
    if not any(c.isdigit() for c in password):
        errores.append("al menos un número")
    if errores:
        raise HTTPException(
            status_code=400,
            detail=f"La contraseña debe contener: {', '.join(errores)}."
        )

# 3. Modelos de SQLAlchemy
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    nombre_completo = Column(String, nullable=False)
    rol = Column(String, default="cliente")  # "cliente" o "abogado"
    password_hash = Column(String, nullable=False)

class SesionDB(Base):
    __tablename__ = "sesiones"
    token = Column(String, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    creado_en = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# 4. Datos iniciales de prueba (usuarios del Figma)
def cargar_usuarios_prueba():
    db = SessionLocal()
    if db.query(UsuarioDB).count() == 0:
        db.add_all([
            UsuarioDB(
                username="SAMUEL2003",
                nombre_completo="Samuel Gossweiler",
                rol="cliente",
                password_hash=hash_password("Abogados123"),
            ),
            UsuarioDB(
                username="CMENDEZ",
                nombre_completo="Dr. Carlos Eduardo Méndez",
                rol="abogado",
                password_hash=hash_password("Abogados123"),
            ),
        ])
        db.commit()
    db.close()

cargar_usuarios_prueba()

# 5. Schemas de Pydantic
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    nombre_completo: str = Field(..., min_length=3, max_length=100)
    rol: str = Field(default="cliente")
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class ChangeUsernameRequest(BaseModel):
    nuevo_username: str = Field(..., min_length=3, max_length=30)

class ChangePasswordRequest(BaseModel):
    password_actual: str
    nueva_password: str
    confirmar_password: str

# 6. App FastAPI + CORS + Bearer Auth
app = FastAPI(title="AbogadosYA API - Módulo de Autenticación")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_sesion_actual(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> tuple[SesionDB, UsuarioDB]:
    sesion = db.query(SesionDB).filter(SesionDB.token == credentials.credentials).first()
    if not sesion:
        raise HTTPException(status_code=401, detail="Sesión inválida o cerrada.")
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == sesion.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado.")
    return sesion, usuario

# --- ENDPOINTS DE AUTENTICACIÓN ---

# Registro de cuenta nueva (útil para pruebas o si se agrega pantalla de registro)
@app.post("/api/auth/register", status_code=201)
def registrar_usuario(datos: RegisterRequest, db: Session = Depends(get_db)):
    username_limpio = datos.username.strip()
    if db.query(UsuarioDB).filter(UsuarioDB.username.ilike(username_limpio)).first():
        raise HTTPException(status_code=409, detail="El nombre de usuario ya está registrado.")
    validar_politica_password(datos.password)

    nuevo = UsuarioDB(
        username=username_limpio,
        nombre_completo=datos.nombre_completo.strip(),
        rol=datos.rol if datos.rol in ("cliente", "abogado") else "cliente",
        password_hash=hash_password(datos.password),
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {
        "id": nuevo.id,
        "username": nuevo.username,
        "nombre_completo": nuevo.nombre_completo,
        "rol": nuevo.rol,
    }

# 1. Iniciar sesión
@app.post("/api/auth/login")
def iniciar_sesion(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(UsuarioDB).filter(UsuarioDB.username == datos.username.strip()).first()
    if not usuario or not verificar_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    token = secrets.token_hex(32)
    nueva_sesion = SesionDB(
        token=token,
        usuario_id=usuario.id,
        creado_en=datetime.now(timezone.utc).isoformat(),
    )
    db.add(nueva_sesion)
    db.commit()

    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "username": usuario.username,
            "nombre_completo": usuario.nombre_completo,
            "rol": usuario.rol,
        },
    }

# 2. Obtener perfil del usuario autenticado
@app.get("/api/auth/me")
def obtener_perfil(actual=Depends(get_sesion_actual)):
    _, usuario = actual
    return {
        "id": usuario.id,
        "username": usuario.username,
        "nombre_completo": usuario.nombre_completo,
        "rol": usuario.rol,
    }

# 3. Cambiar nombre de usuario
@app.patch("/api/auth/username")
def cambiar_username(
    datos: ChangeUsernameRequest,
    actual=Depends(get_sesion_actual),
    db: Session = Depends(get_db),
):
    _, usuario = actual
    nuevo = datos.nuevo_username.strip()

    if nuevo == usuario.username:
        raise HTTPException(status_code=400, detail="El nuevo nombre de usuario es igual al actual.")
    if db.query(UsuarioDB).filter(UsuarioDB.username.ilike(nuevo)).first():
        raise HTTPException(status_code=409, detail="Ese nombre de usuario ya está en uso.")

    usuario.username = nuevo
    db.commit()
    db.refresh(usuario)
    return {
        "mensaje": "Nombre de usuario actualizado.",
        "username": usuario.username,
    }

# 4. Cambiar contraseña (con las 4 reglas del Figma)
@app.patch("/api/auth/password")
def cambiar_password(
    datos: ChangePasswordRequest,
    actual=Depends(get_sesion_actual),
    db: Session = Depends(get_db),
):
    _, usuario = actual

    if not verificar_password(datos.password_actual, usuario.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta.")
    if datos.nueva_password != datos.confirmar_password:
        raise HTTPException(status_code=400, detail="Las contraseñas nuevas no coinciden.")

    validar_politica_password(datos.nueva_password)

    usuario.password_hash = hash_password(datos.nueva_password)
    db.commit()
    return {"mensaje": "Contraseña actualizada correctamente."}

# 5. Cerrar sesión (invalida el token en SQLite)
@app.post("/api/auth/logout")
def cerrar_sesion(actual=Depends(get_sesion_actual), db: Session = Depends(get_db)):
    sesion, _ = actual
    db.delete(sesion)
    db.commit()
    return {"mensaje": "Sesión cerrada correctamente."}