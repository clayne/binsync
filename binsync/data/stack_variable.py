import toml

from ..utils import is_py2, is_py3
from .base import Base

if is_py3():
    unicode = str
    long = int


class StackOffsetType:
    BINJA = 0
    IDA = 1
    GHIDRA = 2
    ANGR = 3


class StackVariable(Base):
    """
    Describes a stack variable for a given function.
    """

    __slots__ = (
        "func_addr",
        "name",
        "stack_offset",
        "stack_offset_type",
        "size",
        "type",
    )

    def __init__(self, stack_offset, offset_type, name, type_, size, func_addr):
        self.stack_offset = stack_offset  # type: int
        self.stack_offset_type = offset_type  # type: int
        self.name = name  # type: str
        self.type = type_  # type: str
        self.size = size  # type: int
        self.func_addr = func_addr  # type: int

        if is_py2():
            self.name = str(self.name)
            self.type = str(self.type)

    def __getstate__(self):
        return dict(
            (k, getattr(self, k)) for k in self.__slots__
        )

    def __setstate__(self, state):
        for k in self.__slots__:
            if is_py2() and isinstance(state[k], unicode):
                setattr(self, k, str(state[k]))
            else:
                setattr(self, k, state[k])

    def __eq__(self, other):
        if isinstance(other, StackVariable):
            for k in self.__slots__:
                if getattr(self, k) != getattr(other, k):
                    return False
            return True
        return False

    def get_offset(self, offset_type):
        if offset_type == self.stack_offset_type:
            return self.stack_offset
        # conversion required
        if self.stack_offset_type in (StackOffsetType.IDA, StackOffsetType.BINJA):
            off = self.stack_offset
        else:
            raise NotImplementedError()
        if offset_type in (StackOffsetType.IDA, StackOffsetType.BINJA):
            return off
        else:
            raise NotImplementedError()

    def dump(self):
        return toml.dumps(self.__getstate__())

    @classmethod
    def parse(cls, s):
        sv = StackVariable(None, None, None, None, None, None)
        sv.__setstate__(toml.loads(s))
        return sv

    @classmethod
    def load_many(cls, path):
        with open(path, "r") as f:
            data = f.read()
        svs_toml = toml.loads(data)

        for sv_toml in svs_toml.values():
            sv = StackVariable(None, None, None, None, None, None)
            sv.__setstate__(sv_toml)
            yield sv

    @classmethod
    def dump_many(cls, path, svs):
        d = { }
        for v in sorted(svs.values(), key=lambda x: x.stack_offset):
            d["%x" % v.stack_offset] = v.__getstate__()
        with open(path, "w") as f:
            toml.dump(d, f)