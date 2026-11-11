; SPI Mode 0
; GPIO0 = SCLK
; GPIO1 = CS
; GPIO7 = MOSI
;
; Transmit 0xA5 = 10100101

; Configure SCLK, CS, MOSI as outputs
DIR 0x83, OUT

; Idle state
CLR 0x01        ; SCLK = 0
SET 0x02        ; CS = 1

; Data byte
LDI R0, 0xA5

; 8 bits to transmit
LDI R1, 8

; Begin SPI transaction
CLR 0x02        ; CS = 0

bit_loop:

    ; Put current MSB on MOSI
    OUT R0, 0x80

    ; Data setup time
    WAIT 2

    ; Rising edge - receiver samples MOSI
    SET 0x01

    ; Clock high
    WAIT 2

    ; Falling edge
    CLR 0x01

    ; Move next bit into bit 7
    LSHIFT R0, 1

    ; One bit completed
    DEC R1

    ; Continue until all 8 bits transmitted
    BNZ bit_loop

; End transaction
SET 0x02        ; CS = 1

HALT