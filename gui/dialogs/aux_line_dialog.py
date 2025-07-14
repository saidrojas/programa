from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

class AuxLineDialog(QDialog):
    def __init__(self, project, aux_line=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Línea Auxiliar")
        self.project = project
        self.aux_line = aux_line  # Puede ser None para nueva línea auxiliar

        self.layout = QVBoxLayout(self)
        form = QFormLayout()
        self.editors = {}

        # Nodo inicial
        self.n1_combo = QComboBox()
        for n in self.project.nodes:
            self.n1_combo.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})", n.id)
        if aux_line is not None:
            idx = self.n1_combo.findData(aux_line.n1.id)
            if idx >= 0:
                self.n1_combo.setCurrentIndex(idx)
        form.addRow("Nodo inicial", self.n1_combo)

        # Nodo final
        self.n2_combo = QComboBox()
        for n in self.project.nodes:
            self.n2_combo.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})", n.id)
        if aux_line is not None:
            idx = self.n2_combo.findData(aux_line.n2.id)
            if idx >= 0:
                self.n2_combo.setCurrentIndex(idx)
        form.addRow("Nodo final", self.n2_combo)

        # Color (opcional)
        # self.color_edit = QLineEdit(getattr(aux_line, "color", "#888888"))
        # form.addRow("Color (hex)", self.color_edit)

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
        n1 = next((n for n in self.project.nodes if n.id == n1_id), None)
        n2 = next((n for n in self.project.nodes if n.id == n2_id), None)
        if not n1 or not n2 or n1.id == n2.id:
            QMessageBox.warning(self, "Error", "Debes seleccionar dos nodos distintos.")
            return
        # color = self.color_edit.text().strip() or "#888888"
        if self.aux_line is not None:
            self.aux_line.n1 = n1
            self.aux_line.n2 = n2
            # self.aux_line.color = color
        else:
            self.aux_line = self.project.add_aux_line(n1, n2)
        super().accept()

    def get_aux_line(self):
        return self.aux_line