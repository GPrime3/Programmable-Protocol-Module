from isa import (
    OPCODES,
    ALU_FUNCTIONS,
    GPIO_FUNCTIONS,
    BRANCH_CONDITIONS,
)

class ProtocolCPU:
    def update_zero_flag(self, value):
        self.z_flag = 1 if value == 0 else 0

    def __init__(self, trace=False):

        self.trace = trace

        # Program counter
        self.pc = 0

        # 4 x 32-bit registers
        self.registers = [0, 0, 0, 0]

        # Zero flag
        self.z_flag = 0

        # GPIO state
        self.gpio_out = 0x00
        self.gpio_oe  = 0x00
        self.gpio_in  = 0x00

        # Processor state
        self.halted = False

        # Timing
        self.cycle_count = 0
        self.wait_counter = 0

        # Instruction memory
        self.instruction_memory = [0] * 256

    def reset(self):

        self.pc = 0

        self.registers = [0, 0, 0, 0]

        self.z_flag = 0

        self.gpio_out = 0x00
        self.gpio_oe = 0x00
        self.gpio_in = 0x00

        self.halted = False

        self.wait_counter = 0
        self.cycle_count = 0

    def load_hex(self, path):

        with open(path, "r") as file:

            address = 0

            for line in file:

                line = line.strip()

                if not line:
                    continue

                instruction = int(line, 16)

                if address >= 256:
                    raise ValueError(
                        "Program exceeds instruction memory"
                    )

                self.instruction_memory[address] = instruction

                address += 1
    
    def fetch(self):

        return self.instruction_memory[self.pc]

    def get_opcode(self, instruction):
        return (instruction >> 12) & 0xF

    def execute_wait(self, instruction):

        count = instruction & 0xFFF

        # Already waiting
        if self.wait_counter > 0:

            self.wait_counter -= 1

            if self.wait_counter == 0:
                self.pc += 1

            return

        # WAIT 0 and WAIT 1 both consume one cycle
        if count <= 1:
            self.pc += 1

        else:
            self.wait_counter = count - 1

    def execute_waitpin(self, instruction):

        pin = (instruction >> 9) & 0b111
        level = (instruction >> 8) & 0b1
        mode = (instruction >> 6) & 0b11

        if mode != 0:
            raise ValueError(
                f"Unsupported WAITPIN mode: {mode:02b}"
            )

        current_level = (self.gpio_in >> pin) & 0b1

        if current_level == level:
            self.pc += 1

    def execute_branch(self, instruction):

        condition = (instruction >> 10) & 0b11
        target = instruction & 0xFF

        # JMP
        if condition == BRANCH_CONDITIONS["JMP"]:
            self.pc = target

        # BZ
        elif condition == BRANCH_CONDITIONS["BZ"]:
            if self.z_flag == 1:
                self.pc = target
            else:
                self.pc += 1

        # BNZ
        elif condition == BRANCH_CONDITIONS["BNZ"]:
            if self.z_flag == 0:
                self.pc = target
            else:
                self.pc += 1

        else:
            raise ValueError(
                f"Unknown branch condition: {condition:02b}"
            )

    def step(self):

        if self.halted:
            return

        instruction = self.fetch()

        opcode = self.get_opcode(instruction)

        if self.trace:
            print(
                f"Cycle={self.cycle_count} "
                f"PC={self.pc:02X} "
                f"Instruction={instruction:04X} "
                f"Opcode={opcode:04b}"
    )

        if opcode == OPCODES["SYS"]:
            self.execute_sys(instruction)

        elif opcode == OPCODES["LDI"]:
            self.execute_ldi(instruction)
        elif opcode == OPCODES["WAITPIN"]:
            self.execute_waitpin(instruction)
        elif opcode == OPCODES["ALU"]:
            self.execute_alu(instruction)
        elif opcode == OPCODES["IO"]:
            self.execute_io(instruction)
        elif opcode == OPCODES["WAIT"]:
            self.execute_wait(instruction)
        elif opcode == OPCODES["GPIO"]:
            self.execute_gpio(instruction)
        elif opcode == OPCODES["BRANCH"]:
            self.execute_branch(instruction)
        else:
            raise ValueError(
                f"Unsupported opcode: {opcode:04b}"
            )

        

        self.cycle_count += 1


    def execute_sys(self, instruction):

        function = (instruction >> 9) & 0b111

        # NOP
        if function == 0b000:
            self.pc += 1

        # HALT
        elif function == 0b001:
            self.halted = True

        else:
            raise ValueError(
                f"Unknown SYS function: {function:03b}"
            )

    def execute_ldi(self, instruction):

        rd = (instruction >> 10) & 0b11

        immediate = instruction & 0x3FF

        self.registers[rd] = immediate

        self.pc += 1

    def execute_io(self, instruction):

        direction = (instruction >> 11) & 0b1
        reg = (instruction >> 9) & 0b11
        mask = (instruction >> 1) & 0xFF

        # IN
        if direction == 0:

            self.registers[reg] = self.gpio_in & mask
            self.update_zero_flag(self.registers[reg])

        # OUT
        else:

            self.gpio_out = (
                (self.gpio_out & (~mask & 0xFF))
                | (self.registers[reg] & mask)
            )

        self.pc += 1
    def execute_gpio(self, instruction):

        function = (instruction >> 10) & 0b11
        argument = (instruction >> 9) & 0b1
        mask = (instruction >> 1) & 0xFF

        # SET
        if function == GPIO_FUNCTIONS["SET"]:

            self.gpio_out |= mask

        # CLR
        elif function == GPIO_FUNCTIONS["CLR"]:

            self.gpio_out &= (~mask & 0xFF)

        # TOGGLE
        elif function == GPIO_FUNCTIONS["TOGGLE"]:

            self.gpio_out ^= mask

        # DIR
        elif function == GPIO_FUNCTIONS["DIR"]:

            if argument == 1:
                # Selected pins become outputs
                self.gpio_oe |= mask

            else:
                # Selected pins become inputs / high-Z
                self.gpio_oe &= (~mask & 0xFF)

        else:
            raise ValueError(
                f"Unknown GPIO function: {function:02b}"
            )

        self.pc += 1

    def execute_alu(self, instruction):

        rd = (instruction >> 10) & 0b11
        rs = (instruction >> 8) & 0b11
        function = (instruction >> 4) & 0b1111
        aux = instruction & 0b1111

    # ADD
        if function == ALU_FUNCTIONS["ADD"]:
            result = (
                self.registers[rd]
                + self.registers[rs]
            ) & 0xFFFFFFFF

            self.registers[rd] = result
            self.update_zero_flag(result)

        # SUB
        elif function == ALU_FUNCTIONS["SUB"]:
            result = (
                self.registers[rd]
                - self.registers[rs]
            ) & 0xFFFFFFFF

            self.registers[rd] = result
            self.update_zero_flag(result)

        # AND
        elif function == ALU_FUNCTIONS["AND"]:
            result = (
                self.registers[rd]
                & self.registers[rs]
            )

            self.registers[rd] = result
            self.update_zero_flag(result)

        # OR
        elif function == ALU_FUNCTIONS["OR"]:
            result = (
                self.registers[rd]
                | self.registers[rs]
            )

            self.registers[rd] = result
            self.update_zero_flag(result)

        # XOR
        elif function == ALU_FUNCTIONS["XOR"]:
            result = (
                self.registers[rd]
                ^ self.registers[rs]
            )

            self.registers[rd] = result
            self.update_zero_flag(result)

        # CMP
        elif function == ALU_FUNCTIONS["CMP"]:

            if self.registers[rd] == self.registers[rs]:
                self.z_flag = 1
            else:
                self.z_flag = 0

        # MOV
        elif function == ALU_FUNCTIONS["MOV"]:
            result = self.registers[rs]

            self.registers[rd] = result
            self.update_zero_flag(result)

        # INC
        elif function == ALU_FUNCTIONS["INC"]:
            result = (
                self.registers[rd] + 1
            ) & 0xFFFFFFFF

            self.registers[rd] = result
            self.update_zero_flag(result)

        # DEC
        elif function == ALU_FUNCTIONS["DEC"]:
            result = (
                self.registers[rd] - 1
            ) & 0xFFFFFFFF

            self.registers[rd] = result
            self.update_zero_flag(result)

        # LSHIFT
        elif function == ALU_FUNCTIONS["LSHIFT"]:
            result = (
                self.registers[rd] << aux
            ) & 0xFFFFFFFF

            self.registers[rd] = result
            self.update_zero_flag(result)

        # RSHIFT
        elif function == ALU_FUNCTIONS["RSHIFT"]:
            result = (
                self.registers[rd] >> aux
            )

            self.registers[rd] = result
            self.update_zero_flag(result)

        else:
            raise ValueError(
                f"Unknown ALU function: {function:04b}"
            )

        self.pc += 1

