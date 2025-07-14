import numpy as np

class Shell:
    _id_seq = 1

    def __init__(self, nodes, thickness=0.2, material=None):
        assert len(nodes) >= 3, "A shell needs at least 3 nodes"
        self.nodes = nodes  # list of Node objects
        self.thickness = thickness
        self.material = material
        self.id = Shell._id_seq
        Shell._id_seq += 1
        self.selected = False

    def as_tuple(self):
        return tuple(n.id for n in self.nodes)

    def __repr__(self):
        return f"Shell(id={self.id}, nodes={[n.id for n in self.nodes]}, thickness={self.thickness}, material={self.material})"

    def get_points(self):
        """Devuelve lista de np.array([x, y, z]) de los nodos"""
        return [np.array([n.x, n.y, n.z]) for n in self.nodes]

    def is_coplanar(self, tol=1e-6):
        """Verifica si los nodos son coplanares"""
        pts = self.get_points()
        if len(pts) < 4:
            return True
        v1 = pts[1] - pts[0]
        v2 = pts[2] - pts[0]
        normal = np.cross(v1, v2)
        normal /= np.linalg.norm(normal)
        for p in pts[3:]:
            if abs(np.dot(p - pts[0], normal)) > tol:
                return False
        return True

    def normal(self):
        """Devuelve el vector normal (promedio de triángulos)"""
        pts = self.get_points()
        n = np.zeros(3)
        for i in range(len(pts)):
            p0 = pts[i]
            p1 = pts[(i+1)%len(pts)]
            n += np.cross(p0, p1)
        norm = np.linalg.norm(n)
        return n/norm if norm > 1e-12 else n

    def area(self):
        """Área usando la proyección óptima del polígono 3D en 2D"""
        pts = np.array(self.get_points())
        nrm = self.normal()
        # Encuentra el plano dominante (proyección con mayor área)
        axes = np.argsort(np.abs(nrm))
        i1, i2 = axes[1], axes[2]
        xy = pts[:, [i1, i2]]
        # Shoelace formula
        area = 0.5*np.abs(np.sum(xy[:-1,0]*xy[1:,1] - xy[1:,0]*xy[:-1,1]) + xy[-1,0]*xy[0,1] - xy[0,0]*xy[-1,1])
        return area

    def centroid(self):
        """Centroide geométrico de la shell"""
        pts = np.array(self.get_points())
        return np.mean(pts, axis=0)

    def edge_lengths(self):
        """Devuelve lista de longitudes de cada lado"""
        pts = self.get_points()
        return [np.linalg.norm(pts[i]-pts[(i+1)%len(pts)]) for i in range(len(pts))]

    def as_2d(self):
        """
        Proyecta los nodos a 2D en el plano del shell.
        Devuelve: puntos_2d, origen, u, v (base ortonormal)
        """
        pts = self.get_points()
        origen = pts[0]
        v1 = pts[1] - origen
        v2 = pts[2] - origen
        normal = np.cross(v1, v2)
        normal /= np.linalg.norm(normal)
        u = v1 / np.linalg.norm(v1)
        v = np.cross(normal, u)
        puntos_2d = []
        for p in pts:
            vec = p - origen
            x2d = np.dot(vec, u)
            y2d = np.dot(vec, v)
            puntos_2d.append([x2d, y2d])
        return puntos_2d, origen, u, v