; UART TX test
; 115200 baud assuming 100 MHz CPU clock
; GPIO0 = TX
;
; Transmit 0x53
;
; 0x53 = 01010011
; UART sends LSB first:
; 1 1 0 0 1 0 1 0

; TX pin is output
DIR 0x01, OUT

; UART idle state is HIGH
SET 0x01

; Byte to transmit
LDI R0, 0x53

; Number of data bits
LDI R1, 8

; -------------------------
; Start bit
; -------------------------

CLR 0x01

; Hold start bit for 868 cycles.
; CLR -> WAIT -> first OUT
; WAIT 867 + instruction transition = 868
WAIT 867


bit_loop:

    ; Output current LSB to GPIO0
    OUT R0, 0x01

    ; The loop itself has instruction overhead:
    ;
    ; WAIT
    ; RSHIFT
    ; DEC
    ; BNZ
    ; next OUT
    ;
    ; Therefore WAIT only needs 864 cycles
    ; to make OUT-to-OUT spacing 868 cycles.
    WAIT 864

    ; Move next UART bit into bit 0
    RSHIFT R0, 1

    ; One fewer bit remaining
    DEC R1

    ; Repeat until 8 bits sent
    BNZ bit_loop


; -------------------------
; Stop bit
; -------------------------

SET 0x01

; Hold stop bit for one full UART bit
WAIT 867

HALT