# Importar modelos para que Flask-SQLAlchemy los registre
from .cliente import Cliente
from .presupuesto import Presupuesto

__all__ = ['Cliente', 'Presupuesto']
