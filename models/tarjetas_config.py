from sqlalchemy import Column, Float, Integer

from database import Base


class TarjetasConfiguracion(Base):
    __tablename__ = "configuracion"

    id = Column(Integer, primary_key=True, default=1)
    descuento_contado = Column(Float, default=0)
    cuotas = Column(Integer, default=1)
    interes = Column(Float, default=0)
