class NodalLoad:
    _id_seq = 1

    def __init__(self, node, fx=0, fy=0, fz=0, mx=0, my=0, mz=0, case=None):
        self.node = node  # Node object
        self.fx = fx
        self.fy = fy
        self.fz = fz
        self.mx = mx
        self.my = my
        self.mz = mz
        self.case = case  # str or int
        self.id = NodalLoad._id_seq
        NodalLoad._id_seq += 1

    def __repr__(self):
        return f"NodalLoad(id={self.id}, node={self.node.id}, fx={self.fx}, fy={self.fy}, fz={self.fz}, mx={self.mx}, my={self.my}, mz={self.mz}, case={self.case})"


class BarLoad:
    _id_seq = 1

    def __init__(self, bar, q1=0, q2=0, direction='z', type_='force', distribution='uniform', case=None):
        self.bar = bar  # Bar object
        self.q1 = q1
        self.q2 = q2
        self.direction = direction  # 'x', 'y', 'z'
        self.type = type_  # 'force' or 'moment'
        self.distribution = distribution  # 'uniform' or 'trapezoidal'
        self.case = case
        self.id = BarLoad._id_seq
        BarLoad._id_seq += 1

    def __repr__(self):
        return f"BarLoad(id={self.id}, bar={self.bar.id}, q1={self.q1}, q2={self.q2}, dir={self.direction}, type={self.type}, distr={self.distribution}, case={self.case})"


class ShellLoad:
    _id_seq = 1

    def __init__(self, shell, q=None, direction='z', type_='force', distribution='uniform', case=None):
        self.shell = shell  # Shell object
        self.q = q if q is not None else [0.0, 0.0, 0.0, 0.0]
        self.direction = direction  # 'x', 'y', 'z'
        self.type = type_  # 'force' or 'moment'
        self.distribution = distribution  # 'uniform' or 'lineal'
        self.case = case
        self.id = ShellLoad._id_seq
        ShellLoad._id_seq += 1

    def __repr__(self):
        return f"ShellLoad(id={self.id}, shell={self.shell.id}, q={self.q}, dir={self.direction}, type={self.type}, distr={self.distribution}, case={self.case})"