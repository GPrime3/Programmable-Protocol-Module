from cpu import ProtocolCPU

def resolve_open_drain(cpu, pin, external_low=False):

    mask = 1 << pin

    # CPU side of the wire:
    # OE = 0 -> released -> pull-up makes it HIGH
    # OE = 1 -> CPU drives gpio_out
    if cpu.gpio_oe & mask:
        cpu_level = (cpu.gpio_out >> pin) & 1
    else:
        cpu_level = 1

    # External device may also pull the line LOW
    external_level = 0 if external_low else 1

    # Open-drain / wired-AND behavior
    return cpu_level & external_level

def update_i2c_inputs(
    cpu,
    slave_scl_low=False,
    slave_sda_low=False
):

    scl = resolve_open_drain(
        cpu,
        0,
        slave_scl_low
    )

    sda = resolve_open_drain(
        cpu,
        1,
        slave_sda_low
    )

    # Clear GPIO0 and GPIO1 input bits
    cpu.gpio_in &= ~0x03

    # Insert actual bus levels
    cpu.gpio_in |= (scl << 0)
    cpu.gpio_in |= (sda << 1)

    return scl, sda



def test_i2c_tx():

    cpu = ProtocolCPU()

    cpu.load_hex(
        "firmware/i2c_tx.hex"
    )

    captured_bits = []

    previous_scl = 1

    rising_edges = 0

    # Slave ACK state
    ack_active = False
    ack_clock_seen = False

    history = []

    while not cpu.halted:

        # Feed actual I2C wire levels into CPU
        update_i2c_inputs(
            cpu,
            slave_sda_low=ack_active
        )

        cpu.step()

        # Resolve lines again after CPU state changes
        scl = resolve_open_drain(
            cpu,
            0
        )

        sda = resolve_open_drain(
            cpu,
            1,
            ack_active
        )

        history.append(
            (
                cpu.cycle_count,
                scl,
                sda
            )
        )

        # ----------------------------------
        # Rising SCL edge
        # ----------------------------------

        if previous_scl == 0 and scl == 1:

            rising_edges += 1

            # First 8 rising edges = data
            if rising_edges <= 8:

                captured_bits.append(sda)

            # 9th rising edge = ACK clock
            elif rising_edges == 9:

                print(
                    "ACK bit:",
                    sda
                )

                # Slave should be holding SDA LOW
                assert sda == 0

                ack_clock_seen = True

        # ----------------------------------
        # Falling SCL edge
        # ----------------------------------

        if previous_scl == 1 and scl == 0:

            # Falling edge after eighth data bit:
            # slave starts driving ACK LOW
            if (
                rising_edges == 8
                and not ack_clock_seen
            ):
                ack_active = True

            # Falling edge after ACK:
            # slave releases SDA
            elif (
                ack_clock_seen
                and ack_active
            ):
                ack_active = False

        previous_scl = scl

    print(
        "I2C transmitted bits:",
        captured_bits
    )

    expected_bits = [
        1, 0, 1, 0,
        0, 1, 0, 1
    ]

    assert captured_bits == expected_bits

    # Master should have sampled ACK LOW
    assert (cpu.registers[2] & 0x02) == 0

    # Bus should finish released / idle
    final_scl = resolve_open_drain(
        cpu,
        0
    )

    final_sda = resolve_open_drain(
        cpu,
        1
    )

    assert final_scl == 1
    assert final_sda == 1

    print(
        "I2C byte transmit + ACK test passed!"
    )


def test_i2c_start_stop():

    cpu = ProtocolCPU()

    cpu.load_hex(
        "firmware/i2c_start_stop.hex"
    )

    history = []

    while not cpu.halted:

        cpu.step()

        scl = resolve_open_drain(cpu, 0)
        sda = resolve_open_drain(cpu, 1)

        history.append(
            (cpu.cycle_count, scl, sda)
        )

    print("\nI2C line history:")

    for cycle, scl, sda in history:
        print(
            f"Cycle={cycle:2} "
            f"SCL={scl} "
            f"SDA={sda}"
        )

    start_found = False
    stop_found = False

    for i in range(1, len(history)):

        _, prev_scl, prev_sda = history[i - 1]
        _, scl, sda = history[i]

        # START:
        # SDA falls while SCL is HIGH
        if (
            prev_sda == 1
            and sda == 0
            and scl == 1
        ):
            start_found = True

        # STOP:
        # SDA rises while SCL is HIGH
        if (
            prev_sda == 0
            and sda == 1
            and scl == 1
        ):
            stop_found = True

    assert start_found
    assert stop_found

    # Bus should finish idle
    assert resolve_open_drain(cpu, 0) == 1
    assert resolve_open_drain(cpu, 1) == 1

    print("I2C START/STOP test passed!")
def test_i2c_clock_stretch():

    cpu = ProtocolCPU()

    cpu.load_hex(
        "firmware/i2c_tx.hex"
    )

    previous_scl = 1

    saw_bus_low = False
    stretch_started = False
    stretch_done = False
    stretch_remaining = 0

    waitpin_pc = None
    stalled_cycles = 0

    while not cpu.halted:

        # After the transaction has started and SCL has
        # already been driven LOW, wait for the master
        # to release SCL for the first data clock.
        master_released_scl = (
            (cpu.gpio_oe & 0x01) == 0
        )

        if (
            saw_bus_low
            and master_released_scl
            and not stretch_started
        ):
            stretch_started = True
            stretch_remaining = 5

        slave_scl_low = (
            stretch_remaining > 0
        )

        # Feed actual bus levels into CPU
        scl, sda = update_i2c_inputs(
            cpu,
            slave_scl_low=slave_scl_low
        )

        old_pc = cpu.pc

        cpu.step()

        # If slave is stretching SCL and PC does not move,
        # WAITPIN is correctly stalling.
        if slave_scl_low:

            if cpu.pc == old_pc:
                stalled_cycles += 1

                if waitpin_pc is None:
                    waitpin_pc = cpu.pc

            stretch_remaining -= 1

            if stretch_remaining == 0:
                stretch_done = True

        # Resolve bus after instruction executes
        scl = resolve_open_drain(
            cpu,
            0,
            slave_scl_low
        )

        if scl == 0:
            saw_bus_low = True

        previous_scl = scl

    print(
        "Clock-stretch stalled cycles:",
        stalled_cycles
    )

    assert stretch_started
    assert stretch_done

    # WAITPIN should have held the CPU for multiple cycles
    assert stalled_cycles > 0

    print(
        "I2C clock stretching test passed!"
    )

def test_spi_tx():

    cpu = ProtocolCPU()

    cpu.load_hex("firmware/spi_tx.hex")

    captured_bits = []
    previous_sclk = 0

    while not cpu.halted:

        cpu.step()

        sclk = cpu.gpio_out & 0x01

        # SPI Mode 0 samples on rising edge
        if previous_sclk == 0 and sclk == 1:

            mosi = (cpu.gpio_out >> 7) & 0x01
            captured_bits.append(mosi)

        previous_sclk = sclk

    assert captured_bits == [
        1, 0, 1, 0,
        0, 1, 0, 1
    ]

    assert cpu.halted is True
    # SCLK should return LOW
    assert (cpu.gpio_out & 0x01) == 0

    # CS should return HIGH
    assert ((cpu.gpio_out >> 1) & 1) == 1
    print("SPI transmit test passed!")

def test_uart_tx():

    BIT_CYCLES = 868

    cpu = ProtocolCPU()

    cpu.load_hex("firmware/uart_tx.hex")

    tx_history = []

    while not cpu.halted:

        cpu.step()

        tx = cpu.gpio_out & 0x01

        tx_history.append(tx)

    # Find falling edge from UART idle HIGH
    # to start bit LOW
    start_cycle = None

    for i in range(1, len(tx_history)):

        if tx_history[i - 1] == 1 and tx_history[i] == 0:
            start_cycle = i
            break

    assert start_cycle is not None

    # Sample middle of start bit
    start_sample = tx_history[
        start_cycle + BIT_CYCLES // 2
    ]

    assert start_sample == 0

    # Sample 8 data bits
    data_bits = []

    for bit in range(8):

        sample_cycle = (
            start_cycle
            + (bit + 1) * BIT_CYCLES
            + BIT_CYCLES // 2
        )

        data_bits.append(
            tx_history[sample_cycle]
        )

    # Sample stop bit
    stop_cycle = (
        start_cycle
        + 9 * BIT_CYCLES
        + BIT_CYCLES // 2
    )

    stop_sample = tx_history[stop_cycle]

    print("UART data bits:", data_bits)
    print("Stop bit:", stop_sample)

    expected_bits = [
        1, 1, 0, 0,
        1, 0, 1, 0
    ]

    assert data_bits == expected_bits
    assert stop_sample == 1

    # Reconstruct byte from LSB-first bits
    received_byte = 0

    for i, bit in enumerate(data_bits):
        received_byte |= bit << i

    print(
        f"Received byte: 0x{received_byte:02X}"
    )

    assert received_byte == 0x53

    print("UART transmit test passed!")

def test_uart_rx():

    BIT_CYCLES = 868
    START_CYCLE = 20

    transmitted_byte = 0x53

    data_bits = [
        (transmitted_byte >> i) & 1
        for i in range(8)
    ]

    cpu = ProtocolCPU()

    cpu.load_hex("firmware/uart_rx.hex")

    while not cpu.halted:

        cycle = cpu.cycle_count

        # UART idle state
        rx = 1

        # Start bit
        if (
            START_CYCLE
            <= cycle
            < START_CYCLE + BIT_CYCLES
        ):
            rx = 0

        else:

            # Data bits
            for bit_index in range(8):

                bit_start = (
                    START_CYCLE
                    + BIT_CYCLES
                    + bit_index * BIT_CYCLES
                )

                bit_end = bit_start + BIT_CYCLES

                if bit_start <= cycle < bit_end:
                    rx = data_bits[bit_index]
                    break

        # Drive GPIO0 externally
        cpu.gpio_in = rx

        cpu.step()

    received_byte = cpu.registers[0] & 0xFF
    stop_bit = cpu.registers[3] & 0x01

    print(
        f"UART RX received byte: "
        f"0x{received_byte:02X}"
    )

    print(
        f"UART RX stop bit: {stop_bit}"
    )

    assert received_byte == 0x53
    assert stop_bit == 1

    print("UART receive test passed!")


test_spi_tx()
test_uart_tx()
test_uart_rx()
test_i2c_start_stop()
test_i2c_tx()
test_i2c_clock_stretch()