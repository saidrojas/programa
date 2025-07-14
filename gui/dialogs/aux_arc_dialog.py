from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

class AuxArcDialog(QDialog):
    def __init__(self, project, aux_arc=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Arco Auxiliar")
        self.project = project
        self.aux_arc = aux_arc  # Puede ser None para nuevo arco

        self.layout = QVBoxLayout(self)
        form = QFormLayout()

        # Nodo inicial
        self.n1_combo = QComboBox()
        for n in self.project.nodes:
            self.n1_combo.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})", n.id)
        if aux_arc is not None:
            idx = self.n1_combo.findData(aux_arc.n1.id)
            if idx >= 0:
                self.n1_combo.setCurrentIndex(idx)
        form.addRow("Nodo inicial", self.n1_combo)

        # Nodo final
        self.n2_combo = QComboBox()
        for n in self.project.nodes:
            self.n2_combo.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})", n.id)
        if aux_arc is not None:
            idx = self.n2_combo.findData(aux_arc.n2.id)
            if idx >= 0:
                self.n2_combo.setCurrentIndex(idx)
        form.addRow("Nodo final", self.n2_combo)

        # Nodo de control (define la curvatura)
        self.n3_combo = QComboBox()
        for n in self.project.nodes:
            self.n3_combo.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})", n.id)
        if aux_arc is not None:
            idx = self.n3_combo.findData(aux_arc.n3.id)
            if idx >= 0:
                self.n3_combo.setCurrentIndex(idx)
        form.addRow("Nodo de control", self.n3_combo)

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
        n1_id = self.n1_combo.currentData()
        n2_id = self.n2_combo.currentData()
        n3_id = self.n3_combo.currentData()
        n1 = next((n for n in self.project.nodes if n.id == n1_id), None)
        n2 = next((n for n in self.project.nodes if n.id == n2_id), None)
        n3 = next((n for n in self.project.nodes if n.id == n3_id), None)
        if not n1 or not n2 or not n3 or len({n1.id, n2.id, n3.id}) < 3:
            QMessageBox.warning(self, "Error", "Debes seleccionar tres nodos distintos.")
            return
        if self.aux_arc is not None:
            self.aux_arc.n1 = n1
            self.aux_arc.n2 = n2
            self.aux_arc.n3 = n3
        else:
            self.aux_arc = self.project.add_aux_arc(n1, n2, n3)
        super().accept()

    def get_aux_arc(self):
        return self.aux_arc