# Vortex

Vortex is an ASIC project exploring hardware acceleration for a
motion-driven, pixelated fluid simulation.

## How it works

The current prototype receives digital inputs and produces an
8-bit output. The existing design is a baseline Tiny Tapeout
example; the FLIP simulation hardware will be developed incrementally.

## How to test

The project uses Cocotb and Icarus Verilog for RTL simulation.
Run the test suite from the test directory:

```bash
cd test
make clean
make
python -m cocotb_tools.check_results results.xml
```
