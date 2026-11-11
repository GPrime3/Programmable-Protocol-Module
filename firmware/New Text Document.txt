; UART RX test
; 115200 baud at 100 MHz
; GPIO0 = RX
;
; Receive one byte, LSB first.
; Final received byte will be stored in R0.

; GPIO0 input
DIR 0x01, IN

; R0 = received byte
LDI R0, 0

; R1 = number of bits remaining
LDI R1, 8

; Wait for UART start bit
WAITPIN GPIO0, LOW

; Move to the middle of the first data bit.
;
; Start bit = 868 cycles
; Half data bit = 434 cycles
; Total = 1302 cycles
;
; WAIT begins one cycle after WAITPIN finishes,
; so WAIT 1301 places IN at the center.
WAIT 1301


bit_loop:

    ; Sample RX into R2 bit 0
    IN R2, 0x01

    ; Move sampled bit to bit 7
    LSHIFT R2, 7

    ; Shift previously received bits right
    RSHIFT R0, 1

    ; Insert new bit into bit 7
    OR R0, R2

    ; One bit received
    DEC R1

    ; Account for instruction overhead so that
    ; successive IN instructions occur every
    ; 868 cycles.
    WAIT 862

    BNZ bit_loop


; We are now in the middle of the stop bit.
; Sample it into R3.
IN R3, 0x01

HALT