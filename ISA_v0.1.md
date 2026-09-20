# Programmable Protocol Emulator ISA 
## 1. Overview
This document defines the initial 16-bit Instruction Set Architecture (ISA) for the programmable protocol emulator processor.
### Architectural assumptions

 
-  **Instruction width:** 16 bits
-  **Primary opcode width:** 4 bits (`[15:12]`)
-  **General-purpose registers:** 4 × 32-bit (`R0`–`R3`)
-  **GPIO pins:** 8 bidirectional pins (`GPIO0`–`GPIO7`)
-  **Instruction memory:** 256 × 16-bit words
-  **Program counter:** 8 bits
-  **Initial status flag:** Zero flag (`Z`)
-  **Target processor clock:** 100 MHz
-  **Normal instruction latency:** 1 cycle unless otherwise specified
The architecture is intended to execute protocol firmware such as UART, SPI, and I²C without dedicated protocol-specific hardware controllers.

---


## 2. Register Encoding
| Bits | Register |
|---|---|
| `00` | `R0` |
| `01` | `R1` |
| `10` | `R2` |
| `11` | `R3` |

All general-purpose registers are 32 bits wide.

  

---

  

## 3. Primary Opcode Map

  

| Opcode `[15:12]` | Instruction Class | Instructions |
|---|---|---|
| `0000` | SYS | `NOP`, `HALT` |
| `0001` | LDI | `LDI` |
| `0010` | ALU | `ADD`, `SUB`, `AND`, `OR`, `XOR`, `CMP`, `MOV`, `INC`, `DEC`, `LSHIFT`, `RSHIFT` |
| `0011` | I/O Data | `IN`, `OUT` |
| `0100` | GPIO Control | `SET`, `CLR`, `TOGGLE`, `DIR` |
| `0101` | WAIT | `WAIT` |
| `0110` | WAITPIN | `WAITPIN` |
| `0111` | BRANCH | `JMP`, `BZ`, `BNZ` |
| `1000` | HOST/FIFO | `PULL`, `PUSH` |
| `1001`–`1111` | Reserved | Future expansion |

  

---

  

# 4. SYS Instruction Class
  

## Instruction Format

  

| Bits | `[15:12]` | `[11:9]` | `[8:0]` |
|---|---|---|---|
| Field | Opcode | Function | Reserved |
| Encoding | `0000` | `Function` | `000000000` |

  

### SYS Function Encoding

  

| Function | Instruction |
|---|---|
| `000` | `NOP` |
| `001` | `HALT` |
| `010`–`111` | Reserved |

  

---

  

## Sub-Instruction: NOP

  

**Syntax**

```asm
NOP
```

  

**Encoding**

  
| Bits | `[15:12]` | `[11:9]` | `[8:0]` |
|---|---|---|---|
| Value | `0000` | `000` | `000000000` |

  

**Operation**

  

```text
PC <- PC + 1
```

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Example**


```asm
NOP
```

  

Useful when an explicit one-cycle delay is required.

  

---

  

## Sub-Instruction: HALT

  

**Syntax**

  

```asm
HALT
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:9]` | `[8:0]` |
|---|---|---|---|
| Value | `0000` | `001` | `000000000` |

  

**Operation**

  

```text
halted <- 1
PC remains at the HALT instruction until reset or an external restart command.
```

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- Enters the halted state after 1 cycle.

- Remains halted indefinitely until restarted.

  

**Example**

  

```asm
HALT
```

  

---

  

# 5. LDI Instruction Class

  

## Instruction: LDI

  

**Syntax**

  

```asm
LDI Rd, Immediate
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:0]` |
|---|---|---|---|
| Field | Opcode | Rd | Immediate |
| Value | `0001` | `Rd` | `IMM10` |

  

**Operation**

  

```text
Rd <- zero_extend(IMM10)
```

  

The 10-bit immediate supports values from `0` to `1023` (`0x000` to `0x3FF`).

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
LDI R0, 0x55
LDI R1, 8
```

  

The first instruction loads `0x55` into `R0`.
The second loads decimal `8` into `R1`.

  

---

  

# 6. ALU Instruction Class

  

## Instruction Format

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Field | Opcode | Rd | Rs | Function | Auxiliary |
| Encoding | `0010` | `Rd` | `Rs` | `Function` | `AUX` |

  

### ALU Function Encoding

  

| Function `[7:4]` | Instruction |
|---|---|
| `0000` | `ADD` |
| `0001` | `SUB` |
| `0010` | `AND` |
| `0011` | `OR` |
| `0100` | `XOR` |
| `0101` | `CMP` |
| `0110` | `MOV` |
| `0111` | `INC` |
| `1000` | `DEC` |
| `1001` | `LSHIFT` |
| `1010` | `RSHIFT` |
| `1011`–`1111` | Reserved |

  

For operations that do not use `Rs` or `AUX`, those fields must be encoded as zero.

  

---

  

## Sub-Instruction: ADD

  

**Syntax**

  

```asm
ADD Rd, Rs
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `Rs` | `0000` | `0000` |

  

**Operation**

  

```text
Rd <- (Rd + Rs) mod 2^32
```

  

**Flags**

  

```text
Z <- 1 if result == 0
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
ADD R0, R1
```

  

Equivalent to:

  

```text
R0 <- R0 + R1
```

  

---

  

## Sub-Instruction: SUB

  

**Syntax**

  

```asm
SUB Rd, Rs
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `Rs` | `0001` | `0000` |

  

**Operation**

  

```text
Rd <- (Rd - Rs) mod 2^32
```

  

**Flags**

  

```text
Z <- 1 if result == 0
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
SUB R2, R1
```

  

Equivalent to:

  

```text
R2 <- R2 - R1
```

  

---

  

## Sub-Instruction: AND

  

**Syntax**

  

```asm
AND Rd, Rs
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `Rs` | `0010` | `0000` |

  

**Operation**

  

```text
Rd <- Rd AND Rs
```

  

**Flags**

  

```text
Z <- 1 if result == 0
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
AND R0, R1
```

  

---

  

## Sub-Instruction: OR

  

**Syntax**

  

```asm
OR Rd, Rs
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `Rs` | `0011` | `0000` |

  

**Operation**

  

```text
Rd <- Rd OR Rs
```

  

**Flags**

  

```text
Z <- 1 if result == 0
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
OR R0, R2
```

  

---

  

## Sub-Instruction: XOR

  

**Syntax**

  

```asm
XOR Rd, Rs
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `Rs` | `0100` | `0000` |

  

**Operation**

  

```text
Rd <- Rd XOR Rs
```

  

**Flags**

  

```text
Z <- 1 if result == 0
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
XOR R3, R0
```

  

---

  

## Sub-Instruction: CMP

  

**Syntax**

  

```asm
CMP Rd, Rs
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `Rs` | `0101` | `0000` |

  

**Operation**

  

```text
temporary <- (Rd - Rs) mod 2^32
Rd and Rs are not modified.
```

  

**Flags**

  

```text
Z <- 1 if Rd == Rs
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
CMP R0, R1
BZ equal
```

  

Branches to `equal` if `R0 == R1`.

  

---

  

## Sub-Instruction: MOV

  

**Syntax**

  

```asm
MOV Rd, Rs
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `Rs` | `0110` | `0000` |

  

**Operation**

  

```text
Rd <- Rs
```

  

**Flags**

  

```text
Z <- 1 if transferred value == 0
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
MOV R0, R2
```

  

Equivalent to:

  

```text
R0 <- R2
```

  

---

  

## Sub-Instruction: INC

  

**Syntax**

  

```asm

INC Rd

```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `00` | `0111` | `0000` |

  

**Operation**

  

```text
Rd <- (Rd + 1) mod 2^32
```

  

**Flags**

  

```text
Z <- 1 if result == 0
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
INC R1
```

  

---

  

## Sub-Instruction: DEC

  

**Syntax**

  

```asm
DEC Rd
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `00` | `1000` | `0000` |

  

**Operation**

  

```text
Rd <- (Rd - 1) mod 2^32
```

  

**Flags**

  

```text
Z <- 1 if result == 0
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
LDI R1, 8
loop:
; protocol operation
DEC R1
BNZ loop
```

  

---

  

## Sub-Instruction: LSHIFT

  

**Syntax**

  

```asm
LSHIFT Rd, Amount
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `00` | `1001` | `Amount` |

  

**Operation**

  

```text
Rd <- (Rd << Amount) mod 2^32
```

`Amount` is a 4-bit unsigned value from `0` to `15`.

  

**Flags**

  

```text
Z <- 1 if result == 0
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
LSHIFT R0, 1
```

  

Equivalent to:

  

```text
R0 <- R0 << 1
```

  

---

  

## Sub-Instruction: RSHIFT

  

**Syntax**

  

```asm
RSHIFT Rd, Amount
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:4]` | `[3:0]` |
|---|---|---|---|---|---|
| Value | `0010` | `Rd` | `00` | `1010` | `Amount` |

  

**Operation**

  

```text
Rd <- Rd >> Amount
```

  

This is a logical right shift; zeros are shifted into the most significant bits.

  

`Amount` is a 4-bit unsigned value from `0` to `15`.

  

**Flags**

  

```text
Z <- 1 if result == 0
Z <- 0 otherwise
```

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
RSHIFT R0, 1
```

  

Useful for serializing data one bit at a time.

  

---

  

# 7. I/O Data Instruction Class

  

## Instruction Format

  

| Bits | `[15:12]` | `[11]` | `[10:9]` | `[8:1]` | `[0]` |
|---|---|---|---|---|---|
| Field | Opcode | Direction | Register | GPIO Mask | Reserved |
| Encoding | `0011` | `DIR` | `R` | `MASK8` | `0` |

  

### Direction Encoding

  

| DIR | Instruction |
|---|---|
| `0` | `IN` |
| `1` | `OUT` |

  

The GPIO mask maps bit-for-bit to the eight GPIO pins:

  

```text
MASK[0] -> GPIO0
MASK[1] -> GPIO1
...
MASK[7] -> GPIO7
```

  

---

  

## Sub-Instruction: IN

  

**Syntax**

  

```asm
IN Rd, Mask
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11]` | `[10:9]` | `[8:1]` | `[0]` |
|---|---|---|---|---|---|
| Value | `0011` | `0` | `Rd` | `MASK8` | `0` |

  

**Operation**

  

```text
Rd <- zero_extend(GPIO_IN[7:0] AND MASK8)
```

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
IN R0, 0x04
```

  

Reads `GPIO2` into bit 2 of `R0`. All unselected bits are written as zero.

  

---

  

## Sub-Instruction: OUT

  

**Syntax**

  

```asm
OUT Rs, Mask
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11]` | `[10:9]` | `[8:1]` | `[0]` |
|---|---|---|---|---|---|
| Value | `0011` | `1` | `Rs` | `MASK8` | `0` |

  

**Operation**

  

For each GPIO bit `i` where `MASK8[i] == 1`:

  

```text
GPIO_OUT[i] <- Rs[i]
```

  

Unselected GPIO output bits are unchanged.

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
OUT R0, 0x0F
```

  

Writes `R0[3:0]` to `GPIO3:GPIO0`.

  

---

  

# 8. GPIO Control Instruction Class

  

## Instruction Format

  

| Bits | `[15:12]` | `[11:10]` | `[9]` | `[8:1]` | `[0]` |
|---|---|---|---|---|---|
| Field | Opcode | Function | Argument | GPIO Mask | Reserved |
| Encoding | `0100` | `FUNC` | `ARG` | `MASK8` | `0` |

  

### GPIO Function Encoding

  

| Function `[11:10]` | Instruction |
|---|---|
| `00` | `SET` |
| `01` | `CLR` |
| `10` | `TOGGLE` |
| `11` | `DIR` |

  

For `SET`, `CLR`, and `TOGGLE`, `ARG` must be `0`.

  

For `DIR`:

  

| ARG | Direction |
|---|---|
| `0` | Input / high-impedance |
| `1` | Output enabled |

  

---

  

## Sub-Instruction: SET

  

**Syntax**

  

```asm
SET Mask
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9]` | `[8:1]` | `[0]` |
|---|---|---|---|---|---|
| Value | `0100` | `00` | `0` | `MASK8` | `0` |

  

**Operation**

  

For each selected GPIO:

  

```text
GPIO_OUT[i] <- 1
```

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
SET 0x01
```

  

Sets `GPIO0` output value high.

  

---

  

## Sub-Instruction: CLR

  

**Syntax**

  

```asm
CLR Mask
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9]` | `[8:1]` | `[0]` |
|---|---|---|---|---|---|
| Value | `0100` | `01` | `0` | `MASK8` | `0` |

  

**Operation**

  

For each selected GPIO:

  

```text
GPIO_OUT[i] <- 0
```

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
CLR 0x04
```

  

Clears `GPIO2` output value.

  

---

  

## Sub-Instruction: TOGGLE

  

**Syntax**

  

```asm
TOGGLE Mask
```

 

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9]` | `[8:1]` | `[0]` |
|---|---|---|---|---|---|
| Value | `0100` | `10` | `0` | `MASK8` | `0` |

  

**Operation**

  

For each selected GPIO:

  

```text
GPIO_OUT[i] <- NOT GPIO_OUT[i]
```

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
TOGGLE 0x01
```

  

Toggles `GPIO0`.

  

---

  

## Sub-Instruction: DIR

  

**Syntax**

  

```asm
DIR Mask, IN
```

  

or

  

```asm
DIR Mask, OUT
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9]` | `[8:1]` | `[0]` |
|---|---|---|---|---|---|
| Value | `0100` | `11` | `ARG` | `MASK8` | `0` |

  

**Operation**

  

If `ARG = 0`:

  

```text
GPIO_OE[i] <- 0 for every selected GPIO
```

  

If `ARG = 1`:

  

```text
GPIO_OE[i] <- 1 for every selected GPIO
```

  

Unselected GPIO direction bits remain unchanged.

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Examples**

  

```asm
DIR 0x04, OUT
DIR 0x04, IN
```

  

The first enables output drive on `GPIO2`.

The second releases `GPIO2` and places it in input/high-impedance mode.

  

This behavior supports open-drain protocols such as I²C by driving a stored `0` when output-enabled and releasing the pin when a logic high is required.

  

---

  

# 9. WAIT Instruction Class

  

## Instruction: WAIT

  

**Syntax**

  

```asm
WAIT Count
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:0]` |
|---|---|---|
| Field | Opcode | Cycle Count |
| Value | `0101` | `COUNT12` |

  

`COUNT12` supports values from `0` to `4095`.

  

**Operation**

  

The processor delays instruction progression for a deterministic number of processor cycles.

  

For `Count > 0`:

  

```text
The interval from the clock edge that begins WAIT
to the clock edge that begins the next instruction
is exactly Count processor cycles.
```

  

`WAIT 0` behaves as a one-cycle no-operation.

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- `Count` cycles when `Count >= 1`

- 1 cycle when `Count = 0`

  

**Example**

  

```asm
SET 0x01
WAIT 50
CLR 0x01
```

  

At a 100 MHz processor clock, `WAIT 50` corresponds to 500 ns.

  

---

  

# 10. WAITPIN Instruction Class

  

## Instruction: WAITPIN

  

**Syntax**

  

```asm
WAITPIN GPIOx, HIGH
```

  

or

  
```asm
WAITPIN GPIOx, LOW
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:9]` | `[8]` | `[7:6]` | `[5:0]` |
|---|---|---|---|---|---|
| Field | Opcode | Pin | Level | Mode | Reserved |
| Value | `0110` | `PIN3` | `LEVEL` | `00` | `000000` |

  

### Pin Encoding

  

| PIN3 | GPIO |
|---|---|
| `000` | GPIO0 |
| `001` | GPIO1 |
| `010` | GPIO2 |
| `011` | GPIO3 |
| `100` | GPIO4 |
| `101` | GPIO5 |
| `110` | GPIO6 |
| `111` | GPIO7 |

  

### Level Encoding

  

| LEVEL | Condition |
|---|---|
| `0` | Wait for LOW |
| `1` | Wait for HIGH |

  

### Mode Encoding

  

| MODE | Meaning |
|---|---|
| `00` | Level wait |
| `01`–`11` | Reserved for future edge/event modes |

  

**Operation**

  

```text
If GPIO_IN[PIN] != LEVEL:
stall processor and hold PC
Else:
PC <- PC + 1
```

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- Minimum 1 cycle.

- Otherwise stalls indefinitely until the selected synchronized GPIO input matches the requested level.

  

**Examples**

  

```asm
WAITPIN GPIO2, LOW
WAITPIN GPIO4, HIGH
```

  

Useful for UART start-bit detection, I²C clock stretching, handshaking, and other asynchronous events.

  

---

  

# 11. BRANCH Instruction Class

  

## Instruction Format

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:0]` |
|---|---|---|---|---|
| Field | Opcode | Condition | Reserved | Target |
| Encoding | `0111` | `COND` | `00` | `TARGET8` |

  

The 8-bit target directly addresses one of the 256 instruction-memory locations.

  

### Branch Condition Encoding

  

| COND | Instruction |
|---|---|
| `00` | `JMP` |
| `01` | `BZ` |
| `10` | `BNZ` |
| `11` | Reserved |

  

---

  

## Sub-Instruction: JMP

  

**Syntax**

  

```asm
JMP Target
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:0]` |
|---|---|---|---|---|
| Value | `0111` | `00` | `00` | `TARGET8` |

  

**Operation**

  

```text
PC <- TARGET8
```

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
loop:
TOGGLE 0x01
WAIT 10
JMP loop
```

  

---

  

## Sub-Instruction: BZ

  

**Syntax**

  

```asm
BZ Target
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:0]` |
|---|---|---|---|---|
| Value | `0111` | `01` | `00` | `TARGET8` |

  

**Operation**

  

```text
if Z == 1:
PC <- TARGET8
else:
PC <- PC + 1
```

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm
CMP R0, R1
BZ equal
```

  

---

  

## Sub-Instruction: BNZ

  

**Syntax**

  

```asm
BNZ Target
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11:10]` | `[9:8]` | `[7:0]` |
|---|---|---|---|---|
| Value | `0111` | `10` | `00` | `TARGET8` |

  

**Operation**

  

```text
if Z == 0:
PC <- TARGET8
else:
PC <- PC + 1
```

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle.

  

**Example**

  

```asm

LDI R1, 8 
loop:
; protocol operation
DEC R1
BNZ loop
```

  

---

  

# 12. HOST/FIFO Instruction Class

  

## Instruction Format

  

| Bits | `[15:12]` | `[11]` | `[10:9]` | `[8:0]` |
|---|---|---|---|---|
| Field | Opcode | Direction | Register | Reserved |
| Encoding | `1000` | `DIR` | `R` | `000000000` |

  

### Direction Encoding

  

| DIR | Instruction |
|---|---|
| `0` | `PULL` |
| `1` | `PUSH` |

  

---

  

## Sub-Instruction: PULL

  

**Syntax**

  

```asm
PULL Rd
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11]` | `[10:9]` | `[8:0]` |
|---|---|---|---|---|
| Value | `1000` | `0` | `Rd` | `000000000` |

  

**Operation**

  

```text
Rd <- TX_FIFO.pop()
```

  

If the TX FIFO is empty, the processor stalls until data is available.

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle when data is available.

- Otherwise stalls until data becomes available.

  

**Example**

  

```asm
PULL R0
```

  

Loads the next host-provided data word into `R0`.

  

---

  

## Sub-Instruction: PUSH

  

**Syntax**

  

```asm
PUSH Rs
```

  

**Encoding**

  

| Bits | `[15:12]` | `[11]` | `[10:9]` | `[8:0]` |
|---|---|---|---|---|
| Value | `1000` | `1` | `Rs` | `000000000` |

  

**Operation**

  

```text
RX_FIFO.push(Rs)
```

  

If the RX FIFO is full, the processor stalls until space is available.

  

**Flags**

  

- No flags modified.

  

**Execution Time**

  

- 1 cycle when space is available.

- Otherwise stalls until FIFO space becomes available.

  

**Example**

  

```asm
PUSH R2
```

  

Transfers `R2` to the host receive FIFO.

  

---

  

# 13. Zero Flag Behavior

  

The initial ISA contains one architectural status flag:

  

```text
Z = Zero Flag
```

  

The following instructions update `Z`:

  

- `ADD`

- `SUB`

- `AND`

- `OR`

- `XOR`

- `CMP`

- `MOV`

- `INC`

- `DEC`

- `LSHIFT`

- `RSHIFT`

  

For result-producing instructions:

  

```text
Z <- 1 if the 32-bit result is zero
Z <- 0 otherwise
```

  

For `CMP`:

  

```text
Z <- 1 if Rd == Rs
Z <- 0 otherwise
```

  

All other V0.1 instructions leave `Z` unchanged.

  

---

  

# 14. GPIO Architectural State

  

The eight physical bidirectional GPIO pins are represented internally by three 8-bit architectural signals:

  

```text
GPIO_OUT[7:0]
GPIO_OE[7:0]
GPIO_IN[7:0]
```

  

### GPIO_OUT

  

Stores the value that will be driven when a pin is configured as an output.

  

### GPIO_OE

  

Controls output enable:

  

```text
GPIO_OE[i] = 1 -> processor actively drives GPIO_OUT[i]
GPIO_OE[i] = 0 -> processor releases the pin / input mode
```

  

### GPIO_IN

  

Contains the synchronized sampled value of each physical GPIO pin.

  

This separation allows protocols such as I²C to implement open-drain signaling:

  

```text
Drive LOW:
GPIO_OUT[SDA] = 0
GPIO_OE[SDA] = 1  
Release HIGH:
GPIO_OE[SDA] = 0
```

  

---

  

# 15. Example Program: Deterministic GPIO Square Wave

  

```asm
; GPIO0 = output
DIR 0x01, OUT
loop:
SET 0x01
WAIT 5
CLR 0x01
WAIT 5
JMP loop
```

  

At a 100 MHz processor clock, each processor cycle is 10 ns. Under the defined `WAIT` semantics, this program can generate a deterministic GPIO waveform whose timing can be predicted directly from instruction execution.

  

---

  

# 16. Example Program: Counted Loop

  

```asm

LDI R1, 8
loop:
TOGGLE 0x01
DEC R1
BNZ loop
HALT
```

  

`DEC` updates the `Z` flag. `BNZ` repeats the loop until `R1` reaches zero.

  

---

  

# 17. Example Program: Register Comparison

  

```asm
LDI R0, 5
LDI R1, 5
CMP R0, R1
BZ equal
HALT
equal:
SET 0x01
HALT
```

  

If `R0` and `R1` contain the same value, `CMP` sets `Z = 1` and `BZ` transfers control to `equal`.

  

---

  

# 18. Reserved Opcode Policy

  

Primary opcodes `1001` through `1111` are intentionally left unused in ISA v0.1.

  

They may later be assigned to features justified by actual protocol workloads, such as:

  

- Generic autonomous timing/toggle hardware

- Extended shift operations

- Event or interrupt handling

- Additional host interfaces

- Memory operations

- Specialized synchronization primitives

  

Reserved encodings must not be generated by the assembler in ISA v0.1.

  

---

  

# 19. ISA v0.1 Design Rule

  

Protocol-specific behavior must be implemented in firmware whenever practical.

  

The processor should not contain instructions or fixed-function hardware named specifically for UART, SPI, I²C, JTAG, or other individual protocols. New hardware features should be added only when they provide a broadly reusable primitive for multiple classes of protocols.
