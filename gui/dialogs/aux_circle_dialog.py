from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

class AuxCircleDialog(QDialog):
    def __init__(self, project, aux_circle=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Círculo Auxiliar")
        self.project = project
        self.aux_circle = aux_circle  # Puede ser None para nuevo círculo

        self.layout = QVBoxLayout(self)
        form = QFormLayout()

        # Nodo centro
        self.center_combo = QComboBox()
        for n in self.project.nodes:
            self.center_combo.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})", n.id)
        if aux_circle is not None:
            idx = self.center_combo.findData(aux_circle.center.id)
            if idx >= 0:
                self.center_combo.setCurrentIndex(idx)
        form.addRow("Centro", self.center_combo)

        # Nodo en circunferencia (define radio)
        self.radius_combo = QComboBox()
        for n in self.project.nodes:
            self.radius_combo.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})", n.id)
        if aux_circle is not None:
            idx = self.radius_combo.findData(aux_circle.radius_node.id)
            if idx >= 0:
                self.radius_combo.setCurrentIndex(idx)
        form.addRow("Nodo en circunferencia", self.radius_combo)

        # Ángulo inicial y final (opcional)
        self.start_angle_spin = QDoubleSpinBox()
        self.start_angle_spin.setDecimals(2)
        self.start_angle_spin.setRange(0, 360)
        self.start_angle_spin.setValue(getattr(aux_circle, "start_angle", 0.0))
        form.addRow("Ángulo inicial [deg]", self.start_angle_spin)

        self.end_angle_spin = QDoubleSpinBox()
        self.end_angle_spin.setDecimals(2)
        self.end_angle_spin.setRange(0, 360)
        self.end_angle_spin.setValue(getattr(aux_circle, "end_angle", 360.0))
        form.addRow("Ángulo final [deg]", self.end_angle_spin)

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

    def accept(self):
        center_id = self.center_combo.currentData()
        radius_id = self.radius_combo.currentData()
        center = next((n for n in self.project.nodes if n.id == center_id), None)
        radius_node = next((n for n in self.project.nodes if n.id == radius_id), None)
        if not center or not radius_node or center.id == radius_node.id:
            QMessageBox.warning(self, "Error", "Debes seleccionar dos nodos distintos para centro y radio.")
            return
        start_angle = self.start_angle_spin.value()
        end_angle = self.end_angle_spin.value()
        if self.aux_circle is not None:
            self.aux_circle.center = center
            self.aux_circle.radius_node = radius_node
            self.aux_circle.start_angle = start_angle
            self.aux_circle.end_angle = end_angle
        else:
            self.aux_circle = self.project.add_aux_circle(center, radius_node, start_angle, end_angle)
        super().accept()

    def get_aux_circle(self):
        return self.aux_circle