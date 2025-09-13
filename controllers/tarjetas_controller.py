from database import SessionLocal
from models.tarjetas_config import Configuracion


def obtener_configuracion():
    session = SessionLocal()
    try:
        config = session.query(Configuracion).filter(Configuracion.id == 1).first()
        if not config:
            config = Configuracion(id=1, descuento_contado=0, cuotas=1, interes=0)
            session.add(config)
            session.commit()
            session.refresh(config)
        return config
    finally:
        session.close()

def guardar_configuracion(descuento_contado, cuotas, interes):
    session = SessionLocal()
    try:
        config = session.query(Configuracion).filter(Configuracion.id == 1).first()
        if not config:
            config = Configuracion(id=1)
            session.add(config)
        config.descuento_contado = descuento_contado
        config.cuotas = cuotas
        config.interes = interes
        session.commit()
        session.refresh(config)
        return config
    finally:
        session.close()
