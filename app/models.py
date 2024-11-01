from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship, backref


Base = declarative_base()

class BmgBook(Base):
    __tablename__ = "bmg_books"
    id = Column(Integer, primary_key=True, index=True)
    pvp = Column(Text)
    moneda = Column(Text)
    formato = Column(Text)
    tipo_notificacion = Column(Text)
    canal_venta = Column(Text)
    isbn13 = Column(Text, unique=True, nullable=False)
    alto = Column(Text)
    ancho = Column(Text)
    peso = Column(Text)
    titulo = Column(Text, nullable=False)
    edicion = Column(Text)
    idioma_edicion = Column(Text, ForeignKey("idioma_iso639.abrev_639_2"))
    paginas = Column(Text)
    resumen = Column(Text)
    imagen_tapa = Column(Text)
    editor = Column(Text)
    pais_edicion = Column(Text)
    fecha_publicacion = Column(Date)
    codigo_bmg = Column(Text)
    autor = Column(Text)
    coleccion = Column(Text)
    sello = Column(Text)
    clasificacion = Column(Text)
    promocion = Column(Text)
    upload = Column(Date)
    
    # Relación con la tabla de idiomas
    idioma = relationship(
        "IdiomaIso639",
        back_populates="books",
        primaryjoin="BmgBook.idioma_edicion == IdiomaIso639.abrev_639_2"
    )


class ClasificacionIBIC(Base):
    __tablename__ = "clasificaciones_ibic"
    id = Column(Integer, primary_key=True, index=True)
    codigo_ibic = Column(String(50), unique=True)
    nombre_clasificacion = Column(String(255))
    
class IdiomaIso639(Base):
    __tablename__ = "idioma_iso639"
    id = Column(Integer, primary_key=True, index=True)
    family = Column(Text)
    name = Column(Text)
    native_name = Column(Text)
    abrev_639_2 = Column(Text)
    abrev_639_3 = Column(Text)
    abrev_639_b = Column(Text)
    spanish = Column(Text)

    # Relación con la tabla de libros
    books = relationship("BmgBook", back_populates="idioma")
