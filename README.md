# AbogadosYA — Primer Incremento Funcional (MVP)

Primer incremento funcional de **AbogadosYA** para el Primer Parcial de Práctica Interna (UPB). Implementa el flujo principal de extremo a extremo: catálogo de servicios legales con tarifas fijas en Bolivianos (Bs.), solicitud mediante **Botón SOS Legal**, emparejamiento (Matchmaking) filtrando únicamente abogados verificados y disponibles, persistencia en base de datos relacional y derivación a WhatsApp.

## Requisitos previos

- Python 3.10 o superior
- Git

## Instalación y arranque (Backend API)

1. Clonar el repositorio e ingresar al directorio del proyecto:
   ```bash
   git clone [https://github.com/TU_USUARIO/abogadosya-mvp.git](https://github.com/TU_USUARIO/abogadosya-mvp.git)
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

3. Instalar las dependencias del proyecto:
   ```bash
   pip install -r requirements.txt
   ```

4. Iniciar el servidor de desarrollo:
   ```bash
   fastapi dev main.py
   ```
   - API disponible en: `http://127.0.0.1:8000`
   - Documentación interactiva (Swagger UI): `http://127.0.0.1:8000/docs`

## Variables de entorno de ejemplo y datos de prueba

El proyecto utiliza SQLite por defecto (`DATABASE_URL=sqlite:///./abogadosya.db`) y no requiere contraseñas ni credenciales reales para su ejecución local.

Al iniciar por primera vez, el sistema crea automáticamente el archivo `abogadosya.db` precargado con datos ficticios:
- **3 servicios legales** con tarifas fijas en Bolivianos (100 Bs., 150 Bs. y 300 Bs.).
- **3 perfiles de abogados de prueba:** dos verificados y disponibles (`verificado=True`, `disponible=True`) y un perfil no verificado (`verificado=False`) para comprobar el filtro de seguridad.

## Endpoints principales

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/servicios` | Lista el catálogo con tarifas fijas en Bs. (acepta filtro `?q=texto`). |
| `POST` | `/api/match` | Ejecuta el emparejamiento SOS o por servicio y registra la solicitud en la BD. |
| `GET` | `/api/solicitudes` | Lista las solicitudes persistidas en la base de datos. |
| `PATCH` | `/api/abogados/{abogado_id}/disponibilidad` | Modifica el estado `disponible` (`true`/`false`) de un abogado para pruebas. |

## Criterios de aceptación y pruebas reproducibles

Las pruebas pueden ejecutarse directamente desde `http://127.0.0.1:8000/docs`:

### 1. Prueba de flujo exitoso (HU1 y HU3)
- **Catálogo y transparencia tarifaria (HU1):** Ejecutar `GET /api/servicios` → devuelve `200 OK` con la lista de servicios y precios exactos en Bs. sin costos ocultos.
- **Asignación de emergencia y derivación (HU3):** Ejecutar `POST /api/match` con el cuerpo `{"servicio_id": null, "es_sos": true}` → devuelve `200 OK`, asigna a una abogada verificada y disponible, y retorna el enlace directo `whatsapp_url`.
- **Verificación de persistencia:** Ejecutar `GET /api/solicitudes` → confirma que la solicitud generada quedó almacenada en SQLite con estado `ASIGNADO`.

### 2. Prueba de error / condición límite (RF-01 y Riesgo R-02)
- Desactivar a los dos abogados verificados ejecutando `PATCH /api/abogados/1/disponibilidad?disponible=false` y `PATCH /api/abogados/2/disponibilidad?disponible=false`.
- Ejecutar `POST /api/match` con `{"servicio_id": null, "es_sos": true}`.
- **Resultado esperado:** El sistema descarta al abogado `id=3` por tener `verificado=false` y responde con código `404 Not Found` indicando que no hay abogados verificados disponibles en ese momento.