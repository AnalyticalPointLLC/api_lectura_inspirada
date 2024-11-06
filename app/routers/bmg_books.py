from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from typing import List, Optional, Dict
from app.database import get_db, SessionLocal
from app import crud, schemas



import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from app.schemas import EmailRequest  # Ajusta la ruta según el lugar donde esté definido

from datetime import datetime  # Asegúrate de importar datetime




# Configuración de Logging
logging.basicConfig(level=logging.DEBUG,  # Cambiar a INFO o ERROR en producción
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

router = APIRouter(
    prefix="",
    tags=["bmg_books"],
    responses={404: {"description": "Not found"}},
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Libros BMG (Books)
# ------------------

@router.get("/", response_model=List[schemas.BmgBook], tags=["Books"], description="Read BMG Books (Leer Libros BMG)")
def read_bmg_books(db: Session = Depends(get_db), limit: int = Query(250, ge=1), offset: int = Query(0, ge=0)):
    try:
        bmg_books = crud.get_bmg_books(db, limit=limit, offset=offset)
        return bmg_books
    except Exception as e:
        logging.error(f"Error al leer los libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/search", response_model=List[schemas.BmgBook], tags=["Books"], description="Search Books (Buscar Libros)")
def search_books(
    titulo: Optional[str] = Query(None),
    isbn13: Optional[str] = Query(None),
    resumen: Optional[str] = Query(None),
    pais_edicion: Optional[str] = Query(None),
    editor: Optional[str] = Query(None),
    año_publicacion: Optional[int] = Query(None),
    autor: Optional[str] = Query(None),
    nombre_clasificacion: Optional[str] = Query(None),
    sello: Optional[str] = Query(None),
    clasificacion: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    search_params = {
        'titulo': titulo,
        'isbn13': isbn13,
        'resumen': resumen,
        'pais_edicion': pais_edicion,
        'editor': editor,
        'fecha_publicacion': año_publicacion,
        'autor': autor,
        'nombre_clasificacion': nombre_clasificacion,
        'sello': sello,
        'clasificacion': clasificacion
    }
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    try:
        books = crud.search_books(db, search_params)
        if not books:
            raise HTTPException(status_code=404, detail="Books not found")
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al buscar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al buscar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/book/{book_id}", response_model=schemas.BmgBook, tags=["Books"], description="Read Book by ID (Leer Libro por ID)")
def read_book_by_id(book_id: int, db: Session = Depends(get_db)):
    try:
        book = crud.get_book_by_id(db, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al obtener libro por ID: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Clasificaciones (Classifications)
# ---------------------------------

@router.get("/classifications/unique", response_model=List[str], tags=["Classifications"], description="Get Classification Name (Obtener Nombre de Clasificación)")
def get_nombre_clasificacion(db: Session = Depends(get_db)):
    try:
        nombres_clasificacion = crud.get_nombre_clasificacion(db)
        return nombres_clasificacion
    except Exception as e:
        logging.error(f"Error al obtener clasificaciones: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/classifications/primary", response_model=List[schemas.ClasificacionIBIC], tags=["Classifications"], description="Get Primary Classifications (Obtener Clasificaciones Primarias)")
def get_primary_classifications(db: Session = Depends(get_db)):
    try:
        primary_classifications = crud.get_primary_classifications(db)
        logging.debug(f"Primary classifications returned: {primary_classifications}")
        return primary_classifications
    except Exception as e:
        logging.error(f"Error al obtener clasificaciones primarias: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/classifications/{primary_code}/subclassifications", response_model=List[Dict[str, str]], tags=["Classifications"], description="Get Subclassifications (Obtener Subclasificaciones)")
def get_subclassifications(primary_code: str, db: Session = Depends(get_db)):
    try:
        subcategories = crud.get_subclassifications(db, primary_code)
        return subcategories  # Devuelve subcategories incluso si está vacío
    except Exception as e:
        logging.error(f"Error al obtener subclasificaciones: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/classifications/subclassifications_by_name/{nombre_clasificacion}", response_model=List[Dict[str, str]], tags=["Classifications"], description="Get Subclassifications by Classification Name (Obtener Subclasificaciones por Nombre de Clasificación)")
def get_subclassifications_by_name(nombre_clasificacion: str, db: Session = Depends(get_db)):
    try:
        subcategories = crud.get_subclassifications_by_name(db, nombre_clasificacion)
        if not subcategories:
            raise HTTPException(status_code=404, detail="No se encontraron subclasificaciones para el nombre de clasificación proporcionado")
        return subcategories
    except Exception as e:
        logging.error(f"Error al obtener subclasificaciones por nombre: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/classifications/books_by_name/{nombre_clasificacion}", response_model=List[schemas.BmgBook], tags=["Classifications"], description="Get Books by Classification Name (Obtener Libros por Nombre de Clasificación)")
def get_books_by_classification_name(nombre_clasificacion: str, db: Session = Depends(get_db)):
    try:
        books = crud.get_books_by_classification_name(db, nombre_clasificacion)
        if not books:
            raise HTTPException(status_code=404, detail="Libros no encontrados para la clasificación proporcionada")
        return books
    except Exception as e:
        logging.error(f"Error al obtener libros por clasificación: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/classifications/books/{classification}", response_model=List[schemas.BmgBook], tags=["Classifications"], description="Get Books by Classification (Obtener Libros por Clasificación)")
def search_books_by_classification(classification: str, db: Session = Depends(get_db)):
    try:
        books = crud.get_books_by_classification(db, classification)
        if not books:
            raise HTTPException(status_code=404, detail="Libros no encontrados para la clasificación proporcionada")
        return books
    except Exception as e:
        logging.error(f"Error general al buscar libros por clasificación: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Autores (Authors)
# -----------------

@router.get("/authors/unique", response_model=List[str], tags=["Authors"], description="Get Author (Obtener Autor)")
def get_autor(db: Session = Depends(get_db)):
    try:
        autores = crud.get_autor(db)
        return autores
    except Exception as e:
        logging.error(f"Error al obtener autores: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/authors/initial/{initial}", response_model=List[str], tags=["Authors"], description="Get Authors by Initial (Obtener Autores por Inicial)")
def get_authors_by_initial(initial: str, db: Session = Depends(get_db)):
    try:
        autores = crud.get_authors_by_initial(db, initial)
        return autores
    except Exception as e:
        logging.error(f"Error al obtener autores por inicial: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/authors/search", response_model=List[str], tags=["Authors"], description="Search Authors (Buscar Autores)")
def search_authors(keyword: str = Query(...), db: Session = Depends(get_db)):
    try:
        autores = crud.search_authors(db, keyword)
        return autores
    except Exception as e:
        logging.error(f"Error al buscar autores: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/authors/books/{author}", response_model=List[schemas.BmgBook], tags=["Authors"], description="Get Books by Author (Obtener Libros por Autor)")
def get_books_by_author(author: str, db: Session = Depends(get_db)):
    try:
        books = crud.get_books_by_author(db, author)
        if not books:
            raise HTTPException(status_code=404, detail="Libros no encontrados para el autor proporcionado")
        return books
    except Exception as e:
        logging.error(f"Error al obtener libros por autor: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Países de Edición (Countries of Edition)
# ----------------------------------------

@router.get("/countries/unique", response_model=List[str], tags=["Countries"], description="Get Country of Edition (Obtener País de Edición)")
def get_pais_edicion(db: Session = Depends(get_db)):
    try:
        paises_edicion = crud.get_pais_edicion(db)
        return paises_edicion
    except Exception as e:
        logging.error(f"Error al obtener países de edición: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Sellos (Labels)
# ---------------

@router.get("/labels/unique", response_model=List[str], tags=["Labels"], description="Get Label (Obtener Sello)")
def get_sello(db: Session = Depends(get_db)):
    try:
        sellos = crud.get_sello(db)
        return sellos
    except Exception as e:
        logging.error(f"Error al obtener sellos: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Nuevos Títulos Diarios (New Titles Daily)
# -----------------------------------------

@router.get("/nuevos-titulos-diarios", response_model=List[schemas.BmgBook], tags=["New Titles"], description="Read New Titles Daily (Leer Nuevos Títulos Diarios)")
def read_nuevostitulosdiarios(db: Session = Depends(get_db), limit: int = Query(100, ge=1), offset: int = Query(0, ge=0)):
    try:
        productos = crud.get_nuevos_titulos_diarios(db, limit=limit, offset=offset)
        return productos
    except Exception as e:
        logging.error(f"Error al leer los nuevos productos diarios: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
    
# Nuevos Títulos Diarios Filtrados por Idioma
@router.get("/nuevos-titulos-diarios-filtrado", response_model=List[schemas.BmgBook], tags=["New Titles"], description="Read New Titles Daily with Language Filter (Leer Nuevos Títulos Diarios con Filtro de Idioma)")
def read_nuevostitulosdiarios_filtrado(
    idiomas: Optional[List[str]] = Query(None, title="Idiomas", description="Lista de idiomas para filtrar"),
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    try:
        productos = crud.get_nuevos_titulos_diarios_filtrado(db, idiomas, limit=limit, offset=offset)
        return productos
    except Exception as e:
        logging.error(f"Error al leer los nuevos productos diarios con filtro: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
@router.get("/search_by_language", response_model=List[schemas.BmgBook], tags=["Books"], description="Search Books by Language (Buscar Libros por Idioma)")
def search_books_by_language(
    idioma: str = Query(..., title="Idioma", description="Nombre del idioma en español"),
    limit: int = Query(100, ge=1, title="Limit", description="Número máximo de resultados a devolver"),
    offset: int = Query(0, ge=0, title="Offset", description="Número de resultados a omitir"),
    db: Session = Depends(get_db)
):
    try:
        books = crud.get_books_by_language(db, idioma, limit=limit, offset=offset)
        if not books:
            raise HTTPException(status_code=404, detail="Books not found")
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al buscar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al buscar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    

# Nuevo endpoint para promocion diaria con búsqueda por idioma
@router.get("/promocion_diaria", response_model=List[schemas.BmgBook], tags=["Books"], description="Search Daily Promotion Books (Buscar Libros en Promoción Diaria)")
def search_daily_promotion_books(
    idioma: str = Query(..., title="Idioma", description="Nombre del idioma en español"),
    limit: int = Query(100, ge=1, title="Limit", description="Número máximo de resultados a devolver"),
    offset: int = Query(0, ge=0, title="Offset", description="Número de resultados a omitir"),
    db: Session = Depends(get_db)
):
    try:
        books = crud.get_daily_promotion_books(db, idioma, limit=limit, offset=offset)
        if not books:
            raise HTTPException(status_code=404, detail="Books not found")
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al buscar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al buscar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
# Nuevo endpoint para buscar por idioma y nombre de clasificación
@router.get("/search_by_language_and_classification", response_model=List[schemas.BmgBook], tags=["Books"], description="Search Books by Language and Classification (Buscar Libros por Idioma y Clasificación)")
def search_books_by_language_and_classification(
    idioma: str = Query(..., title="Idioma", description="Nombre del idioma en español"),
    nombre_clasificacion: str = Query(..., title="Nombre Clasificación", description="Nombre de la clasificación"),
    limit: int = Query(100, ge=1, title="Limit", description="Número máximo de resultados a devolver"),
    offset: int = Query(0, ge=0, title="Offset", description="Número de resultados a omitir"),
    db: Session = Depends(get_db)
):
    try:
        books = crud.get_books_by_language_and_classification(db, idioma, nombre_clasificacion, limit=limit, offset=offset)
        if not books:
            raise HTTPException(status_code=404, detail="Books not found")
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al buscar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al buscar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# Nuevo endpoint para buscar por idioma y título
@router.get("/search_by_language_and_title", response_model=List[schemas.BmgBook], tags=["Books"], description="Search Books by Language and Title (Buscar Libros por Idioma y Título)")
def search_books_by_language_and_title(
    idioma: str = Query(..., title="Idioma", description="Nombre del idioma en español"),
    titulo: str = Query(..., title="Título", description="Título del libro"),
    limit: int = Query(100, ge=1, title="Limit", description="Número máximo de resultados a devolver"),
    offset: int = Query(0, ge=0, title="Offset", description="Número de resultados a omitir"),
    db: Session = Depends(get_db)
):
    try:
        books = crud.get_books_by_language_and_title(db, idioma, titulo, limit=limit, offset=offset)
        if not books:
            raise HTTPException(status_code=404, detail=f"No se encontraron libros con el título '{titulo}' en el idioma '{idioma}'. Error 404")
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al buscar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al buscar libros: {str(e)}")
        raise HTTPException(status_code=500, detail=f"No se encontraron libros con el título '{titulo}' en el idioma '{idioma}'. Error 500")
    
    

# Endpoint para contar libros por idioma y clasificación
@router.get("/count_books_by_language_and_classification", tags=["Books"], description="Count Books by Language and Classification (Contar Libros por Idioma y Clasificación)")
def count_books_by_language_and_classification(
    idioma: str = Query(..., title="Idioma", description="Nombre del idioma en español"),
    clasificacion: str = Query(..., title="Clasificación", description="Clasificación IBIC"),
    db: Session = Depends(get_db)
):
    try:
        count = crud.count_books_by_language_and_classification(db, idioma, clasificacion)
        if count == []:
            raise HTTPException(status_code=500, detail="Error al contar libros")
        return {"count": count}
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al contar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al contar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Endpoint para contar libros por clasificación
@router.get("/count_books_by_classification", tags=["Books"], description="Count Books by Classification (Contar Libros por Clasificación)")
def count_books_by_classification(
    clasificacion: str = Query(..., title="Clasificación", description="Clasificación IBIC"),
    db: Session = Depends(get_db)
):
    try:
        count = crud.count_books_by_classification(db, clasificacion)
        return {"count": count}
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al contar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al contar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")




# Endpoint para listar todos los códigos IBIC y la cantidad de filas
@router.get("/classification_counts", tags=["Books"], description="List Classification Counts (Listar Conteo de Clasificaciones)")
def classification_counts(db: Session = Depends(get_db)):
    try:
        classification_counts = crud.get_all_classification_counts_by_prefix(db)
        if not classification_counts:
            raise HTTPException(status_code=404, detail="No se encontraron clasificaciones")
        return classification_counts
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al listar clasificaciones: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al listar clasificaciones: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
# Endpoint para listar todos los códigos IBIC y la cantidad de filas filtrando por idioma
@router.get("/classification_counts_by_language", tags=["Books"], description="List Classification Counts by Language (Listar Conteo de Clasificaciones por Idioma)")
def classification_counts_by_language(
    idioma: str = Query(..., title="Idioma", description="Nombre del idioma en español"),
    db: Session = Depends(get_db)
):
    try:
        classification_counts = crud.get_classification_counts_by_language(db, idioma)
        if not classification_counts:
            raise HTTPException(status_code=404, detail="No se encontraron clasificaciones para el idioma proporcionado")
        return classification_counts
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al listar clasificaciones: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al listar clasificaciones: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    

# Endpoint para contar libros por clasificación y por idioma
@router.get("/count_books_by_language_and_classification", tags=["Books"], description="Count Books by Language and Classification (Contar Libros por Idioma y Clasificación)")
def count_books_by_language_and_classification(
    idioma: str = Query(..., title="Idioma", description="Nombre del idioma en español"),
    clasificacion: str = Query(..., title="Clasificación", description="Clasificación IBIC"),
    db: Session = Depends(get_db)
):
    try:
        count = crud.count_books_by_language_and_classification(db, idioma, clasificacion)
        if count == 0:
            raise HTTPException(status_code=404, detail="No se encontraron libros para el idioma y clasificación proporcionados")
        return {"count": count}
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al contar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al contar libros: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


## CODIGO PARA BUSCAR LIBROS CON IBIC Y CON IDIOMA
@router.get("/classifications/books/{classification}/language/{language}", response_model=List[schemas.BmgBook], tags=["Classifications"], description="Get Books by Classification and Language (Obtener Libros por Clasificación e Idioma)")
def search_books_by_classification_IBIC_Language(
    classification: str,
    language: str,
    limit: int = Query(100, ge=1, title="Limit", description="Número máximo de resultados a devolver"),
    offset: int = Query(0, ge=0, title="Offset", description="Número de resultados a omitir"),
    db: Session = Depends(get_db)
):
    try:
        books = crud.get_books_by_classification_and_language(db, classification, language, limit=limit, offset=offset)
        if not books:
            raise HTTPException(status_code=404, detail="Libros no encontrados para la clasificación e idioma proporcionados")
        return books
    except Exception as e:
        logging.error(f"Error general al buscar libros por clasificación e idioma: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



## CODIGO PARA BUSCAR LIBROS CON IBIC - primera letra Y CON IDIOMA

@router.get("/classifications/prefix/{prefix}/language/{language}", response_model=List[schemas.BmgBook], tags=["Classifications"], description="Get Books by Classification Prefix and Language")
def get_books_by_classification_prefix_and_language(prefix: str, language: str, limit: int = Query(100, ge=1), offset: int = Query(0, ge=0), db: Session = Depends(get_db)):
    books = crud.get_books_by_classification_prefix_and_language(db, prefix=prefix, language=language, limit=limit, offset=offset)
    if not books:
        raise HTTPException(status_code=404, detail="Books not found")
    return books



## CODIGO PARA EL DESCUENTO 10 unidades
@router.get("/discounted_price/{book_id}", tags=["Books"], description="Get Discounted Price by Book ID 10 units")
def get_discounted_price(book_id: int, db: Session = Depends(get_db)):
    try:
        book = crud.get_book_with_discounted_price(db, book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return {
            "id": book['id'],
            "titulo": book['titulo'],
            "precio_original": book['pvp'],
            "percentaje_descuento": book['percent_discount'],
            "precio_con_descuento": book['discounted_price'],
            
            "percentaje_descuento_100": book['percent_discount_100'],
            "precio_con_descuento_100": book['discounted_price_100'],
            
            "percentaje_descuento_1000": book['percent_discount_1000'],
            "precio_con_descuento_1000": book['discounted_price_1000']
        }
    
    except SQLAlchemyError as e:
        logging.error(f"Error en SQLAlchemy al obtener el precio con descuento: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        logging.error(f"Error general al obtener el precio con descuento: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    


    
    
    
@router.post("/send_email", tags=["Email"])
def send_email(request: EmailRequest):
    # Usar la variable de entorno para la contraseña del email
    email_user = 'mho.digital.contacto@gmail.com'
    email_password = os.getenv('EMAIL_APP_PASSWORD')  # Asegúrate de haber configurado esta variable de entorno
    email_cc = 'ventas@mho.digital'  # Dirección a la que enviar la copia
    email_bcc = 'mho.digital.contacto@gmail.com'  # Agregar el mismo correo como destinatario

    
    # Obtener la fecha y hora actual del envío
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Crear el contenido del mensaje
    message = MIMEMultipart()
    message['From'] = email_user
    message['To'] = request.email  # A quién se envía
    message['Cc'] = email_cc  # Dirección de copia
    message['Subject'] = f"¡Bienvenido/a a Nuestra Librería Mayorista MHO-Digital!"

    main_body = (f"Estimado/a {request.name},\n\n"
            "¡Muchas gracias por registrarte en la Librería Mayorista! Estamos encantados de darte la bienvenida a nuestra comunidad de amantes de los libros.\n\n"
            
            "En la Librería Mayorista de MHO, nos especializamos en ofrecer una amplia selección de libros de alta calidad a precios competitivos. "
            "Como parte de nuestra comunidad, disfrutarás de acceso exclusivo a promociones y descuentos especiales, además de ser el primero en enterarse de nuestras colecciones y novedades más recientes.\n\n"
            
            "Ventajas de ser parte de nuestra comunidad:\n"
            "- Ofertas exclusivas para clientes registrados.\n"
            "- Atención personalizada y recomendaciones basadas en tus intereses.\n"
            "- Acceso anticipado a nuevos lanzamientos y eventos literarios.\n\n"
            
            "Por favor, no dudes en contactarnos si tienes alguna pregunta o necesitas asistencia.\n\n"
            "Gracias nuevamente por elegirnos. Esperamos construir memorias maravillosas a través de nuestras lecturas.\n\n"
            
            "Cordialmente,\n"
            "El Equipo de Librería Mayorista MHO DIGITAL EIRL\n"
            "Correo de contacto: ventas@mho.digital\n"
            "Whatsapp: (+51) 906 681 820\n"
            "Lima - Perú\n"
            "Siguenos en la web: https://libreria-mayorista.mho.digital")  # Continua con el cuerpo del mensaje
    
    # Añadir los detalles del cliente y la fecha y hora del envío al final del cuerpo del mensaje
   
   # Crear una separación visual usando líneas dobles
    separator = "\n" + "="*40 + "\n"
    
    client_details = (separator +
                      f"\nDetalles del cliente:\n"
                      f"Razón Social / Nombre Completo: {request.name}\n"
                      f"RUC / DNI / CE: {request.dni_ruc}\n"
                      f"Email: {request.email}\n"
                      f"Mensaje: {request.message}\n"
                      f"Fecha y hora de envío: {now}\n")

    complete_body = main_body + client_details

    message.attach(MIMEText(complete_body, 'plain'))

    try:
        # Conectar al servidor Gmail y enviar el correo
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email_user, email_password)
        
        # Los destinatarios incluyen el email To y Cc
        recipients = [request.email] + [email_cc] + [email_bcc]
        server.sendmail(email_user, recipients, message.as_string())
        server.quit()
        
        logging.info(f"Correo enviado con éxito a {request.email} y en copia a {email_cc}")
        return {"status": "Correo enviado con éxito"}
    except Exception as e:
        logging.error(f"Error al enviar correo: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al enviar el correo")