# isa.py

OPCODES = {
    "SYS":     0b0000,
    "LDI":     0b0001,
    "ALU":     0b0010,
    "IO":      0b0011,
    "GPIO":    0b0100,
    "WAIT":    0b0101,
    "WAITPIN": 0b0110,
    "BRANCH":  0b0111,
    "HOST":    0b1000,
}

REGISTERS = {
    "R0": 0b00,
    "R1": 0b01,
    "R2": 0b10,
    "R3": 0b11,
}

SYS_FUNCTIONS = {
    "NOP":  0b000,
    "HALT": 0b001,
}

ALU_FUNCTIONS = {
    "ADD":    0b0000,
    "SUB":    0b0001,
    "AND":    0b0010,
    "OR":     0b0011,
    "XOR":    0b0100,
    "CMP":    0b0101,
    "MOV":    0b0110,
    "INC":    0b0111,
    "DEC":    0b1000,
    "LSHIFT": 0b1001,
    "RSHIFT": 0b1010,
}

BINARY_ALU = {
    "ADD",
    "SUB",
    "AND",
    "OR",
    "XOR",
    "CMP",
    "MOV",
}

UNARY_ALU = {
    "INC",
    "DEC",
}

SHIFT_INSTRUCTIONS = {
    "LSHIFT",
    "RSHIFT",
}

GPIO_FUNCTIONS = {
    "SET":    0b00,
    "CLR":    0b01,
    "TOGGLE": 0b10,
    "DIR":    0b11,
}

BRANCH_CONDITIONS = {
    "JMP": 0b00,
    "BZ":  0b01,
    "BNZ": 0b10,
}