class Node:
    _id_seq = 1

    def __init__(self, x, y, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.id = Node._id_seq
        Node._id_seq += 1
        self.selected = False

    def as_tuple(self):
        return (self.x, self.y, self.z)

    def __repr__(self):
        return f"Node(id={self.id}, x={self.x}, y={self.y}, z={self.z})"