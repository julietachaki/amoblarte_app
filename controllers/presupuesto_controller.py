from controllers.tarjetas_controller import obtener_configuracion
from database import SessionLocal
from models.clientes import Cliente
from models.presupuesto import Presupuesto


def agregar_presupuesto(cliente_id, descripcion, precio_lista):
    session = SessionLocal()
    try:
        # Configuración de descuentos y cuotas
        config = obtener_configuracion()
        descuento = config.descuento_contado or 0
        precio_contado = precio_lista * (1 - descuento/100)

        presupuesto = Presupuesto(
            cliente_id=cliente_id,
            descripcion=descripcion,
            precio_lista=precio_lista,
            precio_contado=precio_contado
        )
        session.add(presupuesto)
        session.commit()
        session.refresh(presupuesto)
        return presupuesto
    finally:
        session.close()

def obtener_presupuesto(id_presupuesto):
    session = SessionLocal()
    try:
        return session.query(Presupuesto).filter(Presupuesto.id == id_presupuesto).first()
    finally:
        session.close()

def buscar_presupuestos_por_cliente(nombre_cliente):
    session = SessionLocal()
    try:
        return (
            session.query(Presupuesto)
            .join(Cliente)
            .filter(Cliente.nombre.ilike(f"%{nombre_cliente}%"))
            .all()
        )
    finally:
        session.close()

def modificar_presupuesto(id_presupuesto, descripcion=None, precio_lista=None):
    session = SessionLocal()
    try:
        presupuesto = session.query(Presupuesto).filter(Presupuesto.id == id_presupuesto).first()
        if not presupuesto:
            return None

        config = obtener_configuracion()

        if descripcion:
            presupuesto.descripcion = descripcion
        if precio_lista:
            presupuesto.precio_lista = precio_lista
            presupuesto.precio_contado = precio_lista * (1 - (config.descuento_contado or 0) / 100)

        session.commit()
        session.refresh(presupuesto)
        return presupuesto
    finally:
        session.close()

def eliminar_presupuesto(id_presupuesto):
    session = SessionLocal()
    try:
        presupuesto = session.query(Presupuesto).filter(Presupuesto.id == id_presupuesto).first()
        if presupuesto:
            session.delete(presupuesto)
            session.commit()
            return True
        return False
    finally:
        session.close()
