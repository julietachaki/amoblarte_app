from datetime import datetime

from database import Base
from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship


class Presupuesto(Base):
    __tablename__ = "presupuestos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_presupuesto = Column(String(50), unique=True, nullable=False)
    descripcion = Column(Text)
    imagen = Column(String(255))  # Ruta de la imagen
    precio_materiales = Column(Float, default=0.0)
    precio_mano_obra = Column(Float, default=0.0)
    precio_tarjeta = Column(Float, default=0.0)
    incluye_tarjeta = Column(String(10), default="No")  # "Sí" o "No"
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_modificacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Clave foránea
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    
    # Relación con cliente
    cliente = relationship("Cliente", back_populates="presupuestos")
    
    def __repr__(self):
        return f"<Presupuesto {self.numero_presupuesto}>"
    
    @property
    def total_sin_tarjeta(self):
        return self.precio_materiales + self.precio_mano_obra
    
    @property
    def total_con_tarjeta(self):
        return self.total_sin_tarjeta + self.precio_tarjeta
    
    @property
    def total_final(self):
        if self.incluye_tarjeta == "Sí":
            return self.total_con_tarjeta
        return self.total_sin_tarjeta