from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox, QDoubleSpinBox,
    QPushButton, QLabel, QHBoxLayout, QMessageBox, QSpinBox
)
from PySide6.QtCore import Qt

class TransformDialog(QDialog):
    """
    Diálogo para transformaciones geométricas: mover, copiar, rotar, escalar.
    Permite aplicar la transformación a la selección actual de objetos.
    """

    def __init__(self, project, selection=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transformar Objetos")
        self.project = project
        self.selection = selection or []

        self.layout = QVBoxLayout(self)
        form = QFormLayout()

        # Tipo de transformación
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Mover", "Copiar", "Rotar", "Escalar"])
        self.type_combo.currentIndexChanged.connect(self.update_fields_visibility)
        form.addRow("Tipo de transformación", self.type_combo)

        # Campos para mover/copiar: vector
        self.dx_spin = QDoubleSpinBox()
        self.dy_spin = QDoubleSpinBox()
        self.dz_spin = QDoubleSpinBox()
        for spin in (self.dx_spin, self.dy_spin, self.dz_spin):
            spin.setDecimals(4)
            spin.setRange(-1e6, 1e6)
            spin.setValue(0.0)
        form.addRow("ΔX", self.dx_spin)
        form.addRow("ΔY", self.dy_spin)
        form.addRow("ΔZ", self.dz_spin)

        # Para copiar: cantidad de copias
        self.ncopies_spin = QSpinBox()
        self.ncopies_spin.setMinimum(1)
        self.ncopies_spin.setMaximum(100)
        self.ncopies_spin.setValue(1)
        form.addRow("Cantidad de copias", self.ncopies_spin)

        # Para rotar: punto y ángulo
        self.cx_spin = QDoubleSpinBox()
        self.cy_spin = QDoubleSpinBox()
        self.cz_spin = QDoubleSpinBox()
        for spin in (self.cx_spin, self.cy_spin, self.cz_spin):
            spin.setDecimals(4)
            spin.setRange(-1e6, 1e6)
            spin.setValue(0.0)
        self.angle_spin = QDoubleSpinBox()
        self.angle_spin.setDecimals(2)
        self.angle_spin.setRange(-360.0, 360.0)
        self.angle_spin.setValue(0.0)
        form.addRow("Centro X", self.cx_spin)
        form.addRow("Centro Y", self.cy_spin)
        form.addRow("Centro Z", self.cz_spin)
        form.addRow("Ángulo [grados]", self.angle_spin)

        # Para escalar: punto y factor
        self.sx_spin = QDoubleSpinBox()
        self.sy_spin = QDoubleSpinBox()
        self.sz_spin = QDoubleSpinBox()
        for spin in (self.sx_spin, self.sy_spin, self.sz_spin):
            spin.setDecimals(4)
            spin.setRange(0.001, 1000.0)
            spin.setValue(1.0)
        form.addRow("Factor X", self.sx_spin)
        form.addRow("Factor Y", self.sy_spin)
        form.addRow("Factor Z", self.sz_spin)

        self.s_cx_spin = QDoubleSpinBox()
        self.s_cy_spin = QDoubleSpinBox()
        self.s_cz_spin = QDoubleSpinBox()
        for spin in (self.s_cx_spin, self.s_cy_spin, self.s_cz_spin):
            spin.setDecimals(4)
            spin.setRange(-1e6, 1e6)
            spin.setValue(0.0)
        form.addRow("Centro Escalado X", self.s_cx_spin)
        form.addRow("Centro Escalado Y", self.s_cy_spin)
        form.addRow("Centro Escalado Z", self.s_cz_spin)

        self.layout.addLayout(form)
        self.update_fields_visibility()

        # Botones aceptar/cancelar
        btns = QHBoxLayout()
        self.accept_btn = QPushButton("Aceptar")
        self.accept_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.accept_btn)
        btns.addWidget(self.cancel_btn)
        self.layout.addLayout(btns)

    def update_fields_visibility(self):
        t = self.type_combo.currentText()
        is_move = t == "Mover"
        is_copy = t == "Copiar"
        is_rotate = t == "Rotar"
        is_scale = t == "Escalar"
        # Mover y copiar usan ΔX, ΔY, ΔZ
        self.dx_spin.parentWidget().setVisible(is_move or is_copy)
        self.dy_spin.parentWidget().setVisible(is_move or is_copy)
        self.dz_spin.parentWidget().setVisible(is_move or is_copy)
        self.ncopies_spin.parentWidget().setVisible(is_copy)
        # Rotar
        self.cx_spin.parentWidget().setVisible(is_rotate)
        self.cy_spin.parentWidget().setVisible(is_rotate)
        self.cz_spin.parentWidget().setVisible(is_rotate)
        self.angle_spin.parentWidget().setVisible(is_rotate)
        # Escalar
        self.sx_spin.parentWidget().setVisible(is_scale)
        self.sy_spin.parentWidget().setVisible(is_scale)
        self.sz_spin.parentWidget().setVisible(is_scale)
        self.s_cx_spin.parentWidget().setVisible(is_scale)
        self.s_cy_spin.parentWidget().setVisible(is_scale)
        self.s_cz_spin.parentWidget().setVisible(is_scale)

    def accept(self):
        t = self.type_combo.currentText()
        if not self.selection:
            QMessageBox.warning(self, "Error", "No hay objetos seleccionados.")
            return
        if t == "Mover":
            dx, dy, dz = self.dx_spin.value(), self.dy_spin.value(), self.dz_spin.value()
            self.project.move_objects(self.selection, dx, dy, dz)
        elif t == "Copiar":
            dx, dy, dz = self.dx_spin.value(), self.dy_spin.value(), self.dz_spin.value()
            n = self.ncopies_spin.value()
            self.project.copy_objects(self.selection, dx, dy, dz, n)
        elif t == "Rotar":
            cx, cy, cz = self.cx_spin.value(), self.cy_spin.value(), self.cz_spin.value()
            angle = self.angle_spin.value()
            self.project.rotate_objects(self.selection, cx, cy, cz, angle)
        elif t == "Escalar":
            sx, sy, sz = self.sx_spin.value(), self.sy_spin.value(), self.sz_spin.value()
            cx, cy, cz = self.s_cx_spin.value(), self.s_cy_spin.value(), self.s_cz_spin.value()
            self.project.scale_objects(self.selection, sx, sy, sz, cx, cy, cz)
        super().accept()