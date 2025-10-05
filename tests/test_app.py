import os
import unittest

from app import Cliente, Presupuesto, app, db


class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Create a sample client and budget
            cliente = Cliente(nombre='Juan', apellido='Perez', celular='123', direccion='Calle 123')
            db.session.add(cliente)
            db.session.commit()

            presupuesto = Presupuesto(
                numero_presupuesto='PRE-TEST-001',
                descripcion='Mueble a medida',
                precio_materiales=1000.0,
                precio_mano_obra=500.0,
                incluye_tarjeta='No',
                precio_tarjeta=0.0,
                cliente_id=cliente.id,
            )
            db.session.add(presupuesto)
            db.session.commit()
            self.presupuesto_id = presupuesto.id

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_index_route(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_presupuestos_route(self):
        resp = self.app.get('/presupuestos')
        self.assertEqual(resp.status_code, 200)

    def test_descargar_pdf_inline(self):
        # Ensure PDF can be generated and served inline
        with app.app_context():
            from app import generate_pdf
            generate_pdf(self.presupuesto_id)
        resp = self.app.get(f'/presupuestos/{self.presupuesto_id}/pdf')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('application/pdf', resp.headers.get('Content-Type', 'application/pdf'))


if __name__ == '__main__':
    unittest.main()
