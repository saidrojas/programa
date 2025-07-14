class Support:
    _id_seq = 1

    def __init__(self, node, restraints=None, type_="fixed"):
        self.node = node  # Node object
        self.type = type_  # 'fixed', 'pinned', 'roller-x', etc.
        if restraints is None:
            # [Tx, Ty, Tz, Rx, Ry, Rz] True=fijo
            self.restraints = [True]*6 if type_ == "fixed" else [True, True, True, False, False, False]
        else:
            self.restraints = restraints
        self.id = Support._id_seq
        Support._id_seq += 1

    def is_fixed(self):
        return all(self.restraints)

    def is_pinned(self):
        return self.restraints[:3] == [True, True, True] and self.restraints[3:] == [False, False, False]

    def __repr__(self):
        return f"Support(id={self.id}, node={self.node.id}, type={self.type}, restraints={self.restraints})"