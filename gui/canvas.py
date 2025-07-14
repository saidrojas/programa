from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QApplication, QMessageBox, QToolTip
from PySide6.QtGui import QCursor, QPainter, QPen, QColor, QBrush, QMouseEvent, QWheelEvent, QKeyEvent, QPaintEvent, QPixmap, QPolygon
from PySide6.QtCore import Qt, Signal, QPoint, QRect, QPointF
from OpenGL.GL import *
import math
from PyQt5.QtWidgets import QOpenGLWidget
class Canvas(QOpenGLWidget):
    """
    Canvas profesional OpenGL para ingeniería estructural:
    - Dibuja nodos, barras, shells, sólidos, auxiliares.
    - Selección múltiple, zoom, pan, edición directa, menú contextual, tooltips.
    - Emite señales para integración con árbol y panel de propiedades.
    """
    object_selected = Signal(object)     # Cuando se selecciona un objeto
    model_changed = Signal()             # Cuando cambia el modelo (agregar/borrar/editar)
    selection_changed = Signal(list)     # Cuando cambia la selección

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project = None
        self.selected = []
        self.zoom = 1.0
        self.pan = QPoint(0, 0)
        self.pan_active = False
        self.pan_start = QPoint(0, 0)
        self.dragging = False
        self.drag_start = None
        self.drag_rect = QRect()
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        self.last_hovered = None
        self.cursor_pos = None

    def set_project(self, project):
        self.project = project
        self.selected = []
        self.zoom = 1.0
        self.pan = QPoint(0, 0)
        self.update()

    def set_selected(self, selected_objs):
        self.selected = selected_objs or []
        self.update()
        if self.selected:
            self.object_selected.emit(self.selected[0])
        self.selection_changed.emit(self.selected)

    def initializeGL(self):
        glClearColor(1, 1, 1, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, h, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glTranslatef(self.pan.x(), self.pan.y(), 0)
        glScalef(self.zoom, self.zoom, 1)

        if not self.project:
            glPopMatrix()
            return

        # --- Dibujo de líneas auxiliares ---
        glLineWidth(1)
        glColor3f(0.8, 0.8, 0.8)
        for aux in getattr(self.project, "aux_lines", []):
            glBegin(GL_LINES)
            glVertex2f(aux.p1.x, aux.p1.y)
            glVertex2f(aux.p2.x, aux.p2.y)
            glEnd()

        # --- Dibujo de shells ---
        for s in getattr(self.project, "shells", []):
            if len(s.nodes) > 2:
                if s in self.selected:
                    glColor4f(0, 0.5, 0, 0.4)
                else:
                    glColor4f(0.4, 1, 0.4, 0.3)
                glBegin(GL_POLYGON)
                for n in s.nodes:
                    glVertex2f(n.x, n.y)
                glEnd()
                # Contorno
                if s in self.selected:
                    glColor3f(0, 0.3, 0)
                    glLineWidth(4)
                else:
                    glColor3f(0.2, 0.8, 0.2)
                    glLineWidth(2)
                glBegin(GL_LINE_LOOP)
                for n in s.nodes:
                    glVertex2f(n.x, n.y)
                glEnd()
                glLineWidth(1)

        # --- Dibujo de barras ---
        for b in getattr(self.project, "bars", []):
            if b in self.selected:
                glLineWidth(4)
                glColor3f(1, 0, 1)
            else:
                glLineWidth(2)
                glColor3f(0, 0, 1)
            glBegin(GL_LINES)
            glVertex2f(b.n1.x, b.n1.y)
            glVertex2f(b.n2.x, b.n2.y)
            glEnd()
            glLineWidth(1)

        # --- Dibujo de nodos ---
        for n in getattr(self.project, "nodes", []):
            if n in self.selected:
                glColor3f(1, 0, 0)
                glPointSize(12)
            elif n == self.last_hovered:
                glColor3f(1, 0.5, 0)
                glPointSize(14)
            else:
                glColor3f(0, 0, 0)
                glPointSize(8)
            glBegin(GL_POINTS)
            glVertex2f(n.x, n.y)
            glEnd()
            glPointSize(1)

        glPopMatrix()

        # --- Overlay con QPainter para rectángulo de selección y etiquetas ---
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        if self.dragging and not self.pan_active:
            pen = QPen(Qt.darkGray, 1, Qt.DashLine)
            qp.setPen(pen)
            qp.setBrush(Qt.NoBrush)
            qp.drawRect(self.drag_rect.normalized())
        # Etiquetas de nodos
        if self.project:
            qp.setPen(Qt.gray)
            for n in getattr(self.project, "nodes", []):
                p = self.model_to_screen(QPointF(n.x, n.y))
                qp.drawText(int(p.x())+7, int(p.y())-7, f"#{n.id}")
        qp.end()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            self.open_context_menu(event)
            return

        if event.button() == Qt.MiddleButton:
            self.pan_active = True
            self.pan_start = event.pos() - self.pan
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)
            return

        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()
            self.drag_rect = QRect(self.drag_start, self.drag_start)

        obj = self.find_object_at(event.pos())
        if obj:
            if QApplication.keyboardModifiers() & Qt.ControlModifier:
                if obj in self.selected:
                    self.selected.remove(obj)
                else:
                    self.selected.append(obj)
            else:
                self.selected = [obj]
            self.set_selected(self.selected)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.cursor_pos = event.pos()
        if self.pan_active:
            self.pan = event.pos() - self.pan_start
            self.update()
            return

        if self.dragging:
            self.drag_rect = QRect(self.drag_start, event.pos())
            self.update()
            return

        obj = self.find_object_at(event.pos())
        if obj != self.last_hovered:
            self.last_hovered = obj
            self.update()
            if obj:
                QToolTip.showText(event.globalPos(), self.get_tooltip(obj), self)
            else:
                QToolTip.hideText()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MiddleButton and self.pan_active:
            self.pan_active = False
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            return

        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            if (abs(self.drag_rect.width()) > 5 or abs(self.drag_rect.height()) > 5):
                objs = self.find_objects_in_rect(self.drag_rect.normalized())
                self.set_selected(objs)
            self.update()

    def wheelEvent(self, event: QWheelEvent):
        angle = event.angleDelta().y()
        factor = 1.15 if angle > 0 else 0.87
        old_pos = (event.pos() - self.pan) / self.zoom
        self.zoom *= factor
        self.zoom = max(0.1, min(self.zoom, 10))
        new_pos = (event.pos() - self.pan) / self.zoom
        self.pan += (new_pos - old_pos) * self.zoom
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            if self.selected:
                if QMessageBox.question(self, "Eliminar", "¿Eliminar los objetos seleccionados?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    for obj in list(self.selected):
                        self.delete_object(obj)
                    self.selected = []
                    self.update()
        if event.key() == Qt.Key_A and (event.modifiers() & Qt.ControlModifier):
            all_objs = []
            for attr in ("nodes", "bars", "shells"):
                all_objs.extend(getattr(self.project, attr, []))
            self.set_selected(all_objs)

    def open_context_menu(self, event: QMouseEvent):
        obj = self.find_object_at(event.pos())
        menu = QMenu(self)
        if obj:
            act_prop = QAction("Propiedades", self)
            act_prop.triggered.connect(lambda: self.object_selected.emit(obj))
            menu.addAction(act_prop)
            act_del = QAction("Eliminar", self)
            act_del.triggered.connect(lambda: self.delete_object(obj))
            menu.addAction(act_del)
        else:
            act_zoom_fit = QAction("Zoom a todo", self)
            act_zoom_fit.triggered.connect(self.zoom_fit)
            menu.addAction(act_zoom_fit)
        menu.exec(QCursor.pos())

    def model_to_screen(self, point: QPointF):
        """Convierte coordenada de modelo (n.x, n.y) a pantalla."""
        return QPointF(point.x() * self.zoom + self.pan.x(), point.y() * self.zoom + self.pan.y())

    def screen_to_model(self, point: QPoint):
        """Convierte coordenada de pantalla a coordenada de modelo."""
        return QPointF((point.x() - self.pan.x()) / self.zoom, (point.y() - self.pan.y()) / self.zoom)

    def find_object_at(self, pos: QPoint):
        model_pos = self.screen_to_model(pos)
        # Nodos
        for n in getattr(self.project, "nodes", []):
            if math.hypot(model_pos.x() - n.x, model_pos.y() - n.y) < 10 / self.zoom:
                return n
        # Barras
        for b in getattr(self.project, "bars", []):
            if self.point_near_segment(model_pos, b.n1, b.n2, tol=7 / self.zoom):
                return b
        # Shells
        for s in getattr(self.project, "shells", []):
            if self.point_in_polygon(model_pos, [n for n in s.nodes]):
                return s
        return None

    def find_objects_in_rect(self, rect: QRect):
        top_left = self.screen_to_model(rect.topLeft())
        bottom_right = self.screen_to_model(rect.bottomRight())
        x_min, x_max = min(top_left.x(), bottom_right.x()), max(top_left.x(), bottom_right.x())
        y_min, y_max = min(top_left.y(), bottom_right.y()), max(top_left.y(), bottom_right.y())
        objs = []
        for n in getattr(self.project, "nodes", []):
            if x_min <= n.x <= x_max and y_min <= n.y <= y_max:
                objs.append(n)
        for b in getattr(self.project, "bars", []):
            if (x_min <= b.n1.x <= x_max and y_min <= b.n1.y <= y_max and
                x_min <= b.n2.x <= x_max and y_min <= b.n2.y <= y_max):
                objs.append(b)
        for s in getattr(self.project, "shells", []):
            if all(x_min <= n.x <= x_max and y_min <= n.y <= y_max for n in s.nodes):
                objs.append(s)
        return objs

    def point_near_segment(self, p: QPointF, n1, n2, tol=7):
        x1, y1 = n1.x, n1.y
        x2, y2 = n2.x, n2.y
        px, py = p.x(), p.y()
        dx, dy = x2 - x1, y2 - y1
        if dx == dy == 0:
            dist = math.hypot(px - x1, py - y1)
        else:
            t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            dist = math.hypot(px - proj_x, py - proj_y)
        return dist < tol

    def point_in_polygon(self, point: QPointF, nodes):
        x, y = point.x(), point.y()
        n = len(nodes)
        inside = False
        px1, py1 = nodes[0].x, nodes[0].y
        for i in range(n+1):
            px2, py2 = nodes[i % n].x, nodes[i % n].y
            if y > min(py1, py2):
                if y <= max(py1, py2):
                    if x <= max(px1, px2):
                        if py1 != py2:
                            xinters = (y - py1) * (px2 - px1) / (py2 - py1 + 1e-12) + px1
                        if px1 == px2 or x <= xinters:
                            inside = not inside
            px1, py1 = px2, py2
        return inside

    def get_tooltip(self, obj):
        if hasattr(obj, "id"):
            label = f"ID: {obj.id}"
        else:
            label = str(obj)
        if hasattr(obj, "name"):
            label += f"\nNombre: {obj.name}"
        if hasattr(obj, "material"):
            label += f"\nMaterial: {obj.material}"
        if hasattr(obj, "section"):
            label += f"\nSección: {obj.section}"
        return label

    def zoom_fit(self):
        nodes = getattr(self.project, "nodes", [])
        if not nodes:
            return
        min_x = min(n.x for n in nodes)
        max_x = max(n.x for n in nodes)
        min_y = min(n.y for n in nodes)
        max_y = max(n.y for n in nodes)
        w = max_x - min_x + 30
        h = max_y - min_y + 30
        scale_x = self.width() / w
        scale_y = self.height() / h
        self.zoom = min(scale_x, scale_y, 10)
        self.pan = QPoint(-min_x * self.zoom + 15, -min_y * self.zoom + 15)
        self.update()

    def update_model(self):
        self.update()
        self.model_changed.emit()

    def delete_object(self, obj):
        changed = False
        for coll in ("nodes", "bars", "shells", "solids"):
            items = getattr(self.project, coll, [])
            if obj in items:
                items.remove(obj)
                changed = True
        if changed:
            self.update_model()
        return changed