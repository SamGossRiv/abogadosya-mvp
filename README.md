# AbogadosYA — Primer Incremento Funcional (Módulo de Autenticación)

Primer incremento funcional de **AbogadosYA** para el Primer Parcial de Práctica Interna (UPB). Implementa el módulo de autenticación y gestión de perfil: inicio de sesión con contraseñas cifradas (PBKDF2-SHA256 con *salt*), sesiones persistidas mediante tokens *Bearer* en SQLite, edición de nombre de usuario, cambio de contraseña con validación de complejidad y cierre de sesión con invalidación real del token.

## Requisitos previos

- Python 3.10 o superior
- Git

## Instalación y arranque (Backend API)

1. Clonar el repositorio e ingresar al directorio:
   ```bash
   git clone [https://github.com/SamGossRiv/abogadosya-mvp.git](https://github.com/SamGossRiv/abogadosya-mvp.git)
   cd abogadosya-mvp
   ```

2. Crear y activar el entorno virtual:
   - **Windows:**
     ```cmd
     py -m venv venv
     venv\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Iniciar el servidor de desarrollo:
   ```bash
   fastapi dev main.py
   ```
   - API: `http://127.0.0.1:8000`
   - Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`

## Datos de prueba

Al iniciar por primera vez, el sistema genera automáticamente `abogadosya.db` (SQLite) con credenciales ficticias de prueba (sin datos ni contraseñas reales):

- **Cliente:** usuario `SAMUEL2003` / contraseña `Abogados123`
- **Abogado:** usuario `CMENDEZ` / contraseña `Abogados123`

## Endpoints principales

| Método | Ruta | Auth | Descripción |
| :--- | :--- | :---: | :--- |
| `POST` | `/api/auth/register` | No | Registra un nuevo usuario validando política de contraseña. |
| `POST` | `/api/auth/login` | No | Valida credenciales y genera un `access_token` persistido en BD. |
| `GET` | `/api/auth/me` | Bearer | Devuelve el perfil del usuario autenticado. |
| `PATCH` | `/api/auth/username` | Bearer | Actualiza el nombre de usuario verificando unicidad. |
| `PATCH` | `/api/auth/password` | Bearer | Cambia la contraseña exigiendo mayúsculas, minúsculas, números y 8+ caracteres. |
| `POST` | `/api/auth/logout` | Bearer | Elimina el token de la BD e invalida la sesión. |

## Pruebas reproducibles (desde `/docs`)

1. **Flujo exitoso:**
   - Ejecutar `POST /api/auth/login` con `SAMUEL2003` / `Abogados123` → responde `200 OK` con `access_token`.
   - Configurar el token en el botón **Authorize** de Swagger y ejecutar `GET /api/auth/me` → responde `200 OK` con el perfil.
   - Ejecutar `PATCH /api/auth/username` y `PATCH /api/auth/password` con una clave válida → responde `200 OK` persistiendo cambios en SQLite.
2. **Pruebas de error / condición límite:**
   - Enviar una contraseña débil (ej. `"debil"`) en `PATCH /api/auth/password` → responde `400 Bad Request` detallando las reglas incumplidas.
   - Ejecutar `POST /api/auth/logout` y volver a llamar a `GET /api/auth/me` con el mismo token → responde `401 Unauthorized` confirmando la revocación de sesión.