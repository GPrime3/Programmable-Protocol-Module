; GPIO0 square-wave test

DIR 0x01, OUT

loop:
    SET 0x01
    WAIT 5

    CLR 0x01
    WAIT 5

    JMP loop