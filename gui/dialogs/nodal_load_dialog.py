from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QHBoxLayout, QMessageBox, QWidget
)
from PySide6.QtCore import Qt

class NodalLoadDialog(QDialog):
    def __init__(self, project, nodal_load=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Carga Nodal")
        self.project = project
        self.nodal_load = nodal_load  # Puede ser None para nueva carga

        self.layout = QVBoxLayout(self)
        form = QFormLayout()
        self.editors = {}

        # Nodo asociado
        self.node_combo = QComboBox()
        for n in self.project.nodes:
            self.node_combo.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})", n.id)
        if nodal_load is not None:
            idx = self.node_combo.findData(nodal_load.node.id)
            if idx >= 0:
                self.node_combo.setCurrentIndex(idx)
        form.addRow("Nodo", self.node_combo)

        # Caso de carga
        self.case_combo = QComboBox()
        for lc in getattr(self.project, "load_cases", []):
            self.case_combo.addItem(f"{lc.name} (#{lc.id})", lc.id)
        if nodal_load is not None and hasattr(nodal_load, "case"):
            idx = self.case_combo.findData(nodal_load.case)
            if idx >= 0:
                self.case_combo.setCurrentIndex(idx)
        form.addRow("Caso de carga", self.case_combo)

        # Componentes de la carga
        self.editors["fx"] = self._add_spin(form, "Fx [kN]", getattr(nodal_load, "fx", 0.0))
        self.editors["fy"] = self._add_spin(form, "Fy [kN]", getattr(nodal_load, "fy", 0.0))
        self.editors["fz"] = self._add_spin(form, "Fz [kN]", getattr(nodal_load, "fz", 0.0))
        self.editors["mx"] = self._add_spin(form, "Mx [kN·m]", getattr(nodal_load, "mx", 0.0))
        self.editors["my"] = self._add_spin(form, "My [kN·m]", getattr(nodal_load, "my", 0.0))
        self.editors["mz"] = self._add_spin(form, "Mz [kN·m]", getattr(nodal_load, "mz", 0.0))

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

    def _add_spin(self, form, label, value=0.0):
        spin = QDoubleSpinBox()
        spin.setDecimals(4)
        spin.setRange(-1e8, 1e8)
        spin.setValue(value)
        form.addRow(label, spin)
        return spin

    def accept(self):
        node_id = self.node_combo.currentData()
        node = next((n for n in self.project.nodes if n.id == node_id), None)
        if not node:
            QMessageBox.warning(self, "Error", "Nodo no válido.")
            return
        case_id = self.case_combo.currentData()
        case = case_id if case_id is not None else ""
        fx = self.editors["fx"].value()
        fy = self.editors["fy"].value()
        fz = self.editors["fz"].value()
        mx = self.editors["mx"].value()
        my = self.editors["my"].value()
        mz = self.editors["mz"].value()
        if self.nodal_load is not None:
            self.nodal_load.node = node
            self.nodal_load.case = case
            self.nodal_load.fx = fx
            self.nodal_load.fy = fy
            self.nodal_load.fz = fz
            self.nodal_load.mx = mx
            self.nodal_load.my = my
            self.nodal_load.mz = mz
        else:
            # Debe haber un método en el modelo para agregar la carga
            self.nodal_load = self.project.add_nodal_load(node, fx, fy, fz, mx, my, mz, case)
        super().accept()

    def get_nodal_load(self):
        return self.nodal_load