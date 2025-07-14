from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QAbstractItemView, QComboBox, QPushButton, QLabel, QCheckBox, QLineEdit
)
from PySide6.QtCore import Qt

class ObjectSelectorDialog(QDialog):
    """
    Diálogo para selección avanzada de objetos del modelo.
    Permite filtrar por tipo, buscar por propiedades y seleccionar múltiple.
    """
    def __init__(self, project, selection=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Selector de Objetos")
        self.project = project
        self.selection = selection if selection is not None else set()

        self.layout = QVBoxLayout(self)

        # Filtro por tipo de entidad
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo de objeto:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Todos", "Nodos", "Barras", "Shells", "Sólidos",
            "Líneas Aux.", "Arcos Aux.", "Círculos Aux.", "Polilíneas Aux.", "Splines Aux."
        ])
        self.type_combo.currentIndexChanged.connect(self.update_table)
        type_layout.addWidget(self.type_combo)
        self.layout.addLayout(type_layout)

        # Filtro por nombre/ID
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Buscar:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Nombre, ID o propiedad...")
        self.filter_edit.textChanged.connect(self.update_table)
        filter_layout.addWidget(self.filter_edit)
        self.layout.addLayout(filter_layout)

        # Tabla de objetos
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Tipo", "Etiqueta", "Seleccionar"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.layout.addWidget(self.table)

        # Botón de invertir selección y limpiar
        btns_sel = QHBoxLayout()
        self.invert_btn = QPushButton("Invertir selección")
        self.invert_btn.clicked.connect(self.invert_selection)
        btns_sel.addWidget(self.invert_btn)
        self.clear_btn = QPushButton("Limpiar selección")
        self.clear_btn.clicked.connect(self.clear_selection)
        btns_sel.addWidget(self.clear_btn)
        self.layout.addLayout(btns_sel)

        # Botones aceptar/cancelar
        btns = QHBoxLayout()
        self.accept_btn = QPushButton("Aceptar")
        self.accept_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btns.addWidget(self.accept_btn)
        btns.addWidget(self.cancel_btn)
        self.layout.addLayout(btns)

        self.update_table()

    def get_entities_of_type(self, type_name):
        # Devuelve lista de (objeto, tipo, etiqueta) según el tipo requerido
        items = []
        if type_name in ("Todos",):
            items += [(n, "Nodo", f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})") for n in getattr(self.project, "nodes", [])]
            items += [(b, "Barra", f"#{b.id} [{b.n1.id}-{b.n2.id}]") for b in getattr(self.project, "bars", [])]
            items += [(s, "Shell", f"#{s.id} [{'-'.join(str(n.id) for n in s.nodes)}]") for s in getattr(self.project, "shells", [])]
            items += [(s, "Sólido", f"#{s.id}") for s in getattr(self.project, "solids", [])]
            items += [(l, "Línea Aux.", f"#{l.id} [{l.n1.id}-{l.n2.id}]") for l in getattr(self.project, "aux_lines", [])]
            items += [(a, "Arco Aux.", f"#{a.id} [{a.n1.id}-{a.n2.id}-{a.n3.id}]") for a in getattr(self.project, "aux_arcs", [])]
            items += [(c, "Círculo Aux.", f"#{c.id} ({c.center.id}-{c.radius_node.id})") for c in getattr(self.project, "aux_circles", [])]
            items += [(p, "Polilínea Aux.", f"#{p.id} [{'-'.join(str(n.id) for n in p.nodes)}]") for p in getattr(self.project, "aux_polylines", [])]
            items += [(s, "Spline Aux.", f"#{s.id} [{'-'.join(str(n.id) for n in s.nodes)}]") for s in getattr(self.project, "aux_splines", [])]
        else:
            if type_name == "Nodos":
                items += [(n, "Nodo", f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})") for n in getattr(self.project, "nodes", [])]
            elif type_name == "Barras":
                items += [(b, "Barra", f"#{b.id} [{b.n1.id}-{b.n2.id}]") for b in getattr(self.project, "bars", [])]
            elif type_name == "Shells":
                items += [(s, "Shell", f"#{s.id} [{'-'.join(str(n.id) for n in s.nodes)}]") for s in getattr(self.project, "shells", [])]
            elif type_name == "Sólidos":
                items += [(s, "Sólido", f"#{s.id}") for s in getattr(self.project, "solids", [])]
            elif type_name == "Líneas Aux.":
                items += [(l, "Línea Aux.", f"#{l.id} [{l.n1.id}-{l.n2.id}]") for l in getattr(self.project, "aux_lines", [])]
            elif type_name == "Arcos Aux.":
                items += [(a, "Arco Aux.", f"#{a.id} [{a.n1.id}-{a.n2.id}-{a.n3.id}]") for a in getattr(self.project, "aux_arcs", [])]
            elif type_name == "Círculo Aux.":
                items += [(c, "Círculo Aux.", f"#{c.id} ({c.center.id}-{c.radius_node.id})") for c in getattr(self.project, "aux_circles", [])]
            elif type_name == "Polilíneas Aux.":
                items += [(p, "Polilínea Aux.", f"#{p.id} [{'-'.join(str(n.id) for n in p.nodes)}]") for p in getattr(self.project, "aux_polylines", [])]
            elif type_name == "Splines Aux.":
                items += [(s, "Spline Aux.", f"#{s.id} [{'-'.join(str(n.id) for n in s.nodes)}]") for s in getattr(self.project, "aux_splines", [])]
        return items

    def update_table(self):
        type_name = self.type_combo.currentText()
        filter_text = self.filter_edit.text().lower()
        self.table.setRowCount(0)
        objects = self.get_entities_of_type(type_name)
        for obj, typ, label in objects:
            # Filtro por texto
            if filter_text and filter_text not in label.lower() and filter_text not in typ.lower():
                continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(typ))
            self.table.setItem(row, 1, QTableWidgetItem(label))
            # Checkbox seleccionar
            cb = QCheckBox()
            cb.setChecked(obj in self.selection)
            cb.stateChanged.connect(self.make_check_callback(obj))
            self.table.setCellWidget(row, 2, cb)

    def make_check_callback(self, obj):
        def callback(state):
            if state == Qt.Checked:
                self.selection.add(obj)
            else:
                self.selection.discard(obj)
        return callback

    def invert_selection(self):
        objects = self.get_entities_of_type(self.type_combo.currentText())
        for row in range(self.table.rowCount()):
            cb = self.table.cellWidget(row, 2)
            obj = objects[row][0]
            if cb:
                checked = cb.isChecked()
                cb.setChecked(not checked)
                if not checked:
                    self.selection.add(obj)
                else:
                    self.selection.discard(obj)

    def clear_selection(self):
        for row in range(self.table.rowCount()):
            cb = self.table.cellWidget(row, 2)
            if cb and cb.isChecked():
                cb.setChecked(False)
        self.selection.clear()

    def accept(self):
        # La selección ya se actualiza dinámicamente
        super().accept()

    def get_selected_objects(self):
        return list(self.selection)