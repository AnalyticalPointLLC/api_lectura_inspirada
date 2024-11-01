from pydantic import BaseModel
from typing import Optional
from datetime import date

class BmgBook(BaseModel):
    id: Optional[int]
    pvp: Optional[str]
    moneda: Optional[str]
    formato: Optional[str]
    tipo_notificacion: Optional[str]
    canal_venta: Optional[str]
    isbn13: str
    alto: Optional[str]
    ancho: Optional[str]
    peso: Optional[str]
    titulo: str
    edicion: Optional[str]
    idioma_edicion: Optional[str]
    paginas: Optional[str]
    resumen: Optional[str]
    imagen_tapa: Optional[str]
    editor: Optional[str]
    pais_edicion: Optional[str]
    fecha_publicacion: Optional[date]
    codigo_bmg: Optional[str]
    autor: Optional[str]
    coleccion: Optional[str]
    sello: Optional[str]
    clasificacion: Optional[str]
    promocion: Optional[str]
    upload: Optional[date]
    nombre_clasificacion: Optional[str]

    class Config:
        from_attributes = True  # Actualizado para Pydantic V2

class ClasificacionIBIC(BaseModel):
    codigo_ibic: str
    nombre_clasificacion: str
    max_length: Optional[int] = None

    class Config:
        from_attributes = True  # Actualizado para Pydantic V2
        

class EmailRequest(BaseModel):
    dni_ruc: str
    name: str
    email: str
    message: str