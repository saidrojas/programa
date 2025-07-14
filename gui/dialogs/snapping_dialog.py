from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QCheckBox, QPushButton, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt

class SnappingDialog(QDialog):
    """
    Diálogo para configuración de snapping (ajuste) a entidades geométricas.
    Permite seleccionar a qué entidades o puntos se activa el snap.
    """

    def __init__(self, project, snapping_settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Snapping")
        self.project = project
        # snapping_settings: dict con flags de snaps activos
        self.snapping_settings = snapping_settings or {}

        self.layout = QVBoxLayout(self)
        form = QFormLayout()

        # Opciones de snapping más comunes en CAD/CAE
        self.cb_node = QCheckBox("Nodos")
        self.cb_node.setChecked(self.snapping_settings.get("node", True))
        form.addRow(self.cb_node)

        self.cb_midpoint = QCheckBox("Punto medio de barra")
        self.cb_midpoint.setChecked(self.snapping_settings.get("midpoint", True))
        form.addRow(self.cb_midpoint)

        self.cb_bar = QCheckBox("Sobre barra")
        self.cb_bar.setChecked(self.snapping_settings.get("bar", False))
        form.addRow(self.cb_bar)

        self.cb_aux = QCheckBox("Sobre auxiliar (línea/arco/círculo)")
        self.cb_aux.setChecked(self.snapping_settings.get("aux", False))
        form.addRow(self.cb_aux)

        self.cb_intersection = QCheckBox("Intersección de entidades")
        self.cb_intersection.setChecked(self.snapping_settings.get("intersection", False))
        form.addRow(self.cb_intersection)

        self.cb_perpendicular = QCheckBox("Perpendicular")
        self.cb_perpendicular.setChecked(self.snapping_settings.get("perpendicular", False))
        form.addRow(self.cb_perpendicular)

        self.cb_tangent = QCheckBox("Tangente (arco/círculo)")
        self.cb_tangent.setChecked(self.snapping_settings.get("tangent", False))
        form.addRow(self.cb_tangent)

        self.cb_center = QCheckBox("Centro (círculo/arco)")
        self.cb_center.setChecked(self.snapping_settings.get("center", False))
        form.addRow(self.cb_center)

        self.cb_quadrant = QCheckBox("Cuadrante (círculo/arco)")
        self.cb_quadrant.setChecked(self.snapping_settings.get("quadrant", False))
        form.addRow(self.cb_quadrant)

        self.cb_shell = QCheckBox("Sobre shell")
        self.cb_shell.setChecked(self.snapping_settings.get("shell", False))
        form.addRow(self.cb_shell)

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
        # Actualiza el diccionario de configuración de snaps
        self.snapping_settings["node"] = self.cb_node.isChecked()
        self.snapping_settings["midpoint"] = self.cb_midpoint.isChecked()
        self.snapping_settings["bar"] = self.cb_bar.isChecked()
        self.snapping_settings["aux"] = self.cb_aux.isChecked()
        self.snapping_settings["intersection"] = self.cb_intersection.isChecked()
        self.snapping_settings["perpendicular"] = self.cb_perpendicular.isChecked()
        self.snapping_settings["tangent"] = self.cb_tangent.isChecked()
        self.snapping_settings["center"] = self.cb_center.isChecked()
        self.snapping_settings["quadrant"] = self.cb_quadrant.isChecked()
        self.snapping_settings["shell"] = self.cb_shell.isChecked()
        super().accept()

    def get_snapping_settings(self):
        return self.snapping_settings