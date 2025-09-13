from PyQt6.QtWidgets import (QDialog, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout)

from controllers.tarjetas_controller import (guardar_configuracion,
                                             obtener_configuracion)


class ConfiguracionView(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración de Tarjetas y Descuentos")
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()

        self.descuento_input = QLineEdit()
        self.cuotas_input = QLineEdit()
        self.interes_input = QLineEdit()

        # Cargar valores actuales
        config = obtener_configuracion()
        if config:
            self.descuento_input.setText(str(config[0]))
            self.cuotas_input.setText(str(config[1]))
            self.interes_input.setText(str(config[2]))

        layout.addWidget(QLabel("Descuento contado (%)"))
        layout.addWidget(self.descuento_input)

        layout.addWidget(QLabel("Cantidad de cuotas"))
        layout.addWidget(self.cuotas_input)

        layout.addWidget(QLabel("Interés (%)"))
        layout.addWidget(self.interes_input)

        btn_guardar = QPushButton("Guardar")
        btn_guardar.clicked.connect(self.guardar)
        layout.addWidget(btn_guardar)

        self.setLayout(layout)

    def guardar(self):
        descuento = float(self.descuento_input.text() or 0)
        cuotas = int(self.cuotas_input.text() or 1)
        interes = float(self.interes_input.text() or 0)
        guardar_configuracion(descuento, cuotas, interes)
        self.close()
