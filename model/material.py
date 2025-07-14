class Material:
    _id_seq = 1

    # Lista de tipos soportados por OpenSees (puedes extenderla)
    OPENSEES_TYPES = [
        "Elastic", "Concrete01", "Concrete02", "Steel01", "Steel02", "SteelMPF", "ElasticPP", "Hysteretic",
        "Concrete04", "Concrete06", "Concrete07", "SAWS", "MinMax", "Parallel"
    ]

    def __init__(self, name, type_, params=None):
        self.name = str(name)
        self.type = type_  # Must be one of OPENSEES_TYPES
        self.params = params if params is not None else {}
        self.id = Material._id_seq
        Material._id_seq += 1

    @staticmethod
    def get_opensees_types():
        return Material.OPENSEES_TYPES

    def clone(self):
        return Material(self.name, self.type, self.params.copy())

    def __repr__(self):
        return f"Material(id={self.id}, name={self.name}, type={self.type}, params={self.params})"