from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QHBoxLayout, QMessageBox, QWidget, QScrollArea
)
from PySide6.QtCore import Qt

class MaterialDialog(QDialog):
    def __init__(self, project, material=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material")
        self.project = project
        self.material = material  # Puede ser None para nuevo material

        self.layout = QVBoxLayout(self)
        form_widget = QWidget()
        self.form = QFormLayout(form_widget)
        self.editors = {}

        # Nombre
        self.name_edit = QLineEdit()
        if material is not None:
            self.name_edit.setText(str(material.name))
        self.form.addRow("Nombre", self.name_edit)
        self.editors["name"] = self.name_edit

        # Tipo (OpenSees)
        self.type_combo = QComboBox()
        self.type_combo.addItems(material.get_opensees_types() if material else self.project.materials[0].get_opensees_types())
        if material is not None and hasattr(material, "type"):
            idx = self.type_combo.findText(material.type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
        self.form.addRow("Tipo", self.type_combo)
        self.editors["type"] = self.type_combo

        # Parámetros dinámicos (depende del tipo)
        self.params_widget = QWidget()
        self.params_layout = QFormLayout(self.params_widget)
        self.params_editors = {}
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.params_widget)
        self.layout.addWidget(form_widget)
        self.layout.addWidget(QLabel("Parámetros"))
        self.layout.addWidget(self.scroll)

        # Inicializa parámetros actuales si existe material
        self.current_params = dict(material.params) if material and hasattr(material, "params") else {}

        # Los parámetros se actualizan según el tipo
        self.type_combo.currentIndexChanged.connect(self.update_params_fields)
        self.update_params_fields()  # Llama la primera vez

        # Botones
        btns = QHBoxLayout()
        self.accept_btn = QPushButton("Aceptar")
        self.accept_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.accept_btn)
        btns.addWidget(self.cancel_btn)
        self.layout.addLayout(btns)

    def update_params_fields(self):
        # Limpia parámetros antiguos
        while self.params_layout.rowCount():
            self.params_layout.removeRow(0)
        self.params_editors.clear()
        # Define campos sugeridos según el tipo de material
        mat_type = self.type_combo.currentText()
        params_fields = self._get_param_fields_for_type(mat_type)
        # Usa valores actuales si existen
        for name, default in params_fields:
            current = self.current_params.get(name, default)
            editor = QDoubleSpinBox()
            editor.setDecimals(6)
            editor.setRange(-1e12, 1e12)
            editor.setValue(float(current) if current is not None else 0.0)
            self.params_layout.addRow(name, editor)
            self.params_editors[name] = editor

    def _get_param_fields_for_type(self, mat_type):
        # Aquí puedes ampliar los campos según los tipos de OpenSees
        # Estos son ejemplos comunes, personalízalos para tus necesidades
        if mat_type == "Elastic":
            return [("E", 210000), ("nu", 0.3), ("rho", 7850)]
        elif mat_type in ("Steel01", "Steel02", "SteelMPF"):
            return [("Fy", 355), ("E", 210000), ("b", 0.01)]
        elif mat_type.startswith("Concrete"):
            return [("fpc", -30), ("epsc0", -0.002), ("fpcu", -20), ("epsU", -0.006)]
        else:
            # Tipo desconocido: permite parámetros genéricos
            return list(self.current_params.items()) if self.current_params else [("param1", 0.0), ("param2", 0.0)]

    def accept(self):
        # Validar nombre
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Debes ingresar un nombre.")
            return
        mat_type = self.type_combo.currentText()
        params = {}
        for k, editor in self.params_editors.items():
            params[k] = editor.value()
        # Crear o editar material
        if self.material is not None:
            self.material.name = name
            self.material.type = mat_type
            self.material.params = params
        else:
            self.material = self.project.add_material(name, mat_type, params)
        super().accept()

    def get_material(self):
        return self.material