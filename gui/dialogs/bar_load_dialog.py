from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

class BarLoadDialog(QDialog):
    def __init__(self, project, bar_load=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Carga en Barra")
        self.project = project
        self.bar_load = bar_load  # Puede ser None para nueva carga

        self.layout = QVBoxLayout(self)
        form = QFormLayout()
        self.editors = {}

        # Barra asociada
        self.bar_combo = QComboBox()
        for b in self.project.bars:
            self.bar_combo.addItem(f"#{b.id} [{b.n1.id}-{b.n2.id}]", b.id)
        if bar_load is not None:
            idx = self.bar_combo.findData(bar_load.bar.id)
            if idx >= 0:
                self.bar_combo.setCurrentIndex(idx)
        form.addRow("Barra", self.bar_combo)

        # Caso de carga
        self.case_combo = QComboBox()
        for lc in getattr(self.project, "load_cases", []):
            self.case_combo.addItem(f"{lc.name} (#{lc.id})", lc.id)
        if bar_load is not None and hasattr(bar_load, "case"):
            idx = self.case_combo.findData(bar_load.case)
            if idx >= 0:
                self.case_combo.setCurrentIndex(idx)
        form.addRow("Caso de carga", self.case_combo)

        # Tipo de carga (uniforme, trapezoidal, puntual, etc.)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Uniforme", "Trapezoidal", "Puntual"])
        if bar_load is not None and hasattr(bar_load, "type"):
            idx = self.type_combo.findText(bar_load.type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
        form.addRow("Tipo", self.type_combo)

        # Dirección (local, global X/Y/Z)
        self.dir_combo = QComboBox()
        self.dir_combo.addItems(["Global X", "Global Y", "Global Z", "Local"])
        if bar_load is not None and hasattr(bar_load, "direction"):
            idx = self.dir_combo.findText(bar_load.direction)
            if idx >= 0:
                self.dir_combo.setCurrentIndex(idx)
        form.addRow("Dirección", self.dir_combo)

        # Magnitudes según tipo
        self.q1_spin = QDoubleSpinBox()
        self.q1_spin.setDecimals(4)
        self.q1_spin.setRange(-1e8, 1e8)
        self.q1_spin.setValue(getattr(bar_load, "q1", 0.0))
        form.addRow("q1 [kN/m]", self.q1_spin)
        self.editors["q1"] = self.q1_spin

        self.q2_spin = QDoubleSpinBox()
        self.q2_spin.setDecimals(4)
        self.q2_spin.setRange(-1e8, 1e8)
        self.q2_spin.setValue(getattr(bar_load, "q2", 0.0))
        form.addRow("q2 [kN/m]", self.q2_spin)
        self.editors["q2"] = self.q2_spin

        # Para puntual: posición y magnitud (opcional)
        self.pos_spin = QDoubleSpinBox()
        self.pos_spin.setDecimals(4)
        self.pos_spin.setRange(0.0, 1.0)
        self.pos_spin.setValue(getattr(bar_load, "position", 0.5))
        form.addRow("Posición relativa", self.pos_spin)
        self.editors["position"] = self.pos_spin

        self.mag_spin = QDoubleSpinBox()
        self.mag_spin.setDecimals(4)
        self.mag_spin.setRange(-1e8, 1e8)
        self.mag_spin.setValue(getattr(bar_load, "magnitude", 0.0))
        form.addRow("Magnitud puntual [kN]", self.mag_spin)
        self.editors["magnitude"] = self.mag_spin

        self.type_combo.currentIndexChanged.connect(self._update_fields_visibility)
        self._update_fields_visibility()

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

    def _update_fields_visibility(self):
        t = self.type_combo.currentText()
        self.q1_spin.parentWidget().setVisible(t in ("Uniforme", "Trapezoidal"))
        self.q2_spin.parentWidget().setVisible(t == "Trapezoidal")
        self.pos_spin.parentWidget().setVisible(t == "Puntual")
        self.mag_spin.parentWidget().setVisible(t == "Puntual")

    def accept(self):
        bar_id = self.bar_combo.currentData()
        bar = next((b for b in self.project.bars if b.id == bar_id), None)
        if not bar:
            QMessageBox.warning(self, "Error", "Barra no válida.")
            return
        case_id = self.case_combo.currentData()
        case = case_id if case_id is not None else ""
        load_type = self.type_combo.currentText()
        direction = self.dir_combo.currentText()
        q1 = self.q1_spin.value()
        q2 = self.q2_spin.value()
        position = self.pos_spin.value()
        magnitude = self.mag_spin.value()
        if self.bar_load is not None:
            self.bar_load.bar = bar
            self.bar_load.case = case
            self.bar_load.type = load_type
            self.bar_load.direction = direction
            self.bar_load.q1 = q1
            self.bar_load.q2 = q2
            self.bar_load.position = position
            self.bar_load.magnitude = magnitude
        else:
            self.bar_load = self.project.add_bar_load(bar, q1, q2, load_type, direction, position, magnitude, case)
        super().accept()

    def get_bar_load(self):
        return self.bar_load