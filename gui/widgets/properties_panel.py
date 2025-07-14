from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QPushButton, QHBoxLayout, QGroupBox, QCheckBox, QMessageBox, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal

class PropertiesPanel(QWidget):
    property_changed = Signal(object, str, object)  # (objeto, nombre_prop, valor_nuevo)

    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.current_object = None
        self.group_checkboxes = {}
        self.set_checkboxes = {}

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.title_label = QLabel("Propiedades")
        self.layout.addWidget(self.title_label)
        self.form = QFormLayout()
        self.layout.addLayout(self.form)
        self.editors = {}

        # Mensaje de error
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red")
        self.layout.addWidget(self.error_label)
        self.error_label.setVisible(False)

        # Botón para aplicar cambios
        self.save_btn = QPushButton("Guardar cambios")
        self.save_btn.clicked.connect(self.save_properties)
        self.layout.addWidget(self.save_btn)
        self.save_btn.setVisible(False)

        # Edición avanzada de listas (nodos)
        self.node_list_btn = QPushButton("Editar lista de nodos")
        self.node_list_btn.clicked.connect(self.open_node_list_editor)
        self.layout.addWidget(self.node_list_btn)
        self.node_list_btn.setVisible(False)

    def show_properties(self, obj):
        self.current_object = obj
        self.error_label.setVisible(False)
        while self.form.rowCount():
            self.form.removeRow(0)
        self.editors.clear()
        self.group_checkboxes.clear()
        self.set_checkboxes.clear()
        self.node_list_btn.setVisible(False)

        if obj is None:
            self.title_label.setText("Propiedades")
            self.save_btn.setVisible(False)
            return

        obj_type = type(obj).__name__
        self.title_label.setText(f"Propiedades: {obj_type}")

        # ID (solo lectura)
        if hasattr(obj, "id"):
            le_id = QLineEdit(str(obj.id))
            le_id.setReadOnly(True)
            self.form.addRow("ID", le_id)
            self.editors["id"] = le_id

        # Nombre
        if hasattr(obj, "name"):
            le_name = QLineEdit(str(getattr(obj, "name", "")))
            self.form.addRow("Nombre", le_name)
            self.editors["name"] = le_name

        # Coordenadas
        for coord in ("x", "y", "z"):
            if hasattr(obj, coord):
                spin = QDoubleSpinBox()
                spin.setDecimals(6)
                spin.setRange(-1e8, 1e8)
                spin.setValue(getattr(obj, coord))
                self.form.addRow(coord.upper(), spin)
                self.editors[coord] = spin

        # Shells/sólidos: nodos (editable como lista de IDs)
        if hasattr(obj, "nodes") and isinstance(getattr(obj, "nodes", None), (list, tuple)):
            nodes_str = ", ".join(str(getattr(n, "id", n)) for n in obj.nodes)
            le_nodes = QLineEdit(nodes_str)
            self.form.addRow("Nodos (IDs separados por coma)", le_nodes)
            self.editors["nodes"] = le_nodes
            self.node_list_btn.setVisible(True)

        # Material y sección (combo si posible)
        if hasattr(obj, "material"):
            mat_val = getattr(obj, "material", "")
            values = self.get_materials()
            if values:
                combo = QComboBox()
                combo.addItems(values)
                idx = combo.findText(str(mat_val))
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                self.form.addRow("Material", combo)
                self.editors["material"] = combo
            else:
                le_mat = QLineEdit(str(mat_val))
                self.form.addRow("Material", le_mat)
                self.editors["material"] = le_mat
        if hasattr(obj, "section"):
            sec_val = getattr(obj, "section", "")
            values = self.get_sections()
            if values:
                combo = QComboBox()
                combo.addItems(values)
                idx = combo.findText(str(sec_val))
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                self.form.addRow("Sección", combo)
                self.editors["section"] = combo
            else:
                le_sec = QLineEdit(str(sec_val))
                self.form.addRow("Sección", le_sec)
                self.editors["section"] = le_sec

        # Apoyos/restricciones (checkboxes)
        if hasattr(obj, "restraints") and isinstance(obj.restraints, (list, tuple)):
            group = QGroupBox("Restricciones")
            g_layout = QHBoxLayout()
            group.setLayout(g_layout)
            self.editors["restraints"] = []
            for i, label in enumerate(["X", "Y", "Z", "RX", "RY", "RZ"]):
                cb = QCheckBox(label)
                cb.setChecked(bool(getattr(obj, "restraints", [0]*6)[i]))
                g_layout.addWidget(cb)
                self.editors["restraints"].append(cb)
            self.form.addRow(group)

        # Grupos
        groups = self.get_groups()
        if groups:
            group_box = QGroupBox("Grupos")
            g_layout = QHBoxLayout()
            group_box.setLayout(g_layout)
            for g in groups:
                cb = QCheckBox(str(getattr(g, "name", g)))
                es_miembro = hasattr(g, "members") and obj in getattr(g, "members")
                cb.setChecked(es_miembro)
                g_layout.addWidget(cb)
                self.group_checkboxes[g] = cb
            self.form.addRow(group_box)

        # Sets
        sets = self.get_sets()
        if sets:
            set_box = QGroupBox("Sets")
            s_layout = QHBoxLayout()
            set_box.setLayout(s_layout)
            for s in sets:
                cb = QCheckBox(str(getattr(s, "name", s)))
                es_miembro = hasattr(s, "members") and obj in getattr(s, "members")
                cb.setChecked(es_miembro)
                s_layout.addWidget(cb)
                self.set_checkboxes[s] = cb
            self.form.addRow(set_box)

        self.save_btn.setVisible(bool(self.editors) or bool(self.group_checkboxes) or bool(self.set_checkboxes))

    def get_materials(self):
        project = getattr(self.canvas, "project", None)
        materials = getattr(project, "materials", []) if project else []
        return [str(m.name) for m in materials] if materials else []

    def get_sections(self):
        project = getattr(self.canvas, "project", None)
        sections = getattr(project, "sections", []) if project else []
        return [str(s.name) for s in sections] if sections else []

    def get_groups(self):
        project = getattr(self.canvas, "project", None)
        return getattr(project, "groups", []) if project else []

    def get_sets(self):
        project = getattr(self.canvas, "project", None)
        return getattr(project, "sets", []) if project else []

    def validate(self, data):
        errors = []
        # Unicidad de nombre
        if "name" in data and data["name"]:
            project = getattr(self.canvas, "project", None)
            if project:
                for entity_list in [getattr(project, "nodes", []), getattr(project, "bars", []),
                                    getattr(project, "shells", []), getattr(project, "solids", [])]:
                    for e in entity_list:
                        if e is not self.current_object and getattr(e, "name", None) == data["name"]:
                            errors.append("El nombre ya existe en otro objeto.")
                            break
        # Rangos de coordenadas
        for coord in ("x", "y", "z"):
            if coord in data:
                if not (-1e8 <= data[coord] <= 1e8):
                    errors.append(f"Coordenada {coord.upper()} fuera de rango permitido.")
        # Validación de nodos (si existen)
        if "nodes" in data and isinstance(data["nodes"], list):
            project = getattr(self.canvas, "project", None)
            all_node_ids = set(n.id for n in getattr(project, "nodes", []))
            for nid in data["nodes"]:
                if nid not in all_node_ids:
                    errors.append(f"Nodo con ID {nid} no existe.")
        return errors

    def save_properties(self):
        obj = self.current_object
        if obj is None:
            return
        updated = False
        data = {}

        for name, editor in self.editors.items():
            if isinstance(editor, QLineEdit):
                value = editor.text()
                try:
                    if hasattr(obj, name) and isinstance(getattr(obj, name), int):
                        value = int(value)
                    elif hasattr(obj, name) and isinstance(getattr(obj, name), float):
                        value = float(value)
                    elif name == "nodes":  # lista de IDs
                        value = [int(i.strip()) for i in value.split(",") if i.strip()]
                except Exception:
                    pass
            elif isinstance(editor, QDoubleSpinBox):
                value = editor.value()
            elif isinstance(editor, QSpinBox):
                value = editor.value()
            elif isinstance(editor, QComboBox):
                value = editor.currentText()
            elif isinstance(editor, list) and name == "restraints":
                value = [int(cb.isChecked()) for cb in editor]
            else:
                value = editor.text() if hasattr(editor, "text") else None
            data[name] = value

        errors = self.validate(data)
        if errors:
            self.error_label.setText("\n".join(errors))
            self.error_label.setVisible(True)
            return
        else:
            self.error_label.setVisible(False)

        for name, value in data.items():
            if hasattr(obj, name):
                if getattr(obj, name) != value:
                    setattr(obj, name, value)
                    updated = True
                    self.property_changed.emit(obj, name, value)

        # Actualizar pertenencia a grupos
        for g, cb in self.group_checkboxes.items():
            was_member = hasattr(g, "members") and obj in getattr(g, "members")
            now_member = cb.isChecked()
            if now_member and not was_member:
                g.members.append(obj)
                updated = True
            elif not now_member and was_member:
                g.members.remove(obj)
                updated = True

        # Actualizar pertenencia a sets
        for s, cb in self.set_checkboxes.items():
            was_member = hasattr(s, "members") and obj in getattr(s, "members")
            now_member = cb.isChecked()
            if now_member and not was_member:
                s.members.append(obj)
                updated = True
            elif not now_member and was_member:
                s.members.remove(obj)
                updated = True

        if updated and hasattr(self.canvas, "update"):
            self.canvas.update()

    def open_node_list_editor(self):
        """
        Diálogo avanzado para editar la lista de nodos de un Shell/Solid.
        """
        obj = self.current_object
        if not (obj and hasattr(obj, "nodes")):
            return

        dlg = NodeListEditorDialog(self)
        # Pasa lista de IDs actuales y lista de nodos posibles
        project = getattr(self.canvas, "project", None)
        all_nodes = getattr(project, "nodes", []) if project else []
        current_ids = [getattr(n, "id", n) for n in getattr(obj, "nodes", [])]
        dlg.populate(all_nodes, current_ids)

        if dlg.exec():
            selected_ids = dlg.get_selected_ids()
            # Validación: no se permite lista vacía
            if not selected_ids:
                QMessageBox.warning(self, "Edición de nodos", "Debe seleccionar al menos un nodo.")
                return
            # Actualiza en panel y en objeto
            self.editors["nodes"].setText(", ".join(str(i) for i in selected_ids))
            self.save_properties()

class NodeListEditorDialog(QMessageBox):
    """
    Diálogo modal para edición avanzada de la lista de nodos.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar nodos")
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.list_widget = QListWidget()
        self.layout().addWidget(self.list_widget, 0, 1, 1, 1)
        self.resize(400, 400)

    def populate(self, all_nodes, selected_ids):
        self.list_widget.clear()
        for n in all_nodes:
            nid = getattr(n, "id", n)
            item = QListWidgetItem(f"ID {nid}")
            item.setData(Qt.UserRole, nid)
            item.setCheckState(Qt.Checked if nid in selected_ids else Qt.Unchecked)
            self.list_widget.addItem(item)

    def get_selected_ids(self):
        return [self.list_widget.item(i).data(Qt.UserRole)
                for i in range(self.list_widget.count())
                if self.list_widget.item(i).checkState() == Qt.Checked]