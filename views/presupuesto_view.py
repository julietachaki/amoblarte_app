from PyQt6.QtWidgets import (QComboBox, QDialog, QFileDialog, QHBoxLayout,
                             QLabel, QLineEdit, QListWidget, QMessageBox,
                             QPushButton, QVBoxLayout)

from controllers.clientes_controller import (buscar_cliente_por_nombre,
                                             obtener_cliente)
from controllers.presupuesto_controller import (
    agregar_presupuesto, buscar_presupuestos_por_cliente, eliminar_presupuesto,
    modificar_presupuesto)


class PresupuestoView(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Presupuestos")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        # Selección de cliente
        cliente_layout = QHBoxLayout()
        self.cliente_combo = QComboBox()
        self.cargar_clientes()
        cliente_layout.addWidget(QLabel("Cliente"))
        cliente_layout.addWidget(self.cliente_combo)
        layout.addLayout(cliente_layout)

        # Descripción y precio
        form_layout = QHBoxLayout()
        self.descripcion_input = QLineEdit()
        self.precio_input = QLineEdit()
        form_layout.addWidget(QLabel("Descripción"))
        form_layout.addWidget(self.descripcion_input)
        form_layout.addWidget(QLabel("Precio Lista"))
        form_layout.addWidget(self.precio_input)
        layout.addLayout(form_layout)

        # Imagen temporal
        img_layout = QHBoxLayout()
        self.img_input = QLineEdit()
        self.btn_examinar = QPushButton("Examinar Imagen")
        img_layout.addWidget(QLabel("Imagen Mueble"))
        img_layout.addWidget(self.img_input)
        img_layout.addWidget(self.btn_examinar)
        layout.addLayout(img_layout)

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

        # Lista de presupuestos
        self.lista_presupuestos = QListWidget()
        layout.addWidget(self.lista_presupuestos)

        self.setLayout(layout)

        # Conectar eventos
        self.btn_agregar.clicked.connect(self.agregar)
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_buscar.clicked.connect(self.buscar)
        self.btn_examinar.clicked.connect(self.examinar)

        self.selected_presupuesto_id = None
        self.lista_presupuestos.itemClicked.connect(self.cargar_presupuesto)

    def cargar_clientes(self):
        self.cliente_combo.clear()
        clientes = buscar_cliente_por_nombre("")
        for c in clientes:
            self.cliente_combo.addItem(f"{c.id}: {c.nombre}")

    def examinar(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar Imagen", "", "Imagenes (*.png *.jpg *.jpeg)")
        if file_path:
            self.img_input.setText(file_path)

    def agregar(self):
        cliente_id = int(self.cliente_combo.currentText().split(":")[0])
        descripcion = self.descripcion_input.text()
        precio_lista = float(self.precio_input.text() or 0)
        imagen_temp = self.img_input.text() if self.img_input.text() else None

        presupuesto = agregar_presupuesto(cliente_id, descripcion, precio_lista)
        QMessageBox.information(self, "Éxito", f"Presupuesto generado ID: {presupuesto.id}")
        self.buscar()
        self.limpiar_form()

    def modificar(self):
        if not self.selected_presupuesto_id:
            QMessageBox.warning(self, "Error", "Seleccione un presupuesto")
            return
        descripcion = self.descripcion_input.text()
        precio_lista = float(self.precio_input.text() or 0)
        modificar_presupuesto(self.selected_presupuesto_id, descripcion=descripcion, precio_lista=precio_lista)
        QMessageBox.information(self, "Éxito", "Presupuesto modificado")
        self.buscar()
        self.limpiar_form()

    def eliminar(self):
        if not self.selected_presupuesto_id:
            QMessageBox.warning(self, "Error", "Seleccione un presupuesto")
            return
        confirm = QMessageBox.question(self, "Confirmar", "¿Desea eliminar este presupuesto?")
        if confirm == QMessageBox.StandardButton.Yes:
            from controllers.presupuesto_controller import eliminar_presupuesto
            eliminado = eliminar_presupuesto(self.selected_presupuesto_id)
            if eliminado:
                QMessageBox.information(self, "Éxito", "Presupuesto eliminado")
                self.buscar()
                self.limpiar_form()

    def buscar(self):
        cliente_text = self.cliente_combo.currentText()
        cliente_id = int(cliente_text.split(":")[0]) if cliente_text else None
        if cliente_id:
            presupuestos = buscar_presupuestos_por_cliente(obtener_cliente(cliente_id).nombre)
            self.lista_presupuestos.clear()
            for p in presupuestos:
                self.lista_presupuestos.addItem(f"{p.id}: {p.descripcion} - ${p.precio_lista} - ${p.precio_contado}")

    def cargar_presupuesto(self, item):
        text = item.text()
        presupuesto_id = int(text.split(":")[0])
        self.selected_presupuesto_id = presupuesto_id
        partes = text.split(" - ")
        self.descripcion_input.setText(partes[0].split(":")[1].strip())
        self.precio_input.setText(partes[1].replace("$","").strip())

    def limpiar_form(self):
        self.descripcion_input.clear()
        self.precio_input.clear()
        self.img_input.clear()
        self.selected_presupuesto_id = None
