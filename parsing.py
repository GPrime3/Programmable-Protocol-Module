# parsing.py

from isa import REGISTERS


def parse_number(value):
    value = value.strip()

    try:
        return int(value, 0)
    except ValueError:
        raise ValueError(
            f"Invalid numeric value: {value}"
        )


def parse_register(token):
    token = token.strip().upper()

    if token not in REGISTERS:
        raise ValueError(
            f"Invalid register '{token}'. Expected R0-R3."
        )

    return REGISTERS[token]


def parse_gpio_pin(token):
    token = token.strip().upper()

    if not token.startswith("GPIO"):
        raise ValueError(
            f"Invalid GPIO pin: {token}"
        )

    try:
        pin = int(token[4:])
    except ValueError:
        raise ValueError(
            f"Invalid GPIO pin: {token}"
        )

    if not 0 <= pin <= 7:
        raise ValueError(
            "GPIO pin must be GPIO0-GPIO7"
        )

    return pin

def remove_comment(line):
    # Everything after ';' is ignored
    return line.split(";", 1)[0].strip()


def parse_instruction_line(line):
    """
    Example:
        ADD R0, R1

    Returns:
        mnemonic = "ADD"
        operands = ["R0", "R1"]
    """

    line = remove_comment(line)

    if not line:
        return None, []

    parts = line.split(None, 1)

    mnemonic = parts[0].upper()

    if len(parts) == 1:
        return mnemonic, []

    operand_text = parts[1]

    operands = [
        operand.strip()
        for operand in operand_text.split(",")
    ]

    return mnemonic, operands

def is_label(line):
    line = remove_comment(line)

    return line.endswith(":")

def parse_label(line):
    line = remove_comment(line)

    if not line.endswith(":"):
        raise ValueError(
            f"Invalid label definition: {line}"
        )

    label = line[:-1].strip()

    if not label:
        raise ValueError("Empty label")

    return label

