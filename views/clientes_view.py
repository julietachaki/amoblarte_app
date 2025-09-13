from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QMessageBox, QPushButton,
                             QVBoxLayout)

from controllers.clientes_controller import (agregar_cliente,
                                             buscar_cliente_por_nombre,
                                             eliminar_cliente,
                                             modificar_cliente)


class ClienteView(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Clientes")
        self.setGeometry(200, 200, 500, 400)

        layout = QVBoxLayout()

        # Formulario
        form_layout = QHBoxLayout()
        self.nombre_input = QLineEdit()
        self.telefono_input = QLineEdit()
        self.email_input = QLineEdit()
        form_layout.addWidget(QLabel("Nombre"))
        form_layout.addWidget(self.nombre_input)
        form_layout.addWidget(QLabel("Teléfono"))
        form_layout.addWidget(self.telefono_input)
        form_layout.addWidget(QLabel("Email"))
        form_layout.addWidget(self.email_input)
        layout.addLayout(form_layout)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar")
        self.btn_modificar = QPushButton("Modificar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_buscar = QPushButton("Buscar")
        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_modificar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addWidget(self.btn_buscar)
        layout.addLayout(btn_layout)

        # Lista de clientes
        self.lista_clientes = QListWidget()
        layout.addWidget(self.lista_clientes)

        self.setLayout(layout)

        # Conectar eventos
        self.btn_agregar.clicked.connect(self.agregar)
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_buscar.clicked.connect(self.buscar)

        self.selected_cliente_id = None

        # Al seleccionar un cliente en la lista
        self.lista_clientes.itemClicked.connect(self.cargar_cliente)

        # Cargar clientes inicial
        self.buscar()

    def agregar(self):
        cliente = agregar_cliente(
            self.nombre_input.text(),
            self.telefono_input.text(),
            self.email_input.text()
        )
        QMessageBox.information(self, "Éxito", f"Cliente agregado: {cliente.nombre}")
        self.buscar()
        self.limpiar_form()

    def modificar(self):
        if not self.selected_cliente_id:
            QMessageBox.warning(self, "Error", "Seleccione un cliente para modificar")
            return
        cliente = modificar_cliente(
            self.selected_cliente_id,
            nombre=self.nombre_input.text(),
            telefono=self.telefono_input.text(),
            email=self.email_input.text()
        )
        if cliente:
            QMessageBox.information(self, "Éxito", f"Cliente modificado: {cliente.nombre}")
            self.buscar()
            self.limpiar_form()

    def eliminar(self):
        if not self.selected_cliente_id:
            QMessageBox.warning(self, "Error", "Seleccione un cliente para eliminar")
            return
        confirm = QMessageBox.question(self, "Confirmar", "¿Desea eliminar este cliente?")
        if confirm == QMessageBox.StandardButton.Yes:
            eliminado = eliminar_cliente(self.selected_cliente_id)
            if eliminado:
                QMessageBox.information(self, "Éxito", "Cliente eliminado")
                self.buscar()
                self.limpiar_form()

    def buscar(self):
        nombre = self.nombre_input.text()
        clientes = buscar_cliente_por_nombre(nombre) if nombre else buscar_cliente_por_nombre("")
        self.lista_clientes.clear()
        for c in clientes:
            self.lista_clientes.addItem(f"{c.id}: {c.nombre} - {c.telefono} - {c.email}")

    def cargar_cliente(self, item):
        text = item.text()
        cliente_id = int(text.split(":")[0])
        self.selected_cliente_id = cliente_id
        partes = text.split(" - ")
        self.nombre_input.setText(partes[0].split(":")[1].strip())
        self.telefono_input.setText(partes[1].strip())
        self.email_input.setText(partes[2].strip())

    def limpiar_form(self):
        self.nombre_input.clear()
        self.telefono_input.clear()
        self.email_input.clear()
        self.selected_cliente_id = None
