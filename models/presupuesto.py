from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        func)
from sqlalchemy.orm import relationship

from database import Base


class Presupuesto(Base):
    __tablename__ = "presupuestos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    descripcion = Column(String, nullable=False)
    precio_lista = Column(Float, nullable=False)
    precio_contado = Column(Float, nullable=False)
    fecha = Column(DateTime, default=func.now())

    cliente = relationship("Cliente", back_populates="presupuestos")

Cliente.presupuestos = relationship("Presupuesto", order_by=Presupuesto.id, back_populates="cliente")
