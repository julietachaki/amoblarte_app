from datetime import datetime

from extensions import db


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    celular = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    presupuestos = db.relationship("Presupuesto", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente {self.nombre} {self.apellido}>"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
