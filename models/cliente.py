from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship


class Cliente:
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    celular = Column(String(20), nullable=False)
    direccion = Column(String(200), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    # Relación con presupuestos
    presupuestos = relationship("Presupuesto", back_populates="cliente")
    
    def __repr__(self):
        return f"<Cliente {self.nombre} {self.apellido}>"
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
