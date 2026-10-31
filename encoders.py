from isa import (
    OPCODES,
    SYS_FUNCTIONS,
    ALU_FUNCTIONS,
    BINARY_ALU,
    UNARY_ALU,
    SHIFT_INSTRUCTIONS,
    GPIO_FUNCTIONS,
    BRANCH_CONDITIONS,
)

from parsing import (
    parse_number,
    parse_register,
    parse_gpio_pin,
)

def encode_sys(mnemonic):
    mnemonic = mnemonic.upper()

    if mnemonic not in SYS_FUNCTIONS:
        raise ValueError(
            f"Invalid SYS instruction: {mnemonic}"
        )

    opcode = OPCODES["SYS"]
    function = SYS_FUNCTIONS[mnemonic]

    instruction = (
        (opcode << 12)
        | (function << 9)
    )

    return instruction

def encode_ldi(rd, immediate):
    rd_code = parse_register(rd)
    immediate = parse_number(immediate)

    if not 0 <= immediate <= 0x3FF:
        raise ValueError(
            "LDI immediate must be between 0 and 1023"
        )

    instruction = (
        (OPCODES["LDI"] << 12)
        | (rd_code << 10)
        | immediate
    )

    return instruction

def encode_binary_alu(mnemonic, rd, rs):
    mnemonic = mnemonic.upper()

    if mnemonic not in BINARY_ALU:
        raise ValueError(
            f"Invalid binary ALU instruction: {mnemonic}"
        )

    rd_code = parse_register(rd)
    rs_code = parse_register(rs)

    function = ALU_FUNCTIONS[mnemonic]

    instruction = (
        (OPCODES["ALU"] << 12)
        | (rd_code << 10)
        | (rs_code << 8)
        | (function << 4)
    )

    return instruction

def encode_unary_alu(mnemonic, rd):
    mnemonic = mnemonic.upper()

    if mnemonic not in UNARY_ALU:
        raise ValueError(
            f"Invalid unary ALU instruction: {mnemonic}"
        )

    rd_code = parse_register(rd)
    function = ALU_FUNCTIONS[mnemonic]

    instruction = (
        (OPCODES["ALU"] << 12)
        | (rd_code << 10)
        | (function << 4)
    )

    return instruction

def encode_shift(mnemonic, rd, amount):
    mnemonic = mnemonic.upper()

    if mnemonic not in SHIFT_INSTRUCTIONS:
        raise ValueError(
            f"Invalid shift instruction: {mnemonic}"
        )

    rd_code = parse_register(rd)
    amount = parse_number(amount)

    if not 0 <= amount <= 15:
        raise ValueError(
            "Shift amount must be between 0 and 15"
        )

    function = ALU_FUNCTIONS[mnemonic]

    instruction = (
        (OPCODES["ALU"] << 12)
        | (rd_code << 10)
        | (function << 4)
        | amount
    )

    return instruction

def encode_io(mnemonic, register, mask):
    mnemonic = mnemonic.upper()

    if mnemonic not in {"IN", "OUT"}:
        raise ValueError(
            f"Invalid I/O instruction: {mnemonic}"
        )

    reg_code = parse_register(register)
    mask = parse_number(mask)

    if not 0 <= mask <= 0xFF:
        raise ValueError(
            "GPIO mask must be between 0x00 and 0xFF"
        )

    direction = 0 if mnemonic == "IN" else 1

    instruction = (
        (OPCODES["IO"] << 12)
        | (direction << 11)
        | (reg_code << 9)
        | (mask << 1)
    )

    return instruction

def encode_gpio(mnemonic, mask, direction=None):
    mnemonic = mnemonic.upper()

    if mnemonic not in GPIO_FUNCTIONS:
        raise ValueError(
            f"Invalid GPIO instruction: {mnemonic}"
        )

    mask = parse_number(mask)

    if not 0 <= mask <= 0xFF:
        raise ValueError(
            "GPIO mask must be between 0x00 and 0xFF"
        )

    function = GPIO_FUNCTIONS[mnemonic]

    argument = 0

    if mnemonic == "DIR":
        if direction is None:
            raise ValueError(
                "DIR requires IN or OUT"
            )

        direction = direction.strip().upper()

        if direction == "IN":
            argument = 0
        elif direction == "OUT":
            argument = 1
        else:
            raise ValueError(
                "DIR direction must be IN or OUT"
            )

    elif direction is not None:
        raise ValueError(
            f"{mnemonic} does not take a direction argument"
        )

    instruction = (
        (OPCODES["GPIO"] << 12)
        | (function << 10)
        | (argument << 9)
        | (mask << 1)
    )

    return instruction

def encode_wait(count):
    count = parse_number(count)

    if not 0 <= count <= 0xFFF:
        raise ValueError(
            "WAIT count must be between 0 and 4095"
        )

    instruction = (
        (OPCODES["WAIT"] << 12)
        | count
    )

    return instruction

def encode_waitpin(pin, level):
    pin_code = parse_gpio_pin(pin)

    level = level.strip().upper()

    if level == "LOW":
        level_bit = 0
    elif level == "HIGH":
        level_bit = 1
    else:
        raise ValueError(
            "WAITPIN level must be HIGH or LOW"
        )

    mode = 0b00

    instruction = (
        (OPCODES["WAITPIN"] << 12)
        | (pin_code << 9)
        | (level_bit << 8)
        | (mode << 6)
    )

    return instruction
def encode_branch(mnemonic, target):
    mnemonic = mnemonic.upper()

    if mnemonic not in BRANCH_CONDITIONS:
        raise ValueError(
            f"Invalid branch instruction: {mnemonic}"
        )

    target = parse_number(target)

    if not 0 <= target <= 0xFF:
        raise ValueError(
            "Branch target must be between 0 and 255"
        )

    condition = BRANCH_CONDITIONS[mnemonic]

    instruction = (
        (OPCODES["BRANCH"] << 12)
        | (condition << 10)
        | target
    )

    return instruction

def encode_host(mnemonic, register):
    mnemonic = mnemonic.upper()

    if mnemonic not in {"PULL", "PUSH"}:
        raise ValueError(
            f"Invalid HOST instruction: {mnemonic}"
        )

    reg_code = parse_register(register)

    direction = 0 if mnemonic == "PULL" else 1

    instruction = (
        (OPCODES["HOST"] << 12)
        | (direction << 11)
        | (reg_code << 9)
    )

    return instruction

