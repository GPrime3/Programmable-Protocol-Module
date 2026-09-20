The first version of this project is intended to be a programmable protocol emulator processor that can execute user-defined programs produced by the custom assembler. These programs will be able to directly address the 8 GPIO pins, which will allow the processor to emulate communication protocols.

Requirements

1.  8 GPIO bidrectional pins
2.  16 bit Instruction width
3.  256 * 16 Instruction memory
4.   4* 32 bit general register
5.   8 bit program counter
6.   Target clock: 100 MHz
7.   Initial FPGA/debug clock: 50 MHz
8.   Validation protocols : SPI, UART, I²C firmware
<img width="503" height="521" alt="V1Flowchart" src="https://github.com/user-attachments/assets/7f747f54-63ef-4650-b797-2dbd2fb127fd" />
