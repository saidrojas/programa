import os

class OpenSeesExporter:
    """
    Exportador del modelo a formato OpenSees TCL o JSON.
    """

    def __init__(self, project):
        self.project = project

    def export_to_tcl(self, filepath, only_geometry=False, comments=True, groups=False):
        """
        Exporta a script TCL de OpenSees.
        """
        with open(filepath, "w", encoding="utf-8") as f:
            if comments:
                f.write("# OpenSees TCL exportado por Struktix\n\n")
            # Nodos
            for node in getattr(self.project, "nodes", []):
                line = f"node {node.id} {node.x:.6f} {node.y:.6f} {node.z:.6f}\n"
                if comments:
                    f.write(f"# Nodo {node.id}\n")
                f.write(line)
            f.write("\n")
            # Barras (elementos tipo truss/beam)
            for bar in getattr(self.project, "bars", []):
                eid = bar.id
                n1, n2 = bar.n1.id, bar.n2.id
                if only_geometry:
                    line = f"# element bar {eid} {n1} {n2}\n"
                else:
                    sec = getattr(bar, "section", 1)
                    mat = getattr(bar, "material", 1)
                    line = f"element truss {eid} {n1} {n2} {sec} {mat}\n"
                if comments:
                    f.write(f"# Barra {eid}\n")
                f.write(line)
            # Shells (elementos tipo Shell)
            for shell in getattr(self.project, "shells", []):
                nidstr = " ".join(str(n.id) for n in shell.nodes)
                eid = shell.id
                if only_geometry:
                    line = f"# element shell {eid} {nidstr}\n"
                else:
                    sec = getattr(shell, "section", 1)
                    mat = getattr(shell, "material", 1)
                    line = f"element ShellMITC4 {eid} {nidstr} {sec} {mat}\n"
                if comments:
                    f.write(f"# Shell {eid}\n")
                f.write(line)
            # Sólidos (elementos tipo brick)
            for solid in getattr(self.project, "solids", []):
                nidstr = " ".join(str(n.id) for n in solid.nodes)
                eid = solid.id
                if only_geometry:
                    line = f"# element solid {eid} {nidstr}\n"
                else:
                    mat = getattr(solid, "material", 1)
                    line = f"element Brick {eid} {nidstr} {mat}\n"
                if comments:
                    f.write(f"# Sólido {eid}\n")
                f.write(line)
            # Apoyos
            for support in getattr(self.project, "supports", []):
                n = support.node.id
                restr = getattr(support, "restraints", [1, 1, 1, 1, 1, 1])
                restr_str = " ".join(str(int(r)) for r in restr)
                if comments:
                    f.write(f"# Apoyo nodo {n}\n")
                f.write(f"fix {n} {restr_str}\n")
            # Cargas nodales
            for load in getattr(self.project, "node_loads", []):
                n = load.node.id
                fx, fy, fz = getattr(load, "fx", 0), getattr(load, "fy", 0), getattr(load, "fz", 0)
                mx, my, mz = getattr(load, "mx", 0), getattr(load, "my", 0), getattr(load, "mz", 0)
                if fx or fy or fz or mx or my or mz:
                    if comments:
                        f.write(f"# Carga nodo {n}\n")
                    f.write(f"load {n} {fx} {fy} {fz} {mx} {my} {mz}\n")
            # Agrupaciones (opcional)
            if groups and hasattr(self.project, "groups"):
                for g in self.project.groups:
                    if hasattr(g, "members"):
                        ids = " ".join(str(m.id) for m in g.members)
                        f.write(f"# Grupo {g.name}\n")
                        f.write(f"set {g.name} {{{ids}}}\n")
            f.write("\n# EOF\n")

    def export_to_json(self, filepath, only_geometry=False, comments=True, groups=False):
        """
        Exporta a JSON (para OpenSeesPy o usos avanzados).
        """
        import json
        data = {"nodes": [], "bars": [], "shells": [], "solids": [], "supports": [], "loads": []}
        for node in getattr(self.project, "nodes", []):
            data["nodes"].append({
                "id": node.id,
                "x": node.x, "y": node.y, "z": node.z
            })
        for bar in getattr(self.project, "bars", []):
            d = {"id": bar.id, "n1": bar.n1.id, "n2": bar.n2.id}
            if not only_geometry:
                d["section"] = getattr(bar, "section", 1)
                d["material"] = getattr(bar, "material", 1)
            data["bars"].append(d)
        for shell in getattr(self.project, "shells", []):
            d = {"id": shell.id, "nodes": [n.id for n in shell.nodes]}
            if not only_geometry:
                d["section"] = getattr(shell, "section", 1)
                d["material"] = getattr(shell, "material", 1)
            data["shells"].append(d)
        for solid in getattr(self.project, "solids", []):
            d = {"id": solid.id, "nodes": [n.id for n in solid.nodes]}
            if not only_geometry:
                d["material"] = getattr(solid, "material", 1)
            data["solids"].append(d)
        for support in getattr(self.project, "supports", []):
            data["supports"].append({
                "node": support.node.id,
                "restraints": getattr(support, "restraints", [1,1,1,1,1,1])
            })
        for load in getattr(self.project, "node_loads", []):
            data["loads"].append({
                "node": load.node.id,
                "fx": getattr(load, "fx", 0),
                "fy": getattr(load, "fy", 0),
                "fz": getattr(load, "fz", 0),
                "mx": getattr(load, "mx", 0),
                "my": getattr(load, "my", 0),
                "mz": getattr(load, "mz", 0)
            })
        if groups and hasattr(self.project, "groups"):
            data["groups"] = [
                {"name": g.name, "members": [m.id for m in g.members]} for g in self.project.groups
            ]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)