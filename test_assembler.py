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
from parsing import (
    parse_instruction_line,
    parse_label,
)
from assembler import assemble


def test_square_wave():

    source = """
        DIR 0x01, OUT

    loop:
        SET 0x01
        WAIT 5
        CLR 0x01
        WAIT 5
        JMP loop
    """

    expected = [
        0x4E02,
        0x4002,
        0x5005,
        0x4402,
        0x5005,
        0x7001,
    ]

    assert assemble(source) == expected

    print("Square-wave program test passed!")

def run_tests():

    # SYS
    assert encode_sys("NOP") == 0x0000
    assert encode_sys("HALT") == 0x0200

    # LDI
    assert encode_ldi("R0", "8") == 0x1008
    assert encode_ldi("R1", "8") == 0x1408

    # ALU
    assert (
        encode_binary_alu("ADD", "R0", "R1")
        == 0x2100
    )

    assert (
        encode_unary_alu("DEC", "R1")
        == 0x2480
    )

    assert (
        encode_shift("LSHIFT", "R0", "4")
        == 0x2094
    )

    # IO
    assert (
        encode_io("IN", "R0", "0x04")
        == 0x3008
    )

    # GPIO
    assert (
        encode_gpio("SET", "0x01")
        == 0x4002
    )

    assert (
        encode_gpio("CLR", "0x04")
        == 0x4408
    )

    assert (
        encode_gpio("DIR", "0x01", "OUT")
        == 0x4E02
    )

    # WAIT
    assert (
        encode_wait("10")
        == 0x500A
    )

    # WAITPIN
    assert (
        encode_waitpin("GPIO2", "LOW")
        == 0x6400
    )

    assert (
        encode_waitpin("GPIO2", "HIGH")
        == 0x6500
    )

    # BRANCH
    assert (
        encode_branch("JMP", "0x12")
        == 0x7012
    )

    assert (
        encode_branch("BZ", "0x12")
        == 0x7412
    )

    assert (
        encode_branch("BNZ", "0x12")
        == 0x7812
    )

    # HOST
    assert (
        encode_host("PULL", "R0")
        == 0x8000
    )

    assert (
        encode_host("PUSH", "R1")
        == 0x8A00
    )

    print("All encoding tests passed!")


if __name__ == "__main__":
    run_tests()


from parsing import parse_instruction_line

print(parse_instruction_line("ADD R0, R1"))
print(parse_instruction_line("WAIT 10 ; delay"))
print(parse_instruction_line("NOP"))
print(parse_label("loop:"))