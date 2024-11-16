from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects import postgresql
from . import models, schemas
import logging

from typing import List

def log_query(query):
    try:
        logging.debug(query.statement.compile(dialect=postgresql.dialect()))
    except SQLAlchemyError as e:
        logging.error(f"Error en log_query: {str(e)}")

def get_bmg_books(db: Session, limit: int = 250, offset: int = 0):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).filter(
            models.BmgBook.promocion == 'semanal'
        ).order_by(
            models.BmgBook.upload.desc()
        ).limit(limit).offset(offset)
        
        log_query(query)
        result = query.all()
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_bmg_books: {str(e)}")
        return []

def get_nuevos_titulos_diarios(db: Session, limit: int = 250, offset: int = 0):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).filter(models.BmgBook.promocion == 'diaria').order_by(models.BmgBook.upload.desc()).limit(limit).offset(offset)
        
        log_query(query)
        result = query.all()
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_nuevos_titulos_diarios: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_nuevos_titulos_diarios: {str(e)}")
        return []

def get_book_by_id(db: Session, book_id: int):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).filter(models.BmgBook.id == book_id)
        log_query(query)
        result = query.one_or_none()
        if result:
            book_dict = result[0].__dict__
            book_dict['nombre_clasificacion'] = result[1]
            return book_dict
        else:
            return None
    except SQLAlchemyError as e:
        logging.error(f"Error en get_book_by_id: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado en get_book_by_id: {str(e)}")
        return None

def search_books(db: Session, search_params: dict):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        )
        
        # Añadir condiciones dinámicamente basado en los parámetros
        if 'titulo' in search_params:
            query = query.filter(models.BmgBook.titulo.ilike(f"%{search_params['titulo']}%"))
        if 'isbn13' in search_params:
            query = query.filter(models.BmgBook.isbn13.ilike(f"%{search_params['isbn13']}%"))
        if 'resumen' in search_params:
            query = query.filter(models.BmgBook.resumen.ilike(f"%{search_params['resumen']}%"))
        if 'pais_edicion' in search_params:
            query = query.filter(models.BmgBook.pais_edicion.ilike(f"%{search_params['pais_edicion']}%"))
        if 'editor' in search_params:
            query = query.filter(models.BmgBook.editor.ilike(f"%{search_params['editor']}%"))
        if 'fecha_publicacion' in search_params:
            query = query.filter(models.BmgBook.fecha_publicacion.like(f"{search_params['fecha_publicacion']}%"))
        if 'autor' in search_params:
            query = query.filter(models.BmgBook.autor.ilike(f"%{search_params['autor']}%"))
        if 'nombre_clasificacion' in search_params:
            query = query.filter(models.ClasificacionIBIC.nombre_clasificacion.ilike(f"%{search_params['nombre_clasificacion']}%"))
        if 'sello' in search_params:
            query = query.filter(models.BmgBook.sello.ilike(f"%{search_params['sello']}%"))
        if 'clasificacion' in search_params:
            query = query.filter(models.BmgBook.clasificacion.ilike(f"%{search_params['clasificacion']}%"))

        log_query(query)
        result = query.all()
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en search_books: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en search_books: {str(e)}")
        return []

def get_nombre_clasificacion(db: Session):
    try:
        nombres_clasificacion = db.query(models.ClasificacionIBIC.nombre_clasificacion).distinct().order_by(models.ClasificacionIBIC.nombre_clasificacion).all()
        return [nombre[0] for nombre in nombres_clasificacion if nombre[0] is not None]
    except SQLAlchemyError as e:
        logging.error(f"Error en get_nombre_clasificacion: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_nombre_clasificacion: {str(e)}")
        return []

def get_pais_edicion(db: Session):
    try:
        paises_edicion = db.query(models.BmgBook.pais_edicion).distinct().order_by(models.BmgBook.pais_edicion).all()
        return [pais[0] for pais in paises_edicion if pais[0] is not None]
    except SQLAlchemyError as e:
        logging.error(f"Error en get_pais_edicion: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_pais_edicion: {str(e)}")
        return []

def get_autor(db: Session):
    try:
        autores = db.query(models.BmgBook.autor).distinct().order_by(models.BmgBook.autor).all()
        return [autor[0] for autor in autores if autor[0] is not None]
    except SQLAlchemyError as e:
        logging.error(f"Error en get_autor: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_autor: {str(e)}")
        return []

def get_titulo(db: Session):
    try:
        titulos = db.query(models.BmgBook.titulo).distinct().order_by(models.BmgBook.titulo).all()
        return [titulo[0] for titulo in titulos if titulo[0] is not None]
    except SQLAlchemyError as e:
        logging.error(f"Error en get_titulo: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_titulo: {str(e)}")
        return []

def get_sello(db: Session):
    try:
        sellos = db.query(models.BmgBook.sello).distinct().order_by(models.BmgBook.sello).all()
        return [sello[0] for sello in sellos if sello[0] is not None]
    except SQLAlchemyError as e:
        logging.error(f"Error en get_sello: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_sello: {str(e)}")
        return []

def get_authors_by_initial(db: Session, initial: str):
    try:
        autores = db.query(models.BmgBook.autor).filter(models.BmgBook.autor.ilike(f"{initial}%")).distinct().order_by(models.BmgBook.autor).all()
        return [autor[0] for autor in autores if autor[0] is not None]
    except SQLAlchemyError as e:
        logging.error(f"Error en get_authors_by_initial: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_authors_by_initial: {str(e)}")
        return []

def search_authors(db: Session, keyword: str):
    try:
        autores = db.query(models.BmgBook.autor).filter(models.BmgBook.autor.ilike(f"%{keyword}%")).distinct().order_by(models.BmgBook.autor).all()
        return [autor[0] for autor in autores if autor[0] is not None]
    except SQLAlchemyError as e:
        logging.error(f"Error en search_authors: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en search_authors: {str(e)}")
        return []

def get_books_by_author(db: Session, author: str):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).filter(models.BmgBook.autor.ilike(f"%{author}%"))
        
        log_query(query)
        result = query.all()
        
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_books_by_author: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_books_by_author: {str(e)}")
        return []

def get_primary_classifications(db: Session):
    try:
        primary_classifications = db.query(
            models.ClasificacionIBIC.codigo_ibic,
            models.ClasificacionIBIC.nombre_clasificacion
        ).filter(
            func.length(models.ClasificacionIBIC.codigo_ibic) == 1
        ).order_by(models.ClasificacionIBIC.codigo_ibic).distinct().all()
        
        # Agregar consulta para obtener la cantidad máxima de subclasificaciones
        max_subclass_lengths = db.query(
            func.substr(models.ClasificacionIBIC.codigo_ibic, 1, 1).label('primary_code'),
            func.max(func.length(models.ClasificacionIBIC.codigo_ibic)).label('max_length')
        ).group_by(
            func.substr(models.ClasificacionIBIC.codigo_ibic, 1, 1)
        ).all()
        
        max_length_dict = {item.primary_code: item.max_length for item in max_subclass_lengths}

        result = [
            {
                'codigo_ibic': classification[0],
                'nombre_clasificacion': classification[1],
                'max_length': max_length_dict.get(classification[0], 1)
            }
            for classification in primary_classifications if classification[0] is not None
        ]
        logging.debug(f"Result from primary classifications query: {result}")
        return result
    except SQLAlchemyError as e:
        logging.error(f"Error en get_primary_classifications: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_primary_classifications: {str(e)}")
        return []

def get_subclassifications(db: Session, primary_code: str):
    try:
        logging.debug(f"Obteniendo subclasificaciones para el código principal: {primary_code}")
        query = db.query(
            models.ClasificacionIBIC.codigo_ibic,
            models.ClasificacionIBIC.nombre_clasificacion
        ).filter(
            models.ClasificacionIBIC.codigo_ibic.like(f'{primary_code}%'),
            func.length(models.ClasificacionIBIC.codigo_ibic) > 1
        ).order_by(models.ClasificacionIBIC.codigo_ibic).distinct()
        
        log_query(query)
        result = query.all()
        
        subclassifications = [
            {
                'codigo_ibic': sub.codigo_ibic,
                'nombre_clasificacion': sub.nombre_clasificacion
            } for sub in result if sub.nombre_clasificacion is not None  # Filtrar entradas donde `nombre_clasificacion` es None
        ]
        
        logging.debug(f"Subclassifications result: {subclassifications}")
        return subclassifications
    except SQLAlchemyError as e:
        logging.error(f"Error en get_subclassifications: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_subclassifications: {str(e)}")
        return []

def get_subclassifications_by_name(db: Session, nombre_clasificacion: str):
    try:
        query = db.query(
            models.ClasificacionIBIC.codigo_ibic,
            models.ClasificacionIBIC.nombre_clasificacion
        ).filter(
            models.ClasificacionIBIC.nombre_clasificacion.ilike(f'%{nombre_clasificacion}%'),
            func.length(models.ClasificacionIBIC.codigo_ibic) > 1
        ).order_by(models.ClasificacionIBIC.codigo_ibic).distinct()
        
        log_query(query)
        result = query.all()
        
        subclassifications = [
            {
                'codigo_ibic': sub[0],
                'nombre_clasificacion': sub[1]
            } for sub in result if sub[1] is not None  # Filtrar entradas donde `nombre_clasificacion` es None
        ]
        
        logging.debug(f"Subclassifications by name result: {subclassifications}")
        return subclassifications
    except SQLAlchemyError as e:
        logging.error(f"Error en get_subclassifications_by_name: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_subclassifications_by_name: {str(e)}")
        return []

def get_books_by_classification_name(db: Session, nombre_clasificacion: str):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).filter(
            models.ClasificacionIBIC.nombre_clasificacion.ilike(f"%{nombre_clasificacion}%")
        )
        
        log_query(query)
        result = query.all()
        
        books = [
            {**r[0].__dict__, 'nombre_clasificacion': r[1]}
            for r in result
        ]
        
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_books_by_classification_name: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_books_by_classification_name: {str(e)}")
        return []

def get_books_by_classification(db: Session, classification: str):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).filter(models.BmgBook.clasificacion.ilike(f"%{classification}%"))
        
        log_query(query)
        result = query.all()
        
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_books_by_classification: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_books_by_classification: {str(e)}")
        return []

def get_nuevos_titulos_semanal(db: Session, limit: int = 250, offset: int = 0):
    try:
        query = db.query(models.NuevosTitulosSemanal).limit(limit).offset(offset)
        log_query(query)
        return query.all()
    except SQLAlchemyError as e:
        logging.error(f"Error en get_nuevos_titulos_semanal: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_nuevos_titulos_semanal: {str(e)}")
        return []
    
    
def get_nuevos_titulos_diarios_filtrado(db: Session, idiomas: List[str], limit: int = 100, offset: int = 0):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).filter(
            models.BmgBook.promocion == 'diaria'
        )
        
        if idiomas:
            query = query.filter(models.BmgBook.idioma_edicion.in_(idiomas))
        
        query = query.order_by(models.BmgBook.upload.desc()).limit(limit).offset(offset)
        
        log_query(query)
        result = query.all()
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_nuevos_titulos_diarios_filtrado: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_nuevos_titulos_diarios_filtrado: {str(e)}")
        return []
    
    
## BUSQUEDA DE LIBROS IDIOMA GENERAL    
def get_books_by_language(db: Session, idioma: str, limit: int = 100, offset: int = 0):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).join(
            models.IdiomaIso639,
            models.BmgBook.idioma_edicion == models.IdiomaIso639.abrev_639_2
        ).filter(
            models.IdiomaIso639.spanish.ilike(idioma)
        ).order_by(
            models.BmgBook.upload.desc()
        ).limit(limit).offset(offset)
        
        log_query(query)  # Llamada a log_query para registrar y mostrar la consulta
        result = query.all()
        
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_books_by_language: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_books_by_language: {str(e)}")
        return []
    
    

    
## BUSQUEDA DE LIBROS EN PROMOCION DIARIA
def get_daily_promotion_books(db: Session, idioma: str, limit: int = 100, offset: int = 0):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).join(
            models.IdiomaIso639,
            models.BmgBook.idioma_edicion == models.IdiomaIso639.abrev_639_2
        ).filter(
            models.BmgBook.promocion == 'diaria',
            models.IdiomaIso639.spanish.ilike(idioma)
        ).order_by(
            models.BmgBook.upload.desc()
        ).limit(limit).offset(offset)
        
        log_query(query)  # Llamada a log_query para registrar y mostrar la consulta
        result = query.all()
        
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_daily_promotion_books: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_daily_promotion_books: {str(e)}")
        return []
    
    
## BUSQUEDA DE LIBROS POR IDIOMA Y CLASIFICACION
def get_books_by_language_and_classification(db: Session, idioma: str, nombre_clasificacion: str, limit: int = 100, offset: int = 0):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).join(
            models.IdiomaIso639,
            models.BmgBook.idioma_edicion == models.IdiomaIso639.abrev_639_2
        ).filter(
            models.IdiomaIso639.spanish.ilike(idioma),
            models.ClasificacionIBIC.nombre_clasificacion.ilike(nombre_clasificacion)
        ).order_by(
            models.BmgBook.upload.desc()
        ).limit(limit).offset(offset)
        
        log_query(query)  # Llamada a log_query para registrar y mostrar la consulta
        result = query.all()
        
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_books_by_language_and_classification: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_books_by_language_and_classification: {str(e)}")
        return []
    
    
## BUSQUEDA DE LIBROS POR IDIOMA Y TITULO
def get_books_by_language_and_title(db: Session, idioma: str, titulo: str, limit: int = 100, offset: int = 0):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).join(
            models.IdiomaIso639,
            models.BmgBook.idioma_edicion == models.IdiomaIso639.abrev_639_2
        ).filter(
            models.IdiomaIso639.spanish.ilike(idioma),
            models.BmgBook.titulo.ilike(f"%{titulo}%")
        ).order_by(
            models.BmgBook.upload.desc()
        ).limit(limit).offset(offset)
        
        log_query(query)  # Llamada a log_query para registrar y mostrar la consulta
        result = query.all()
        
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_books_by_language_and_title: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_books_by_language_and_title: {str(e)}")
        return []
    
    
## CONTAR LIBROS POR IDIOMA Y CLASIFICACION
def count_books_by_language_and_classification(db: Session, idioma: str, clasificacion: str):
    try:
        query = db.query(
            func.count(models.BmgBook.id)
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).join(
            models.IdiomaIso639,
            models.BmgBook.idioma_edicion == models.IdiomaIso639.abrev_639_2
        ).filter(
            models.IdiomaIso639.spanish.ilike(f"%{idioma}%"),
            models.ClasificacionIBIC.nombre_clasificacion.ilike(f"%{clasificacion}%")
        )

        log_query(query)  # Llamada a log_query para registrar y mostrar la consulta
        count = query.scalar()
        
        logging.debug(f"Conteo de libros para idioma '{idioma}' y clasificación '{clasificacion}': {count}")
        
        return count
    except SQLAlchemyError as e:
        logging.error(f"Error en count_books_by_language_and_classification: {str(e)}")
        return 0
    except Exception as e:
        logging.error(f"Error inesperado en count_books_by_language_and_classification: {str(e)}")
        return 0


## CONTAR LIBROS POR CLASIFICACION
def count_books_by_classification(db: Session, clasificacion: str):
    try:
        query = db.query(
            func.count(models.BmgBook.id)
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).filter(
            models.ClasificacionIBIC.nombre_clasificacion.ilike(f"%{clasificacion}%")
        )
        
        log_query(query)  # Llamada a log_query para registrar y mostrar la consulta
        count = query.scalar()
        
        logging.debug(f"Conteo de libros para clasificación '{clasificacion}': {count}")
        
        return count
    except SQLAlchemyError as e:
        logging.error(f"Error en count_books_by_classification: {str(e)}")
        return 0
    except Exception as e:
        logging.error(f"Error inesperado en count_books_by_classification: {str(e)}")
        return 0
    
## CONTAR LIBROS POR CLASIFICACION, NOMBRE_CLASIFICACION Y CODIGO_IBIC

# Lista de códigos IBIC y nombres de clasificación
IBIC_CODES = [
    { "codigo_ibic": "A", "nombre_clasificacion": "Las artes" },
    { "codigo_ibic": "B", "nombre_clasificacion": "Biografía e historias reales" },
    { "codigo_ibic": "C", "nombre_clasificacion": "Lenguaje" },
    { "codigo_ibic": "D", "nombre_clasificacion": "Literatura y estudios literarios" },
    { "codigo_ibic": "E", "nombre_clasificacion": "Enseñanza de la lengua inglesa" },
    { "codigo_ibic": "F", "nombre_clasificacion": "Ficción y temas afines" },
    { "codigo_ibic": "G", "nombre_clasificacion": "Consulta, información y temas interdisciplinarios" },
    { "codigo_ibic": "H", "nombre_clasificacion": "Humanidades" },
    { "codigo_ibic": "J", "nombre_clasificacion": "Sociedad y ciencias sociales" },
    { "codigo_ibic": "K", "nombre_clasificacion": "Economía, finanzas, empresa y gestión" },
    { "codigo_ibic": "L", "nombre_clasificacion": "Derecho" },
    { "codigo_ibic": "M", "nombre_clasificacion": "Medicina" },
    { "codigo_ibic": "P", "nombre_clasificacion": "Matemáticas y ciencia" },
    { "codigo_ibic": "R", "nombre_clasificacion": "Ciencias de la tierra, geografía, medioambiente, planificación" },
    { "codigo_ibic": "T", "nombre_clasificacion": "Tecnología, ingeniería, agricultura" },
    { "codigo_ibic": "U", "nombre_clasificacion": "Computación e informática" },
    { "codigo_ibic": "V", "nombre_clasificacion": "Salud y desarrollo personal" },
    { "codigo_ibic": "W", "nombre_clasificacion": "Estilo de vida, deporte y ocio" },
    { "codigo_ibic": "Y", "nombre_clasificacion": "Infantiles, juveniles y didácticos" }
]

## CONTAR LIBROS CUYAS CLASIFICACIONES COMIENZAN CON LAS LETRAS DEL LISTADO IBIC
def count_books_by_classification_prefix(db: Session, prefix: str):
    try:
        query = db.query(
            func.count(models.BmgBook.id)
        ).filter(
            models.BmgBook.clasificacion.ilike(f"{prefix}%")
        )
        
        log_query(query)  # Llamada a log_query para registrar y mostrar la consulta
        count = query.scalar()
        
        logging.debug(f"Conteo de libros para clasificación que comienza con '{prefix}': {count}")
        
        return count
    except SQLAlchemyError as e:
        logging.error(f"Error en count_books_by_classification_prefix: {str(e)}")
        return 0
    except Exception as e:
        logging.error(f"Error inesperado en count_books_by_classification_prefix: {str(e)}")
        return 0

## LISTAR TODOS LOS CODIGOS IBIC Y SU CANTIDAD DE FILAS CONTANDO LAS CLASIFICACIONES QUE COMIENZAN CON ESAS LETRAS
def get_all_classification_counts_by_prefix(db: Session):
    try:
        classification_counts = []
        for ibic in IBIC_CODES:
            count = count_books_by_classification_prefix(db, ibic['codigo_ibic'])
            classification_counts.append({
                'codigo_ibic': ibic['codigo_ibic'],
                'nombre_clasificacion': ibic['nombre_clasificacion'],
                'count': count
            })
        
        return classification_counts
    except SQLAlchemyError as e:
        logging.error(f"Error en get_all_classification_counts_by_prefix: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_all_classification_counts_by_prefix: {str(e)}")
        return []
    

## LISTAR TODOS LOS CODIGOS IBIC Y SU CANTIDAD DE FILAS CONTANDO LAS CLASIFICACIONES FILTRANDO POR IDIOMA
def get_classification_counts_by_language(db: Session, idioma: str):
    try:
        classification_counts = []
        for ibic in IBIC_CODES:
            query = db.query(
                func.count(models.BmgBook.id)
            ).join(
                models.IdiomaIso639,
                models.BmgBook.idioma_edicion == models.IdiomaIso639.abrev_639_2
            ).filter(
                models.BmgBook.clasificacion.ilike(f"{ibic['codigo_ibic']}%"),
                models.IdiomaIso639.spanish.ilike(f"%{idioma}%")
            )
            
            log_query(query)  # Llamada a log_query para registrar y mostrar la consulta
            count = query.scalar()
            
            classification_counts.append({
                'codigo_ibic': ibic['codigo_ibic'],
                'nombre_clasificacion': ibic['nombre_clasificacion'],
                'count': count
            })
        
        return classification_counts
    except SQLAlchemyError as e:
        logging.error(f"Error en get_classification_counts_by_language: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_classification_counts_by_language: {str(e)}")
        return []
    
# Función para contar libros por idioma y clasificación
def count_books_by_language_and_classification(db: Session, idioma: str, clasificacion: str):
    try:
        query = db.query(
            func.count(models.BmgBook.id)
        ).join(
            models.IdiomaIso639,
            models.BmgBook.idioma_edicion == models.IdiomaIso639.abrev_639_2
        ).filter(
            models.BmgBook.clasificacion == clasificacion,
            models.IdiomaIso639.spanish.ilike(f"%{idioma}%")
        )
        
        log_query(query)  # Llamada a log_query para registrar y mostrar la consulta
        count = query.scalar()
        
        logging.debug(f"Conteo de libros para clasificación '{clasificacion}' y idioma '{idioma}': {count}")
        
        return count
    except SQLAlchemyError as e:
        logging.error(f"Error en count_books_by_language_and_classification: {str(e)}")
        return 0
    except Exception as e:
        logging.error(f"Error inesperado en count_books_by_language_and_classification: {str(e)}")
        return 0
    
## CODIGO PARA BUSCAR LIBROS CON IBIC Y CON IDIOMA

def get_books_by_classification_and_language(db: Session, classification: str, language: str, limit: int = 100, offset: int = 0):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).join(
            models.IdiomaIso639,
            models.BmgBook.idioma_edicion == models.IdiomaIso639.abrev_639_2
        ).filter(
            models.BmgBook.clasificacion.ilike(f"%{classification}%"),
            models.IdiomaIso639.spanish.ilike(f"%{language}%")
        ).limit(limit).offset(offset)
        
        log_query(query)
        result = query.all()
        
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_books_by_classification_and_language: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_books_by_classification_and_language: {str(e)}")
        return []





def get_books_by_classification_prefix_and_language(db: Session, prefix: str, language: str, limit: int = 100, offset: int = 0):
    try:
        query = db.query(
            models.BmgBook,
            models.ClasificacionIBIC.nombre_clasificacion
        ).join(
            models.ClasificacionIBIC,
            models.BmgBook.clasificacion == models.ClasificacionIBIC.codigo_ibic
        ).join(
            models.IdiomaIso639,
            models.BmgBook.idioma_edicion == models.IdiomaIso639.abrev_639_2
        ).filter(
            models.BmgBook.clasificacion.ilike(f"{prefix}%"),
            models.IdiomaIso639.spanish.ilike(f"%{language}%")
        ).order_by(
            models.BmgBook.upload.desc()
        ).limit(limit).offset(offset)
        
        log_query(query)  # Registrar la consulta
        result = query.all()
        
        books = []
        for r in result:
            book_dict = r[0].__dict__
            book_dict['nombre_clasificacion'] = r[1]
            books.append(book_dict)
        
        return books
    except SQLAlchemyError as e:
        logging.error(f"Error en get_books_by_classification_prefix_and_language: {str(e)}")
        return []
    except Exception as e:
        logging.error(f"Error inesperado en get_books_by_classification_prefix_and_language: {str(e)}")
        return []
    
    #Codigo para precio con descuento
def get_book_with_discounted_price(db: Session, book_id: int):
    try:
        query = db.query(models.BmgBook).filter(models.BmgBook.id == book_id)
        log_query(query)
        
        book = query.one_or_none()
        
        if not book:
            return None
        
        # Asegúrate de que el campo pvp sea convertible a número
        original_price = book.pvp
        if original_price is None:
            raise ValueError("El campo pvp está vacío o es nulo")
        
        try:
            original_price_numeric = float(original_price)
        except ValueError:
            raise ValueError("El campo pvp no es un número válido")
        
        # Calcular el precio con descuento 12%
        percent_discount = 12
        discounted_price = original_price_numeric * (1 - (percent_discount / 100))
        
        # Redondear el precio con descuento a dos decimales
        discounted_price = round(discounted_price, 2)
        
        #========================================================#
        
        # Calcular el precio con descuento x 100u 17%
        percent_discount_100 = 17
        discounted_price_100 = original_price_numeric * (1 - (percent_discount_100 / 100))
        
        # Redondear el precio con descuento a dos decimales
        discounted_price_100 = round(discounted_price_100, 2)
        
        #========================================================#
        
        # Calcular el precio con descuento x 1000u 22%
        percent_discount_1000 = 22
        discounted_price_1000 = original_price_numeric * (1 - (percent_discount_1000 / 100))
        
        # Redondear el precio con descuento a dos decimales
        discounted_price_1000 = round(discounted_price_1000, 2)
        
        
        #========================================================#
        
        # Calcular el precio con descuento x 9u 7%
        percent_discount_9 = 7
        discounted_price_9 = original_price_numeric * (1 - (percent_discount_9 / 100))
        
        # Redondear el precio con descuento a dos decimales
        discounted_price_9 = round(discounted_price_9, 2)
        
        
        
        #========================================================#
        
        
        
        # Devolver datos del libro junto con el precio con descuento
        book_dict = book.__dict__.copy()
        book_dict['discounted_price'] = discounted_price
        book_dict['percent_discount'] = percent_discount
        
        book_dict['discounted_price'] = discounted_price_9
        book_dict['percent_discount'] = percent_discount_9
        
        book_dict['discounted_price_100'] = discounted_price_100
        book_dict['percent_discount_100'] = percent_discount_100
        
        book_dict['discounted_price_1000'] = discounted_price_1000
        book_dict['percent_discount_1000'] = percent_discount_1000
        return book_dict

    except SQLAlchemyError as e:
        logging.error(f"Error en get_book_with_discounted_price: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado en get_book_with_discounted_price: {str(e)}")
        return None
    
    
    
def get_book_with_discounted_price_100_cien_unidades(db: Session, book_id: int):
    try:
        query = db.query(models.BmgBook).filter(models.BmgBook.id == book_id)
        log_query(query)
        
        book = query.one_or_none()
        
        if not book:
            return None
        
        # Asegúrate de que el campo pvp sea convertible a número
        original_price = book.pvp
        if original_price is None:
            raise ValueError("El campo pvp está vacío o es nulo")
        
        try:
            original_price_numeric = float(original_price)
        except ValueError:
            raise ValueError("El campo pvp no es un número válido")
        
        # Calcular el precio con descuento 17%
        percent_discount = 17
        discounted_price = original_price_numeric * (1 - (percent_discount / 100))
        
        # Redondear el precio con descuento a dos decimales
        discounted_price = round(discounted_price, 2)
        
        # Devolver datos del libro junto con el precio con descuento
        book_dict = book.__dict__.copy()
        book_dict['discounted_price'] = discounted_price
        book_dict['percent_discount'] = percent_discount
        return book_dict

    except SQLAlchemyError as e:
        logging.error(f"Error en get_book_with_discounted_price: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado en get_book_with_discounted_price: {str(e)}")
        return None
    
    
    
def get_book_with_discounted_price_1000_mil_unidades(db: Session, book_id: int):
    try:
        query = db.query(models.BmgBook).filter(models.BmgBook.id == book_id)
        log_query(query)
        
        book = query.one_or_none()
        
        if not book:
            return None
        
        # Asegúrate de que el campo pvp sea convertible a número
        original_price = book.pvp
        if original_price is None:
            raise ValueError("El campo pvp está vacío o es nulo")
        
        try:
            original_price_numeric = float(original_price)
        except ValueError:
            raise ValueError("El campo pvp no es un número válido")
        
        # Calcular el precio con descuento 22%
        percent_discount = 22
        discounted_price = original_price_numeric * (1 - (percent_discount / 100))
        
        # Redondear el precio con descuento a dos decimales
        discounted_price = round(discounted_price, 2)
        
        # Devolver datos del libro junto con el precio con descuento
        book_dict = book.__dict__.copy()
        book_dict['discounted_price'] = discounted_price
        book_dict['percent_discount'] = percent_discount
        return book_dict

    except SQLAlchemyError as e:
        logging.error(f"Error en get_book_with_discounted_price: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado en get_book_with_discounted_price: {str(e)}")
        return None