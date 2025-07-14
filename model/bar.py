import numpy as np

class Bar:
    _id_seq = 1

    def __init__(self, n1, n2, section=None, material=None):
        self.n1 = n1  # Node object
        self.n2 = n2  # Node object
        self.section = section  # Section object or ID
        self.material = material  # Material object or ID
        self.id = Bar._id_seq
        Bar._id_seq += 1
        self.selected = False

    def as_tuple(self):
        return (self.n1.id, self.n2.id)

    def __repr__(self):
        return (f"Bar(id={self.id}, n1={self.n1.id}, n2={self.n2.id}, "
                f"section={self.section}, material={self.material})")

    def length(self):
        """Longitud de la barra."""
        dx = self.n2.x - self.n1.x
        dy = self.n2.y - self.n1.y
        dz = self.n2.z - self.n1.z
        return np.sqrt(dx*dx + dy*dy + dz*dz)

    def centroid(self):
        """Centroide de la barra."""
        return np.array([(self.n1.x + self.n2.x)/2,
                         (self.n1.y + self.n2.y)/2,
                         (self.n1.z + self.n2.z)/2])

    def direction_vector(self):
        """Vector director (no unitario) de la barra."""
        return np.array([self.n2.x - self.n1.x,
                         self.n2.y - self.n1.y,
                         self.n2.z - self.n1.z])

    def unit_vector(self):
        """Vector unitario de dirección."""
        v = self.direction_vector()
        norm = np.linalg.norm(v)
        return v / norm if norm > 1e-12 else v

    def local_system(self):
        """
        Devuelve la matriz de transformación local-global (3x3).
        X local: dirección barra, Y y Z locales: ortogonales.
        """
        x_local = self.unit_vector()
        # Busca un vector no paralelo para hacer producto cruzado
        tmp = np.array([0, 0, 1]) if abs(x_local[2]) < 0.9 else np.array([0, 1, 0])
        y_local = np.cross(x_local, tmp)
        y_local /= np.linalg.norm(y_local) if np.linalg.norm(y_local) > 1e-12 else 1
        z_local = np.cross(x_local, y_local)
        return np.vstack([x_local, y_local, z_local]).T  # 3x3

    def is_degenerate(self, tol=1e-10):
        """True si la barra es de longitud prácticamente nula."""
        return self.length() < tol

    def divide(self, n_segments):
        """
        Divide la barra en n_segments sub-barras, devuelve lista de nodos intermedios (no los crea en el modelo).
        """
        nodes = [self.n1]
        for i in range(1, n_segments):
            t = i / n_segments
            x = self.n1.x + t * (self.n2.x - self.n1.x)
            y = self.n1.y + t * (self.n2.y - self.n1.y)
            z = self.n1.z + t * (self.n2.z - self.n1.z)
            from model.node import Node
            nodes.append(Node(x, y, z))
        nodes.append(self.n2)
        return nodes

    def intermediate_nodes(self, n_points):
        """
        Devuelve lista de nodos intermedios a lo largo de la barra (sin incluir extremos).
        Ideal para integración de cargas distribuidas o refinamiento.
        """
        nodes = []
        for i in range(1, n_points+1):
            t = i / (n_points + 1)
            x = self.n1.x + t * (self.n2.x - self.n1.x)
            y = self.n1.y + t * (self.n2.y - self.n1.y)
            z = self.n1.z + t * (self.n2.z - self.n1.z)
            from model.node import Node
            nodes.append(Node(x, y, z))
        return nodes

    def transform(self, matrix, translation=(0,0,0)):
        """
        Aplica una transformación 3D (matriz 3x3 y vector de traslación) a ambos nodos.
        """
        p1 = np.dot(matrix, np.array([self.n1.x, self.n1.y, self.n1.z])) + translation
        p2 = np.dot(matrix, np.array([self.n2.x, self.n2.y, self.n2.z])) + translation
        self.n1.x, self.n1.y, self.n1.z = p1
        self.n2.x, self.n2.y, self.n2.z = p2

    def as_opensees_dict(self):
        """
        Exporta la barra como diccionario listo para OpenSees.
        """
        return {
            "id": self.id,
            "n1": self.n1.id,
            "n2": self.n2.id,
            "material": self.material.id if hasattr(self.material, "id") else self.material,
            "section": self.section.id if hasattr(self.section, "id") else self.section
        }

    def angle2d(self):
        """Ángulo de la barra respecto al eje X en el plano XY (en radianes)."""
        dx = self.n2.x - self.n1.x
        dy = self.n2.y - self.n1.y
        return np.arctan2(dy, dx)

    def compare(self, other, tol=1e-7):
        """
        Compara esta barra con otra (por nodos, independientemente del orden).
        Devuelve True si conectan los mismos nodos (con tolerancia).
        """
        def coord_close(n1, n2):
            return (abs(n1.x - n2.x) < tol and
                    abs(n1.y - n2.y) < tol and
                    abs(n1.z - n2.z) < tol)
        nodes_self = [self.n1, self.n2]
        nodes_other = [other.n1, other.n2]
        return ((coord_close(nodes_self[0], nodes_other[0]) and coord_close(nodes_self[1], nodes_other[1])) or
                (coord_close(nodes_self[0], nodes_other[1]) and coord_close(nodes_self[1], nodes_other[0])))