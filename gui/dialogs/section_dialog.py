from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QHBoxLayout, QMessageBox, QWidget, QScrollArea
)
from PySide6.QtCore import Qt

class SectionDialog(QDialog):
    def __init__(self, project, section=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sección")
        self.project = project
        self.section = section  # Puede ser None para nueva sección

        self.layout = QVBoxLayout(self)
        form_widget = QWidget()
        self.form = QFormLayout(form_widget)
        self.editors = {}

        # Nombre
        self.name_edit = QLineEdit()
        if section is not None:
            self.name_edit.setText(str(section.name))
        self.form.addRow("Nombre", self.name_edit)
        self.editors["name"] = self.name_edit

        # Tipo de sección
        self.type_combo = QComboBox()
        types = section.get_section_types() if section else self.project.sections[0].get_section_types()
        self.type_combo.addItems(types)
        if section is not None and hasattr(section, "type"):
            idx = self.type_combo.findText(section.type)
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)
        self.form.addRow("Tipo", self.type_combo)
        self.editors["type"] = self.type_combo

        # Material asociado
        self.material_combo = QComboBox()
        self.material_combo.addItem("Ninguno", None)
        current_material_id = getattr(section.material, "id", section.material) if section is not None else None
        for m in self.project.materials:
            label = f"{m.name} (#{m.id})"
            self.material_combo.addItem(label, m.id)
            if m.id == current_material_id:
                self.material_combo.setCurrentIndex(self.material_combo.count()-1)
        self.form.addRow("Material", self.material_combo)
        self.editors["material"] = self.material_combo

        # Parámetros dinámicos
        self.params_widget = QWidget()
        self.params_layout = QFormLayout(self.params_widget)
        self.params_editors = {}
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.params_widget)
        self.layout.addWidget(form_widget)
        self.layout.addWidget(QLabel("Parámetros"))
        self.layout.addWidget(self.scroll)

        # Inicializa parámetros si existe sección
        self.current_params = dict(section.params) if section and hasattr(section, "params") else {}

        # Los parámetros se actualizan según el tipo de sección
        self.type_combo.currentIndexChanged.connect(self.update_params_fields)
        self.update_params_fields()

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
        # Define campos sugeridos según el tipo de sección
        sec_type = self.type_combo.currentText()
        params_fields = self._get_param_fields_for_type(sec_type)
        for name, default in params_fields:
            current = self.current_params.get(name, default)
            editor = QDoubleSpinBox()
            editor.setDecimals(6)
            editor.setRange(-1e12, 1e12)
            editor.setValue(float(current) if current is not None else 0.0)
            self.params_layout.addRow(name, editor)
            self.params_editors[name] = editor

    def _get_param_fields_for_type(self, sec_type):
        # Personaliza para los tipos que maneje tu app
        if sec_type == "Rectangular":
            return [("b", 0.3), ("h", 0.5)]
        elif sec_type == "Circular":
            return [("d", 0.3)]
        elif sec_type == "IPE" or sec_type == "HEB":
            return [("profile", 100)]  # Ejemplo: "IPE100", "HEB200", etc.
        elif sec_type == "Custom":
            return [("A", 0.01), ("Iy", 1e-6), ("Iz", 1e-6), ("J", 1e-8)]
        else:
            return list(self.current_params.items()) if self.current_params else [("param1", 0.0), ("param2", 0.0)]

    def accept(self):
        # Validar nombre
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Debes ingresar un nombre.")
            return
        sec_type = self.type_combo.currentText()
        # Material seleccionado
        mat_id = self.material_combo.currentData()
        material = None
        for m in self.project.materials:
            if m.id == mat_id:
                material = m
                break
        # Parámetros
        params = {}
        for k, editor in self.params_editors.items():
            params[k] = editor.value()
        # Crear o editar sección
        if self.section is not None:
            self.section.name = name
            self.section.type = sec_type
            self.section.params = params
            self.section.material = material
        else:
            self.section = self.project.add_section(name, sec_type, params, material)
        super().accept()

    def get_section(self):
        return self.section