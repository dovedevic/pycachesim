import enum


class AddressSpace(enum.Enum):
    """
    Defines the address space supported by a system or cache
    """
    in128Bit = 0xffffffffffffffffffffffffffffffff
    in112Bit = 0xffffffffffffffffffffffffffff
    in96Bit = 0xffffffffffffffffffffffff
    in80Bit = 0xffffffffffffffffffff
    in64Bit = 0xffffffffffffffff
    in48Bit = 0xffffffffffff
    in32Bit = 0xffffffff
    in16Bit = 0xffff
    in8Bit = 0xff
