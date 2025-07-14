from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt

class ShellLoadDialog(QDialog):
    def __init__(self, project, shell_load=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Carga en Shell")
        self.project = project
        self.shell_load = shell_load

        self.layout = QVBoxLayout(self)
        form = QFormLayout()
        self.editors = {}

        # Shell asociado
        self.shell_combo = QComboBox()
        for s in self.project.shells:
            nids = "-".join(str(n.id) for n in s.nodes)
            self.shell_combo.addItem(f"#{s.id} [{nids}]", s.id)
        if shell_load is not None:
            idx = self.shell_combo.findData(shell_load.shell.id)
            if idx >= 0:
                self.shell_combo.setCurrentIndex(idx)
        form.addRow("Shell", self.shell_combo)

        # Caso de carga
        self.case_combo = QComboBox()
        for lc in getattr(self.project, "load_cases", []):
            self.case_combo.addItem(f"{lc.name} (#{lc.id})", lc.id)
        if shell_load is not None and hasattr(shell_load, "case"):
            idx = self.case_combo.findData(shell_load.case)
            if idx >= 0:
                self.case_combo.setCurrentIndex(idx)
        form.addRow("Caso de carga", self.case_combo)

        # Tipo de carga (uniforme, trapezoidal, puntual, etc.)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Uniforme", "Trapezoidal", "Puntual"])
        if shell_load is not None and hasattr(shell_load, "type"):
            idx = self.type_combo.findText(shell_load.type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
        form.addRow("Tipo", self.type_combo)

        # Dirección (Global Z, Local Z, etc.)
        self.dir_combo = QComboBox()
        self.dir_combo.addItems(["Global Z", "Local Z"])
        if shell_load is not None and hasattr(shell_load, "direction"):
            idx = self.dir_combo.findText(shell_load.direction)
            if idx >= 0:
                self.dir_combo.setCurrentIndex(idx)
        form.addRow("Dirección", self.dir_combo)

        # Magnitud (q)
        self.q_spin = QDoubleSpinBox()
        self.q_spin.setDecimals(4)
        self.q_spin.setRange(-1e8, 1e8)
        self.q_spin.setValue(getattr(shell_load, "q", 0.0))
        form.addRow("q [kN/m²]", self.q_spin)
        self.editors["q"] = self.q_spin

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
        shell_id = self.shell_combo.currentData()
        shell = next((s for s in self.project.shells if s.id == shell_id), None)
        if not shell:
            QMessageBox.warning(self, "Error", "Shell no válido.")
            return
        case_id = self.case_combo.currentData()
        case = case_id if case_id is not None else ""
        load_type = self.type_combo.currentText()
        direction = self.dir_combo.currentText()
        q = self.q_spin.value()
        if self.shell_load is not None:
            self.shell_load.shell = shell
            self.shell_load.case = case
            self.shell_load.type = load_type
            self.shell_load.direction = direction
            self.shell_load.q = q
        else:
            self.shell_load = self.project.add_shell_load(shell, q, load_type, direction, case)
        super().accept()

    def get_shell_load(self):
        return self.shell_load