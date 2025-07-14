from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QSpinBox,
    QPushButton, QLabel, QHBoxLayout, QDoubleSpinBox, QMessageBox
)
from PySide6.QtCore import Qt

class ExtrudeDialog(QDialog):
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Extruir")
        self.project = project

        self.layout = QVBoxLayout(self)
        form = QFormLayout()

        # Tipo de extrusión
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Nodo → Barra",
            "Barra → Shell",
            "Shell → Sólido"
        ])
        form.addRow("Tipo de extrusión", self.type_combo)

        # Elemento base
        self.base_combo = QComboBox()
        self.update_base_combo()
        self.type_combo.currentIndexChanged.connect(self.update_base_combo)
        form.addRow("Elemento base", self.base_combo)

        # Número de divisiones
        self.divs_spin = QSpinBox()
        self.divs_spin.setMinimum(1)
        self.divs_spin.setMaximum(100)
        self.divs_spin.setValue(5)
        form.addRow("Divisiones", self.divs_spin)

        # Longitud total de extrusión
        self.length_spin = QDoubleSpinBox()
        self.length_spin.setDecimals(4)
        self.length_spin.setMinimum(0.001)
        self.length_spin.setMaximum(1e6)
        self.length_spin.setValue(1.0)
        form.addRow("Longitud", self.length_spin)

        # Dirección (vector)
        self.dir_x_spin = QDoubleSpinBox()
        self.dir_x_spin.setDecimals(4)
        self.dir_x_spin.setRange(-1e3, 1e3)
        self.dir_x_spin.setValue(1.0)
        form.addRow("Dirección X", self.dir_x_spin)

        self.dir_y_spin = QDoubleSpinBox()
        self.dir_y_spin.setDecimals(4)
        self.dir_y_spin.setRange(-1e3, 1e3)
        self.dir_y_spin.setValue(0.0)
        form.addRow("Dirección Y", self.dir_y_spin)

        self.dir_z_spin = QDoubleSpinBox()
        self.dir_z_spin.setDecimals(4)
        self.dir_z_spin.setRange(-1e3, 1e3)
        self.dir_z_spin.setValue(0.0)
        form.addRow("Dirección Z", self.dir_z_spin)

        self.layout.addLayout(form)

        # Botones aceptar/cancelar
        btns = QHBoxLayout()
        self.accept_btn = QPushButton("Aceptar")
        self.accept_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.accept_btn)
        btns.addWidget(self.cancel_btn)
        self.layout.addLayout(btns)

    def update_base_combo(self):
        extrude_type = self.type_combo.currentText()
        self.base_combo.clear()
        if extrude_type == "Nodo → Barra":
            for n in self.project.nodes:
                self.base_combo.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})", n.id)
        elif extrude_type == "Barra → Shell":
            for b in self.project.bars:
                self.base_combo.addItem(f"#{b.id} [{b.n1.id}-{b.n2.id}]", b.id)
        elif extrude_type == "Shell → Sólido":
            for s in self.project.shells:
                nids = "-".join(str(n.id) for n in s.nodes)
                self.base_combo.addItem(f"#{s.id} [{nids}]", s.id)

    def accept(self):
        extrude_type = self.type_combo.currentText()
        base_id = self.base_combo.currentData()
        ndivs = self.divs_spin.value()
        length = self.length_spin.value()
        dir_x = self.dir_x_spin.value()
        dir_y = self.dir_y_spin.value()
        dir_z = self.dir_z_spin.value()
        if length <= 0 or (dir_x == 0 and dir_y == 0 and dir_z == 0):
            QMessageBox.warning(self, "Error", "Debes ingresar una longitud y una dirección válidas.")
            return
        # Lógica: delega a métodos del modelo
        if extrude_type == "Nodo → Barra":
            base = next((n for n in self.project.nodes if n.id == base_id), None)
            if not base:
                QMessageBox.warning(self, "Error", "Nodo base no válido.")
                return
            self.project.extrude_node_to_bars(base, ndivs, length, (dir_x, dir_y, dir_z))
        elif extrude_type == "Barra → Shell":
            base = next((b for b in self.project.bars if b.id == base_id), None)
            if not base:
                QMessageBox.warning(self, "Error", "Barra base no válida.")
                return
            self.project.extrude_bar_to_shells(base, ndivs, length, (dir_x, dir_y, dir_z))
        elif extrude_type == "Shell → Sólido":
            base = next((s for s in self.project.shells if s.id == base_id), None)
            if not base:
                QMessageBox.warning(self, "Error", "Shell base no válido.")
                return
            self.project.extrude_shell_to_solids(base, ndivs, length, (dir_x, dir_y, dir_z))
        super().accept()