from database import Base, SessionLocal, engine
from models import cliente, configuracion, presupuesto
from views.main_view import start_app

if __name__ == "__main__":
    # Crea las tablas si no existen
    Base.metadata.create_all(bind=engine)
    start_app()
