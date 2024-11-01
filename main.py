from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import bmg_books

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Lectura Inspirada",
    description="API para gestionar la lectura inspirada",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuración de CORS
origins = [

     "https://api-lectura-testing.analyticalpoint.com",
     "https://api-lectura-testing.analyticalpoint.com/bmg_books/promocion_diaria",
     
     "https://libreria-mho-digital.flutterflow.app"
     "https://libreria.mho.digital",
     "https://lecturainspirada.com",
     "http://canal.bibliomanager.com",
     "http://localhost:4200",
     "http://localhost",
     "https://libreria-testing.analyticalpoint.com",
     "https://libreria-mayorista.mho.digital",
     "https://distribucion-libros.mho.digital"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://libreria.mho.digital", "https://libreria-mho-digital.flutterflow.app", "http://localhost:4200", "http://localhost",
                   "https://libreria-testing.analyticalpoint.com", "https://libreria-mayorista.mho.digital",
                   "https://lecturainspirada.com", "https://distribucion-libros.mho.digital"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
#     allow_origins=origins,  # Usa dominios específicos en lugar de ["*"]
#     allow_credentials=False,  # Ponlo en False si no necesitas credenciales
#     allow_methods=["GET", "POST", "OPTIONS"],  # Especifica los métodos permitidos
#     allow_headers=["Content-Type", "Authorization"],  # Especifica los headers permitidos

)

# Incluir routers
app.include_router(bmg_books.router, prefix='/bmg_books', tags=["bmg_books"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de lectura inspirada"}