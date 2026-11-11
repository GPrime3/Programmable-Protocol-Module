; =========================================
; I2C START / STOP test
;
; GPIO0 = SCL
; GPIO1 = SDA
;
; Open-drain behavior:
; OUT = drive LOW
; IN  = release line -> pull-up makes HIGH
; =========================================

; Make sure output latch is LOW for both pins
CLR 0x03

; Release SCL and SDA
; External pull-ups make both HIGH
DIR 0x03, IN

WAIT 5

; -------------------------
; START condition
; SDA: HIGH -> LOW
; while SCL remains HIGH
; -------------------------

DIR 0x02, OUT

WAIT 5

; Pull SCL LOW
DIR 0x01, OUT

WAIT 5

; -------------------------
; STOP condition
;
; First release SCL HIGH
; SDA remains LOW
; -------------------------

DIR 0x01, IN

WAIT 5

; Release SDA HIGH while SCL HIGH
DIR 0x02, IN

WAIT 5

HALT