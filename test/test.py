import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


# Convert a real number to signed Q12 fixed-point representation.
def to_q12(value):
    raw = round(value * 4096)
    assert -32768 <= raw <= 32767, f"{value} is outside signed 16-bit Q12 range"
    return raw & 0xFFFF


# Expected multiplier result, represented as a 32-bit two's-complement value.
def expected_product(a_raw, b_raw):
    a_signed = a_raw if a_raw < 0x8000 else a_raw - 0x10000
    b_signed = b_raw if b_raw < 0x8000 else b_raw - 0x10000

    # Match the hardware's signed multiplication followed by arithmetic >> 12.
    full_product = a_signed * b_signed
    result = full_product >> 12
    return result & 0xFFFFFFFF


@cocotb.test()
async def test_multiplier_cases(dut):
    dut._log.info("Starting expanded Vortex multiplier tests")

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    async def write_byte(command, data):
        dut.ui_in.value = command
        dut.uio_in.value = data
        await ClockCycles(dut.clk, 1)

    async def read_byte(command):
        dut.ui_in.value = command
        await ClockCycles(dut.clk, 1)
        return int(dut.uo_out.value)

    async def multiply(a_raw, b_raw):
        # Load signed 16-bit operands, low byte first.
        await write_byte(0x10, a_raw & 0xFF)
        await write_byte(0x11, (a_raw >> 8) & 0xFF)
        await write_byte(0x20, b_raw & 0xFF)
        await write_byte(0x21, (b_raw >> 8) & 0xFF)

        # Allow the registered multiplier to capture the new operands.
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, 2)

        commands = [0x40, 0x41, 0x42, 0x43]
        result = 0

        for index, command in enumerate(commands):
            byte = await read_byte(command)
            result |= byte << (8 * index)

        return result

    # Values are raw signed Q12 integers.
    cases = [
        ("positive x positive", to_q12(1.5), to_q12(2.0)),
        ("negative x positive", to_q12(-1.5), to_q12(2.5)),
        ("negative x negative", to_q12(-2.0), to_q12(-3.0)),
        ("zero x positive", to_q12(0.0), to_q12(2.5)),
        ("positive x zero", to_q12(1.25), to_q12(0.0)),
        ("one x one", to_q12(1.0), to_q12(1.0)),
        ("fractional product", to_q12(0.5), to_q12(0.5)),
        ("small negative product", to_q12(-0.5), to_q12(0.25)),
        ("maximum x zero", 0x7FFF, 0x0000),
        ("minimum x zero", 0x8000, 0x0000),
        ("minimum x one", 0x8000, to_q12(1.0)),
        ("maximum x maximum", 0x7FFF, 0x7FFF),
        ("minimum x maximum", 0x8000, 0x7FFF),
    ]

    for name, a_raw, b_raw in cases:
        expected = expected_product(a_raw, b_raw)
        actual = await multiply(a_raw, b_raw)

        dut._log.info(
            f"{name}: a=0x{a_raw:04X}, b=0x{b_raw:04X}, "
            f"result=0x{actual:08X}, expected=0x{expected:08X}"
        )

        assert actual == expected, (
            f"{name} failed: a=0x{a_raw:04X}, b=0x{b_raw:04X}, "
            f"expected 0x{expected:08X}, got 0x{actual:08X}"
        )

    dut._log.info(f"All {len(cases)} multiplier cases passed!")
