from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import models
from models import SessionLocal, engine
from typing import List, Optional

# Crear las tablas al iniciar si se usa SQLite (en una DB PostgreSQL como Aiven normalmente deberíamos usar migraciones como Alembic)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="EventMaster API", description="API para gestión de eventos y recintos")

# Dependencia para obtener la DB en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_index():
    return {"message": "Bienvenido a la API de EventMaster", "documentacion": "/docs"}

# --- ENDPOINTS RECINTOS ---
@app.post("/recintos/", response_model=models.RecintoResponse)
def crear_recinto(recinto: models.RecintoCreate, db: Session = Depends(get_db)):
    db_recinto = models.Recinto(**recinto.model_dump())
    db.add(db_recinto)
    db.commit()
    db.refresh(db_recinto)
    return db_recinto

@app.get("/recintos/", response_model=List[models.RecintoResponse])
def leer_recintos(db: Session = Depends(get_db)):
    return db.query(models.Recinto).all()

@app.put("/recintos/{recinto_id}", response_model=models.RecintoResponse)
def actualizar_recinto(recinto_id: int, recinto_update: models.RecintoUpdate, db: Session = Depends(get_db)):
    db_recinto = db.query(models.Recinto).filter(models.Recinto.id == recinto_id).first()
    if not db_recinto:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")
    
    for key, value in recinto_update.model_dump().items():
        setattr(db_recinto, key, value)
        
    db.commit()
    db.refresh(db_recinto)
    return db_recinto

@app.delete("/recintos/{recinto_id}")
def eliminar_recinto(recinto_id: int, db: Session = Depends(get_db)):
    db_recinto = db.query(models.Recinto).filter(models.Recinto.id == recinto_id).first()
    if not db_recinto:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")
    
    db.delete(db_recinto)
    db.commit()
    return {"detail": "Recinto eliminado satisfactoriamente"}


# --- ENDPOINTS EVENTOS ---
@app.post("/eventos/", response_model=models.EventoResponse)
def crear_evento(evento: models.EventoCreate, db: Session = Depends(get_db)):
    # Validar precio >= 0 (ya lo hace Pydantic, pero podemos asegurarnos aquí si preferimos)
    # Comprobar si el recinto existe
    db_recinto = db.query(models.Recinto).filter(models.Recinto.id == evento.recinto_id).first()
    if not db_recinto:
         raise HTTPException(status_code=404, detail="El recinto asociado no existe")

    db_evento = models.Evento(**evento.model_dump())
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@app.get("/eventos/", response_model=List[models.EventoResponse])
def leer_eventos(ciudad: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Evento)
    if ciudad:
        query = query.join(models.Recinto).filter(models.Recinto.ciudad.ilike(f"%{ciudad}%"))
    return query.all()

@app.patch("/eventos/{evento_id}/comprar", response_model=models.EventoResponse)
def comprar_tickets(evento_id: int, compra: models.CompraTickets, db: Session = Depends(get_db)):
    db_evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    db_recinto = db_evento.recinto
    
    if db_evento.tickets_vendidos + compra.cantidad > db_recinto.capacidad:
        raise HTTPException(status_code=400, detail="Aforo insuficiente en el recinto")
    
    db_evento.tickets_vendidos += compra.cantidad
    db.commit()
    db.refresh(db_evento)
    return db_evento
