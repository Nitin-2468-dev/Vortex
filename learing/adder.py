from amaranth import *
from amaranth.sim import Simulator
from amaranth.back import rtlil, verilog
# import amaranth_playground
from amaranth.lib.wiring import In, Out
from amaranth.lib import wiring

class Adder(wiring.Component):
    "Adds to 4 bits value together"

    c_in: In(1) # carry in 1 bit
    a: In(4) # 4 bits for var A
    b: In(4) # 4 bits For var B
    Sum: Out(4) # 4 bits (max sum of var A and var B) (8192 = 4096 + 4096)
    c_out: Out(1) # 1 bit carry out 
        
    def elaborate(self, platfrom):
        m = Module()

        ans = Signal(5)
        m.d.comb +=  ans.eq(cat(self.a, const(0, 1)) +  cat(self.b, const(0, 1)) + cat(self.c_in, const(0, 1)))

        m.d.comb += self.Sum.eq(ans[0:4])
        m.d.comb += self.c_out.eq(ans[4])

        return m


dut = Adder()

async def bench(ctx):
    ctx.set(dut.a, 7)
    ctx.set(dut.b, 8)
    ctx.set(dut.c_in, 1)

    await ctx.delay(1e-6)

    ans = ctx.get(dut.Sum)
    carry = ctx.get(dut.c_out)

    print("A        : " , 7)
    print("B        : " , 8)
    print("Carry in : " , 1)
    print("----------------------")
    print("sum : " , ans , " and Carry : " , carry)

    assert ans == 0
    assert carry == 1
sim = Simulator(dut)
sim.add_testbench(bench)
sim.run()

