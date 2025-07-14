from model.node import Node
from model.bar import Bar
from model.shell import Shell
from model.solid import Solid
from model.material import Material
from model.section import Section
from model.load import NodalLoad, BarLoad, ShellLoad
from model.support import Support
from core.export_opensees import OpenSeesExporter

from PySide6.QtCore import QObject, Signal

class Project(QObject):
    model_changed = Signal()

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.bars = []
        self.shells = []
        self.solids = []
        self.materials = []
        self.sections = []
        self.nodal_loads = []
        self.bar_loads = []
        self.shell_loads = []
        self.supports = []
        self.load_combinations = []
        self.history = []
        self.future = []

    # Métodos de alta y consulta
    def add_node(self, x, y, z=0.0):
        n = Node(x, y, z)
        self.nodes.append(n)
        self.model_changed.emit()
        return n

    def add_bar(self, n1, n2, section=None, material=None):
        b = Bar(n1, n2, section, material)
        self.bars.append(b)
        self.model_changed.emit()
        return b

    def add_shell(self, nodes, thickness=0.2, material=None):
        s = Shell(nodes, thickness, material)
        self.shells.append(s)
        self.model_changed.emit()
        return s

    def add_solid(self, nodes, material=None):
        so = Solid(nodes, material)
        self.solids.append(so)
        self.model_changed.emit()
        return so

    def add_material(self, name, type_, params=None):
        m = Material(name, type_, params)
        self.materials.append(m)
        self.model_changed.emit()
        return m

    def add_section(self, name, type_, params=None, material=None):
        s = Section(name, type_, params, material)
        self.sections.append(s)
        self.model_changed.emit()
        return s

    def add_nodal_load(self, node, fx=0, fy=0, fz=0, mx=0, my=0, mz=0, case=None):
        l = NodalLoad(node, fx, fy, fz, mx, my, mz, case)
        self.nodal_loads.append(l)
        self.model_changed.emit()
        return l

    def add_bar_load(self, bar, q1=0, q2=0, direction='z', type_='force', distribution='uniform', case=None):
        l = BarLoad(bar, q1, q2, direction, type_, distribution, case)
        self.bar_loads.append(l)
        self.model_changed.emit()
        return l

    def add_shell_load(self, shell, q=None, direction='z', type_='force', distribution='uniform', case=None):
        l = ShellLoad(shell, q, direction, type_, distribution, case)
        self.shell_loads.append(l)
        self.model_changed.emit()
        return l

    def add_support(self, node, restraints=None, type_="fixed"):
        s = Support(node, restraints, type_)
        self.supports.append(s)
        self.model_changed.emit()
        return s

    # Métodos de consulta rápida
    def get_node(self, id_):
        for n in self.nodes:
            if n.id == id_:
                return n
        return None

    def get_bar(self, id_):
        for b in self.bars:
            if b.id == id_:
                return b
        return None

    def get_shell(self, id_):
        for s in self.shells:
            if s.id == id_:
                return s
        return None

    def get_solid(self, id_):
        for so in self.solids:
            if so.id == id_:
                return so
        return None

    # Undo/Redo simple
    def undo(self):
        if self.history:
            state = self.history.pop()
            self.future.append(self._snapshot())
            self._restore(state)
            self.model_changed.emit()

    def redo(self):
        if self.future:
            state = self.future.pop()
            self.history.append(self._snapshot())
            self._restore(state)
            self.model_changed.emit()

    def _snapshot(self):
        import copy
        return (
            copy.deepcopy(self.nodes),
            copy.deepcopy(self.bars),
            copy.deepcopy(self.shells),
            copy.deepcopy(self.solids),
            copy.deepcopy(self.materials),
            copy.deepcopy(self.sections),
            copy.deepcopy(self.nodal_loads),
            copy.deepcopy(self.bar_loads),
            copy.deepcopy(self.shell_loads),
            copy.deepcopy(self.supports),
            copy.deepcopy(self.load_combinations)
        )

    def _restore(self, state):
        (
            self.nodes, self.bars, self.shells, self.solids, self.materials, self.sections,
            self.nodal_loads, self.bar_loads, self.shell_loads, self.supports, self.load_combinations
        ) = state

    # Guardar/Cargar (serialización simple JSON)
    def save(self, filename):
        import json
        def default(o):
            if hasattr(o, '__dict__'):
                d = dict(o.__dict__)
                # serializa nodos por id
                if "n1" in d and hasattr(d["n1"], "id"):
                    d["n1"] = d["n1"].id
                if "n2" in d and hasattr(d["n2"], "id"):
                    d["n2"] = d["n2"].id
                if "nodes" in d:
                    d["nodes"] = [n.id if hasattr(n, "id") else n for n in d["nodes"]]
                if "node" in d and hasattr(d["node"], "id"):
                    d["node"] = d["node"].id
                if "bar" in d and hasattr(d["bar"], "id"):
                    d["bar"] = d["bar"].id
                if "shell" in d and hasattr(d["shell"], "id"):
                    d["shell"] = d["shell"].id
                if "solid" in d and hasattr(d["solid"], "id"):
                    d["solid"] = d["solid"].id
                return d
            else:
                return str(o)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({
                "nodes": self.nodes,
                "bars": self.bars,
                "shells": self.shells,
                "solids": self.solids,
                "materials": self.materials,
                "sections": self.sections,
                "nodal_loads": self.nodal_loads,
                "bar_loads": self.bar_loads,
                "shell_loads": self.shell_loads,
                "supports": self.supports,
                "load_combinations": self.load_combinations
            }, f, indent=2, default=default)

    def load(self, filename):
        import json
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Nota: esta carga es simplificada. Para producción, deberías tener un sistema robusto de deserialización.
        self.nodes = [Node(**n) for n in data.get("nodes", [])]
        self.bars = [Bar(self.get_node(b["n1"]), self.get_node(b["n2"]),
                         b.get("section"), b.get("material")) for b in data.get("bars", [])]
        self.shells = [Shell([self.get_node(nid) for nid in s["nodes"]],
                             s.get("thickness", 0.2), s.get("material")) for s in data.get("shells", [])]
        self.solids = [Solid([self.get_node(nid) for nid in so["nodes"]],
                             so.get("material")) for so in data.get("solids", [])]
        self.materials = [Material(**m) for m in data.get("materials", [])]
        self.sections = [Section(**s) for s in data.get("sections", [])]
        # Loads y supports requieren vinculación por id
        self.nodal_loads = []
        for l in data.get("nodal_loads", []):
            n = self.get_node(l["node"])
            self.nodal_loads.append(NodalLoad(n, l["fx"], l["fy"], l["fz"], l["mx"], l["my"], l["mz"], l.get("case")))
        self.bar_loads = []
        for l in data.get("bar_loads", []):
            b = self.get_bar(l["bar"])
            self.bar_loads.append(BarLoad(b, l["q1"], l["q2"], l["direction"], l["type"], l["distribution"], l.get("case")))
        self.shell_loads = []
        for l in data.get("shell_loads", []):
            s = self.get_shell(l["shell"])
            self.shell_loads.append(ShellLoad(s, l["q"], l["direction"], l["type"], l["distribution"], l.get("case")))
        self.supports = []
        for s in data.get("supports", []):
            n = self.get_node(s["node"])
            self.supports.append(Support(n, s["restraints"], s["type"]))
        self.load_combinations = data.get("load_combinations", [])
        self.model_changed.emit()

    # Edición de propiedades desde el panel
    def set_property(self, element_id, prop, value):
        typ, idx = element_id
        if typ == 'node':
            n = self.get_node(idx)
            if n:
                setattr(n, prop, value)
        elif typ == 'bar':
            b = self.get_bar(idx)
            if b:
                setattr(b, prop, value)
        elif typ == 'shell':
            s = self.get_shell(idx)
            if s:
                setattr(s, prop, value)
        elif typ == 'solid':
            so = self.get_solid(idx)
            if so:
                setattr(so, prop, value)
        # ...otros tipos...
        self.model_changed.emit()

    def export_to_opensees_tcl(self, filepath, only_geometry=False, comments=True, groups=False):
        exporter = OpenSeesExporter(self)
        exporter.export_to_tcl(filepath, only_geometry, comments, groups)

    def export_to_opensees_json(self, filepath, only_geometry=False, comments=True, groups=False):
        exporter = OpenSeesExporter(self)
        exporter.export_to_json(filepath, only_geometry, comments, groups)