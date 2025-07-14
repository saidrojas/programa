from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout, QLabel, QFileDialog, QCheckBox
)
from PySide6.QtCore import Qt

class ExportOpenSeesDialog(QDialog):
    """
    Diálogo para exportar el modelo actual a un archivo/script OpenSees.
    Permite seleccionar opciones de exportación y destino.
    """
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exportar a OpenSees")
        self.project = project

        self.layout = QVBoxLayout(self)
        form = QFormLayout()

        # Ruta destino
        self.file_edit = QLineEdit()
        browse_btn = QPushButton("Examinar...")
        browse_btn.clicked.connect(self.browse_file)
        hfile = QHBoxLayout()
        hfile.addWidget(self.file_edit)
        hfile.addWidget(browse_btn)
        form.addRow("Archivo destino", hfile)

        # Formato de exportación
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "Script TCL (OpenSees clásico)",
            "Script JSON (OpenSeesPy, experimental)"
        ])
        form.addRow("Formato", self.format_combo)

        # Opciones adicionales
        self.cb_elements = QCheckBox("Exportar sólo geometría (sin propiedades)")
        self.cb_elements.setChecked(False)
        form.addRow(self.cb_elements)

        self.cb_comments = QCheckBox("Agregar comentarios explicativos")
        self.cb_comments.setChecked(True)
        form.addRow(self.cb_comments)

        self.cb_groups = QCheckBox("Exportar grupos/sets si existen")
        self.cb_groups.setChecked(False)
        form.addRow(self.cb_groups)

        self.layout.addLayout(form)

        # Botones aceptar/cancelar
        btns = QHBoxLayout()
        self.accept_btn = QPushButton("Exportar")
        self.accept_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.accept_btn)
        btns.addWidget(self.cancel_btn)
        self.layout.addLayout(btns)

    def browse_file(self):
        ftype = "Archivos TCL (*.tcl);;Archivos JSON (*.json);;Todos los archivos (*)"
        default = self.file_edit.text() or ""
        path, _ = QFileDialog.getSaveFileName(self, "Seleccionar archivo destino", default, ftype)
        if path:
            self.file_edit.setText(path)

    def accept(self):
        filepath = self.file_edit.text().strip()
        if not filepath:
            self.file_edit.setFocus()
            return
        fmt = self.format_combo.currentText()
        only_geom = self.cb_elements.isChecked()
        with_comments = self.cb_comments.isChecked()
        with_groups = self.cb_groups.isChecked()
        # Llama al método de exportación del modelo
        try:
            if fmt.startswith("Script TCL"):
                self.project.export_to_opensees_tcl(
                    filepath,
                    only_geometry=only_geom,
                    comments=with_comments,
                    groups=with_groups
                )
            elif fmt.startswith("Script JSON"):
                self.project.export_to_opensees_json(
                    filepath,
                    only_geometry=only_geom,
                    comments=with_comments,
                    groups=with_groups
                )
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error de exportación", str(e))
            return
        super().accept()