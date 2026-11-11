# assembler.py
import sys
from pathlib import Path
from parsing import (
    remove_comment,
    is_label,
    parse_label,
    parse_instruction_line,
)

from encoders import (
    encode_sys,
    encode_ldi,
    encode_binary_alu,
    encode_unary_alu,
    encode_shift,
    encode_io,
    encode_gpio,
    encode_wait,
    encode_waitpin,
    encode_branch,
    encode_host,
)

from isa import (
    SYS_FUNCTIONS,
    BINARY_ALU,
    UNARY_ALU,
    SHIFT_INSTRUCTIONS,
    GPIO_FUNCTIONS,
    BRANCH_CONDITIONS,
)

def first_pass(lines):

    labels = {}

    address = 0

    for line_number, raw_line in enumerate(lines, start=1):

        line = remove_comment(raw_line)

        # Ignore blank lines
        if not line:
            continue

        # Label
        if is_label(line):

            label = parse_label(line)

            if label in labels:
                raise ValueError(
                    f"Line {line_number}: "
                    f"duplicate label '{label}'"
                )

            labels[label] = address

            continue

        # Normal instruction
        address += 1

        if address > 256:
            raise ValueError(
                "Program exceeds 256 instruction words"
            )

    return labels

def encode_instruction(mnemonic, operands, labels):
    mnemonic = mnemonic.upper()

    # SYS
    if mnemonic in SYS_FUNCTIONS:
        if len(operands) != 0:
            raise ValueError(
                f"{mnemonic} takes no operands"
            )

        return encode_sys(mnemonic)

    # LDI
    if mnemonic == "LDI":
        if len(operands) != 2:
            raise ValueError(
                "LDI syntax: LDI Rd, immediate"
            )

        return encode_ldi(
            operands[0],
            operands[1]
        )

    # Binary ALU
    if mnemonic in BINARY_ALU:
        if len(operands) != 2:
            raise ValueError(
                f"{mnemonic} syntax: {mnemonic} Rd, Rs"
            )

        return encode_binary_alu(
            mnemonic,
            operands[0],
            operands[1]
        )

    # Unary ALU
    if mnemonic in UNARY_ALU:
        if len(operands) != 1:
            raise ValueError(
                f"{mnemonic} syntax: {mnemonic} Rd"
            )

        return encode_unary_alu(
            mnemonic,
            operands[0]
        )

    # Shift
    if mnemonic in SHIFT_INSTRUCTIONS:
        if len(operands) != 2:
            raise ValueError(
                f"{mnemonic} syntax: {mnemonic} Rd, amount"
            )

        return encode_shift(
            mnemonic,
            operands[0],
            operands[1]
        )
        # ------------------------
    # ------------------------
# IN / OUT
# ------------------------

    if mnemonic in {"IN", "OUT"}:

        if len(operands) != 2:
            raise ValueError(
                f"{mnemonic} syntax: "
                f"{mnemonic} R, mask"
        )

        return encode_io(
            mnemonic,
            operands[0],
            operands[1]
    )
    # GPIO
    # ------------------------

    if mnemonic in GPIO_FUNCTIONS:

        if mnemonic == "DIR":

            if len(operands) != 2:
                raise ValueError(
                    "DIR syntax: DIR mask, IN/OUT"
                )

            return encode_gpio(
                mnemonic,
                operands[0],
                operands[1]
            )

        else:

            if len(operands) != 1:
                raise ValueError(
                    f"{mnemonic} syntax: "
                    f"{mnemonic} mask"
                )

            return encode_gpio(
                mnemonic,
                operands[0]
            )
            # ------------------------
    # WAIT
    # ------------------------

    if mnemonic == "WAIT":

        if len(operands) != 1:
            raise ValueError(
                "WAIT syntax: WAIT count"
            )

        return encode_wait(
            operands[0]
        )

    # ------------------------
    # WAITPIN
    # ------------------------

    if mnemonic == "WAITPIN":

        if len(operands) != 2:
            raise ValueError(
                "WAITPIN syntax: "
                "WAITPIN GPIOx, HIGH/LOW"
            )

        return encode_waitpin(
            operands[0],
            operands[1]
        )
        # ------------------------
    # ------------------------
# Branches
# ------------------------

    if mnemonic in BRANCH_CONDITIONS:

        if len(operands) != 1:
            raise ValueError(
                f"{mnemonic} syntax: "
                f"{mnemonic} target"
            )

        target = operands[0]

        if target in labels:
            target = str(labels[target])

        else:
            try:
                int(target, 0)

            except ValueError:
                raise ValueError(
                    f"Undefined label '{target}'"
                )

        return encode_branch(
            mnemonic,
            target
        )
        # ------------------------
    # PULL / PUSH
    # ------------------------

    if mnemonic in {"PULL", "PUSH"}:

        if len(operands) != 1:
            raise ValueError(
                f"{mnemonic} syntax: "
                f"{mnemonic} register"
            )

        return encode_host(
            mnemonic,
            operands[0]
        )
    raise ValueError(
        f"Unknown instruction '{mnemonic}'"
    )

def second_pass(lines, labels):

    machine_code = []

    for line_number, raw_line in enumerate(lines, start=1):

        line = remove_comment(raw_line)

        if not line:
            continue

        if is_label(line):
            continue

        try:

            mnemonic, operands = parse_instruction_line(line)

            instruction = encode_instruction(
                mnemonic,
                operands,
                labels
            )

            machine_code.append(instruction)

        except ValueError as error:

            raise ValueError(
                f"Line {line_number}: {error}"
            )

    return machine_code

def assemble(source_text):

    lines = source_text.splitlines()

    labels = first_pass(lines)

    machine_code = second_pass(
        lines,
        labels
    )

    return machine_code

def write_hex(machine_code, output_path):
    with open(output_path, "w") as file:
        for instruction in machine_code:
            file.write(f"{instruction:04X}\n")

def assemble_file(input_path, output_path):

    with open(input_path, "r") as file:
        source_text = file.read()

    machine_code = assemble(source_text)

    write_hex(
        machine_code,
        output_path
    )

    return machine_code

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(
            "Usage: python assembler.py <program.asm>"
        )
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(
            f"Error: file '{input_path}' does not exist."
        )
        sys.exit(1)

    if input_path.suffix.lower() != ".asm":
        print(
            "Error: input file must use the .asm extension."
        )
        sys.exit(1)

    output_path = input_path.with_suffix(".hex")

    try:
        machine_code = assemble_file(
            input_path,
            output_path
        )

    except ValueError as error:
        print(f"Assembly error: {error}")
        sys.exit(1)

    print(
        f"Assembled {len(machine_code)} instructions."
    )

    print(
        f"Output written to: {output_path}"
    )
