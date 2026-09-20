The first version of this project is intended to be a programmable protocol emulator processor that can execute user-defined programs produced by the custom assembler. These programs will be able to directly address the 8 GPIO pins, which will allow the processor to emulate communication protocols.

Requirements

    8 GPIO bidrectional pins
    16 bit Instruction width
    256 * 16 Instruction memory
    4* 32 bit general register
    8 bit program counter
    Target clock: 100 MHz
    Initial FPGA/debug clock: 50 MHz
    1 validation protocols : SPI, UART, I²C firmware
