class Section:
    _id_seq = 1

    # Tipos de sección predefinidos
    TYPES = [
        "Rectangular", "Circular", "IPE", "HEB", "Custom"
    ]

    def __init__(self, name, type_, params=None, material=None):
        self.name = str(name)
        self.type = type_  # One of TYPES
        self.params = params if params is not None else {}
        self.material = material
        self.id = Section._id_seq
        Section._id_seq += 1

    @staticmethod
    def get_section_types():
        return Section.TYPES

    def clone(self):
        return Section(self.name, self.type, self.params.copy(), self.material)

    def __repr__(self):
        return f"Section(id={self.id}, name={self.name}, type={self.type}, params={self.params}, material={self.material})"