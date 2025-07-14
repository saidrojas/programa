import numpy as np

class Solid:
    _id_seq = 1

    def __init__(self, nodes, material=None):
        """
        nodes: list of Node objects (length 4 for tetrahedron, 8 for hexahedron)
        material: Material object or identifier
        """
        assert len(nodes) in (4, 8), "Solid must have 4 (tetrahedron) or 8 (hexahedron) nodes"
        self.nodes = nodes
        self.material = material
        self.id = Solid._id_seq
        Solid._id_seq += 1
        self.selected = False

    def get_points(self):
        """Returns list of np.array([x, y, z]) of the nodes."""
        return [np.array([n.x, n.y, n.z]) for n in self.nodes]

    def faces(self):
        """Returns a list of lists of Node objects, each representing a face."""
        if len(self.nodes) == 4:
            n = self.nodes
            return [
                [n[0], n[1], n[2]],
                [n[0], n[1], n[3]],
                [n[0], n[2], n[3]],
                [n[1], n[2], n[3]],
            ]
        elif len(self.nodes) == 8:
            n = self.nodes
            return [
                [n[0], n[1], n[2], n[3]],  # bottom face
                [n[4], n[5], n[6], n[7]],  # top face
                [n[0], n[1], n[5], n[4]],
                [n[1], n[2], n[6], n[5]],
                [n[2], n[3], n[7], n[6]],
                [n[3], n[0], n[4], n[7]],
            ]
        else:
            return []

    def edges(self):
        """Returns list of pairs of Node objects representing unique edges."""
        edges = set()
        for face in self.faces():
            for i in range(len(face)):
                a, b = face[i], face[(i + 1) % len(face)]
                edge = tuple(sorted((a.id, b.id)))
                edges.add(edge)
        # Return as Node objects
        return [(self.get_node_by_id(a), self.get_node_by_id(b)) for a, b in edges]

    def get_node_by_id(self, nid):
        for n in self.nodes:
            if n.id == nid:
                return n
        return None

    def volume(self):
        """Returns the volume of the solid."""
        pts = self.get_points()
        if len(pts) == 4:
            # Tetrahedron: V = |(b−a)·[(c−a)×(d−a)]|/6
            a, b, c, d = pts
            v = np.abs(np.dot((b - a), np.cross((c - a), (d - a)))) / 6.0
            return v
        elif len(pts) == 8:
            # Sum up the volumes of five tetrahedra that fill the hexahedron
            # This is a general method for convex hexahedra.
            idxs = [
                [0, 1, 3, 4],
                [1, 2, 3, 6],
                [1, 3, 4, 6],
                [4, 5, 6, 1],
                [3, 4, 6, 7]
            ]
            vol = 0.0
            for a, b, c, d in idxs:
                v = np.abs(np.dot((pts[b] - pts[a]), np.cross((pts[c] - pts[a]), (pts[d] - pts[a])))) / 6.0
                vol += v
            return vol
        else:
            return 0.0

    def centroid(self):
        """Returns the centroid (geometric center) as a numpy array."""
        pts = self.get_points()
        return np.mean(pts, axis=0)

    def surface_area(self):
        """Returns the total surface area of the solid."""
        total = 0.0
        faces = self.faces()
        for face in faces:
            pts = [np.array([n.x, n.y, n.z]) for n in face]
            if len(pts) == 3:
                # Triangle area
                total += 0.5 * np.linalg.norm(np.cross(pts[1] - pts[0], pts[2] - pts[0]))
            elif len(pts) == 4:
                # Quadrilateral: split into two triangles
                total += 0.5 * np.linalg.norm(np.cross(pts[1] - pts[0], pts[2] - pts[0]))
                total += 0.5 * np.linalg.norm(np.cross(pts[3] - pts[0], pts[2] - pts[0]))
        return total

    def is_degenerate(self, tol=1e-10):
        """Returns True if the solid's volume is (almost) zero."""
        return self.volume() < tol

    def as_tuple(self):
        """Returns a tuple of node IDs."""
        return tuple(n.id for n in self.nodes)

    def __repr__(self):
        return f"Solid(id={self.id}, nodes={[n.id for n in self.nodes]}, material={self.material})"

    def principal_axes(self):
        """Returns the principal axes and moments of inertia (for 8-node hexahedron only)."""
        if len(self.nodes) != 8:
            return None, None
        pts = np.array(self.get_points())
        centroid = np.mean(pts, axis=0)
        X = pts - centroid
        Ixx = np.sum(X[:, 1] ** 2 + X[:, 2] ** 2)
        Iyy = np.sum(X[:, 0] ** 2 + X[:, 2] ** 2)
        Izz = np.sum(X[:, 0] ** 2 + X[:, 1] ** 2)
        # Products of inertia are not strictly correct for a general polyhedron, but for a cube/cuboid it's meaningful
        Ixy = -np.sum(X[:, 0] * X[:, 1])
        Ixz = -np.sum(X[:, 0] * X[:, 2])
        Iyz = -np.sum(X[:, 1] * X[:, 2])
        inertia_tensor = np.array([[Ixx, Ixy, Ixz],
                                   [Ixy, Iyy, Iyz],
                                   [Ixz, Iyz, Izz]])
        eigvals, eigvecs = np.linalg.eigh(inertia_tensor)
        return eigvecs, eigvals