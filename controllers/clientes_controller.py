from database import SessionLocal
from models.clientes import Cliente


def agregar_cliente(nombre, telefono, email):
    session = SessionLocal()
    try:
        cliente = Cliente(nombre=nombre, telefono=telefono, email=email)
        session.add(cliente)
        session.commit()
        session.refresh(cliente)
        return cliente
    finally:
        session.close()

def obtener_cliente(id_cliente):
    session = SessionLocal()
    try:
        return session.query(Cliente).filter(Cliente.id == id_cliente).first()
    finally:
        session.close()

def buscar_cliente_por_nombre(nombre):
    session = SessionLocal()
    try:
        return session.query(Cliente).filter(Cliente.nombre.ilike(f"%{nombre}%")).all()
    finally:
        session.close()

def modificar_cliente(id_cliente, nombre=None, telefono=None, email=None):
    session = SessionLocal()
    try:
        cliente = session.query(Cliente).filter(Cliente.id == id_cliente).first()
        if not cliente:
            return None
        if nombre: cliente.nombre = nombre
        if telefono: cliente.telefono = telefono
        if email: cliente.email = email
        session.commit()
        session.refresh(cliente)
        return cliente
    finally:
        session.close()

def eliminar_cliente(id_cliente):
    session = SessionLocal()
    try:
        cliente = session.query(Cliente).filter(Cliente.id == id_cliente).first()
        if cliente:
            session.delete(cliente)
            session.commit()
            return True
        return False
    finally:
        session.close()