from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QToolBar, QMessageBox, QSizePolicy,
    QSplitter, QFileDialog, QMenuBar, QMenu
)
from PySide6.QtGui import QIcon, QKeySequence
from PySide6.QtCore import QSize, Qt

from core.undo_redo_manager import UndoRedoManager
from gui.dialogs.export_opensees_dialog import ExportOpenSeesDialog
from gui.dialogs.snapping_dialog import SnappingDialog
from gui.dialogs.object_selector_dialog import ObjectSelectorDialog
from gui.dialogs.transform_dialog import TransformDialog
from gui.dialogs.aux_line_dialog import AuxLineDialog
from gui.dialogs.aux_arc_dialog import AuxArcDialog
from gui.dialogs.aux_circle_dialog import AuxCircleDialog
from gui.dialogs.aux_polyline_dialog import AuxPolylineDialog
from gui.dialogs.aux_spline_dialog import AuxSplineDialog
from gui.dialogs.extrude_dialog import ExtrudeDialog

from gui import canvas
from gui.widgets.properties_panel import PropertiesPanel
from gui.widgets.navigation_tree import NavigationTree

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected = set()
        self.setWindowTitle("Struktix")
        self.setWindowIcon(QIcon("icons/struktix.png"))
        self.setGeometry(100, 100, 2000, 900)

        # --- Instancias principales ---
        self.canvas = canvas(self)
        self.properties_panel = PropertiesPanel(self.canvas)
        self.tree = NavigationTree(self.canvas, self.properties_panel, parent=self)

        # --- Undo/Redo Manager ---
        self.undo_manager = UndoRedoManager()

        # --- Panel izquierdo: árbol + propiedades ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.tree.setMinimumWidth(200)
        left_widget.setMinimumWidth(80)
        left_layout.addWidget(self.tree, stretch=1)
        left_layout.addWidget(self.properties_panel, stretch=0)
        left_widget.setLayout(left_layout)

        # --- Panel derecho: barra de herramientas + canvas ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self.canvas)
        right_widget.setLayout(right_layout)

        # --- Splitter central ---
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        # --- QToolBar ---
        toolbar = QToolBar("Herramientas")
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        # Acciones principales
        action_undo = QAction(QIcon("icons/deshacer.png"), "Deshacer", self)
        action_undo.setToolTip("Deshacer")
        action_undo.setShortcut(QKeySequence.Undo)
        action_undo.triggered.connect(self.on_undo)
        toolbar.addAction(action_undo)

        action_redo = QAction(QIcon("icons/rehacer.png"), "Rehacer", self)
        action_redo.setToolTip("Rehacer")
        action_redo.setShortcut(QKeySequence.Redo)
        action_redo.triggered.connect(self.on_redo)
        toolbar.addAction(action_redo)
        toolbar.addSeparator()

        action_nodo = QAction(QIcon("icons/nodo.png"), "Crear nodo", self)
        action_nodo.setToolTip("Crear nodo")
        action_nodo.triggered.connect(lambda: self.set_mode('nodo'))
        toolbar.addAction(action_nodo)

        action_barra = QAction(QIcon("icons/barra1.png"), "Crear barra", self)
        action_barra.setToolTip("Crear barra")
        action_barra.triggered.connect(lambda: self.set_mode('barra'))
        toolbar.addAction(action_barra)

        action_shell = QAction(QIcon("icons/shell1.png"), "Crear Placa", self)
        action_shell.setToolTip("Crear Placa")
        action_shell.triggered.connect(lambda: self.set_mode('shell'))
        toolbar.addAction(action_shell)
        toolbar.addSeparator()

        action_extruir_nodo = QAction(QIcon("icons/extruir_nodo_barra1.png"), "Extruir Nodo→Línea", self)
        action_extruir_nodo.setToolTip("Extruir Nodo→Línea")
        action_extruir_nodo.triggered.connect(lambda: self.extruir_con_dialogo('nodo'))
        toolbar.addAction(action_extruir_nodo)

        action_extruir_barra = QAction(QIcon("icons/extruir_barra_shell1.png"), "Extruir Línea→Shell", self)
        action_extruir_barra.setToolTip("Extruir Línea→Shell")
        action_extruir_barra.triggered.connect(lambda: self.extruir_con_dialogo('barra'))
        toolbar.addAction(action_extruir_barra)

        action_extruir_shell = QAction(QIcon("icons/extruir_shell_solid1.png"), "Extruir Shell→Sólido", self)
        action_extruir_shell.setToolTip("Extruir Shell→Sólido")
        action_extruir_shell.triggered.connect(lambda: self.extruir_con_dialogo('shell'))
        toolbar.addAction(action_extruir_shell)
        toolbar.addSeparator()

        action_dividir = QAction(QIcon("icons/dividir_barra1.png"), "Dividir barra en intersección", self)
        action_dividir.setToolTip("Dividir barra en intersección")
        action_dividir.triggered.connect(self.dividir_barras_seleccionadas)
        toolbar.addAction(action_dividir)

        action_dividir_barra_shell = QAction(QIcon("icons/dividir_barra_shell1.png"), "Dividir barra con shell", self)
        action_dividir_barra_shell.setToolTip("Dividir barra con shell")
        action_dividir_barra_shell.triggered.connect(self.dividir_barra_con_shell)
        toolbar.addAction(action_dividir_barra_shell)

        action_interseccion_shells = QAction(QIcon("icons/dividir_shell_shell1.png"), "Nodos intersección shells", self)
        action_interseccion_shells.setToolTip("Nodos intersección shells")
        action_interseccion_shells.triggered.connect(self.crear_nodos_interseccion_shells)
        toolbar.addAction(action_interseccion_shells)
        toolbar.addSeparator()

        action_apoyo = QAction(QIcon("icons/apoyo1.png"), "Crear Apoyo", self)
        action_apoyo.setToolTip("Crear Apoyo")
        action_apoyo.triggered.connect(self.mostrar_dialogo_asignar_apoyo)
        toolbar.addAction(action_apoyo)

        action_apoyo_winkler = QAction(QIcon("icons/apoyo_shell1.png"), "Apoyo Placa", self)
        action_apoyo_winkler.setToolTip("Apoyo Placa")
        action_apoyo_winkler.triggered.connect(self.mostrar_dialogo_asignar_apoyo_winkler)
        toolbar.addAction(action_apoyo_winkler)
        toolbar.addSeparator()

        action_carga = QAction(QIcon("icons/carga_nodal1.png"), "Crear Nodal", self)
        action_carga.setToolTip("Crear Nodal")
        action_carga.triggered.connect(self.mostrar_dialogo_asignar_carga_nodal)
        toolbar.addAction(action_carga)

        action_carga_dist = QAction(QIcon("icons/carga_barra1.png"), "Crear Distribuida", self)
        action_carga_dist.setToolTip("Crear Distribuida")
        action_carga_dist.triggered.connect(self.mostrar_dialogo_asignar_carga_distribuida)
        toolbar.addAction(action_carga_dist)

        action_carga_shell = QAction(QIcon("icons/carga_shell1.png"), "Crear sobre placa", self)
        action_carga_shell.setToolTip("Crear sobre placa")
        action_carga_shell.triggered.connect(self.mostrar_dialogo_asignar_carga_shell)
        toolbar.addAction(action_carga_shell)
        toolbar.addSeparator()

        action_materiales = QAction(QIcon("icons/materiales.png"), "Materiales", self)
        action_materiales.setToolTip("Materiales")
        action_materiales.triggered.connect(self.mostrar_dialogo_materiales)
        toolbar.addAction(action_materiales)

        action_linea_aux = QAction(QIcon("icons/barra_aux.png"), "Crear Línea Auxiliar", self)
        action_linea_aux.setToolTip("Crear Línea Auxiliar")
        action_linea_aux.triggered.connect(self.crear_linea_aux_con_dialogo)
        toolbar.addAction(action_linea_aux)

        action_arco_aux = QAction(QIcon("icons/arco_aux.png"), "Crear Arco Auxiliar", self)
        action_arco_aux.setToolTip("Crear Arco Auxiliar")
        action_arco_aux.triggered.connect(self.crear_arco_aux_con_dialogo)
        toolbar.addAction(action_arco_aux)

        action_circulo_aux = QAction(QIcon("icons/circulo_aux.png"), "Crear Círculo Auxiliar", self)
        action_circulo_aux.setToolTip("Crear Círculo Auxiliar")
        action_circulo_aux.triggered.connect(self.crear_circulo_aux_con_dialogo)
        toolbar.addAction(action_circulo_aux)

        # --- Menú Bar y menús adicionales ---
        menubar = self.menuBar()
        herramientas_menu = menubar.addMenu("Herramientas Avanzadas")
        snapping_action = QAction("Snapping...", self)
        snapping_action.triggered.connect(self.open_snapping_dialog)
        herramientas_menu.addAction(snapping_action)

        selector_action = QAction("Selector de objetos...", self)
        selector_action.triggered.connect(self.open_selector_dialog)
        herramientas_menu.addAction(selector_action)

        transformar_action = QAction("Transformar selección...", self)
        transformar_action.triggered.connect(self.open_transform_dialog)
        herramientas_menu.addAction(transformar_action)

        exportar_action = QAction("Exportar a OpenSees...", self)
        exportar_action.triggered.connect(self.open_export_opensees_dialog)
        herramientas_menu.addAction(exportar_action)

    # --- Métodos de integración Undo/Redo y diálogos avanzados ---

    def on_undo(self):
        if self.undo_manager.can_undo():
            self.undo_manager.undo()
            self.canvas.update()
        else:
            QMessageBox.information(self, "Deshacer", "No hay acciones para deshacer.")

    def on_redo(self):
        if self.undo_manager.can_redo():
            self.undo_manager.redo()
            self.canvas.update()
        else:
            QMessageBox.information(self, "Rehacer", "No hay acciones para rehacer.")

    def open_snapping_dialog(self):
        dlg = SnappingDialog(self.canvas.project, getattr(self, "snapping_settings", {}), self)
        if dlg.exec():
            self.snapping_settings = dlg.get_snapping_settings()
            # Si tu canvas soporta configuración de snaps:
            if hasattr(self.canvas, "set_snapping_settings"):
                self.canvas.set_snapping_settings(self.snapping_settings)

    def open_selector_dialog(self):
        dlg = ObjectSelectorDialog(self.canvas.project, set(self.selected), self)
        if dlg.exec():
            self.selected = dlg.get_selected_objects()
            if hasattr(self.canvas, "set_selected"):
                self.canvas.set_selected(self.selected)

    def open_transform_dialog(self):
        if not self.selected:
            QMessageBox.warning(self, "Transformar", "Primero selecciona objetos.")
            return
        dlg = TransformDialog(self.canvas.project, list(self.selected), self)
        if dlg.exec():
            self.canvas.update()

    def open_export_opensees_dialog(self):
        dlg = ExportOpenSeesDialog(self.canvas.project, self)
        if dlg.exec():
            QMessageBox.information(self, "Exportación", "Exportación completada con éxito.")

    # --- Métodos de barra de herramientas, integrando tus diálogos clásicos y nuevos ---
    def set_mode(self, modo):
        if hasattr(self.canvas, "set_mode"):
            self.canvas.set_mode(modo)

    def extruir_con_dialogo(self, tipo):
        dlg = ExtrudeDialog(self.canvas.project, self)
        if dlg.exec():
            self.canvas.update()

    def dividir_barras_seleccionadas(self):
        if hasattr(self.canvas, "dividir_barras_seleccionadas"):
            self.canvas.dividir_barras_seleccionadas()

    def dividir_barra_con_shell(self):
        if hasattr(self.canvas, "dividir_barra_con_shell"):
            self.canvas.dividir_barra_con_shell()

    def crear_nodos_interseccion_shells(self):
        if hasattr(self.canvas, "crear_nodos_interseccion_shells"):
            self.canvas.crear_nodos_interseccion_shells()

    def mostrar_dialogo_asignar_apoyo(self):
        if hasattr(self.canvas, "mostrar_dialogo_asignar_apoyo"):
            self.canvas.mostrar_dialogo_asignar_apoyo()

    def mostrar_dialogo_asignar_apoyo_winkler(self):
        if hasattr(self.canvas, "mostrar_dialogo_asignar_apoyo_winkler"):
            self.canvas.mostrar_dialogo_asignar_apoyo_winkler()

    def mostrar_dialogo_asignar_carga_nodal(self):
        if hasattr(self.canvas, "mostrar_dialogo_asignar_carga_nodal"):
            self.canvas.mostrar_dialogo_asignar_carga_nodal()

    def mostrar_dialogo_asignar_carga_distribuida(self):
        if hasattr(self.canvas, "mostrar_dialogo_asignar_carga_distribuida"):
            self.canvas.mostrar_dialogo_asignar_carga_distribuida()

    def mostrar_dialogo_asignar_carga_shell(self):
        if hasattr(self.canvas, "mostrar_dialogo_asignar_carga_shell"):
            self.canvas.mostrar_dialogo_asignar_carga_shell()

    def mostrar_dialogo_materiales(self):
        if hasattr(self.canvas, "mostrar_dialogo_materiales"):
            self.canvas.mostrar_dialogo_materiales()

    def crear_linea_aux_con_dialogo(self):
        dlg = AuxLineDialog(self.canvas.project, parent=self)
        if dlg.exec():
            self.canvas.update()

    def crear_arco_aux_con_dialogo(self):
        dlg = AuxArcDialog(self.canvas.project, parent=self)
        if dlg.exec():
            self.canvas.update()

    def crear_circulo_aux_con_dialogo(self):
        dlg = AuxCircleDialog(self.canvas.project, parent=self)
        if dlg.exec():
            self.canvas.update()

    # --- Integración de otros diálogos auxiliares si los tienes ---
    def crear_polilinea_aux_con_dialogo(self):
        dlg = AuxPolylineDialog(self.canvas.project, parent=self)
        if dlg.exec():
            self.canvas.update()

    def crear_spline_aux_con_dialogo(self):
        dlg = AuxSplineDialog(self.canvas.project, parent=self)
        if dlg.exec():
            self.canvas.update()

    # --- Manejo de cierre de la ventana ---
    def closeEvent(self, event):
        # Si tienes control de cambios, puedes preguntar aquí si guardar antes de salir
        # if self.canvas.project.has_unsaved_changes():
        #     res = QMessageBox.question(self, "Salir", "¿Desea guardar antes de salir?")
        #     if res == QMessageBox.Yes:
        #         self.save_project()
        #     elif res == QMessageBox.Cancel:
        #         event.ignore()
        #         return
        event.accept()