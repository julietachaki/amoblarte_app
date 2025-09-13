from sqlalchemy import Column, Integer, String

from database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    email = Column(String, nullable=True)

    def __repr__(self):
        return f"<Cliente(nombre={self.nombre}, telefono={self.telefono})>"
