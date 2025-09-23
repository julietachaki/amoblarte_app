from datetime import datetime

from extensions import db


class Presupuesto(db.Model):
    __tablename__ = "presupuestos"

    id = db.Column(db.Integer, primary_key=True, index=True)
    numero_presupuesto = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    imagen = db.Column(db.String(255))
    precio_materiales = db.Column(db.Float, default=0.0)
    precio_mano_obra = db.Column(db.Float, default=0.0)
    precio_tarjeta = db.Column(db.Float, default=0.0)
    descuento_porcentaje = db.Column(db.Float, default=0.0)
    cuotas_3 = db.Column(db.Float, default=0.0)
    cuotas_6 = db.Column(db.Float, default=0.0)
    incluye_tarjeta = db.Column(db.String(10), default="No")  # "Sí" o "No"
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    cliente = db.relationship("Cliente", back_populates="presupuestos")

    def __repr__(self):
        return f"<Presupuesto {self.numero_presupuesto}>"

    @property
    def total_sin_tarjeta(self):
        return (self.precio_materiales or 0.0) + (self.precio_mano_obra or 0.0)

    @property
    def total_sin_tarjeta_con_descuento(self):
        subtotal = self.total_sin_tarjeta
        desc = (self.descuento_porcentaje or 0.0) / 100.0
        if desc <= 0:
            return subtotal
        return max(0.0, subtotal * (1 - desc))

    @property
    def total_con_tarjeta(self):
        return self.total_sin_tarjeta + (self.precio_tarjeta or 0.0)

    @property
    def total_final(self):
        if (self.incluye_tarjeta or "No").strip().lower() in ["si", "sí", "yes", "y", "true", "1"]:
            return self.total_con_tarjeta
        return self.total_sin_tarjeta_con_descuento
