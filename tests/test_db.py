import unittest

from app import Cliente, Presupuesto, app, db


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            self.ctx = app.app_context()
            self.ctx.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_create_cliente_and_presupuesto_totals(self):
        cliente = Cliente(nombre='Ana', apellido='Gomez', celular='456', direccion='Av 456')
        db.session.add(cliente)
        db.session.commit()

        p = Presupuesto(
            numero_presupuesto='PRE-TEST-002',
            descripcion='Placard',
            precio_materiales=2000.0,
            precio_mano_obra=800.0,
            incluye_tarjeta='Sí',
            precio_tarjeta=300.0,
            cliente_id=cliente.id,
        )
        db.session.add(p)
        db.session.commit()

        self.assertAlmostEqual(p.total_sin_tarjeta, 2800.0)
        self.assertAlmostEqual(p.total_con_tarjeta, 3100.0)
        self.assertAlmostEqual(p.total_final, 3100.0)


if __name__ == '__main__':
    unittest.main()
