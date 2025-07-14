from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QDoubleSpinBox, QPushButton, QLabel, QHBoxLayout, QMessageBox, QWidget, QComboBox
)
from PySide6.QtCore import Qt

class LoadCombinationDialog(QDialog):
    def __init__(self, project, load_comb=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Combinación de cargas")
        self.project = project
        self.load_comb = load_comb  # Puede ser None para nueva combinación

        self.layout = QVBoxLayout(self)
        form_widget = QWidget()
        form = QFormLayout(form_widget)
        self.layout.addWidget(form_widget)

        # Nombre
        self.name_edit = QLineEdit()
        if load_comb is not None:
            self.name_edit.setText(str(load_comb.get("name", "")))
        form.addRow("Nombre", self.name_edit)

        # Tabla de factores y casos de carga
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Caso de carga", "Factor"])
        self.layout.addWidget(QLabel("Factores de combinación:"))
        self.layout.addWidget(self.table)
        self._populate_table_from_comb(load_comb)

        # Botones para agregar/quitar filas
        btns_row = QHBoxLayout()
        self.add_row_btn = QPushButton("Añadir caso")
        self.add_row_btn.clicked.connect(self.add_row)
        self.del_row_btn = QPushButton("Eliminar caso")
        self.del_row_btn.clicked.connect(self.del_row)
        btns_row.addWidget(self.add_row_btn)
        btns_row.addWidget(self.del_row_btn)
        self.layout.addLayout(btns_row)

        # Botones aceptar/cancelar
        btns = QHBoxLayout()
        self.accept_btn = QPushButton("Aceptar")
        self.accept_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.accept_btn)
        btns.addWidget(self.cancel_btn)
        self.layout.addLayout(btns)

    def _populate_table_from_comb(self, load_comb):
        if load_comb and "factors" in load_comb:
            for case_name, factor in load_comb["factors"].items():
                self.add_row(case_name, factor)
        else:
            # Añade una fila vacía por defecto
            self.add_row()

    def add_row(self, case_name=None, factor=None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        # Caso de carga: combo con los casos disponibles
        case_combo = QComboBox()
        for load_case in getattr(self.project, "load_cases", []):
            case_combo.addItem(f"{load_case.name} (#{load_case.id})", load_case.name)
        if case_name:
            idx = case_combo.findText(case_name)
            if idx >= 0:
                case_combo.setCurrentIndex(idx)
        self.table.setCellWidget(row, 0, case_combo)
        # Factor
        factor_spin = QDoubleSpinBox()
        factor_spin.setDecimals(3)
        factor_spin.setRange(-1e3, 1e3)
        if factor is not None:
            factor_spin.setValue(float(factor))
        else:
            factor_spin.setValue(1.0)
        self.table.setCellWidget(row, 1, factor_spin)

    def del_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def accept(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Debes ingresar un nombre.")
            return
        # Leer factores
        factors = {}
        for row in range(self.table.rowCount()):
            case_combo = self.table.cellWidget(row, 0)
            factor_spin = self.table.cellWidget(row, 1)
            case_name = case_combo.currentText() if case_combo else ""
            factor = factor_spin.value() if factor_spin else 1.0
            if case_name:
                factors[case_name] = factor
        if not factors:
            QMessageBox.warning(self, "Error", "Debes agregar al menos un caso de carga.")
            return
        # Guardar en el modelo
        if self.load_comb is not None:
            self.load_comb["name"] = name
            self.load_comb["factors"] = factors
        else:
            if not hasattr(self.project, "load_combinations"):
                self.project.load_combinations = []
            self.project.load_combinations.append({
                "name": name,
                "factors": factors
            })
        super().accept()

    def get_combination(self):
        return self.load_comb