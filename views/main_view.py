from views.tarjetas_view import ConfiguracionView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Muebles")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        btn_cliente = QPushButton("Agregar Cliente de Prueba")
        btn_cliente.clicked.connect(self.add_cliente)
        layout.addWidget(btn_cliente)

        btn_presupuesto = QPushButton("Crear Presupuesto de Prueba")
        btn_presupuesto.clicked.connect(self.add_presupuesto)
        layout.addWidget(btn_presupuesto)

        btn_config = QPushButton("Configuración de Tarjetas")
        btn_config.clicked.connect(self.open_config)
        layout.addWidget(btn_config)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add_cliente(self):
        agregar_cliente("Juan Pérez", "123456789", "juan@test.com")
        print("Cliente agregado")

    def add_presupuesto(self):
        agregar_presupuesto(1, "Juego de comedor", 1000, 850)
        print("Presupuesto generado")

    def open_config(self):
        dialog = ConfiguracionView()
        dialog.exec()
