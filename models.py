from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURACIÓN POSTGRESQL ---
# Por defecto se usa sqlite si no hay DATABASE_URL en el entorno (útil para desarrollo local si no hay PostgreSQL)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eventmaster.db")

# Adaptación para Aiven PostgreSQL si la URL empieza por postgres://
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Los connect_args son necesarios para SQLite, pero pueden dar error en PostgreSQL
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELOS DE BASE DE DATOS (SQLAlchemy) ---
class Recinto(Base):
    __tablename__ = "recintos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    capacidad = Column(Integer, nullable=False)
    
    eventos = relationship("Evento", back_populates="recinto", cascade="all, delete-orphan")

class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    fecha = Column(DateTime, nullable=False)
    precio = Column(Float, nullable=False)
    tickets_vendidos = Column(Integer, default=0, nullable=False)
    recinto_id = Column(Integer, ForeignKey("recintos.id"), nullable=False)

    recinto = relationship("Recinto", back_populates="eventos")

# --- ESQUEMAS PARA LA API (Pydantic) ---
class RecintoBase(BaseModel):
    nombre: str
    ciudad: str
    capacidad: int

class RecintoCreate(RecintoBase):
    pass

class RecintoUpdate(RecintoBase):
    pass

class RecintoResponse(RecintoBase):
    id: int
    class Config:
        from_attributes = True

class EventoBase(BaseModel):
    nombre: str
    fecha: datetime
    precio: float
    recinto_id: int

class EventoCreate(EventoBase):
    @field_validator('precio')
    @classmethod
    def validate_precio(cls, v):
        if v < 0:
            raise ValueError('El precio no puede ser negativo')
        return v

class EventoResponse(EventoBase):
    id: int
    tickets_vendidos: int
    class Config:
        from_attributes = True

class CompraTickets(BaseModel):
    cantidad: int
    @field_validator('cantidad')
    @classmethod
    def validate_cantidad(cls, v):
        if v <= 0:
            raise ValueError('La cantidad de tickets a comprar debe ser mayor que 0')
        return v