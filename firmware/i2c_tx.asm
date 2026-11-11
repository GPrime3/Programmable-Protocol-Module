; =========================================
; I2C transmit one byte: 0xA5
;
; GPIO0 = SCL
; GPIO1 = SDA
;
; Open drain:
; DIR OUT = drive LOW
; DIR IN  = release HIGH
; =========================================

; Output latches must stay LOW
CLR 0x03

; Release bus
DIR 0x03, IN

WAIT 5

; -------------------------
; START
; -------------------------

; SDA LOW while SCL HIGH
DIR 0x02, OUT

WAIT 5

; Pull SCL LOW
DIR 0x01, OUT

; -------------------------
; Setup data
; -------------------------

LDI R0, 0xA5
LDI R1, 8
LDI R3, 0x80

bit_loop:

    ; Copy byte so we can inspect MSB
    MOV R2, R0

    ; Test bit 7
    AND R2, R3

    ; Z = 1 means MSB was 0
    BZ send_zero

send_one:

    ; Logical 1 = release SDA
    DIR 0x02, IN

    JMP bit_ready

send_zero:

    ; Logical 0 = drive SDA LOW
    DIR 0x02, OUT

bit_ready:

    ; Data setup time
    WAIT 3

    ; Release SCL HIGH
    DIR 0x01, IN

    ; Wait until physical SCL is HIGH
    ; Supports clock stretching
    WAITPIN GPIO0, HIGH

    WAIT 3

    ; Pull SCL LOW
    DIR 0x01, OUT

    ; Move next bit into MSB position
    LSHIFT R0, 1

    ; One fewer bit remaining
    DEC R1

    ; Continue until all 8 bits sent
    BNZ bit_loop

; -------------------------
; ACK cycle
; -------------------------

; Release SDA so slave can control it
DIR 0x02, IN

WAIT 3

; Release SCL HIGH
DIR 0x01, IN

WAITPIN GPIO0, HIGH

WAIT 3

; Sample ACK
; ACK = SDA LOW
IN R2, 0x02

; Pull SCL LOW
DIR 0x01, OUT

; -------------------------
; STOP
; -------------------------

; Make sure SDA is LOW
DIR 0x02, OUT

WAIT 3

; Release SCL HIGH
DIR 0x01, IN

WAITPIN GPIO0, HIGH

WAIT 3

; SDA LOW -> HIGH while SCL HIGH
DIR 0x02, IN

WAIT 3

HALT
