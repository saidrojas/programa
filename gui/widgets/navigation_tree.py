from PySide6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
class NavigationTree(QTreeWidget):
    """
    Árbol de navegación del modelo para explorar y seleccionar entidades.
    Permite selección múltiple y acciones de contexto (eliminar, propiedades, etc).
    """
    object_selected = Signal(object)

    def __init__(self, canvas, properties_panel, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.properties_panel = properties_panel
        self.setColumnCount(1)
        self.setHeaderLabels(["Modelo"])
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.itemClicked.connect(self.on_item_clicked)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)
        self.refresh()

    def refresh(self):
        """
        Reconstruye el árbol a partir del contenido actual del modelo.
        """
        self.clear()
        project = getattr(self.canvas, "project", None)
        if project is None:
            return

        # Categorías principales
        categorias = [
            ("Nodos", getattr(project, "nodes", [])),
            ("Barras", getattr(project, "bars", [])),
            ("Shells", getattr(project, "shells", [])),
            ("Sólidos", getattr(project, "solids", [])),
            ("Líneas Aux.", getattr(project, "aux_lines", [])),
            ("Arcos Aux.", getattr(project, "aux_arcs", [])),
            ("Círculos Aux.", getattr(project, "aux_circles", [])),
            ("Polilíneas Aux.", getattr(project, "aux_polylines", [])),
            ("Splines Aux.", getattr(project, "aux_splines", [])),
        ]

        for cat_name, objs in categorias:
            cat_item = QTreeWidgetItem(self, [cat_name])
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsSelectable)
            for obj in objs:
                label = self.get_object_label(obj)
                obj_item = QTreeWidgetItem(cat_item, [label])
                obj_item.setData(0, Qt.UserRole, obj)
        self.expandAll()

    def get_object_label(self, obj):
        """
        Devuelve una etiqueta amigable para el objeto.
        """
        if hasattr(obj, "id"):
            if hasattr(obj, "x") and hasattr(obj, "y") and hasattr(obj, "z"):
                return f"Nodo #{obj.id} ({obj.x:.2f},{obj.y:.2f},{obj.z:.2f})"
            elif hasattr(obj, "n1") and hasattr(obj, "n2"):
                return f"Barra #{obj.id} [{obj.n1.id}-{obj.n2.id}]"
            elif hasattr(obj, "nodes"):
                return f"Shell #{obj.id} [{'-'.join(str(n.id) for n in obj.nodes)}]"
            else:
                return f"Objeto #{obj.id}"
        return str(obj)

    def on_item_clicked(self, item, column):
        obj = item.data(0, Qt.UserRole)
        if obj is not None:
            self.properties_panel.show_properties(obj)
            self.object_selected.emit(obj)
            if hasattr(self.canvas, "set_selected"):
                self.canvas.set_selected([obj])

    def open_context_menu(self, pos):
        item = self.itemAt(pos)
        if item is None:
            return

        obj = item.data(0, Qt.UserRole)
        if obj is None:
            return

        menu = QMenu(self)
        act_prop = QAction("Propiedades", self)
        act_prop.triggered.connect(lambda: self.properties_panel.show_properties(obj))
        menu.addAction(act_prop)

        act_elim = QAction("Eliminar", self)
        act_elim.triggered.connect(lambda: self.delete_object(obj))
        menu.addAction(act_elim)

        menu.exec(self.viewport().mapToGlobal(pos))

    def delete_object(self, obj):
        # Lógica de borrado: delega en el modelo/canvas
        if hasattr(self.canvas, "delete_object"):
            ok = self.canvas.delete_object(obj)
            if ok:
                self.refresh()
            else:
                QMessageBox.warning(self, "Eliminar", "No fue posible eliminar el objeto.")
        else:
            QMessageBox.warning(self, "Eliminar", "La acción no está implementada.")