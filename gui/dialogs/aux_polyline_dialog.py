from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QListWidget, QPushButton,
    QHBoxLayout, QMessageBox, QLabel, QComboBox, QWidget
)
from PySide6.QtCore import Qt

class AuxPolylineDialog(QDialog):
    def __init__(self, project, aux_polyline=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Polilínea Auxiliar")
        self.project = project
        self.aux_polyline = aux_polyline  # Puede ser None para nueva polilínea

        self.layout = QVBoxLayout(self)
        form = QFormLayout()

        # Lista de nodos
        self.nodes_list = QListWidget()
        if aux_polyline is not None:
            for n in aux_polyline.nodes:
                self.nodes_list.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})")
        form.addRow(QLabel("Nodos (en orden):"), self.nodes_list)

        # Agregar/quitar nodos
        btns_nodo = QHBoxLayout()
        self.node_combo = QComboBox()
        for n in self.project.nodes:
            self.node_combo.addItem(f"#{n.id} ({n.x:.2f},{n.y:.2f},{n.z:.2f})", n.id)
        btns_nodo.addWidget(self.node_combo)
        self.add_node_btn = QPushButton("Agregar nodo")
        self.add_node_btn.clicked.connect(self.add_node)
        btns_nodo.addWidget(self.add_node_btn)
        self.del_node_btn = QPushButton("Quitar nodo")
        self.del_node_btn.clicked.connect(self.del_node)
        btns_nodo.addWidget(self.del_node_btn)
        form.addRow(btns_nodo)

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

    def add_node(self):
        node_id = self.node_combo.currentData()
        node = next((n for n in self.project.nodes if n.id == node_id), None)
        if not node:
            return
        # Evita repetir nodos
        for i in range(self.nodes_list.count()):
            if self.nodes_list.item(i).text().startswith(f"#{node.id} "):
                return
        self.nodes_list.addItem(f"#{node.id} ({node.x:.2f},{node.y:.2f},{node.z:.2f})")

    def del_node(self):
        idx = self.nodes_list.currentRow()
        if idx >= 0:
            self.nodes_list.takeItem(idx)

    def accept(self):
        node_ids = []
        for i in range(self.nodes_list.count()):
            txt = self.nodes_list.item(i).text()
            nid = int(txt.split()[0][1:])
            node_ids.append(nid)
        if len(node_ids) < 2:
            QMessageBox.warning(self, "Error", "Debes agregar al menos dos nodos.")
            return
        nodes = [n for n in self.project.nodes if n.id in node_ids]
        if len(nodes) != len(node_ids):
            QMessageBox.warning(self, "Error", "Algún nodo no es válido.")
            return
        if self.aux_polyline is not None:
            self.aux_polyline.nodes = nodes
        else:
            self.aux_polyline = self.project.add_aux_polyline(nodes)
        super().accept()

    def get_aux_polyline(self):
        return self.aux_polyline