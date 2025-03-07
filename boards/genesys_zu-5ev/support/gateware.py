#! /usr/bin/env python3

from migen.build.generic_platform import IOStandard, Pins
from migen.build.xilinx.platform import XilinxPlatform
from migen.fhdl.module import Module
from migen.fhdl.specials import Instance
from migen.fhdl.structure import ClockDomain, Signal
from migen.genlib.resetsync import AsyncResetSynchronizer


class Platform(XilinxPlatform):
    IO = [
        ("pl_leds", 0, Pins("J14"), IOStandard("LVCMOS33")),
        ("pl_leds", 1, Pins("K14"), IOStandard("LVCMOS33")),
        ("pl_leds", 2, Pins("L13"), IOStandard("LVCMOS33")),
        ("pl_leds", 3, Pins("L14"), IOStandard("LVCMOS33")),
    ]

    CONNECTORS = []

    def __init__(self):
        super().__init__(
            "xczu5ev-sfvc784-1-e",
            self.IO,
            self.CONNECTORS,
            name="genesys_zu-5ev",
            toolchain="vivado",
        )

        self.add_platform_command(
            "set_property BITSTREAM.GENERAL.COMPRESS TRUE [current_design]"
        )
        self.add_platform_command("set_property DCI_CASCADE {{64}} [get_iobanks 65]")

        self.toolchain.pre_synthesis_commands.extend(
            [
                "create_ip -vlnv xilinx.com:ip:zynq_ultra_ps_e -module_name zynq_ultra_ps_e_0",
                "set_property -dict [list CONFIG.PSU__USE__M_AXI_GP2 0] [get_ips zynq_ultra_ps_e_0]",
                "synth_ip [get_ips zynq_ultra_ps_e_0]",
            ]
        )


class Top(Module):
    def __init__(self, platform: Platform):
        super().__init__()

        self.pl_resetn0 = Signal()
        self.clock_domains.cd_sys = ClockDomain()
        self.specials += Instance(
            "zynq_ultra_ps_e_0", o_pl_resetn0=self.pl_resetn0, o_pl_clk0=self.cd_sys.clk
        )
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~self.pl_resetn0)

        counter = Signal(30)
        self.sync.sys += counter.eq(counter + 1)

        leds = [platform.request("pl_leds", i) for i in range(4)]
        self.comb += [
            leds[0].eq(counter[29]),
            leds[1].eq(counter[28]),
            leds[2].eq(counter[27]),
            leds[3].eq(counter[26]),
        ]


P = Platform()
M = Top(P)
P.build(M, build_dir="migen-ws", run=True)
